#!/usr/bin/env python3
from pprint import pprint

from questionary import select, checkbox, Choice

import data_util

print('ANTHC Heat Recovery Billing Program\n')
print('Acquiring data...\n')
cust_recs = data_util.customer_records()
util_fuel_prices = data_util.utility_fuel_prices()
akwarm_city_data = data_util.akwarm_city_data()

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

pprint(target_cust)