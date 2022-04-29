from decimal import Decimal
from datetime import datetime
from pathlib import Path

from borb.pdf.document import Document
from borb.pdf.page.page import Page
from borb.pdf.pdf import PDF
from borb.pdf.canvas.layout.page_layout.multi_column_layout import SingleColumnLayout
from PIL import Image

# Invoice information tables and functions  
from invoice.invoice_elements import *


def create_invoice(
    pdf_path: Path,    # file to store invoice in
    invoice_date: datetime,
    bill_period_start: datetime,
    bill_period_end: datetime,
    user: str,
    utility: str,
    bill_amt:  float,
    gal_saved: float,              # gallons saved during billing period
    bill_rate_per_gal: float,    # rate charged per gallon of fuel saved 
    retail_rate_per_gal: float,  # 
    fuel_value: float,
    graph_billing_period: Image,
    graph_historical_period: Image,
    ):

    # Create document
    pdf = Document()

    # Add page
    page = Page()
    pdf.append_page(page)

    # page object for appending items
    page_layout = SingleColumnLayout(page)
    page_layout.vertical_margin = page.get_page_info().get_height() * Decimal(0.02)

    # building the elements/building blocks of the complete invoice. 
    # set in order in which they will be added to the page object 
    building_page = [
        build_title(), 
        build_dates(
            report_date=invoice_date,
            bill_period_start=bill_period_start,
            bill_period_end=bill_period_end,
            user=user,
            utility=utility
        ), 
        table_spacing(),
        build_invoice_amount_due(bill_amt=bill_amt),
        table_spacing(),
        build_items_header(),
        build_item_descriptions(
            gal_saved=gal_saved,
            bill_amt=bill_amt,
            fuel_value=fuel_value,
            bill_period_start=bill_period_start,
            bill_period_end=bill_period_end,
            bill_rate_per_gal=bill_rate_per_gal,
            retail_rate_per_gal=retail_rate_per_gal
        ),
        table_spacing(),
        build_graph_header(),
        build_graph_images(
            graph_month=graph_billing_period, 
            graph_history=graph_historical_period
        ),
        table_spacing(),
        table_spacing(),
        build_notes(),
    ]
    
    for element in building_page:
        page_layout.add(element)

    with open(pdf_path, "wb") as pdf_file_handle:
        PDF.dumps(pdf_file_handle, pdf)

def create_no_data_invoice(
    pdf_path: Path,    # file to store invoice in
    bill_year: int,    # the year being requested, e.g. 2021
    bill_month: int,   # the month being requested, e.g. 11
    invoice_date: datetime,
    user: str,
    utility: str,
    graph_billing_period: Image,
    graph_historical_period: Image,
    ):

    # Create document
    pdf = Document()

    # Add page
    page = Page()
    pdf.append_page(page)

    # page object for appending items
    page_layout = SingleColumnLayout(page)
    page_layout.vertical_margin = page.get_page_info().get_height() * Decimal(0.02)

    # building the elements/building blocks of the complete invoice. 
    # set in order in which they will be added to the page object 
    building_page = [
        build_title(), 
        table_spacing(),
        build_dates_nodata(
            report_date=invoice_date,
            bill_year=bill_year,
            bill_month=bill_month,
            user=user,
            utility=utility
        ),
        table_spacing(),
        build_graph_header(),
        build_graph_images(
            graph_month=graph_billing_period, 
            graph_history=graph_historical_period
        ),
        table_spacing(),
        table_spacing(),
        build_notes(),
    ]
    
    for element in building_page:
        page_layout.add(element)

    with open(pdf_path, "wb") as pdf_file_handle:
        PDF.dumps(pdf_file_handle, pdf)