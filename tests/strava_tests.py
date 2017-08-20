# Copyright (c) 2016 Martin Galpin (galpin@gmail.com).

from collections import namedtuple
from datetime import datetime
from unittest import TestCase

import numpy as np
from mock import Mock

from pycycle import strava


Stream = namedtuple('Stream', ['series_type', 'data'])
Activity = namedtuple('Activity', ['start_date_local'])


class MockStravaClient(Mock):
    def configure(self):
        self.configure_get_activity(Activity(start_date_local=datetime.now()))
        self.configure_get_activity_streams([])

    def configure_get_activity_streams(self, series_types, data=None):
        data = data or [np.arange(0, 500, 1) for _ in series_types]
        streams_dict = {x: Stream(x, y) for x, y in zip(series_types, data)}
        self.get_activity_streams.return_value = streams_dict
        return streams_dict

    def configure_get_activity(self, activity):
        self.get_activity.return_value = activity


def load(activity_id=None, token=None):
    return strava.load(activity_id, token)


class StravaTestCase(TestCase):
    def setUp(self):
        self.factory = Mock()
        self.client = MockStravaClient()
        self.client.configure()
        self.factory.return_value = self.client
        strava.configure_stravalib_factory(self.factory)

    def assertColumn(self, df, name, dtype):
        self.assertIn(name, df.columns)
        self.assertEqual(df[name].dtype, dtype)


class ClientTestCase(StravaTestCase):
    def test_creates_client_with_specified_access_token(self):
        expected_access_token = 'token'
        load('activity_id', expected_access_token)
        self.factory.assert_called_once_with(expected_access_token)

    def test_requests_activity_with_activity_id(self):
        expected_activity_id = 'activity_id'
        load(expected_activity_id, 'token')
        self.client.get_activity.assert_called_once_with(expected_activity_id)

    def test_requests_activity_streams_with_activity_id_and_streams(self):
        expected_activity_id = 'activity_id'
        expected_streams = ['altitude', 'cadence', 'distance', 'grade_smooth',
                            'heartrate', 'latlng', 'temp', 'time', 'velocity_smooth', 'watts']
        load(expected_activity_id, 'token')
        self.client.get_activity_streams.assert_called_once_with(expected_activity_id, types=expected_streams)


class AltitudeTestCase(StravaTestCase):
    def test_adds_column_when_stream_is_provided(self):
        self.client.configure_get_activity_streams(['altitude'])
        df = load()
        self.assertColumn(df, 'Altitude', np.dtype('float64'))

    def test_does_not_throw_when_stream_is_not_provided(self):
        self.client.configure_get_activity_streams([])
        df = load()
        self.assertNotIn('Altitude', df)

    def test_does_not_convert_units(self):
        streams = self.client.configure_get_activity_streams(['altitude'])
        expected = streams['altitude'].data
        df = load()
        np.testing.assert_array_equal(expected, df['Altitude'].values)


class CadenceTestCase(StravaTestCase):
    def test_adds_column_when_stream_is_provided(self):
        self.client.configure_get_activity_streams(['cadence'])
        df = load()
        self.assertColumn(df, 'Cadence', np.dtype('float64'))

    def test_does_not_throw_when_stream_is_not_provided(self):
        self.client.configure_get_activity_streams([])
        df = load()
        self.assertNotIn('Cadence', df)

    def test_does_not_convert_units(self):
        streams = self.client.configure_get_activity_streams(['cadence'])
        expected = streams['cadence'].data
        df = load()
        np.testing.assert_array_equal(expected, df['Cadence'].values)


class DistanceTestCase(StravaTestCase):
    def test_adds_column_when_stream_is_provided(self):
        self.client.configure_get_activity_streams(['time', 'distance'])
        df = load()
        self.assertColumn(df, 'Distance', np.dtype('float64'))

    def test_adds_column_when_stream_is_provided_and_sets_index(self):
        self.client.configure_get_activity_streams(['distance'])
        df = load()
        actual = df.index
        self.assertEqual('Distance', actual.name)
        self.assertEqual(np.dtype('float64'), actual.dtype)

    def test_does_not_throw_when_stream_is_not_provided(self):
        self.client.configure_get_activity_streams([])
        df = load()
        self.assertNotIn('Distance', df)

    def test_does_not_convert_units(self):
        streams = self.client.configure_get_activity_streams(['time', 'distance'])
        expected = streams['distance'].data
        df = load()
        np.testing.assert_array_equal(expected, df['Distance'].values)


