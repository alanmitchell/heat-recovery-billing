#!/usr/bin/env python3
"""Main script to generate and email waste heat bills.
"""
from datetime import datetime
from pathlib import Path

from questionary import select, checkbox, Choice
import numpy as np
from rich import print as rprint
from PIL import Image

import config
import util.data_util
import util.heat_calcs
import invoice.create_invoice

print('ANTHC Heat Recovery Billing Program\n')
print('Acquiring data...\n')
cust_recs = util.data_util.customer_records()
util_fuel_prices = util.data_util.utility_fuel_prices()
akwarm_city_data, akwarm_lib_version = util.data_util.akwarm_city_data()

choices = [
    'Dry Run (no Emails)',
    'Final Run (send Emails)',
]
run_type = select(
    'Is this a:',
    choices=choices).ask()

send_emails = (run_type == choices[1])

choices = [
    'All',
    'Selected Customers'
]
cust_set = select(
    'Process which Customers?',
    choices=choices).ask()

if cust_set == choices[0]:
    target_customers = cust_recs
else:
    # assemble a list of choices
    choices = [Choice(f"{rec['city']} - {rec['customer']}", ix)  for ix, rec in enumerate(cust_recs)]
    selected = checkbox(
        'Select Customers to process:',
        choices = choices
    ).ask()
    target_customers = [cust_recs[ix] for ix in selected]

cur_date = datetime.now()

choices = [
    'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
    'September', 'October', 'November', 'December'
]
def_choice = (cur_date.month - 2) % 12      # default choice is prior month, indexed base 0
month = select(
    'Select Month to Bill:',
    choices=choices,
    default=choices[def_choice]).ask()
month = choices.index(month) + 1

choices = [str(cur_date.year), str(cur_date.year - 1), str(cur_date.year - 2)]
def_choice = 0 if cur_date.month != 1 else 1
year = select(
    'Select Year to Bill:',
    choices=choices,
    default=choices[def_choice]
).ask()
year = int(year)

# Make sure the output directory for invoices exists.
invoice_folder = Path(config.invoice_folder)
try:
    invoice_folder.mkdir(parents=True, exist_ok=True)
except:
    rprint(f"[red]Error creating the Invoice directory specified in the configuration file:[\red]\n{config.invoice_folder}")

# A testing placeholder image for the two graphs.
im_test_graph = Image.open('test-data/sample-graph.png')

# Loop through the customers to bill
for cust in target_customers:

    print(f"\nProcessing: {cust['city']} - {cust['customer']}")

    try:
        # determine BTUs to bill and billing date range for the customer.
        btu_total, bill_start, bill_end = util.heat_calcs.btus_delivered(
                    month, year, cust['sensor_id'], cust['btu_mult'])
        if not np.isnan(btu_total):
            fn_invoice = invoice_folder / f"{year}-{month:02X} - {cust['city']} - {cust['customer']}.pdf"
            gal_saved = btu_total / (config.oil_btu_content * config.oil_heating_effic)
            
            # Determine the price per gallon charged by the electric utility
            if not np.isnan(cust['util_fuel_override']):
                util_fuel_price = cust['util_fuel_override']

            elif cust['fuel_categ'] == 'Other':
                util_fuel_price = akwarm_city_data[cust['akwarm_city']]['Oil1Price'] * (1.0 - cust['util_akw_disc'])

            else:
                util_fuel_price = util_fuel_prices[cust['fuel_categ']]

            billed_price = util_fuel_price * cust['pct_fuel_billed']

            # Determine the price of fuel avoided by the waste heat user.
            if not np.isnan(cust['cust_fuel_override']):
                cust_price = cust['cust_fuel_override']
            
            else:
                cust_price = akwarm_city_data[cust['akwarm_city']]['Oil1Price'] * (1.0 - cust['cust_fuel_disc'])
             
            sender = dict(
                organization = 'Alaska Village Electric Cooperative',
                contact_name = 'Waste Heat Billing Technician',
                address1 = '4831 Eagle Street',
                address2 = '',
                city = 'Anchorage',
                state = 'AK',
                zip = '99503',
                phone = ''
            )
            customer = dict(
                organization = f"{cust['city']} - {cust['customer']}",
                contact_name = 'Accounts Payable',
                address1 = '',
                address2 = '',
                city = '',
                state = '',
                zip = '',
                phone = ''
            )
            invoice.create_invoice.create_invoice(
                fn_invoice,
                datetime.now(),
                bill_start,
                bill_end,
                sender,
                customer,
                gal_saved * billed_price,
                gal_saved,
                billed_price,
                cust_price,
                gal_saved * cust_price,
                im_test_graph,
                im_test_graph
            )
            rprint('[green3]Completed!')

        else:
            rprint("[red]No BTU Meter Data available during this billing period.")

    except BaseException as err:
        rprint(f"[red]Error: {err}")
        #raise err

print()