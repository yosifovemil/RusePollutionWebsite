import pandas as pd
from graphs.config import CompoundConfig
import numpy as np


def perform_analysis(data: pd.DataFrame, operation: str, compound_config: CompoundConfig) -> pd.DataFrame:
    resampled_data = data.resample('D', on='DateTime')

    limit = compound_config.get_limit(operation)

    if operation == 'mean':
        summarised_data = resampled_data.mean()
    elif operation == 'max':
        summarised_data = resampled_data.max()
    else:
        raise RuntimeError("Unknown operation ${op}".format(op=operation))

    summarised_data = summarised_data.reset_index()

    if limit is not None:
        summarised_data['Limit'] = np.where(summarised_data[compound_config.get_name()] >= limit, True, False)
    else:
        summarised_data['Limit'] = False

    return summarised_data
