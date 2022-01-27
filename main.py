#!/usr/bin/env python3
"""Main script to generate and email waste heat bills.
"""
from pprint import pprint
from datetime import datetime

from questionary import select, checkbox, Choice

import util.data_util
import util.heat_calcs

print('ANTHC Heat Recovery Billing Program\n')
print('Acquiring data...\n')
cust_recs = util.data_util.customer_records()
util_fuel_prices = util.data_util.utility_fuel_prices()
akwarm_city_data = util.data_util.akwarm_city_data()

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
    target_cust = cust_recs
else:
    # assemble a list of choices
    choices = [Choice(f"{rec['city']} - {rec['customer']}", ix)  for ix, rec in enumerate(cust_recs)]
    selected = checkbox(
        'Select Customers to process:',
        choices = choices
    ).ask()
    target_cust = [cust_recs[ix] for ix in selected]

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
