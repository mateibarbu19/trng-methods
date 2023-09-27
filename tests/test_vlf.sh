#!/bin/bash

python3 src/main.py \
    --source vlf \
    --acquire \
    --plot_types distribution+spectrum+spectrogram+magnitude_distribution+phase_distribution \
    --test_type ent

python3 src/main.py \
    --source vlf \
    --operations expand_band+uniformize_spectrum_median+uniformize_signal/block_size=65536 \
    --name test \
    --block_size 64 \
    --plot_types distribution+spectrum+spectrogram+magnitude_distribution+phase_distribution \
    --test_type fips
