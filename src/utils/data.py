import numpy as np

def sample_width_to_np_dtype(sw):
    return {
        1: np.uint8,   # Usually unsigned 8-bit PCM
        2: np.int16,   # Standard 16-bit PCM
        4: np.int32    # 32-bit PCM
    }.get(sw)
