'''Module with functions to calculate total heat recovery BTUs in the billing
period and check data quality.
'''

import pandas as pd
import bmondata

import config

def get_sensor_data(sensor_id, bmon_server_url, start_date, end_date):
    """Returns a Pandas Dataframe containing the waste heat BTU meter sensor data.
    'sensor_id' is the BMON Sensor ID of that sensor, expected to be found on the
    BMON server pointed to by 'bmon_server_url'.  'start_date' and 'end_date'
    give the date range of the data to return; they are both Python Datetimes.

    If 'sensor_id' begins with 'test-' it is considered to be a test sensor, and
    a test dataframe is returned from the 'test-data/' folder of this repository.
    """

    if sensor_id.startswith('test-'):
        # requesting a test data sensor
        df = pd.read_pickle(f'test-data/{sensor_id[5:]}.pkl', compression='bz2')
        return df
