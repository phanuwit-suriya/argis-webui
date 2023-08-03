import json

import numpy as np
import requests


def fetch_datapoints(endpoint: str,
                     payload: dict,
                     replace_nan: bool = True) -> np.ndarray:
    with requests.post(endpoint, payload) as response:
        if replace_nan:
            return np.nan_to_num(np.array(
                response.json()[0]['datapoints'], np.float64
            ))
        else:
            return np.array(
                response.json()[0]['datapoints'], np.float64
            )


def get_step_size(datapoints: np.ndarray) -> int:
    return int(datapoints[1][1] - datapoints[0][1])


def validate_step_size(datapoints: np.ndarray, step_size: int) -> bool:
    return np.all(np.diff(datapoints[:, 1]) == step_size)


def create_windows(datapoints: np.ndarray,
                   window_point: int,
                   offset_point: int) -> np.ndarray:
    r_sh, c_sh = datapoints.shape
    r_st, c_st = datapoints.strides
    shape = ((r_sh - window_point + 1) // offset_point) + 1, window_point, c_sh
    strides = r_st * offset_point, r_st, c_st

    return np.lib.stride_tricks.as_strided(
        x=datapoints,
        shape=shape,
        strides=strides,
        writeable=False
    )


def create_sub_windows(datapoints: np.ndarray,
                       sub_window_point: int) -> np.ndarray:
    r_sh, c_sh = datapoints.shape
    r_st, c_st = datapoints.strides
    shape = r_sh - sub_window_point + 1, sub_window_point, c_sh
    strides = r_st, r_st, c_st

    return np.lib.stride_tricks.as_strided(
        x=datapoints,
        shape=shape,
        strides=strides,
        writeable=False
    )


def detect_anomaly(args: tuple):
    datapoints, sub_window_point, alert_window_size = args

    sub_windows = create_sub_windows(datapoints, sub_window_point)
    
    minimums = []
    for i in range(len(sub_windows)):
        minuend = sub_windows[i]
        if i < sub_window_point:
            subtrahends = sub_windows[i + sub_window_point:]
        else:
            subtrahends = np.append(
                sub_windows[0:i - sub_window_point + 1],
                sub_windows[i + sub_window_point:],
                axis=0
            )

    #     if not np.any(np.isnan(minuend), axis=(0, 1)):
    #         subtrahends = subtrahends[~np.any(np.isnan(subtrahends), axis=(1, 2))]
    #         try:
    #             minimums.append({
    #                 'value': np.min(np.sum(np.abs(minuend[:, 0] - subtrahends[:, :, 0]), axis=1)),
    #                 'from': minuend[0][1],
    #                 'to': minuend[-1][1]
    #             })
    #         except ValueError:
    #             print('Not enough windows to calculated')
    # return max(minimums, key=lambda e: e['value'])

        if not np.any(np.isnan(minuend), axis=(0, 1)):
            subtrahends = subtrahends[~np.any(np.isnan(subtrahends), axis=(1, 2))]
            try:
                minimums.append([
                    np.min(np.sum(np.abs(minuend[:, 0] - subtrahends[:, :, 0]), axis=1)),   # Value
                    minuend[0][1],  # From timestamp
                    minuend[-1][1]  # To timestamp
                ])
            except ValueError:
                print('Not enough windows to calculated')

    minimums = np.array(minimums)
    for anomaly in minimums[minimums[:, 0].argsort()[-5:]]:
        if anomaly[2] > datapoints[-1][1] - alert_window_size:
            return  anomaly.tolist()
    return None
