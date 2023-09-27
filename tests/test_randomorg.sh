#!/bin/bash

python3 src/main.py \
    --source randomorg \
    --acquire \
    --plot_types distribution+spectrum+spectrogram+magnitude_distribution+phase_distribution \
    --test_type ent+fips
