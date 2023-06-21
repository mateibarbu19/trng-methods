#!/bin/bash

python3 src/main.py \
    --source vlf \
    --acquire \
    --plot_types spectrogram+spectrum+magnitude_distribution

python3 src/main.py \
    --source vlf \
    --operations expand_band+uniformize_spectrum_median+uniformize_signal \
    --name test \
    --block_size 64 \
    --plot_types spectrogram+spectrum+magnitude_distribution
