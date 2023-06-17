#!/bin/bash

python3 src/main.py \
    --source vlf \
    --acquire \
    --plot_types distribution,spectrogram

python3 src/main.py \
    --source vlf \
    --transformations uniformize,spec-filter-med,uniformize \
    --name v0.1 \
    --plot_types distribution,spectrogram
