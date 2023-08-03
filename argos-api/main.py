import multiprocessing
from datetime import datetime

import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

import argos

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

class DatapointsForm(BaseModel):
    endpoint: str
    metric: str
    fromDatetime: str
    toDatetime: str


class OtherForm(BaseModel):
    data: list
    windowSize: int
    offsetSize: int
    subWindowSize: int
    alertWindowSize: int


class CompassForm(BaseModel):
    endpoint: str
    metric: str
    fromDatetime: str
    toDatetime: str
    windowSize: int
    offsetSize: int
    subWindowSize: int
    alertWindowSize: int


@app.get('/')
def index():
    return {'Hello': 'World'}


@app.post('/api/fetch/compass')
def fetch(form: DatapointsForm):
    endpoint = form.endpoint
    target = form.metric

    from_datetime = datetime.strptime(form.fromDatetime[:-6], '%Y-%m-%dT%H:%M:%S')
    until_datetime = datetime.strptime(form.toDatetime[:-6], '%Y-%m-%dT%H:%M:%S')

    zero_datetime = datetime.utcfromtimestamp(0)
    from_timestamp = int((from_datetime - zero_datetime).total_seconds())
    until_timestamp = int((until_datetime - zero_datetime).total_seconds())

    payload = {
        'target': target.replace('/\n|\r/g', ''),
        'from': from_timestamp,
        'until': until_timestamp,
        'format': 'json'
    }

    datapoints = argos.fetch_datapoints(endpoint, payload)

    try:
        step_size = argos.get_step_size(datapoints)
    except Exception as e:
        return {
            'status': 'failed',
            'error': e
        }
    else:
        return {
            'status': 'success',
            'datapoints': {
                'data': np.nan_to_num(datapoints).astype(np.uint64).tolist(),
                'pointStart': from_timestamp,
                'pointEnd': until_timestamp,
                'pointInterval': step_size
            }
        }


@app.post('/api/examine')
def compute(form: OtherForm):
    print(form)

    window_size = form.windowSize
    offset_size = form.offsetSize
    sub_window_size = form.subWindowSize
    alert_window_size = form.alertWindowSize

    datapoints = np.array(form.data, dtype=np.float64)

    from_timestamp = datapoints[0][1]
    until_timestamp = datapoints[-1][1]

    step_size = argos.get_step_size(datapoints)

    if argos.validate_step_size(datapoints, step_size):
        pass
    else:
        return {
            'status': 'failed',
            'error': 'All differences along timestamp must be equal'
        }

    window_point = window_size // step_size
    offset_point = offset_size // step_size
    sub_window_point = sub_window_size // step_size

    if offset_point > 0:
        windows = argos.create_windows(
            datapoints,
            window_point,
            offset_point
        )

        args = [
            (window, sub_window_point, alert_window_size) for window in windows
        ]

        pool = multiprocessing.Pool(6)

        results = pool.map_async(argos.detect_anomaly, args)

        pool.close()
        pool.join()

        return {
            'status': 'success',
            'datapoints': {
                'pointStart': from_timestamp,
                'pointEnd': until_timestamp,
                'pointInterval': step_size
            },
            'anomalies': {
                'timestamp': [
                    {
                        'from': anomaly[1],
                        'to': anomaly[2]
                    }
                    for anomaly in results.get()
                    if anomaly is not None
                ],
                'index': [
                    {
                        'from': (anomaly[1] - from_timestamp) // step_size,
                        'to': (anomaly[2] - from_timestamp) // step_size
                    }
                    for anomaly in results.get()
                    if anomaly is not None
                ]
            }
        }
    else:
        result = argos.detect_anomaly(
            (datapoints, sub_window_point, alert_window_size))

        return {
            'status': 'success',
            'datapoints': {
                'pointStart': from_timestamp,
                'pointEnd': until_timestamp,
                'pointInterval': step_size
            },
            'anomalies': {
                'timestamp': [
                    {
                        'from': result[1], 'to': result[2]
                    }
                    if result else None
                ],
                'index': [
                    {
                        'from': (result[1] - from_timestamp) // step_size,
                        'to': (result[2] - from_timestamp) // step_size
                    }
                    if result else None
                ]
            }
        }


@app.post('/api/examine/compass')
def examine(form: CompassForm):
    print(form)

    endpoint = form.endpoint
    target = form.metric

    from_datetime = datetime.strptime(form.fromDatetime[:-6], '%Y-%m-%dT%H:%M:%S')
    until_datetime = datetime.strptime(form.toDatetime[:-6], '%Y-%m-%dT%H:%M:%S')

    zero_datetime = datetime.utcfromtimestamp(0)
    from_timestamp = int((from_datetime - zero_datetime).total_seconds())
    until_timestamp = int((until_datetime - zero_datetime).total_seconds())

    window_size = form.windowSize
    offset_size = form.offsetSize
    sub_window_size = form.subWindowSize
    alert_window_size = form.alertWindowSize

    payload = {
        'target': target.replace('/\n|\r/g', ''),
        'from': from_timestamp,
        'until': until_timestamp,
        'format': 'json'
    }

    datapoints = argos.fetch_datapoints(endpoint, payload)

    step_size = argos.get_step_size(datapoints)

    if argos.validate_step_size(datapoints, step_size):
        pass
    else:
        return {
            'status': 'failed',
            'error': 'Incorrect step size'
        }

    window_point = window_size // step_size
    offset_point = offset_size // step_size
    sub_window_point = sub_window_size // step_size

    if offset_point > 0:
        windows = argos.create_windows(
            datapoints,
            window_point,
            offset_point
        )

        args = [
            (window, sub_window_point, alert_window_size) for window in windows
        ]

        pool = multiprocessing.Pool(6)

        results = pool.map_async(argos.detect_anomaly, args)

        pool.close()
        pool.join()

        return {
            'status': 'success',
            'datapoints': {
                'data': np.nan_to_num(datapoints).astype(np.uint64).tolist(),
                'pointStart': from_timestamp,
                'pointEnd': until_timestamp,
                'pointInterval': step_size
            },
            'anomalies': [
                {'from': anomaly[1], 'to': anomaly[2]}
                for anomaly in results.get()
                if anomaly is not None
            ]
        }
    else:
        result = argos.detect_anomaly(
            (datapoints, sub_window_point, alert_window_size))

        return {
            'status': 'success',
            'datapoints': {
                'data': np.nan_to_num(datapoints).astype(np.uint64).tolist(),
                'pointStart': from_timestamp,
                'pointEnd': until_timestamp,
                'pointInterval': step_size
            },
            'anomalies': [
                {'from': result[1], 'to': result[2]} if result else None
            ]
        }
