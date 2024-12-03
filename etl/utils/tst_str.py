"""Пример программы для отправки многоканальных данных по протоколу LSL"""
import random
from random import random as rand
from pylsl import StreamInfo, StreamOutlet, local_clock


def main():
    srate = 250 # Частота дискретизации
    name = 'MNE3' # Название источника потока
    sigtype = 'Random signal' # Название сигнала

    n_channels = 4 # Число каналов
    info = StreamInfo(name, sigtype, n_channels, srate, 'float32', 'MNE device')
    outlet = StreamOutlet(info)
    print("Начало отправки данных...")
    start_time = local_clock()
    sent_samples = 0
    while True:
        elapsed_time = local_clock() - start_time
        required_samples = int(srate * elapsed_time) - sent_samples
        for sample_ix in range(required_samples):
            # Создаем новый набор случайных данных
            mysample = [rand(), rand(), random.uniform(1, 15), random.uniform(1, 15)] # Два канала, но может быть больше
            # Отправка
            outlet.push_sample(mysample)
            print(mysample)

        sent_samples += required_samples


if __name__ == '__main__':
    main()
