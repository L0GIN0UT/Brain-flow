"""
Путем возведения в квадрат, получаем мощность сигнала и анализируем разности между пиками этой мощности. В результате,
получаем массив значений разниц и вычисляем их среднее значение. Это среднее значение можно назвать средней разностью
мощности по выборке разниц между пиками. Очертив эту величину, мы можем определить, связана ли она с десинхронизацией
или с синхронизацией только при сравнении с базовой линией.
"""

import numpy as np
from scipy.signal import find_peaks
from deprecated import deprecated


class ProcessingManager:
    def __init__(self):
        # Атрибуты
        self.old_desynch: list[float] = []
        self.corr_global: dict = {'Fp1': 0, 'Fp2': 0, 'F7': 0, 'F3': 0, 'Fz': 0, 'F4': 0, 'F8': 0, 'T3': 0, 'C3': 0,
                                  'Cz': 0, 'C4': 0, 'T4': 0, 'T5': 0, 'P3': 0, 'Pz': 0, 'P4': 0, 'T6': 0, 'Po3': 0,
                                  'O1': 0, 'Oz': 0, 'O2': 0,
                                  'Po4': 0}  # Последние значения корелляций по всем электродам
        self.label_electrodes: list = ['Fp1', 'Fp2', 'F7', 'F3', 'Fz', 'F4', 'F8', 'T3', 'C3', 'Cz', 'C4', 'T4', 'T5',
                                       'P3', 'Pz', 'P4', 'T6', 'Po3', 'O1', 'Oz', 'O2',
                                       'Po4']

    # Расчёт десинхронизации основанный на поиска средней мощности в ЭЭГ данных

    @staticmethod
    def squaring_list(eeg_list: list[float]) -> list[float]:
        """
        возводим в квадрат каждую выборку амплитуды для получения выборок мощности\n
        Возводит значения листа в квадрат
        :param eeg_list: данные ЭЭГ для преобразования,
        :return: list
        """

        square_eeg_list = [x ** 2 for x in eeg_list]
        return square_eeg_list

    @staticmethod
    def find_peaks(eeg_list: list[float]) -> np.ndarray[float]:
        """
        Находит пиковые значения мощности в данных ЭЭГ
        :param eeg_list: данные ЭЭГ для поиска пиков,
        :return: list
        """

        peaks, _ = find_peaks(eeg_list)
        return peaks

    @staticmethod
    def calculate_difference(array: np.ndarray[float]) -> np.ndarray[float]:
        """
        Получаем массив с разницами между пиками мощности\n
        Находит разность между соседними значениями в массиве, стоит учитывать,
        что размерность выходного массива меньше входного\n

        >>x = np.array([1, 2, 4, 7, 0])\n
        >>np.diff(x)\n
        array([ 1,  2,  3, -7])\n

        param array: массив со значениями разности мощности между соседними пиками мощности,
        :return: ndarray
        """

        diff = np.diff(array)
        return diff

    @staticmethod
    def calculate_average(array: np.ndarray[float]) -> float:
        """
        Рассчитываем среднюю разность мощности по массиву с разницами мощности между пиками мощности /n
        рассчитывает среднее значение в массиве
        param float: среднее значение десинхронизации в данных ЭЭГ
        :return: ndarray
        """

        average = np.average(array)
        return average

    @staticmethod
    def get_average_power(eeg_list: list[float]) -> float:
        """
        Выполняет все необходимые операции для расчёта средней разности мощности в данных ЭЭГ
        param eeg_list: данные ЭЭГ для расчёта средней разности мощности,
        :return: float
        """

        squares_list = ProcessingManager.squaring_list(eeg_list)
        peaks = ProcessingManager.find_peaks(squares_list)
        diff = ProcessingManager.calculate_difference(peaks)
        average = ProcessingManager.calculate_average(diff)

        return average

    @staticmethod
    def get_desync(eeg_list: list[list[float]], baseline_list: np.ndarray) -> dict:

        """
        Выполняет необходимые операции для расчёта средней разности мощности в данных ЭЭГ, формируя словарь формата
         {'Електрод': значение} на выходе
        param electrodes_list: словарь с именами электродов, eeg_list: данные ЭЭГ для расчёта десинхронизации
        :return: dict
        """

        average_power = [ProcessingManager.get_average_power(eeg) for eeg in eeg_list]
        # Добавить расчет десинхронизации относительно baseline
        average_power = np.array(average_power)
        desync = np.around(average_power / baseline_list, 2)

        return desync

    @staticmethod
    def get_average_difference(eeg_list_a: list[list[float]], eeg_list_b: list[list[float]], average_baseline):
        """
        Рассчитать разницу средних мощностей
        :param eeg_list_a: массив данных с отфильтрованных по Альфа-ритму
        :param eeg_list_b: массив данных с отфильтрованных по Бета-ритму
        :param average_min: минимальное значение разности средних мощностей при каллибровке
        :param average_max: максимальное значение разности средних мощностей при каллибровке
        """

        average_power_a = [ProcessingManager.get_average_power(eeg) for eeg in eeg_list_a]
        average_power_b = [ProcessingManager.get_average_power(eeg) for eeg in eeg_list_b]

        average_a = np.array(average_power_a)
        average_b = np.array(average_power_b)
        average = average_a - average_b

        # Конвертирует значение в проценты относительно минимального и максимального значений
        # percentage = 100 * (1 - (value - min_value) / (max_value - min_value))
        '''
        # Пример использования
        
        # Изначальные значения
        min_value = 3
        max_value = 10
        
        #Реализация
        value = 3
        percentage = 100 * (1 - (value - min_value) / (max_value - min_value))
        print(f"{value_1} соответствует {percentage:.2f}% на шкале.")
        '''
        average_in_percentages = np.array(
            [100 * (1 - (average[i] - average_baseline.get(f'Ch_{i}', {}).get('min', None)) / (
                    average_baseline.get(f'Ch_{i}', {}).get('max', None) - average_baseline.get(
                f'Ch_{i}', {}).get('min', None))) for i in range(len(average))])

        return average_in_percentages

    @staticmethod
    def get_average_all_channel_segments(eeg_data, sample_segment_size):
        """
        Разбиваем входные данные на каналы, каналы делим на сегменты, считаем среднюю мощность по сегментам.
        :param eeg_data: массив данных ЭЭГ количество каналов -строки, значения биопотенциала канала-столбцы
        :param sample_segment_size: длина сегмента в семплах (см. частоту дискретизации - 250,500,1000 и т.д. и умножай на длительность сегмента - 250Гц * 3сек. = 750 семплов)
        """
        # Получаем сдесь для создания пустого массива подходящего размера
        num_segments = len(eeg_data[0]) // sample_segment_size
        average_all_channel = np.zeros((0, num_segments))

        for num_channel in range(len(eeg_data)):

            # разбивает всю запись на массив из N сегментов, каждый с количеством семплов == segment_size
            segments_array = np.array(
                [eeg_data[num_channel][i * sample_segment_size:(i + 1) * sample_segment_size] for i in range(num_segments)])

            # Рассчитываем среднюю мощность для каждого сегмента выбранного канала
            average_channel = np.array([])
            for segments in segments_array:
                chunk_average = ProcessingManager.get_average_power(segments)
                average_channel = np.append(average_channel, chunk_average)

            average_all_channel = np.vstack([average_all_channel, average_channel])
        return average_all_channel

    # Старый расчёт десинхронизации

    @staticmethod
    @deprecated("Obsolete method for calculating desynchronization")
    def get_percent(number: float, percent: float) -> float:
        """
        Возвращает процент от числа
        :param number: float число
        :param percent: float процент
        :return: float процент от числа
        """
        return number - (number * percent / 100.0)

    @deprecated("Obsolete method for calculating desynchronization")
    def get_old_desynch(self):
        return self.old_desynch

    @deprecated("Obsolete method for calculating desynchronization")
    def set_old_desynch(self, value):
        self.old_desynch = value

    @deprecated("Obsolete method for calculating desynchronization")
    def calculate_desynchronization(self, eeg_list) -> list:
        """
        Считает дeсинхронизацию в заданных ЭЭГ данных
        :param eeg_list: ЭЭГ данные
        :return: list возвращает величену дeсихронизации в заданных ЭЭГ данных
        """
        # Длина семпла зависит от метода get_percent, расчет идет в процентном соотношении

        desync = []
        for e in range(len(eeg_list)):
            sample_previous = eeg_list[e][200:225]
            sample_now = eeg_list[e][225:250]
            corr = round(np.corrcoef(sample_previous, sample_now)[0, 1], 2)
            desync.append(corr)
        return desync

    @deprecated("Obsolete method for calculating desynchronization")
    def calculate_corr(self, size, new_desynch) -> dict:
        """
        Считает корреляцию потока
        :param filtred_eeg: отфильтрованный поток
        :param new_desynch: новый дисихронизованный поток
        :return: dict возвращает корреляцию потока
        """
        for e in range(size):
            if len(self.get_old_desynch()) != 0:
                self.corr_global[f'{self.label_electrodes[e]}'] = (self.get_old_desynch()[e] - new_desynch[e])
        self.set_old_desynch(new_desynch)
        return self.corr_global
