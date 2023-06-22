#!/bin/bash

python3 src/main.py \
    --source osrandom \
    --acquire \
    --plot_types distribution+spectrogram+spectrum+magnitude_distribution+phase_distribution
