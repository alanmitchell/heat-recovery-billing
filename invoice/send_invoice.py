"""Module for creating and sending an email containing the Heat Recovery report.
"""
import yagmail
from datetime import datetime

import config


def main(
    to_addresses: list,
    to_cc: list,
    to_bcc: list,
    billing_period_start: datetime,
    billing_period_end: datetime,
    bill_amt: float,
    bill_rate_per_gal: float,
    gal_saved: float,
    retail_rate_per_gal: float,
    fuel_value: float,
    pdf_file_handle: str,
):
    """Main function to call to create and send an email of the Heat Recovery Report.
    """

    subject = email_subject(
        billing_period_start=billing_period_start,
        billing_period_end=billing_period_end
    )
    contents = email_contents(
        billing_period_start=billing_period_start,
        billing_period_end=billing_period_end,
        bill_amt=bill_amt,
        bill_rate_per_gal=bill_rate_per_gal,
        gal_saved=gal_saved,
        retail_rate_per_gal=retail_rate_per_gal,
        fuel_value=fuel_value
    )

    yag_sender = make_sender()
    yag_sender.send(
        to=to_addresses,
        cc=to_cc,
        bcc=to_bcc,
        subject=subject,
        contents=contents,
        attachments=pdf_file_handle,
    )


### Functions used to build the email

def make_sender() -> yagmail.sender.SMTP:
    """Use credentials in the config file to make a yagmail sender.
    """
    return yagmail.SMTP(user=config.email_user, password=config.email_password)


def email_subject(
    billing_period_start: datetime,
    billing_period_end: datetime,
) -> str:
    """Return the subject line of the email.
    """

    start = billing_period_start.strftime('%m/%d/%Y')
    end = billing_period_end.strftime('%m/%d/%Y')
    subject = f"Heat Recovery Report for {start} - {end}"
    return subject


def email_contents(
    billing_period_start: datetime,
    billing_period_end: datetime,
    bill_amt: float,
    bill_rate_per_gal: float,
    gal_saved: float,
    retail_rate_per_gal: float,
    fuel_value: float
) -> str:
    """Return the body of the email.
    """

    # additional calculations for the body of the paragraph
    start = billing_period_start.strftime('%m/%d/%Y')
    end = billing_period_end.strftime('%m/%d/%Y')
    total_days = (billing_period_end - billing_period_start).days + 1
    gallons_saved = round(gal_saved, 1)
    fuel_savings = fuel_value - bill_amt

    body = [
        "Heat Recovery Savings Report",
        "------------------------------------------------------------------------------------------------",
        "- ", #spacing 
        f"""This billing period includes the days from {start} through {end} for a total 
        of {total_days} billing days.""",
        f"""The amount of waste heat measured equated to {gallons_saved} gallons of fuel. 
        This fuel is charged at ${bill_rate_per_gal:,.2f}/gallon for a calculated bill amount of 
        ${bill_amt:,.2f}.""",
        f"""The retail rate of fuel is at ${retail_rate_per_gal:,.2f}/gallon which 
        puts the value of the fuel saved from using the excess heat to be ${fuel_value:.2f}. 
        This results in a fuel saving cost of {fuel_savings:,.2f}.""",
        "-" # spacing,
        "-" # spacing,
        "Attached to this email is the report as a PDF."
    ]
    return body
