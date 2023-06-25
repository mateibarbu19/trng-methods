#!/bin/bash

python3 src/main.py \
    --source fm \
    --acquire \
    --plot_types distribution+spectrum+spectrogram+magnitude_distribution+phase_distribution \
    --test_type ent

python3 src/main.py \
    --source fm \
    --operations winsorize_spectrum/sup_prec=0.2+uniformize_spectrum_median/block_size=64+winsorize_spectrum/sup_prec=0.15+uniformize_signal \
    --name test \
    --block_size 65536 \
    --plot_types distribution+spectrum+spectrogram+magnitude_distribution+phase_distribution \
    --test_type fips
