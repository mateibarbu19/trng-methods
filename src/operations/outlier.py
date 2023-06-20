from operations.operation import operation

import numpy as np
from scipy.fft import rfft, irfft
from scipy.stats.mstats import winsorize


class winsorize_spectrum(operation):
    def __init__(self, prec=0.5, **kwargs):
        super().__init__(**kwargs)

        self.limits = [0, prec]

    def blocks_func(self, data):
        # Compute the Fourier transform
        spectrum = rfft(data)

        # Compute the magnitudes and phases of the spectrum
        magnitudes = np.abs(spectrum)
        phases = np.angle(spectrum)

        # Winsorize the magnitudes
        winsorized_magnitudes = winsorize(magnitudes, self.limits)

        # Retain original phase
        winsorized_spectrum = np.multiply(
            winsorized_magnitudes, np.exp(1j*phases))

        # Inverse FFT
        adjusted_data = np.real(irfft(winsorized_spectrum))

        # Normalize and scale the transformed data to the range of 16-bit signed integers
        max_val = np.iinfo(np.int16).max
        adjusted_data = np.int16(
            adjusted_data / np.max(np.abs(adjusted_data)) * max_val)

        return adjusted_data
