import os
import math
import scipy.io.wavfile as wav
import numpy as np
from .utils import timer, array_chunk, pprint, pretty_time
from .utils import convert_data, locate_folder


def _rms(arr):
    return np.sqrt(np.mean(np.square(arr)))


@timer
def butter_lowpass_filter(data, cutoff, fs, order):
    from scipy.signal import butter, filtfilt

    normal_cutoff = cutoff / (fs / 2)
    # Get the filter coefficients
    b, a = butter(order, normal_cutoff, btype="low", analog=False)
    y = filtfilt(b, a, data)
    return y


@timer
def extract_volume(filename):
    sample_rate, data = wav.read(filename)

    data_type = np.int32
    data = data.astype(data_type)

    channels = data.shape[1]
    duration = int(len(data) / sample_rate)
    length = duration * sample_rate
    # cut off some data at the end
    data = data[:length]

    # convert to mono
    mono = np.zeros(length, dtype=data_type)
    for chan in range(channels):
        mono += data[:, chan]
    mono = mono / channels  # mono /= channels -> not working

    # low pass filter
    mono = butter_lowpass_filter(mono, 200, sample_rate, 2)

    data = np.array_split(mono, duration)
    rms_list = [_rms(arr) for arr in data]
    return rms_list


@timer
def extract_volume_stream(filename):
    import wave, struct

    file = wave.open(filename, "rb")

    length = file.getnframes()
    channels = file.getnchannels()
    sample_rate = file.getframerate()
    duration = int(length / sample_rate)

    rms_list = []

    first = True
    # read in the wave file in one second chunks
    for _ in range(duration):
        binary = file.readframes(sample_rate)
        data = np.frombuffer(binary, dtype=np.int16, count=sample_rate * channels)

        # check if int16 matches the input
        if first:
            test_data = struct.unpack(f"<{sample_rate * channels}h", binary)
            test_data = np.array(test_data)
            if (test_data != data).any():
                raise Exception("Import does not match int16 type!")

            first = False

        data_type = np.int32
        data = data.astype(data_type).reshape(-1, channels)

        # convert to mono
        mono = np.zeros(sample_rate, dtype=data_type)
        for chan in range(channels):
            mono += data[:, chan]
        mono = mono / channels  # mono /= channels -> not working

        rms_list.append(_rms(mono))

    file.close()

    return rms_list


def analyze_audio_test(chunk_size=1):
    volumes = extract_volume("scriptworld.wav")

    chunked = array_chunk(volumes, chunk_size)
    avg = np.array([np.average(arr) for arr in chunked])

    output = convert_data(avg, chunk_size)

    sort = sorted(output, reverse=True, key=lambda x: x["value"])
    # pprint(sort[:10])
    sorted_top = sorted(sort[:10], key=lambda x: x["from"])
    return sort[:10]


def analyze_audio(ident, chunk_size):
    folder = locate_folder(ident)
    files = os.listdir(folder)
    chunks = [file for file in files if file.startswith("chunk")]

    volumes = []
    for chunk in sorted(chunks):
        filename = f"{folder}/{chunk}"
        volumes += extract_volume(filename)
        print(f"{chunk} done")

    chunked = array_chunk(volumes, chunk_size)
    avg = np.array([np.average(arr) for arr in chunked])

    output = convert_data(avg, chunk_size)

    sort = sorted(output, reverse=True, key=lambda x: x["value"])
    # pprint(sort[:10])
    sorted_top = sorted(sort[:10], key=lambda x: x["from"])
    return sort[:10]
