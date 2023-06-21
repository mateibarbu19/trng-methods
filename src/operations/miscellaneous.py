from operations.operation import operation

import numpy as np
from scipy.fft import rfft, irfft
from scipy.signal import convolve
from scipy.ndimage import zoom

DEFAULT_BAND = (4000, 13000)


class autocorrelate_signal(operation):
    def blocks_func(self, data):
        return convolve(data, data[::-1], mode='same')


class autocorrelate_spectrum(operation):
    def blocks_func(self, data):
        # Compute the Fourier transform
        spectrum = rfft(data)

        auto_corr_spectrum = convolve(spectrum, spectrum[::-1], mode='same')

        # Inverse FFT
        adjusted_data = np.real(irfft(auto_corr_spectrum))

        # Normalize and scale the transformed data to the range of 16-bit signed integers
        return operation.normalize_and_scale(adjusted_data)


class expand_band(operation):
    def __init__(self, band=DEFAULT_BAND, order=5, **kwargs):
        super().__init__(**kwargs)

        self.order = order

        self.band_idx = (
            self.get_fft_index(band[0]),
            self.get_fft_index(band[1]))

    def blocks_func(self, data):
        # Compute the Fourier transform
        spectrum = rfft(data)

        # Extract the spectrum in the band of interest
        band_spectrum = spectrum[self.band_idx[0]:self.band_idx[1]]

        # Calculate the zoom factor
        zoom_factor = spectrum.size / band_spectrum.size

        # Interpolate the spectrum in the band of interest
        enlarged_spectrum = zoom(band_spectrum, zoom_factor, order=self.order)

        # Inverse FFT
        adjusted_data = np.real(irfft(enlarged_spectrum))

        # Normalize and scale the transformed data to the range of 16-bit signed integers
        return operation.normalize_and_scale(adjusted_data)
