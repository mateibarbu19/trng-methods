#!/bin/bash

python3 src/main.py \
    --source fm \
    --acquire \
    --plot_types distribution+spectrum+spectrogram+magnitude_distribution+phase_distribution

python3 src/main.py \
    --source fm \
    --operations filter_spectrum_notch \
    --name test \
    --block_size 65536 \
    --plot_types distribution+spectrum+spectrogram+magnitude_distribution+phase_distribution
