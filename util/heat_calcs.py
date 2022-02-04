'''Module with functions to calculate total heat recovery BTUs in the billing
period and check data quality.
'''

from datetime import datetime, timedelta
import io

import pandas as pd
import numpy as np
import bmondata
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import PIL

import config

def get_btu_data(btu_sensor_id, btu_mult, bmon_server_url, start_date, end_date):
    """Returns a Pandas Dataframe containing the waste heat BTU meter sensor data.
    'sensor_id' is the BMON Sensor ID of that sensor, expected to be found on the
    BMON server pointed to by 'bmon_server_url'.  'start_date' and 'end_date'
    give the date range of the data to return; they are both Python Datetimes.
    'btu_mult' is a multiplier that converts the sensor value into BTUs.

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
    df['btus'] *= btu_mult

    return df

def mpl_to_image():
    """Returns the current Matplotlib figure as a PIL image.
    """
    buf = io.BytesIO()
    plt.savefig(buf)
    buf.seek(0)
    return PIL.Image.open(buf)

def gallons_delivered(bill_month, bill_year, btu_sensor_id, btu_mult, expected_gallons):
    """Returns BTU billing information for the requested month and BTU meter sensor.
    'bill_month' is the month number (1 - 12) of the month to calculate.  'bill_year' 
    is the year of the billing month (e.g. 2022). 'btu_sensor_id' is the BMON Sensor
    ID of the BTU meter.  The 'btu_mult' is applied to convert the sensor reading
    into BTUs; it is 1.0 if no conversion is needed.

    'expected_gallons' is a dictionary that maps month number to expected number
    saved gallons, for graphing purposes.

    Uses values from the config file to convert BTUs into oil gallons avoided.

    Returns a tuple:  oil gallons avoided, start of billing period (Python date/time), end of
        billing period (Python datetime).
    """
    # get sensor readings a full year prior to start of billing month through readings
    # a bit into the next month.
    rdg_start = datetime(bill_year, bill_month, 1) - timedelta(days=365)
    rdg_end = datetime(bill_year, bill_month, 1) + timedelta(days=31)

    df = get_btu_data(btu_sensor_id, btu_mult, config.bmon_url, rdg_start, rdg_end)
    if len(df) == 0:
        return np.nan, None, None, None, None

    # Calculate differences in the BTU count so that resets can be handled (by eliminating
    # negative differences).
    df['change'] = df.btus.diff()
    df['change'] = df.change.where(df.change >= 0.0)

    # add a column for fuel oil gallon equivalents
    df['gallons'] = df.change / (config.oil_btu_content * config.oil_heating_effic)

    # gives a column that gives the timestamp of the prior reading that was involved
    # in the difference.
    df['ts'] = pd.to_datetime(df.index).values
    df['prior_ts'] = df.ts.shift(1)

    # make columns that hold the month number and year number
    df['month'] = df.index.month
    df['year'] = df.index.year

    # now narrow the dataframe to just the billing month.
    df_mo = df.query('month == @bill_month and year == @bill_year').copy()
    if len(df_mo) == 0:
        return np.nan, None, None, None, None

    # drop the rows where this a missing change value, as we need to use the first
    # row with a real change.
    df_mo.dropna(subset=['change'], inplace=True)

    gal_total = df_mo.gallons.sum()
    bill_start = df_mo.iloc[0].prior_ts.to_pydatetime()
    bill_end = df_mo.index[-1].to_pydatetime()

    # Make the graphs
    #plt.style.use('bmh')
    plt.rcParams['figure.constrained_layout.use'] = True
    plt.rcParams['font.size'] = 10
    
    # gallons avoided by day for the billing month.
    plt.clf()
    plt.figure(figsize=(4.4, 3.0))
    df_mo.resample('D').sum().gallons.plot()
    plt.ylim(0, None)
    plt.ylabel('gallons saved / day')
    ax = plt.gca()
    #ax.yaxis.grid()
    ax.xaxis.set_major_formatter(
        mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
    mo_graph_image = mpl_to_image()

    # historical savings.
    plt.clf()
    plt.figure(figsize=(4.4, 3.0))
    dfh = df.resample('M').sum()
    # make the x labels, actual gallons saved and expected gallons for graphing.
    xlabels = []
    actual_gal = []
    expected_gal = []
    bill_mo_str = f'{bill_year}-{bill_month:02d}'
    for d, row in dfh.iterrows():
        this_year_mo = f'{d.year}-{d.month:02d}'
        if this_year_mo <= bill_mo_str:
            # the test above eliminates the bit of data past the billing month.
            xlabels.append(f"{d.strftime('%b')} '{d.strftime('%y')}")
            actual_gal.append(row.gallons)
            expected_gal.append(expected_gallons[d.month])

    plt.bar(xlabels, actual_gal, label='Actual')
    plt.plot(xlabels, expected_gal, 'ro--', label='Expected')
    plt.legend()
    ax = plt.gca()
    #ax.yaxis.grid()
    for label in ax.get_xticklabels(which='major'):
        label.set(rotation=45, horizontalalignment='right')
    plt.ylim(0, None)
    plt.ylabel('gallons saved / month')
    hist_graph_image = mpl_to_image()

    return gal_total, bill_start, bill_end, mo_graph_image, hist_graph_image
