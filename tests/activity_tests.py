# Copyright (c) 2016 Martin Galpin (galpin@gmail.com).

from datetime import datetime
from unittest import TestCase
from mock import Mock


from pycycle import from_strava, strava
from pycycle.activity import ActivityDataFrame
from strava_tests import MockStravaClient


class StravaTestCase(TestCase):
    def setUp(self):
        self.factory = Mock()
        self.client = MockStravaClient()
        self.client.configure()
        self.factory.return_value = self.client
        strava.configure_stravalib_factory(self.factory)

    def test_from_strava_delegates_to_load(self):
        expected_activity_id = 'activity_id'
        expected_access_token = 'token'
        df = from_strava(expected_activity_id, expected_access_token)
        self.factory.assert_called_once_with(expected_access_token)
        self.client.get_activity.assert_called_once_with(expected_activity_id)


class IndexTestCase(TestCase):
    def test_init_when_timestamp_column_exists_sets_index(self):
        data = {'Timestamp': [datetime.now()]}
        sut = ActivityDataFrame.from_dict(data)
        self.assertIsNotNone(sut.index)
        self.assertEqual('Timestamp', sut.index.name)

    def test_init_when_distance_column_exists_sets_index(self):
        data = {'Distance': range(1)}
        sut = ActivityDataFrame.from_dict(data)
        self.assertIsNotNone(sut.index)
        self.assertEqual('Distance', sut.index.name)

    def test_init_when_timestamp_and_distance_columns_exists_prefers_timestamp(self):
        data = {'Timestamp': [datetime.now()], 'Distance': range(1)}
        sut = ActivityDataFrame.from_dict(data)
        self.assertIsNotNone(sut.index)
        self.assertEqual('Timestamp', sut.index.name)