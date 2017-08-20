# Copyright (c) 2016 Martin Galpin (galpin@gmail.com).

from collections import namedtuple
from units.predefined import define_units, unit

define_units()

Column = namedtuple('Column', ['name', 'units'])

"""
A list of predefined channels pertinent to cycling.
"""
COLUMNS = [
    Column('Timestamp', None),
    Column('Distance', unit('m')),
    Column('Altitude', unit('m')),
    Column('Gradient', unit('m')),
    Column('Temperature', unit('c')),
    Column('Latitude', unit('deg')),
    Column('Longitude', unit('deg')),
    Column('Heart Rate', unit('bpm')),
    Column('Power', unit('W')),
    Column('Power Balance', unit('%')),
    Column('Cadence', unit('rpm')),
    Column('Velocity', unit('kph'))
]

"""
A dict that provides the predefined channels indexed by name.
"""
COLUMNS_BY_NAME = {x.name: x for x in COLUMNS}
