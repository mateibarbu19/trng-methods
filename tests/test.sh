#!/bin/bash

python3 src/main.py \
    --source vlf \
    --acquire \
    --plot_types wave,distribution,spectrogram,spectrum,magnitude_distribution,phase_distribution,bitmap

python3 src/main.py \
    --source vlf \
    --transformations uniformize-spectrum \
    --name test \
    --block_size 65536 \
    --plot_types wave,distribution,spectrogram,spectrum,magnitude_distribution,phase_distribution,bitmap
