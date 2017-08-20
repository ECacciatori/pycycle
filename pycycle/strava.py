# Copyright (c) 2016 Martin Galpin (galpin@gmail.com).

import numpy as np

from collections import namedtuple, defaultdict

from pandas import Series
from stravalib import Client

from pycycle.activity import ActivityDataFrame
from pycycle.columns import COLUMNS_BY_NAME


def _standard_stravalib_factory(access_token):
    return Client(access_token)


_STRAVALIB_FACTORY = _standard_stravalib_factory


def configure_stravalib_factory(factory):
    global _STRAVALIB_FACTORY
    _STRAVALIB_FACTORY = factory


Context = namedtuple('Context', ['start_time'])


class ValueConverter(object):
    def __init__(self, from_name, to_name):
        self.from_name = from_name
        self.to_name = to_name

    def convert(self, ctx, value):
        return self.convert_core(ctx, value) if value is not None else None

    def convert_core(self, ctx, value):
        raise NotImplementedError()


class TimeDeltaValueConverter(ValueConverter):
    def convert_core(self, ctx, value):
        seconds = int(value)
        return ctx.start_time + np.timedelta64(seconds, 's')


class TupleToFloatValueConverter(ValueConverter):
    def __init__(self, from_name, to_name, index):
        super(TupleToFloatValueConverter, self).__init__(from_name, to_name)
        self.index = index

    def convert_core(self, ctx, value):
        return float(value[self.index])


class FloatValueConverter(ValueConverter):
    def __init__(self, from_name, to_name, func=None):
        super(FloatValueConverter, self).__init__(from_name, to_name)
        self.func = func or (lambda x: x)

    def convert_core(self, ctx, value):
        return self.func(float(value))


def ms_to_kmh(x): return x * 3.6

_CONVERTERS = [
    FloatValueConverter('altitude', COLUMNS_BY_NAME['Altitude'].name),
    FloatValueConverter('cadence', COLUMNS_BY_NAME['Cadence'].name),
    FloatValueConverter('distance', COLUMNS_BY_NAME['Distance'].name),
    FloatValueConverter('grade_smooth', COLUMNS_BY_NAME['Gradient'].name),
    FloatValueConverter('heartrate', COLUMNS_BY_NAME['Heart Rate'].name),
    TupleToFloatValueConverter('latlng', COLUMNS_BY_NAME['Latitude'].name, index=0),
    TupleToFloatValueConverter('latlng', COLUMNS_BY_NAME['Longitude'].name, index=1),
    FloatValueConverter('temp', COLUMNS_BY_NAME['Temperature'].name),
    TimeDeltaValueConverter('time', COLUMNS_BY_NAME['Timestamp'].name),
    FloatValueConverter('velocity_smooth', COLUMNS_BY_NAME['Velocity'].name, func=ms_to_kmh),
    FloatValueConverter('watts', COLUMNS_BY_NAME['Power'].name)
]
_STREAM_TYPES = list(np.unique([x.from_name for x in _CONVERTERS]))


def _create_series(streams, ctx):
    data_dict = defaultdict(list)
    for converter in _CONVERTERS:
        stream = streams.get(converter.from_name)
        if stream is None:
            continue
        for value in stream.data:
            converted = converter.convert(ctx, value)
            if converted is None:
                continue
            data_dict[converter.to_name].append(converted)
    return {key: Series(value) for key, value in data_dict.items()}


def load(activity_id, access_token=None):
    """
    Returns a ActivityDataFrame from a Strava activity.

    *activity_id* is the Strava activity identifier. *access_token* is the
    optional Strava API access token for the athlete that owns the activity.
    """
    client = _STRAVALIB_FACTORY(access_token)
    activity = client.get_activity(activity_id)
    streams = client.get_activity_streams(activity_id, types=_STREAM_TYPES)
    ctx = Context(np.datetime64(activity.start_date_local))
    series_dict = _create_series(streams, ctx)
    return ActivityDataFrame.from_dict(series_dict)
