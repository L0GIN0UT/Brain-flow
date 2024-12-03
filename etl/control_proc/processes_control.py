from multiprocessing import Process, Event

from pylsl import StreamInlet

from load_data.load_data import RethinkDB, PostgresqlDB
from config.logs_config import logger_processes_control
from datatransform.filtration_manager import FiltrationManager
from interfaces.interface import LslRead
from control_proc.changefeed import change_feed
from control_proc.transform_data import TransformData


class ControlProcesses:
    def __init__(self):
        self.process_list: dict = dict()
        self.streams_dict: dict = dict()
        self.filtration = FiltrationManager()
        self.time_calibration: int = 0

    def start_stop_process(self):
        """
         Запуск и остановка процессов
         """
        while True:
            """ Тут слушаем таблицу dev_desync rethink """
            dict_change = change_feed()
            device_name = dict_change.get('device')
            calibration = dict_change.get('calibration')
            desync_data_uuid = dict_change.get('desync_data_uuid')
            status = dict_change.get('status')
            self.time_calibration = dict_change.get('time_calibration')
            if status:
                if calibration:
                    RethinkDB.rethink_status_state(device=device_name, research_status='in_process')
                    if not self.stop_process(device_name):
                        break
                # self.time_calibration = time_calibration
                self.start_process(device_name, calibration, desync_data_uuid)
            else:
                if self.stop_process(device_name):
                    RethinkDB.rethink_calibration_false(device_name)
                    RethinkDB.rethink_status_state(device=device_name, research_status='close')


    def get_streams_dict(self) -> dict:
        """
         Получение словаря с именами каналов и значений
         :return: dict
         """
        streams_list = LslRead().create_inlet_eeg()
        self.streams_dict = {stream.info().name(): stream for stream in streams_list}
        return self.streams_dict

    def start_process(self, device_name: str, calibration: bool, desync_data_uuid: str):
        """
        Старт процесса. Запуск устройства
        """
        process = self.process_list.get(device_name)
        if not process:

            stream = self.streams_dict.get(device_name, None)

            if not stream:
                # возможность добавить новое устройство, resolved ещё раз
                self.streams_dict = self.get_streams_dict()
                stream = self.streams_dict.get(device_name, None)
            if stream:
                p = Process(name=device_name, target=self.transform_load_data,
                            args=(stream, calibration, desync_data_uuid))
                self.process_list[device_name] = p
                p.start()
                logger_processes_control.info(f'The process {device_name} is started')
            else:
                logger_processes_control.error(f'Stream {device_name} not found')
                RethinkDB.rethink_status_false(device_name)
        logger_processes_control.info(f'The {device_name} process is already running')

    def stop_process(self, device_name: str):
        """
        Остановка процесса по имени девайса
        """
        process = self.process_list.get(device_name)
        # if process:
        try:
            process.terminate()
            del self.process_list[device_name]
            logger_processes_control.info(f'The process {device_name} is stopped')
            return True
        except Exception as e:
            logger_processes_control.error(f'Process {device_name} error: ', e)
            return None
        # else:
        #     logger_processes_control.error(f'Process {device_name} not found')

    def transform_load_data(self, inlet_data: StreamInlet, calibration: bool, desync_data_uuid: str) -> None:
        """
        Вызывается при работе с устройством
        """
        transform_data = TransformData(self.filtration)
        if calibration:
            transform_data.get_average_baseline_mne(inlet_data=inlet_data, time_calibration=self.time_calibration)
        impedance_names = LslRead.get_impedance_name(inlet_data)
        while True:
            transform_data.work_constantly(inlet_data=inlet_data, impedance_names=impedance_names,
                                           calibration=calibration, desync_data_uuid=desync_data_uuid)
