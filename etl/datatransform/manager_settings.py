from config.logs_config import logger_manager_settings


class ManagerSettings:
    """Класс настроек фильтрации"""

    def __init__(self):
        self._sampling_frequency: int = 250
        self._notch_filter = {'border': 50}
        self._alpha_filter_frequency = {'low_border': 7, 'high_border': 12}
        self._beta_filter_frequency = {'low_border': 13, 'high_border': 30}
        self._ppf: float = 20
        self._number_of_electrodes_for_filtration: int = 22

    def get_sampling_frequency(self):

        """Получить частоту дискретизации."""
        return self._sampling_frequency

    def set_sampling_frequency(self, value: float = None):
        """
        Установить частоту дискретизации
        """
        if value is None:
            logger_manager_settings.error("sampling_frequency is None.")
        self._sampling_frequency = value

    def get_notch_filter_border(self):
        """Получить верхнюю границу частоты."""
        return self._notch_filter['border']

    def get_alpha_low_border(self):
        """Получить нижнюю границу Альфа-частоты."""
        return self._alpha_filter_frequency['low_border']

    def get_alpha_high_border(self):
        """Получить верхнюю границу Альфа-частоты."""
        return self._alpha_filter_frequency['high_border']

    def get_beta_low_border(self):
        """Получить нижнюю границу Бета-частоты."""
        return self._beta_filter_frequency['low_border']

    def get_beta_high_border(self):
        """Получить верхнюю границу Бета-частоты."""
        return self._beta_filter_frequency['high_border']


    def set_freq(self, f_high: float = 50, f_low: float = 0.5):
        """
        Устанавливает значения границ
        :param f_high: float верхний порог
        :param f_low: float нижний порог
        """
        if f_high is None and f_low is None:
            # logger_manager_settings.error("f_high or f_low is None.")
            raise ValueError("f_high or f_low is None.")
        self._freq_high_border = f_high
        self._freq_low_border = f_low

    def get_number_of_electrodes_for_filtration(self):
        """Получить количество электродов для фильтрации."""
        return self._number_of_electrodes_for_filtration

    def set_get_number_of_electrodes_for_filtration(self, value: int = None):
        """
        Установить количество электродов для фильтрации
        """
        if value is None:
            # logger_manager_settings.error("number_of_electrodes is None.")
            raise ValueError("number_of_electrodes is None.")
        self._number_of_electrodes_for_filtration = value

    def get_ppf(self):
        """Получить коэффициент фильтрации."""
        return self._ppf


    def set_ppf(self, value: int = None):
        """
        Установить коэффициент фильтрации
        """
        if value is None:
            # logger_manager_settings.error("ppf is None.")
            raise ValueError("ppf is None.")
        self._ppf = value
