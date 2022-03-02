#!/usr/bin/env python3
"""Main script to generate and email heat recovery reports.
"""
from datetime import datetime
from pathlib import Path
import pickle

from questionary import select, checkbox, Choice
import numpy as np
from rich import print as rprint

import config
import util.data_util
from util.data_util import akwarm_city_data, chgnan
import util.heat_calcs
import invoice.create_invoice
import invoice.send_invoice


def make_report_file_name(customer_name, customer_city, billing_year, billing_month):
    """Returns the file name for the Heat Recovery report for a customer 
    (customer_name, customer_city) and a billing period (billing_year, billing_month).
    """
    return f"{billing_year}-{billing_month:02d} - {customer_city} - {customer_name}.pdf"


def create_report(
    customer, 
    billing_year, 
    billing_month, 
    akwarm_city_data, 
    util_fuel_prices, 
    results,                # dictionary of results (modified by this routine)
):

    # make a dictionary mapping month number to expected gallon savings
    expected_gallons = {}
    for mo in range(1, 13):
        expected_gallons[mo] =  customer[f'feas_g_{mo:02d}']

    # determine gallons to bill and billing date range for the customer.
    gal_saved, bill_start, bill_end, mo_graph, hist_graph = util.heat_calcs.gallons_delivered(
                billing_year, billing_month, customer['sensor_id'], customer['btu_mult'], expected_gallons)

    if not np.isnan(gal_saved):
        path_report = report_folder / make_report_file_name(customer['customer'], customer['city'], year, month)

        # Get the AkWarm Fuel Price
        if customer['akwarm_city'] == '':
            rprint('[purple]You need to select an AkWarm Fuel City.')
            akwarm_fuel_price = np.nan
        else:
            akwarm_fuel_price = akwarm_city_data[customer['akwarm_city']]['Oil1Price']
            if akwarm_fuel_price is None:
                akwarm_fuel_price = np.nan
            if np.isnan(akwarm_fuel_price) and \
                ((customer['fuel_categ'].lower() == 'other') or np.isnan(customer['cust_fuel_override'])):
                rprint('[purple]AkWarm Fuel Price is not available for selected AkWarm City.')
        
        # Determine the price per gallon charged by the electric utility
        if not np.isnan(customer['util_fuel_override']):
            util_fuel_price = customer['util_fuel_override']

        elif customer['fuel_categ'].lower() == 'other':
            if np.isnan(customer['util_akw_disc']):
                rprint('[purple]You have selected the Other utility fuel price cateogry; you need to enter a Discount off of the AkWarm fuel price.')
            util_fuel_price = akwarm_fuel_price * (1.0 - customer['util_akw_disc'])

        elif customer['fuel_categ'] == '':
            rprint('[purple]You need to select a Utility Fuel Price Category if you do not provide an override.')
            util_fuel_price = np.nan

        else:
            util_fuel_price = util_fuel_prices[customer['fuel_categ']]

        if np.isnan(customer['pct_fuel_billed']):
            rprint('[purple]You must enter a % of Utility Fuel Price that is billed for Waste Heat.')
        billed_price = util_fuel_price * customer['pct_fuel_billed']

        # Determine the price of fuel avoided by the waste heat user.
        if not np.isnan(customer['cust_fuel_override']):
            cust_price = customer['cust_fuel_override']
        
        else:
            cust_price = akwarm_fuel_price * (1.0 - chgnan(customer['cust_fuel_disc'], 0.0))
        
        invoice.create_invoice.create_invoice(
            path_report,
            datetime.now(),
            bill_start,
            bill_end,
            f"{customer['city']} - {customer['customer']}",
            customer['utility_name'],
            gal_saved * billed_price,
            gal_saved,
            billed_price,
            cust_price,
            gal_saved * cust_price,
            mo_graph,
            hist_graph
        )

        # update the results dictionary
        results[path_report.name] = dict(
            gal_saved = gal_saved,
            bill_start = bill_start,
            bill_end = bill_end,
            billed_price = billed_price,
            cust_price = cust_price
        )
        rprint(f"[green3]Completed: {gal_saved:,.0f} gallons saved")

    else:
        rprint("[red]No BTU Meter Data available during this billing period.")


if __name__ == '__main__':

    rprint('\n[blue]------- ANTHC Heat Recovery Reporting Program -------\n')
    rprint('[red]Red messages indicate an error that will stop report creation for that customer.')
    rprint('[purple]Purple messages indicate an error that will cause missing information in the report.')
    rprint('[green3]A Green message indicates a report was completed.\n')
    print('Acquiring data...\n')
    cust_recs = util.data_util.customer_records()
    util_fuel_prices = util.data_util.utility_fuel_prices()
    akwarm_city_data, akwarm_lib_version = util.data_util.akwarm_city_data()
    #from pickle import dump, load
    #dump( (util_fuel_prices, akwarm_city_data), open('data.pkl', 'wb'))
    #util_fuel_prices, akwarm_city_data = load(open('data.pkl', 'rb'))

    task_choices = [
        'Create Reports',
        'Email Reports',
    ]
    task = select(
        'Choose an Task:',
        choices=task_choices).ask()

    # convert to an abbreviation for task so easier tested below
    task = 'create' if task == task_choices[0] else 'email'

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
            'Use Space Bar to select desired Customers:',
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

    # Make sure the output directory for reports exists.
    report_folder = Path(config.report_folder)
    try:
        report_folder.mkdir(parents=True, exist_ok=True)
    except:
        rprint(f"[red]Error creating the Report directory specified in the configuration file:[\red]\n{config.report_folder}")

    # Loop through the customers to bill

    # Read the database that holds the summary results from each report created
    # 'results' is a dictionary, with the keys being report file names and the values
    # being dictionaries of summary values.
    results_path = report_folder / 'results.pkl'
    if Path(results_path).exists():
        with open(results_path, 'rb') as results_fh:
            results = pickle.load(results_fh)
    else:
        results = {}

    for customer in target_customers:

        print(f"\nProcessing: {customer['city']} - {customer['customer']}")

        try:
            if task == 'create':
                create_report(customer, year, month, akwarm_city_data, util_fuel_prices, results)

            elif task == 'email':

                if len(customer['cust_email']) > 0 or len(customer['anthc_emails']) > 0:

                    # retrieve summary results for this customer's report for the billing month
                    report_fn = make_report_file_name(customer['customer'], customer['city'], year, month)
                    cr = results[report_fn]

                    invoice.send_invoice.send_email(
                        to_addresses = [cust.strip() for cust in customer['cust_email'].split(',')],
                        to_cc = [addr.strip() for addr in customer['anthc_emails'].split(',')],
                        to_bcc = [],
                        billing_period_start = cr['bill_start'],
                        billing_period_end = cr['bill_end'],
                        gal_saved = cr['gal_saved'],
                        fuel_value = cr['gal_saved'] * cr['cust_price'],
                        pdf_file_name = str(report_folder / report_fn),
                    )
                    rprint('[green3]Email sent!')

                else:
                    rprint('[red]No recipients listed in the customer spreadsheet.')
                

        except BaseException as err:
            rprint(f"[red]Error: {err}")
            #raise err

        finally:
            if task == 'create':
                # Update the pickle file on disk holding report results
                try:
                    with open(results_path, 'wb') as results_fh:
                        pickle.dump(results, results_fh)
                except:
                    rprint('[red]Error saving summary results information to disk.')

    print()