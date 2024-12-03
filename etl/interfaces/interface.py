import numpy as np
from pylsl import StreamInlet, resolve_streams
from deprecated import deprecated

from config.logs_config import logger_interface
from config.settings import settings


class LslRead:
    """
    Класс для получения данных для работы
    """
    @staticmethod
    def create_inlet_eeg():
        """
        Получение множества объектов входных данных
        используем set для исключения повторяющихся потоков
        """
        logger_interface.info('Start create_inlet_eeg')
        streams = resolve_streams()
        inlets_eeg = {StreamInlet(stream) for stream in streams}

        if len(inlets_eeg) == 0:
            logger_interface.exception('Streams not found')
        return inlets_eeg

    @staticmethod
    @deprecated("Use only if you need to receive one at a time sample")
    def get_eeg(inlet_eeg: StreamInlet, eeg: list) -> tuple[list, list]:
        """
        Добавление и получение списка eeg
        """
        logger_interface.info('Add and get eeg')
        sample, _ = inlet_eeg.pull_sample()

        if sample is None:  # TODO разобраться из за чего выкидывает None после 30 минут записи
            sample = np.zeros(len(eeg[0]))
        eeg_last = eeg.copy()
        eeg.pop(0)
        eeg.append(sample)
        logger_interface.info(f'Eeg  {eeg}')
        return eeg_last, eeg

    @staticmethod
    def get_channel_names(inlet_eeg: StreamInlet, use_impedance: bool = settings.use_impedance) -> list:
        """
        Получение имен для каналов
        :param inlet_eeg: StreamInlet
        :param use_impedance: bool
        :return: list
        """
        stream_info = inlet_eeg.info()
        stream_fs = stream_info.nominal_srate()
        stream_xml = stream_info.desc()
        chans_xml = stream_xml.child("channels")
        chan_xml_list = []
        ch = chans_xml.child("channel")
        while ch.name() == "channel":
            chan_xml_list.append(ch)
            ch = ch.next_sibling("channel")
        channel_names = [ch_xml.child_value("label") for ch_xml in chan_xml_list]
        if not channel_names:
            if use_impedance:
                channel_names = ['Ch:' + str(i) for i in range(int(stream_info.channel_count()))]
            else:
                channel_names = ['Ch:' + str(i) for i in range(int(stream_info.channel_count() / 2))]

        logger_interface.info(f"Reading from inlet named {stream_info.name()} with channels "
                              f"{channel_names} sending data at {stream_fs} Hz")

        return channel_names

    @staticmethod
    def get_impedance_name(inlet_eeg: StreamInlet, use_impedance: bool = settings.use_impedance) -> list:
        """
         Получение имен для импеданса
         :param inlet_eeg: StreamInlet
         :param use_impedance: bool
         :return: list
         """
        stream_info = inlet_eeg.info()
        if use_impedance:
            channel_names_impedance = ['Ch:' + str(i) for i in range(int(stream_info.channel_count()))]
        else:
            channel_names_impedance = ['I:' + str(i) for i in range(int(stream_info.channel_count() / 2))]

        return channel_names_impedance

    @staticmethod
    def create_chunk_sample(inlet_eeg: StreamInlet, timeout: float = 4.0, max_samples: int = settings.max_samples,
                            use_impedance: bool = settings.use_impedance) -> \
            list[list[float]]:
        """
        Создание chunk sample
        """
        logger_interface.info('Start create chunk sample')
        chunk, _ = inlet_eeg.pull_chunk(timeout=timeout, max_samples=max_samples)
        if use_impedance:
            for i in range(len(chunk)):
                chunk[i].extend([0] * len(chunk[i]))
        return chunk


""" Запуск для тестов """
if __name__ == '__main__':
    inlet_set = LslRead().create_inlet_eeg()
    for inlet in inlet_set:
        chunk = LslRead().create_chunk_sample(inlet)
        for i in range(4):
            eeg_last, eeg = LslRead().get_eeg(inlet, chunk)
            chunk = eeg
