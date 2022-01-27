#!/usr/bin/env python
from lib.heat_calcs import get_sensor_data

print(get_sensor_data('test-clean_dataset', None, None, None).head())