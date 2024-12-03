import mne
import numpy as np
import logging
import os
import sys
import warnings
from pylsl import StreamInlet
from deprecated import deprecated

from datatransform.filtration_manager import FiltrationManager
from load_data.load_data import RethinkDB, PostgresqlDB
from config.logs_config import logger_processes_control
from datatransform.processing_manager import ProcessingManager
from interfaces.interface import LslRead
from database_etl.models import DesyncDatas
from config.settings import settings

class DevNullHandler(logging.Handler):
    def emit(self, record):
        pass
# Убрал записи деленя на ноль при калтбровке
if not settings.mne_parameter:
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')
    warnings.filterwarnings('ignore')
    mne_logger = logging.getLogger('mne')
    mne_logger.handlers = [DevNullHandler()]

class TransformData:
    def __init__(self, filtration):
        self.table_initialization: bool = True
        self.five_minute_sample: int = 0
        self.channel_names: list = []
        self.baseline_list: list = []
        self.desync_prev: list = []
        self.filtration: FiltrationManager = filtration
        self.average_baseline = {'Ch_0': {'max': 0, 'min': 0}}

    def work_constantly(self, inlet_data, impedance_names, calibration, desync_data_uuid):
        """
        Бесконечный метод. Всегда обновляет импеданс в RethinkDB
        """
        all_data = LslRead().create_chunk_sample(inlet_data)
        all_data = np.array(all_data)
        impedance = np.around(all_data[-1, len(all_data[0]) // 2:], 2)
        impedance_dict = dict(zip(impedance_names, impedance))
        if calibration:
            self.calibrate_and_record(all_data=all_data, desync_data_uuid=desync_data_uuid, inlet_data=inlet_data,
                                      impedance_dict=impedance_dict)

        else:
            RethinkDB.rethink_update_impedance(desync_data_uuid, impedance_dict)

    def create_mne_raw(self, data_input, sampling_freq: int):
        """Создание Raw объекта библиотеки MNE, который необходим для дальнейшей фильтрации
        :param data_input: массив сырых ЭЭГ данных
        :param sampling_freq: частота дискретизации ЭЭГ сигнала
        """
        n_channels = len(data_input)
        ch_types = ["eeg"] * n_channels
        sampling_freq = sampling_freq  # в Герцах

        info = mne.create_info(n_channels, ch_types=ch_types, sfreq=sampling_freq)

        simulated_raw = mne.io.RawArray(data_input, info)
        return simulated_raw

    def mne_raw_filtration(self, eeg_data, sfreq: int):
        """
        Фильтрация сырых данных ЭЭГ по Альфа и бетта ритму
        :param eeg_data: массив сырых ЭЭГ данных
        :param sfreq: частота дискретизации ЭЭГ сигнала
        """
        """Создание Raw Объекта"""
        simulated_raw = self.create_mne_raw(eeg_data, sfreq)
        eeg_pick = mne.pick_types(simulated_raw.info, eeg=True)

        """Фильтрация данных"""
        raw_notch = simulated_raw.copy().notch_filter(freqs=[50], picks=eeg_pick)  # Вырезаем помехи от электросети
        raw_beta = raw_notch.copy().filter(l_freq=13, h_freq=30)  # 13-30ГЦ Бета ритм
        raw_alpha = raw_notch.copy().filter(l_freq=7, h_freq=13)  # 7-13ГЦ Альфа ритм

        """Преобразуем raw объект обратно в данные ЭЭГ"""
        beta_data = raw_beta.get_data().tolist()
        alpha_data = raw_alpha.get_data().tolist()

        return (alpha_data, beta_data)

    def data_processing(self, eeg_data, average_baseline: dict, sfreq: int):
        """Обработка сырых ЭЭГ с выводом % вероятности motor imagery (desync)
        :param eeg_data: массив сырых ЭЭГ данных
        :param average_baseline: словарь с минимальным и максимальным значением разницы между Альфа и бетта ритмом в каждом канале
        :param sfreq: частота дискретизации ЭЭГ сигнала
        """

        alpha_data, beta_data = self.mne_raw_filtration(eeg_data,sfreq)

        """Итоговый расчёт"""
        desync = ProcessingManager.get_average_difference(alpha_data, beta_data, average_baseline)

        return desync

    def calibrate_and_record(self, all_data, desync_data_uuid, inlet_data, impedance_dict):
        """
        Работает при calibration is True. Обновление данных в RethinkDB и в PostgreSQL
        """
        logger_processes_control.debug(all_data[0])
        data_from_device = all_data[:, :len(all_data[0]) // 2]

        """Обработка данных"""
        desync = self.data_processing(data_from_device.T, self.average_baseline,
                                      self.filtration.settings.get_sampling_frequency())

        """Запись в RethinkDB"""
        desync_dict = dict(zip(self.channel_names, desync))
        if len(self.desync_prev):
            # Todo определиться с выбором среднего значения
            desync_average = np.vstack([self.desync_prev, desync])
            desync_average = np.around(np.mean(desync_average, axis=0), 2)
            self.five_minute_sample += 1
            if self.five_minute_sample == settings.five_minute_sample:
                desync_dict_average = dict(zip(self.channel_names, desync_average))
                PostgresqlDB.update_desync_data(desync_data_uuid, desync_dict_average, DesyncDatas)
                self.five_minute_sample = 0
        self.desync_prev = desync
        logger_processes_control.debug(desync_dict)
        RethinkDB.rethink_update_data(inlet_data, desync_dict, impedance_dict)

    @deprecated
    def get_baseline_old(self, inlet_data: StreamInlet, time_calibration: float):
        """
        Поиск baseline для десинхронизации
        """
        channel_names = LslRead().get_channel_names(inlet_data)

        all_data = LslRead().create_chunk_sample(inlet_data, timeout=time_calibration + 1.0,
                                                 max_samples=int(time_calibration * 250))
        logger_processes_control.debug(all_data[0])
        all_data = np.array(all_data)
        data_from_device = all_data[:, :len(all_data[0]) // 2]

        baseline_list = np.around(np.mean(data_from_device, axis=0), 2)
        baseline = dict(zip(channel_names, baseline_list))
        RethinkDB.rethink_update_baseline(inlet_data, baseline)
        self.channel_names, self.baseline_list = channel_names, baseline_list

    @deprecated
    def get_average_baseline(self, inlet_data: StreamInlet, time_calibration: float):

        channel_names = LslRead().get_channel_names(inlet_data)
        all_data = LslRead().create_chunk_sample(inlet_data, timeout=time_calibration + 1.0,
                                                 max_samples=int(time_calibration * 250))

        logger_processes_control.debug(all_data[0])

        all_data = np.array(all_data)
        data_from_device = all_data[:, :len(all_data[0]) // 2]
        alpha_data = np.array(
            self.filtration.data_filtration(data_from_device, self.filtration.settings.get_alpha_low_border(),
                                            self.filtration.settings.get_alpha_high_border()))
        beta_data = np.array(
            self.filtration.data_filtration(data_from_device, self.filtration.settings.get_beta_low_border(),
                                            self.filtration.settings.get_beta_high_border()))

        average_a_array = ProcessingManager.get_average_all_channel_segments(alpha_data, settings.max_samples)
        average_b_array = ProcessingManager.get_average_all_channel_segments(beta_data, settings.max_samples)

        difference_average = average_a_array - average_b_array
        average_baseline = []  # TODO По сути не информативна, можно переделать запись на максимальное и минимальное значение разницы
        for average_difference_channel in difference_average:
            mean_channel_difference = np.mean(average_difference_channel)
            average_baseline.append(mean_channel_difference)

        self.average_baseline = {'max': np.max(difference_average), 'min': np.min(difference_average)}

        baseline = dict(zip(channel_names, average_baseline))
        RethinkDB.rethink_update_baseline(inlet_data, baseline)
        self.channel_names, self.baseline_list = channel_names, average_baseline

    def get_average_baseline_mne(self, inlet_data: StreamInlet, time_calibration: float):
        """
        Расчёт базовых значений минимальных и максимальных разницы между Альфа и бетта ритмом в каждом канале
        :return: float
        """
        """Получение данных"""
        channel_names = LslRead().get_channel_names(inlet_data)
        all_data = LslRead().create_chunk_sample(inlet_data, timeout=time_calibration + 1.0,
                                                 max_samples=int(time_calibration * 250))

        logger_processes_control.debug(all_data[0])

        all_data = np.array(all_data)
        data_from_device = all_data[:, :len(all_data[0]) // 2]

        '''Процес фильтрации данных по Альфа и Бета ритму'''
        alpha_data, beta_data = self.mne_raw_filtration(data_from_device.T, self.filtration.settings.get_sampling_frequency())

        """считаем мощности по разным каналам разных ритмов"""
        average_a_array = ProcessingManager.get_average_all_channel_segments(alpha_data, settings.max_samples)
        average_b_array = ProcessingManager.get_average_all_channel_segments(beta_data, settings.max_samples)

        difference_average = average_a_array - average_b_array

        """Ищем минимальные и максимальные значения разниц между Альфа и бета ритмами в каждом канале"""
        average_baseline = []  # TODO По сути не информативна, можно переделать запись на максимальное и минимальное значение разницы
        for i in range(len(difference_average)):
            mean_channel_difference = np.mean(difference_average[i])
            average_baseline.append(mean_channel_difference)
            self.average_baseline[f'Ch_{i}'] = {'max': np.max(difference_average[i]),
                                                'min': np.min(difference_average[i])}

        """Запись данных в RethinkDB"""
        baseline = dict(zip(channel_names, average_baseline))
        RethinkDB.rethink_update_baseline(inlet_data, baseline)
        self.channel_names, self.baseline_list = channel_names, average_baseline
