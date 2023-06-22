#!/bin/bash

python3 src/main.py \
    --source randomorg \
    --acquire \
    --duration 1 \
    --plot_types distribution+spectrogram+spectrum+magnitude_distribution+phase_distribution
