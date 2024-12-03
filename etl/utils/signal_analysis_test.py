import mne
from mne.datasets import eegbci
from mne.io import concatenate_raws, read_raw_edf
from mne.channels import make_standard_montage
import matplotlib
import pathlib

import numpy as np
from matplotlib import pyplot as plt

# from config.settings import settings
from scipy.fftpack import rfft, irfft

from datatransform.processing_manager import ProcessingManager


def calculate_desync_and_average_old(data_input, baseline, average_out, desync_out, segment_size=750):
    """
        Рассчитать десинхронизацию и среднюю мощность по старому алгоритму
        :param data_input: массив данных с одного канала, на котором планируется анализ
        :param baseline: базовое значение средней мощности, для процентного сравнения новых значений
        :param average_out: выходной массив для значений средних мощностей
        :param desync_out: выходной массив для значений десинхронизации
        :param segment_size: размер сегмента (в нашем случае 750 т.к. берём данные за 3 сек при s.r.= 250)
    """
    # количество сегментов в оригинальном массиве
    num_segments = len(data_input) // segment_size

    # массив сегментов
    segments_array = np.array([data_input[i * segment_size:(i + 1) * segment_size] for i in range(num_segments)])

    for i in segments_array:
        chunk_average = ProcessingManager.get_average_power(i)
        average_out.append(chunk_average)

        chunk_desync = chunk_average / baseline * 100  # процент
        desync_out.append(chunk_desync)


def create_mne_raw(data_input, sfreq):
    n_channels = len(data_input)
    ch_types = ["eeg"] * n_channels
    sampling_freq = sfreq  # in Hertz
    info = mne.create_info(n_channels, ch_types=ch_types, sfreq=sampling_freq)
    simulated_raw = mne.io.RawArray(data_input, info)
    return simulated_raw


def calculated_discrete_sampled_signal(raw):
    """Создать массив данных ээг,где 1- движение, 0- отсутствие движения, 0.5- обновременное наличие меток движения и его отсутствия
    :param raw: объект mne.raw
    :return sampled_signal проанализированная версия сигнала
    """
    # Создание массива для меток движений
    discrete_signal = np.zeros(len(raw.times))
    print(raw.annotations.description)
    # Установка меток для движения руками (T1) и движения ногами (T2), для 0 не задаём т.к. массив уже нулевой
    for annot in raw.annotations:
        if annot['description'] == 'T1' or annot['description'] == 'T2':
            # Получение времени начала и окончания события в сэмплах
            start_sample = int(raw.time_as_index(annot['onset'], use_rounding=True))
            end_sample = int(raw.time_as_index(annot['onset'] + annot['duration'], use_rounding=True))

            # Установка метки 1 в соответствующих семплах
            discrete_signal[start_sample:end_sample + 1] = 1  # Нужно проверить корректность +1

    # Итерация по участкам по 750 семплов
    sample_size = 750
    sampled_signal = np.zeros(int(len(discrete_signal) / sample_size))
    i = 0
    for start_sample in range(0, len(discrete_signal),
                              sample_size):  # в конце мы выходим за пределы массива,но питон не ругается и мы не будем =)
        end_sample = start_sample + sample_size
        analysis_samples = discrete_signal[start_sample:end_sample]
        # Проверка наличия меток T1 или T2 в участке
        if analysis_samples.sum() // len(analysis_samples):
            print("T1 or T2")
            sampled_signal[i] = 1
        # Проверка наличия меток T0 в участке
        elif not (analysis_samples.sum() // len(analysis_samples)):
            if analysis_samples.sum() > 0:
                print("T1 or T2 and T0")
                sampled_signal[i] = 0.5
                i += 1
                continue  # тут запарывается счётчик
            print("T0")
            sampled_signal[i] = 0
        i += 1
    # Вывод результата
    return sampled_signal


# Записи по моторному воображению с MNE датасета
subject = 1
runs = [6, 10, 14]  # Моторное воображение: Рука и нога
raw_fnames = eegbci.load_data(subject, runs)
raw = concatenate_raws([read_raw_edf(f, preload=True) for f in raw_fnames])

# Установка корректных названий каналов
eegbci.standardize(raw)
montage = make_standard_montage("standard_1005")
raw.set_montage(montage)

raw.resample(250)  # для подъёма частоты дискретизации исходных данных со 160 до 250

raw.load_data()  # Сохраняем raw объект в память(помоему), необходимо для обработки больших файлов
eeg_pick = mne.pick_types(raw.info, eeg=True)  # список количества ЭЭГ каналов

## Для теста создания raw
# print(raw.info)
# simulated_raw = create_mne_raw(raw.get_data()[:, :], 250)

# Тест для создания дискретного сигнала по меткам
discrete_signal = calculated_discrete_sampled_signal(raw)

# Фильтрация
raw_notch = raw.copy().notch_filter(freqs=[50], picks=eeg_pick)  # Вырезаем помехи от электросети
raw_beta = raw_notch.copy().filter(l_freq=13, h_freq=30)  # 13-30ГЦ Бета ритм
raw_alpha = raw_notch.copy().filter(l_freq=7, h_freq=13)  # 7-13ГЦ Альфа ритм

beta_c3 = raw_beta.get_data(picks=['C3']).flatten()
alpha_c3 = raw_alpha.get_data(picks=['C3']).flatten()

# проводим расчёты десинхронизации классическим методом

# базлайны по всей длине записи 1 канала
baseline_a = ProcessingManager.get_average_power(alpha_c3)
baseline_b = ProcessingManager.get_average_power(beta_c3)

# Массивы для визуализации с полученными в ходе расчётов данными
chunks_average_a = []
chunks_desync_a = []

chunks_average_b = []
chunks_desync_b = []

# Расчёт "дессинхронизации"
calculate_desync_and_average_old(alpha_c3, baseline_a, chunks_average_a, chunks_desync_a)
calculate_desync_and_average_old(beta_c3, baseline_b, chunks_average_b, chunks_desync_b)

chunks_average_a = np.array(chunks_average_a)
chunks_average_b = np.array(chunks_average_b)

# Вычитание мощностей
average_difference = chunks_average_a - chunks_average_b

# Поиск минимума и максимума
average_min = np.min(average_difference)
average_max = np.max(average_difference)

# Подсчёт процентов
average_in_percentages = np.array(
    [100 * (1 - (average_i - average_min) / (average_max - average_min)) for average_i in average_difference])

# Визуализация
fig, axs = plt.subplots(nrows=4, ncols=1)

axs[0].plot(chunks_average_a, marker='o', linestyle='-', color='r', label='desync_a')
axs[0].plot(chunks_average_b, marker='o', linestyle='-', color='b', label='desync_b')
axs[1].plot(average_difference, marker='o', linestyle='-', color='g', label='average_difference')
axs[2].plot(discrete_signal, marker='o', linestyle='-', color='black', label='discrete_signal')
axs[3].plot(average_in_percentages, marker='o', linestyle='-', color='y', label='average_in_percentages')

# Добавление легенды (лейблы)
axs[0].legend()
axs[1].legend()
axs[2].legend()
axs[3].legend()

# Включаем сетку
axs[0].grid(True)
axs[1].grid(True)
axs[2].grid(True)
axs[3].grid(True)

plt.show(block=True)
