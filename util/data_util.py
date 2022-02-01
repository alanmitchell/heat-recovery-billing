import math
from io import BytesIO
import gzip
import xml.etree.ElementTree as ET

import requests
import gspread

import config

# Get a handle to the Heat Recovery Billing spreadsheet on Google Sheets.  Needed 
# for a couple different data routines below.
gc = gspread.service_account(filename=config.spreadsheet_creds_file)
cust_wb = gc.open_by_key(config.spreadsheet_id)

def customer_records():
    """Returns a list of heat recovery customer records from the customer Google Sheet.
    Each record is a dictionary with keys being the column abbreviations.  Any values that
    can be converted to floating point numbers are converted.
    """
    # list of the numeric fiedls
    num_flds = ('btu_mult', 'pct_fuel_billed', 'util_akw_disc', 'util_fuel_override', 'cust_fuel_disc', 
        'cust_fuel_override', 'feas_g_01', 'feas_g_02', 'feas_g_03', 'feas_g_04', 'feas_g_05', 'feas_g_06', 
        'feas_g_07', 'feas_g_08', 'feas_g_09', 'feas_g_10', 'feas_g_11', 'feas_g_12')

    rows = cust_wb.worksheet('Customers').get_all_values()

    # find row with column abbreviations and then make records from the rest of the rows
    recs = []
    fld_names = None
    for row in rows:
        if 'sensor_id' in row:
            fld_names = row.copy()
        else:
            if fld_names:
                rec = dict(zip(fld_names, row))
                for key, val in rec.items():
                    if key in num_flds:
                        if val == '':
                            val = math.nan
                        elif val.endswith('%'):
                            val = float(val[:-1]) / 100.0
                        else:
                            val = float(val.replace('$', '').replace(',', ''))
                        rec[key] =  val

                recs.append(rec)

    return recs

def utility_fuel_prices():
    """Returns a dictionary mapping utility fuel price category to an actual fuel price per gallon.
    Data comes from the Heat Recovery Billing spreadsheet.
    """
    rows = cust_wb.worksheet('Utility Fuel Prices').get_all_values()
    prices = {}
    for row in rows[1:]:
        try:
            prices[row[0]] = float(row[1].replace('$', ''))
        except:
            prices[row[0]] = math.nan

    return prices

def akwarm_lib_xml():
    """Returns the root XML ElementTree of the most current AkWarm Energy Library.
    Prints the name of that library.  Requires an Internet connection to retrieve
    data online.
    """
    resp = requests.get('https://analysisnorth.com/AkWarm/update_combined/Library_Info.txt')
    cur_lib_name = resp.text.splitlines()[-1].split('\t')[0]
    resp = requests.get(f'https://analysisnorth.com/AkWarm/update_combined/{cur_lib_name}')
    res = [ x ^ 30 for x in resp.content]
    file_res = BytesIO(bytes(res))
    del res   # to save memory
    lib = gzip.GzipFile(mode='r', fileobj=file_res).read()
    root = ET.fromstring(lib.decode('utf-8'))
    return root, cur_lib_name

def akwarm_city_data():
    """Returns a dictionary keyed on City Name with the dictionary value being a dictionary
    of key fields and values from the City table in the most recent AkWarm Energy Library.
    Makes an attempt to convert the field value to a float.
    """
    root, lib_name = akwarm_lib_xml()
    city_data = {}
    targets = ('Oil1Price', 'Oil2Price')
    cities = root.find("./item/key/string[.='City']/../../value/ArrayOfCity")
    for city in cities:
        fields = {}    
        for fld in targets:
            val = city.find(fld).text
            try:
                val = float(city.find(fld).text)
            except:
                pass
            fields[fld] = val
        city_data[city.find("Name").text] = fields

    return city_data, lib_name
