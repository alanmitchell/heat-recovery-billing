'''Module with functions to calculate total heat recovery BTUs in the billing
period and check data quality.
'''

from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import bmondata

import config

def get_btu_data(btu_sensor_id, bmon_server_url, start_date, end_date):
    """Returns a Pandas Dataframe containing the waste heat BTU meter sensor data.
    'sensor_id' is the BMON Sensor ID of that sensor, expected to be found on the
    BMON server pointed to by 'bmon_server_url'.  'start_date' and 'end_date'
    give the date range of the data to return; they are both Python Datetimes.

    If 'sensor_id' begins with 'test-' it is considered to be a test sensor, and
    a test dataframe is returned from the 'test-data/' folder of this repository.

    The returned DataFrame has one column with the name 'btus'; the DataFrame
    index has the timestamps of the readings.
    """

    if btu_sensor_id.startswith('test-'):
        # requesting a test data sensor
        df = pd.read_pickle(f'test-data/{btu_sensor_id[5:]}.pkl', compression='bz2')
        df = df.query('index >= @start_date and index <= @end_date').copy()

    else:
        # get data from BMON
        server = bmondata.Server(bmon_server_url)
        df = server.sensor_readings(btu_sensor_id, str(start_date), str(end_date))

    df.columns = ['btus']

    return df

def btus_delivered(bill_month, bill_year, btu_sensor_id, btu_mult=1.0):
    """Returns BTU billing information for the requested month and BTU meter sensor.
    'bill_month' is the month number (1 - 12) of the month to calculate.  'bill_year' 
    is the year of the billing month (e.g. 2022). 'btu_sensor_id' is the BMON Sensor
    ID of the BTU meter.  The 'btu_mult' is applied to convert the sensor reading
    into BTUs; it is 1.0 if no conversion is needed.

    Returns a tuple:  BTUs delivered, start of billing period (Python date/time), end of
        billing period (Python datetime).
    """
    # get sensor readings a full month prior to start of billing month through readings
    # a bit into the next month.
    rdg_start = datetime(bill_year, bill_month, 1) - timedelta(days=31)
    rdg_end = datetime(bill_year, bill_month, 1) + timedelta(days=31)

    df = get_btu_data(btu_sensor_id, config.bmon_url, rdg_start, rdg_end)
    if len(df) == 0:
        return np.nan, None, None

    # Calculate differences in the BTU count so that resets can be handled (by eliminating
    # negative differences).
    df['change'] = df.btus.diff()
    df['change'] = df.change.where(df.change >= 0.0)

    # gives a column that gives the timestamp of the prior reading that was involved
    # in the difference.
    df['ts'] = pd.to_datetime(df.index).values
    df['prior_ts'] = df.ts.shift(1)

    # make a column that holds the month number
    df['month'] = df.index.month

    # now narrow the dataframe to just the billing month.
    df_mo = df.query('month == @bill_month').copy()
    if len(df_mo) == 0:
        return np.nan, None, None

    # drop the rows where this a missing change value, as we need to use the first
    # row with a real change.
    df_mo.dropna(subset=['change'], inplace=True)

    btu_total = df_mo.change.sum() * btu_mult
    bill_start = df_mo.iloc[0].prior_ts.to_pydatetime()
    bill_end = df_mo.index[-1].to_pydatetime()

    return btu_total, bill_start, bill_end