class GradientTestCase(StravaTestCase):
    def test_adds_column_when_stream_is_provided(self):
        self.client.configure_get_activity_streams(['grade_smooth'])
        df = load('activity_id', 'token')
        self.assertColumn(df, 'Gradient', np.dtype('float64'))

    def test_does_not_throw_when_stream_is_not_provided(self):
        self.client.configure_get_activity_streams([])
        df = load()
        self.assertNotIn('Gradient', df)

    def test_does_not_convert_units(self):
        streams = self.client.configure_get_activity_streams(['grade_smooth'])
        expected = streams['grade_smooth'].data
        df = load()
        np.testing.assert_array_equal(expected, df['Gradient'].values)


class HeartRateTestCase(StravaTestCase):
    def test_adds_column_when_stream_is_provided(self):
        self.client.configure_get_activity_streams(['heartrate'])
        df = load()
        self.assertColumn(df, 'Heart Rate', np.dtype('float64'))

    def test_does_not_throw_when_stream_is_not_provided(self):
        self.client.configure_get_activity_streams([])
        df = load()
        self.assertNotIn('Heart Rate', df)

    def test_does_not_convert_units(self):
        streams = self.client.configure_get_activity_streams(['heartrate'])
        expected = streams['heartrate'].data
        df = load()
        np.testing.assert_array_equal(expected, df['Heart Rate'].values)


class LatitudeLongitudeTestCase(StravaTestCase):
    def test_adds_columns_when_stream_is_provided(self):
        streams, data = self.create_activity_streams()
        self.client.configure_get_activity_streams(streams, data)
        df = load()
        self.assertColumn(df, 'Latitude', np.dtype('float64'))
        self.assertColumn(df, 'Longitude', np.dtype('float64'))

    def test_extracts_components_from_latlng_tuple(self):
        streams, data = self.create_activity_streams()
        self.client.configure_get_activity_streams(streams, data)
        expected_latitude = [coord[0] for coord in data[0]]
        expected_longitude = [coord[1] for coord in data[0]]
        df = load()
        np.testing.assert_array_equal(expected_latitude, df['Latitude'].values)
        np.testing.assert_array_equal(expected_longitude, df['Longitude'].values)

    def test_does_not_throw_when_stream_is_not_provided(self):
        self.client.configure_get_activity_streams([])
        df = load()
        self.assertNotIn('Latitude', df)
        self.assertNotIn('Longitude', df)

    @staticmethod
    def create_activity_streams():
        streams = ['latlng']
        data = [[(np.random.rand(), np.random.rand()) for _ in range(100)]]
        return streams, data


class TemperatureTestCase(StravaTestCase):
    def test_adds_column_when_stream_is_provided(self):
        self.client.configure_get_activity_streams(['temp'])
        df = load()
        self.assertColumn(df, 'Temperature', np.dtype('float64'))

    def test_does_not_throw_when_stream_is_not_provided(self):
        self.client.configure_get_activity_streams([])
        df = load()
        self.assertNotIn('Temperature', df)

    def test_does_not_convert_units(self):
        streams = self.client.configure_get_activity_streams(['temp'])
        expected = streams['temp'].data
        df = load()
        np.testing.assert_array_equal(expected, df['Temperature'].values)


class VelocityTestCase(StravaTestCase):
    def test_adds_column_when_stream_is_provided(self):
        self.client.configure_get_activity_streams(['velocity_smooth'])
        df = load()
        self.assertColumn(df, 'Velocity', np.dtype('float64'))

    def test_does_not_throw_when_stream_is_not_provided(self):
        self.client.configure_get_activity_streams([])
        df = load()
        self.assertNotIn('Velocity', df)

    def test_converts_from_mps_to_kph(self):
        def mps_to_kph(x):
            return x * 3.6
        streams = self.client.configure_get_activity_streams(['velocity_smooth'])
        expected = [mps_to_kph(x) for x in streams['velocity_smooth'].data]
        df = load()
        np.testing.assert_almost_equal(expected, df['Velocity'].values)


class PowerTestCase(StravaTestCase):
    def test_adds_column_when_stream_is_provided(self):
        self.client.configure_get_activity_streams(['watts'])
        df = load()
        self.assertColumn(df, 'Power', np.dtype('float64'))

    def test_does_not_throw_when_stream_is_not_provided(self):
        self.client.configure_get_activity_streams([])
        df = load()
        self.assertNotIn('Power', df)

    def test_does_not_convert_units(self):
        streams = self.client.configure_get_activity_streams(['watts'])
        expected = streams['watts'].data
        df = load()
        np.testing.assert_array_equal(expected, df['Power'].values)


class TimestampTestCase(StravaTestCase):
    def test_adds_column_when_stream_is_provided_and_sets_index(self):
        self.client.configure_get_activity_streams(['time'])
        df = load()
        actual = df.index
        self.assertEqual('Timestamp', actual.name)
        self.assertEqual(np.dtype('<M8[ns]'), actual.dtype)

    def test_does_not_throw_when_stream_is_not_provided(self):
        self.client.configure_get_activity_streams([])
        df = load()
        self.assertNotIn('Timestamp', df)

