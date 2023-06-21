from operations.operation import operation

import numpy as np
from scipy.fft import rfft, irfft
from scipy.stats.mstats import winsorize


class winsorize_signal(operation):
    def __init__(self, inf_prec=0, sup_prec=0.05, **kwargs):
        super().__init__(**kwargs)

        self.limits = [inf_prec, sup_prec]

    def blocks_func(self, data):
        # Winsorize the data
        winsorize(data, self.limits, inplace=True)

        return data


class winsorize_spectrum(operation):
    def __init__(self, inf_prec=0, sup_prec=0.05, **kwargs):
        super().__init__(**kwargs)

        self.limits = [inf_prec, sup_prec]

    def blocks_func(self, data):
        # Compute the Fourier transform
        spectrum = rfft(data)

        # Compute the magnitudes and phases of the spectrum
        magnitudes = np.abs(spectrum)
        phases = np.angle(spectrum)

        # Winsorize the magnitudes
        winsorize(magnitudes, self.limits, inplace=True)

        # Retain original phase
        winsorized_spectrum = np.multiply(magnitudes, np.exp(1j*phases))

        # Inverse FFT
        adjusted_data = np.real(irfft(winsorized_spectrum))

        # Normalize and scale the transformed data to the range of 16-bit signed integers
        return operation.normalize_and_scale(adjusted_data)
