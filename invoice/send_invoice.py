import yagmail
from datetime import datetime


def main(
    user_email: str,
    user_pw: str,
    email_host: str,
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
    user_info = user_information(
        user_email=user_email,
        user_pw=user_pw,
        email_host=email_host,
    )
    recipients = email_recipients(
        to_addreses=to_addresses,
        to_cc=to_cc,
        to_bcc=to_bcc
    )
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
    attachments = email_attachments(
        pdf_file_handle=pdf_file_handle
    )

    send_email(
        yag_info = user_info,
        recipients = recipients,
        subject = subject,
        contents = contents,
        attachments = attachments
    )

    return (
        print('----------------------------------',end='\n'), 
        print('         Email Sent', end='\n'), 
        print('----------------------------------')
    )


### Functions used to build the email
# login information for yagmail user class
def user_information(
    user_email: str,
    user_pw: str,
    email_host: str,
) -> yagmail:
    return yagmail.SMTP(user=user_email, password=user_pw, host=email_host)

# input of addresses for TO, CC, BCC
def email_recipients(
    to_addreses: list,
    to_cc: list,
    to_bcc: list,
) -> dict:
    return {'To': to_addreses, 'CC': to_cc, 'BCC': to_bcc}

# subject line of email
def email_subject(
    billing_period_start: datetime,
    billing_period_end: datetime,
) -> str:
    start = billing_period_start.strftime('%m/%d/%Y')
    end = billing_period_end.strftime('%m/%d/%Y')
    subject = f"Deering Utility Invoice for {start} - {end}"
    return subject
    
# email message body
def email_contents(
    billing_period_start: datetime,
    billing_period_end: datetime,
    bill_amt: float,
    bill_rate_per_gal: float,
    gal_saved: float,
    retail_rate_per_gal: float,
    fuel_value: float
) -> str:
    # addiitional calucaltions for the bod of the paragraph
    start = billing_period_start.strftime('%m/%d/%Y')
    end = billing_period_end.strftime('%m/%d/%Y')
    total_days = (billing_period_end - billing_period_start).days + 1
    gallons_saved = round(gal_saved, 1)
    fuel_savings = fuel_value - bill_amt

    body = [
        "This is an official notice of a bill from Deering Electric Utilities.",
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
        "Attached to this email is the official invoice."
    ]
    return body

# input of str or list of strings for document attachment
def email_attachments(
    pdf_file_handle: str,
) -> str:
    return pdf_file_handle

# complies all email fields into yagmail send method
def send_email(
    yag_info: yagmail,
    recipients: dict,
    subject: str,
    contents: list,
    attachments: str
) -> yagmail:
    return yag_info.send(
        to=recipients['To'],
        cc=recipients['CC'],
        bcc=recipients['BCC'],
        subject=subject,
        contents=contents,
        attachments=attachments
    )

