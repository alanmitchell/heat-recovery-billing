#!/usr/bin/env python
from datetime import datetime

from util.heat_calcs import get_btu_data, gallons_delivered

""" st = datetime(2021, 5, 1)
end = datetime(2021, 7, 31)

print(str(st))

df = get_btu_data('test-clean_dataset', None, st, end)

print(df.head())
print(df.tail())
 """

df = gallons_delivered(3, 2021, 'test-sensor_resets')
print(df.head())
print(df.tail())
print(df.change.sum())