# Copyright (c) 2016 Martin Galpin (galpin@gmail.com).

from pandas import DataFrame


class ActivityDataFrame(DataFrame):
    """
    A pandas.DataFrame that has specialized information related to cycling
    analysis. In addition to the standard DataFrame constructor arguments,
    ActivityDataFrame also accepts the following keyword arguments:

    Keyword Arguments
    -----------------
    athlete_dict : dict (optional)
        A dict of athlete parameters.
    """

    def __init__(self, *args, **kwargs):
        self.athlete_dict = kwargs.pop('athlete_dict', None)
        super(ActivityDataFrame, self).__init__(*args, **kwargs)
        self._maybe_set_index()

    _metadata = ['athlete_dict']

    @property
    def _constructor(self):
        return ActivityDataFrame

    def _maybe_set_index(self):
        if 'Timestamp' in self.columns:
            self.set_index('Timestamp', inplace=True)
        elif 'Distance' in self.columns:
            self.set_index('Distance', inplace=True)
