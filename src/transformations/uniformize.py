from transformations.transform import Transformation

import numpy as np
from scipy.stats import rankdata

class Uniformize(Transformation):
    def block_func(self, data):
        # Normalize the data to the range of int16
        data = data / np.max(np.abs(data))

        # Apply the quantile transformation
        ranked_data = rankdata(data, method='average')
        uniform_data = (ranked_data - 1) / (len(ranked_data) - 1)

        # Scale the data back to int16
        uniform_data_int16 = np.int16(
            uniform_data * (np.iinfo(np.int16).max - np.iinfo(np.int16).min) + np.iinfo(np.int16).min)

        return uniform_data_int16


