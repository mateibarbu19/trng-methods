from transformations.transform import Transformation

import numpy as np
from scipy.signal import convolve, medfilt


class FilterSpectrumAverage(Transformation):
    def __init__(self, window_size=50, **kwargs):
        super().__init__(**kwargs)
        assert window_size % 2 == 0, "Window size must be even"
        self.window_size = window_size

    def block_func(self, data):
        # Take FFT
        fft_data = np.fft.rfft(data)

        # Smooth the magnitude spectrum with a moving average
        smoothed_magnitude = convolve(np.abs(fft_data), np.ones(
            self.window_size)/self.window_size, mode='same')

        # Retain original phase
        smoothed_fft_data = np.multiply(
            smoothed_magnitude, np.exp(1j*np.angle(fft_data)))

        # Inverse FFT
        smoothed_data = np.fft.irfft(smoothed_fft_data)

        # Ensure data is in the correct format
        max_val = np.iinfo(np.int16).max
        smoothed_data = np.int16(
            smoothed_data / np.max(np.abs(smoothed_data)) * max_val)

        return smoothed_data


class FilterSpectrumMedian(Transformation):
    def __init__(self, window_size=51, **kwargs):
        super().__init__(**kwargs)
        assert window_size % 2 == 1, "Window size must be odd"
        self.window_size = window_size

    def block_func(self, data):
        # Take FFT
        fft_data = np.fft.rfft(data)

        # Apply median filter to the magnitude spectrum
        filtered_magnitude = medfilt(np.abs(fft_data), self.window_size)

        # Retain original phase
        filtered_fft_data = np.multiply(
            filtered_magnitude, np.exp(1j*np.angle(fft_data)))

        # Inverse FFT
        filtered_data = np.fft.irfft(filtered_fft_data)

        # Ensure data is in the correct format
        max_val = np.iinfo(np.int16).max
        filtered_data = np.int16(
            filtered_data / np.max(np.abs(filtered_data)) * max_val)

        return filtered_data


class FilterSpectrumWiener(Transformation):
    def __init__(self, proc=0.1, **kwargs):
        super().__init__(**kwargs)
        self.proc = proc

    def block_func(self, data):
        # Transform to the frequency domain
        fft_data = np.fft.rfft(data)

        # Estimate the noise level as a percentage of the signal strength
        noise_level = np.mean(np.abs(fft_data)) * self.proc

        # Create Wiener filter in frequency domain
        wiener_filter = np.abs(fft_data)**2 / \
            (np.abs(fft_data)**2 + noise_level**2)

        # Apply Wiener filter
        filtered_fft_data = fft_data * wiener_filter

        # Transform back to the time domain
        filtered_data = np.fft.irfft(filtered_fft_data)

        # Ensure data is in the correct format
        max_val = np.iinfo(np.int16).max
        filtered_data = np.int16(
            filtered_data / np.max(np.abs(filtered_data)) * max_val)

        return filtered_data
