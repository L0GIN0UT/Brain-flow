# import pathlib
#
# import matplotlib.pyplot as plt
# from mne.io import read_raw
# from mne_realtime import LSLClient, MockLSLStream
#
# # from config import settings
#
#
# class FakeStream:
#     """
#     Класс для создания фейкового стрима данных
#     """
#     def __init__(self, host: str = 'MNE', wait_max: int = 5, n_epochs: int = 2):
#         self.path = pathlib.Path(f'./Альфа.edf') #{settings.data_filename}')
#         print(self.path)
#         self.raw = read_raw(self.path).crop(0, 30).load_data().pick('eeg')
#         self.host = host
#         self.wait_max = wait_max
#         self.n_epochs = n_epochs
#
#     def connecting(self) -> None:
#         _, ax = plt.subplots(1)
#         with MockLSLStream(self.host, self.raw, 'eeg'):
#             with LSLClient(info=self.raw.info, host=self.host, wait_max=self.wait_max) as client:
#                 client_info = client.get_measurement_info()
#                 sfreq = int(client_info['sfreq'])
#
#                 # let's observe ten seconds of data
#                 for ii in range(self.n_epochs):
#                     epoch = client.get_data_as_epoch(n_samples=sfreq)
#                     epoch.average().plot(axes=ax)  # при удалении plot стрим падает
#
#
# if __name__ == '__main__':
#     fs = FakeStream()
#     fs.connecting()

import pathlib
import time

import mne
from pylsl import StreamInfo, StreamOutlet, local_clock
from config.settings import settings


def main():
    srate = 250  # Частота дискретизации
    name = 'MNE2'  # Название источника потока
    sigtype = 'fake signal'  # Название сигнала

    n_channels = 4  # Число каналов
    info = StreamInfo(name, sigtype, n_channels, srate, 'float32', 'MNE device')
    outlet = StreamOutlet(info)
    print("Начало отправки данных...")
    start_time = local_clock()
    sent_samples = 0
    print(f'{settings.data_file_name}')
    path = pathlib.Path(f'{settings.data_file_name}')  # (f'./Альфа.edf')
    raw = mne.io.read_raw(path)
    data = raw.get_data()
    iter_sample = 0
    while True:
        elapsed_time = local_clock() - start_time
        required_samples = int(srate * elapsed_time) - sent_samples
        for sample_ix in range(required_samples):
            sample_out = data[0:n_channels, iter_sample].tolist()
            rounded_list = [round(value * 1000000, 2) for value in
                            sample_out]  # без умножения слишком маленькие значения
            outlet.push_sample(rounded_list)
            print(rounded_list)
            iter_sample = iter_sample + 1
            if iter_sample >= data.shape[1]:  # для бесконечного цикла
                iter_sample = 0
            # time.sleep(1 / srate) # можно отправлять значения без цикла for

        sent_samples += required_samples


if __name__ == '__main__':
    main()
