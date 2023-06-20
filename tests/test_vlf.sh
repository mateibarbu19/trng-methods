#!/bin/bash

python3 src/main.py \
    --source vlf \
    --acquire \
    --plot_types spectrogram+spectrum+magnitude_distribution

python3 src/main.py \
    --source vlf \
    --operations uniformize_spectrum+uniformize_signal \
    --name test \
    --block_size 65536 \
    --plot_types spectrogram+spectrum+magnitude_distribution
