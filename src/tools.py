import os

import wave
from scipy.io import wavfile
from pydub import AudioSegment

import hashlib

import numpy as np

from scipy.signal import convolve, medfilt
from scipy.stats import rankdata

# List of colors to use for plots.
color_list = ['skyblue', 'orange', 'green', 'red',
              'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']


def quantile_transformation(audio_file, output):
    # Read the WAV file
    sample_rate, data = wavfile.read(audio_file)

    # Flatten the data to 1D if it's stereo
    if len(data.shape) > 1:
        data = data.flatten()

    # Normalize the data to the range of int16
    data = data / np.max(np.abs(data))

    # Apply the quantile transformation
    ranked_data = rankdata(data, method='average')
    uniform_data = (ranked_data - 1) / (len(ranked_data) - 1)

    # Scale the data back to int16
    uniform_data_int16 = np.int16(
        uniform_data * (np.iinfo(np.int16).max - np.iinfo(np.int16).min) + np.iinfo(np.int16).min)

    # Write the transformed data to a new WAV file
    wavfile.write(output, sample_rate, uniform_data_int16)


def xor_reduce(audio_file, output, chunk_size=None, nr_chunks=None):
    # if both chunk_size and nr_chunks are None, set nr_chunks to 1
    if chunk_size is None and nr_chunks is None:
        nr_chunks = 1

    # open the wave file
    with wave.open(audio_file, 'rb') as f:
        params = f.getparams()
        nchannels, sampwidth, framerate, nframes = params[:4]
        str_data = f.readframes(nframes)
        wave_data = np.frombuffer(str_data, dtype=np.int16)

    # pad the signal if necessary
    if chunk_size is None:
        block = nr_chunks
    else:
        block = chunk_size

    remainder = len(wave_data) % block
    if remainder != 0:
        pad_size = block - remainder
        wave_data = np.pad(wave_data, (0, pad_size))

    # if chunk_size is None, update it based on nr_chunks
    if chunk_size is None:
        chunk_size = len(wave_data) // nr_chunks

    # make sure chunk_size is a multiple of number of channels
    chunk_size *= nchannels

    # divide into chunks
    chunks = np.array_split(wave_data, len(wave_data) // chunk_size)

    # xor all chunks
    xor_chunk = np.bitwise_xor.reduce(chunks)

    # create output wave file
    with wave.open(output, 'wb') as f:
        f.setnchannels(nchannels)
        f.setsampwidth(sampwidth)
        f.setframerate(framerate)
        f.writeframes(xor_chunk.astype(np.int16).tobytes())


def xor_zip(audio_file1, audio_file2, output):
    # open the first wave file
    with wave.open(audio_file1, 'rb') as f:
        params1 = f.getparams()
        nchannels1, sampwidth1, framerate1, nframes1 = params1[:4]
        str_data1 = f.readframes(nframes1)
        wave_data1 = np.frombuffer(str_data1, dtype=np.int16)

    # open the second wave file
    with wave.open(audio_file2, 'rb') as f:
        params2 = f.getparams()
        nchannels2, sampwidth2, framerate2, nframes2 = params2[:4]
        str_data2 = f.readframes(nframes2)
        wave_data2 = np.frombuffer(str_data2, dtype=np.int16)

    # make sure the files have the same parameters
    if nchannels1 != nchannels2 or sampwidth1 != sampwidth2 or framerate1 != framerate2:
        raise ValueError(
            'The two files must have the same number of channels, sample width, and frame rate.')

    # truncate the longer file if necessary
    min_length = min(len(wave_data1), len(wave_data2))
    wave_data1 = wave_data1[:min_length]
    wave_data2 = wave_data2[:min_length]

    # xor the two files
    xor_data = np.bitwise_xor(wave_data1, wave_data2)

    # create output wave file
    with wave.open(output, 'wb') as f:
        f.setnchannels(nchannels1)
        f.setsampwidth(sampwidth1)
        f.setframerate(framerate1)
        f.writeframes(xor_data.astype(np.int16).tobytes())


def moving_average_specteral_smooth(audio_file, output, window_size=50):
    # Read WAV file
    sample_rate, data = wavfile.read(audio_file)

    # Take FFT
    fft_data = np.fft.rfft(data)

    # Smooth the magnitude spectrum with a moving average
    smoothed_magnitude = convolve(np.abs(fft_data), np.ones(
        window_size)/window_size, mode='same')

    # Retain original phase
    smoothed_fft_data = np.multiply(
        smoothed_magnitude, np.exp(1j*np.angle(fft_data)))

    # Inverse FFT
    smoothed_data = np.fft.irfft(smoothed_fft_data)

    # Ensure data is in the correct format
    max = np.iinfo(np.int16).max
    smoothed_data = np.int16(
        smoothed_data / np.max(np.abs(smoothed_data)) * max)

    # Write back to a new WAV file
    wavfile.write(output, sample_rate, smoothed_data)


def median_filtering_specteral_smooth(audio_file, output, window_size=51):
    # Read WAV file
    sample_rate, data = wavfile.read(audio_file)

    # Take FFT
    fft_data = np.fft.rfft(data)

    # Apply median filter to the magnitude spectrum
    filtered_magnitude = medfilt(np.abs(fft_data), window_size)

    # Retain original phase
    filtered_fft_data = np.multiply(
        filtered_magnitude, np.exp(1j*np.angle(fft_data)))

    # Inverse FFT
    filtered_data = np.fft.irfft(filtered_fft_data)

    # Ensure data is in the correct format
    max = np.iinfo(np.int16).max
    filtered_data = np.int16(
        filtered_data / np.max(np.abs(filtered_data)) * max)

    # Write back to a new WAV file
    wavfile.write(output, sample_rate, filtered_data)


def wiener_filter_specteral_smooth(audio_file, output, proc=0.1):
    # Read WAV file
    sample_rate, data = wavfile.read(audio_file)

    # Transform to the frequency domain
    fft_data = np.fft.rfft(data)

    # Estimate the noise level as a percentage of the signal strength
    noise_level = np.mean(np.abs(fft_data)) * proc  # proc% noise level

    # Create Wiener filter in frequency domain
    wiener_filter = np.abs(fft_data)**2 / \
        (np.abs(fft_data)**2 + noise_level**2)

    # Apply Wiener filter
    filtered_fft_data = fft_data * wiener_filter

    # Transform back to the time domain
    filtered_data = np.fft.irfft(filtered_fft_data)

    # Ensure data is in the correct format
    max = np.iinfo(np.int16).max
    filtered_data = np.int16(
        filtered_data / np.max(np.abs(filtered_data)) * max)

    # Write back to a new WAV file
    wavfile.write(output, sample_rate, filtered_data)


def get_min_duration(directory):
    # Initialize minimum duration
    min_duration = float('inf')

    # Iterate through all wav files in the directory
    for file in os.listdir(directory):
        if file.endswith(".wav"):
            # Load audio file
            audio = AudioSegment.from_wav(os.path.join(directory, file))

            # Update minimum duration
            min_duration = min(min_duration, len(audio))

    return min_duration


def trim_files_to_min_duration(directory, min_duration):
    for file in os.listdir(directory):
        if file.endswith(".wav"):
            # Set the path
            path = os.path.join(directory, file)

            # Load audio file
            audio = AudioSegment.from_wav(path)

            # Trim audio file
            trimmed_audio = audio[:min_duration]

            # Export trimmed audio file
            trimmed_audio.export(path, format="wav")


def md5_wav(audio_file, output):
    # Read the WAV file
    sample_rate, data = wavfile.read(audio_file)

    # Flatten the data to 1D if it's stereo
    if len(data.shape) > 1:
        data = data.flatten()

    # Convert the data to bytes
    data_bytes = data.astype(np.int16).tobytes()

    # Pad the data bytes to a multiple of 16 bytes
    padding = b'\0' * (16 - (len(data_bytes) % 16))
    data_bytes_padded = data_bytes + padding

    # Hash the data in 16-byte blocks
    hashed_bytes = b''
    for i in range(0, len(data_bytes_padded), 16):
        block = data_bytes_padded[i:i+16]
        hashed_block = hashlib.md5(block).digest()
        hashed_bytes += hashed_block

    # Convert the hashed bytes back to int16 data
    hashed_data = np.frombuffer(hashed_bytes, dtype=np.int16)

    # Write the hashed data to a new WAV file
    wavfile.write(output, sample_rate, hashed_data)
