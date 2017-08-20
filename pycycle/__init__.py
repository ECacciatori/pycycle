# Copyright (c) 2016 Martin Galpin (galpin@gmail.com).

from . import strava


def from_strava(activity_id=None, access_token=None):
    """
    Alternate constructor to create an ActivityDataFrame from a Strava activity.

    Example:
        df = pycycle.from_strava(activity_id=0123456)

    Wraps pycycle.strava.load(). For additional help, see load().
    """
    return strava.load(activity_id, access_token)
