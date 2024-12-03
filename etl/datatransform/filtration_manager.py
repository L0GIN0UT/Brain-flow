from http import HTTPStatus
from http.client import HTTPException

import numpy as np
from scipy.fftpack import rfft, irfft

from datatransform.manager_settings import ManagerSettings
from config.logs_config import logger_filtration_manager
from deprecated import deprecated


class FiltrationManager:
    """Фильтрация данных"""

    def __init__(self):
        # Атрибуты
        self.raw_data: list[float] = []
        self.filtered_data: list[float] = []
        self.settings = ManagerSettings()

    def ppf_calculate(self, eeg_data) -> float:
        """Раcсчет ppf"""
        return len(eeg_data) / (self.settings.get_sampling_frequency() / 2)

    @deprecated
    def data_filtration(self, selection: list, freq_low_border: int, freq_high_border: int) -> list:
        """Фильтрация сырых данных"""

        y_fft = []

        try:
            transposed_matrix = np.array(selection).T[0:self.settings.get_number_of_electrodes_for_filtration()]
        except ValueError as e:
            logger_filtration_manager.error(f"transposed_matrix: Value error - {selection}_____ERROR:{e}")
            return

        for i in transposed_matrix:
            try:
                i_rfft = rfft(i)  # Дискретное преобразование Фурье действительной последовательности.
                i_rfft[:int(freq_low_border * self.settings.get_ppf())] = 0
                i_rfft[int(freq_high_border * self.settings.get_ppf()):] = 0
                i_irfft = irfft(i_rfft)  # обратное дискретное преобразование Фурье действительной последовательности
                y_fft.append(i_irfft)
            except ValueError:
                logger_filtration_manager.error(f"CYCLE: Value error - {selection}")
                return

        return y_fft
