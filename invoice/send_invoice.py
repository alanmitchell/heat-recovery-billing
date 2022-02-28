"""Module for creating and sending an email containing the Heat Recovery report.
"""
import yagmail
from datetime import datetime

import config


def send_email(
    to_addresses: list,
    to_cc: list,
    to_bcc: list,
    billing_period_start: datetime,
    billing_period_end: datetime,
    gal_saved: float,
    fuel_value: float,
    pdf_file_name: str,
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
        gal_saved=gal_saved,
        fuel_value=fuel_value
    )

    yag_sender = make_sender()
    yag_sender.send(
        to=to_addresses,
        cc=to_cc,
        bcc=to_bcc,
        subject=subject,
        contents=contents,
        attachments=pdf_file_name,
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
    gal_saved: float,
    fuel_value: float
) -> str:
    """Return the body of the email.
    """

    # additional calculations for the body of the paragraph
    start = billing_period_start.strftime('%m/%d/%Y')
    end = billing_period_end.strftime('%m/%d/%Y')
    total_days = (billing_period_end - billing_period_start).total_seconds() / 3600 / 24

    body = [
        "<h2>Heat Recovery Savings Report</h2>",
        "Attached is a report showing the savings you realized from using recovered heat from "
        f"your electric utility.  The report covers the period {start} through {end} for a total "
        f"of {total_days:.1f} days. You saved {gal_saved:,.0f} gallons of heating oil worth ${fuel_value:,.0f}.",
    ]
    return body
