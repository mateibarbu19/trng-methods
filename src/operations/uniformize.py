from operations.operation import operation
from abc import abstractmethod

import numpy as np
from scipy.stats import rankdata, mode
from scipy.fft import rfft, irfft


class uniformize_signal(operation):
    def __init__(self, method='ordinal', **kwargs):
        super().__init__(**kwargs)
        self.method = method

    def blocks_func(self, data):
        # Normalize the data to the range of int16
        data = data / np.max(np.abs(data))

        # Apply the quantile transformation
        ranked_data = rankdata(data, method=self.method)
        uniform_data = (ranked_data - 1) / (len(ranked_data) - 1)

        # Scale the data back to int16
        max_val = np.iinfo(np.int16).max
        min_val = np.iinfo(np.int16).min
        uniform_data = np.int16(uniform_data * (max_val - min_val) + min_val)

        return uniform_data


class uniformize_spectrum(operation):
    def blocks_func(self, data):
        # Compute the Fourier transform
        spectrum = rfft(data)

        # Compute the magnitudes of the spectrum
        magnitudes = np.abs(spectrum)

        # Compute the yardstick
        yardstick = self.get_yardstick(magnitudes)

        # Replace the zero values with one to avoid division by zero
        magnitudes[magnitudes == 0] = 1

        # Compute the whitened spectrum
        whitened_spectrum = (spectrum / magnitudes) * yardstick

        # Return the inverse Fourier transform of the whitened spectrum
        # We use np.real to discard the imaginary part which occurs due to numerical errors
        whitened_data = np.real(irfft(whitened_spectrum))

        return whitened_data.astype(np.int16)

    @abstractmethod
    def get_yardstick(self, magnitudes):
        pass


class uniformize_spectrum_mean(uniformize_spectrum):
    def get_yardstick(self, magnitudes):
        return np.mean(magnitudes)


class uniformize_spectrum_median(uniformize_spectrum):
    def get_yardstick(self, magnitudes):
        return np.median(magnitudes)

class uniformize_spectrum_maximum(uniformize_spectrum):
    def get_yardstick(self, magnitudes):
        return np.max(magnitudes)
