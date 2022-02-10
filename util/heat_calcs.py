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
from PIL import Image

import config

# Constant that controls whether a particular month's data is included in the
# historical Monthly graph.  This is the largest acceptable deviation in 
# billed days from the actual number of days in the month.
MAX_BILL_DAY_ERR = 6.0 

def get_gallon_data(btu_sensor_id, btu_mult, bmon_server_url, bill_year, bill_month):
    """Returns two items in a tuple with information on gallons of oil saved 
    from use of recovered heat:
    Monthly Summary Pandas Dataframe that gives gallons saved and billing date range info
       for the requested billing month and the 12 prior months if available.
    Pandas Series with daily total gallons saved for the requested billing month

    'sensor_id' is the BMON Sensor ID of that sensor, expected to be found on the
    BMON server pointed to by 'bmon_server_url'.  'bill_year' and 'bill_month'
    identify the current billing month.
    'btu_mult' is a multiplier that converts the sensor value into BTUs.

    If 'sensor_id' begins with 'test-' it is considered to be a test sensor, and
    a test dataframe is returned from the 'test-data/' folder of this repository.
    """

    # get sensor readings a full year prior to start of billing month through readings
    # a bit into the next month.
    start_date = datetime(bill_year, bill_month, 1) - timedelta(days=365)
    end_date = datetime(bill_year, bill_month, 1) + timedelta(days=31)

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

    # No longer need btus and change columns
    df.drop(columns=['btus', 'change'], inplace=True)

    # Create a Dataframe with monthly aggregated data
    df_mo = df.resample('M').agg({'gallons': sum, 'ts': 'max', 'prior_ts': 'min'})
    # billing days in the month total
    df_mo['bill_days'] = (df_mo.ts - df_mo.prior_ts).dt.total_seconds() / (3600 * 24)
    # the difference between the billed number of days and the days in the month
    df_mo['full_month_err'] = df_mo.bill_days - df_mo.index.days_in_month
    # trim it back to the billing month and before
    df_mo = df_mo.query('index < @end_date').copy()

    # Create a Pandas Series that gives daily total gallons for the one month that
    # is being billed.
    df_billed_mo = df[(df.index.year == bill_year) & (df.index.month == bill_month)]
    df_daily = df_billed_mo.resample('D').agg({'gallons': sum, 'ts': 'max', 'prior_ts': 'min'})
    df_daily['bill_days'] = (df_daily.ts - df_daily.prior_ts).dt.total_seconds() / (3600 * 24)
    df_daily.drop(columns=['ts', 'prior_ts'], inplace=True)

    return df_mo, df_daily

def mpl_to_image():
    """Returns the current Matplotlib figure as a PIL image.
    """
    buf = io.BytesIO()
    plt.savefig(buf)
    buf.seek(0)
    return Image.open(buf)

def gallons_delivered(bill_year, bill_month, btu_sensor_id, btu_mult, expected_gallons):
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
    df_mo, df_daily = get_gallon_data(btu_sensor_id, btu_mult, config.bmon_url, bill_year, bill_month)

    # Set general graph properties
    plt.rcParams['figure.constrained_layout.use'] = True
    plt.rcParams['font.size'] = 10

    if len(df_daily) > 0:
        # pull the summary record for the requested billing month from the monthly
        # summary dataframe.
        df_billed_month = df_mo[(df_mo.index.year == bill_year) & (df_mo.index.month == bill_month)]
        ser_billed_month = df_billed_month.iloc[0]
        gal_total = ser_billed_month.gallons
        bill_start = ser_billed_month.prior_ts.to_pydatetime()
        bill_end = ser_billed_month.ts.to_pydatetime()
    
        # gallons avoided by day for the billing month.
        plt.clf()
        plt.figure(figsize=(4.4, 3.0))
        df_daily.gallons.plot()
        plt.ylim(0, None)
        plt.ylabel('gallons saved / day')
        ax = plt.gca()
        ax.xaxis.set_major_formatter(
            mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
        mo_graph_image = mpl_to_image()

    else:
        # no data for the requested billing month.
        gal_total = np.nan
        bill_start = None
        bill_end = None
        mo_graph_image = Image.open('images/no-data.png')


    if len(df_mo) > 0:
        # There is some historical data.  Make a graph.
        plt.clf()
        plt.figure(figsize=(4.4, 3.0))
        # make the x labels, actual gallons saved and expected gallons for graphing.
        xlabels = []
        actual_gal = []
        expected_gal = []
        for d, row in df_mo.iterrows():
            xlabels.append(f"{d.strftime('%b')} '{d.strftime('%y')}")
            actual_gal.append(row.gallons)
            expected_gal.append(expected_gallons[d.month])

        plt.bar(xlabels, actual_gal, label='Actual')
        plt.plot(xlabels, expected_gal, 'ro--', label='Expected')
        plt.legend()
        ax = plt.gca()
        for label in ax.get_xticklabels(which='major'):
            label.set(rotation=45, horizontalalignment='right')
        plt.ylim(0, None)
        plt.ylabel('gallons saved / month')
        hist_graph_image = mpl_to_image()

    else:
        hist_graph_image = Image.open('images/no-data.png')

    return gal_total, bill_start, bill_end, mo_graph_image, hist_graph_image
