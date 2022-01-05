print('----------------------------------')
print('      Borb Invoice Creation       ')
print()


# imports from Borb
from borb.pdf.document import Document
from borb.pdf.page.page import Page

from borb.pdf.pdf import PDF

from borb.pdf.canvas.layout.page_layout.multi_column_layout import SingleColumnLayout
from decimal import Decimal

# Invoice information tables and functions  
from invoice_elements import *

### add module import here for importing in values and graph objects

###############################################################

# Create document
pdf = Document()

# Add page
page = Page()
pdf.append_page(page)

# page object for appending items
page_layout = SingleColumnLayout(page)
page_layout.vertical_margin = page.get_page_info().get_height() * Decimal(0.02)


def main(
    ### add the attributes that are required for generating the invoice
    file_name: str,    # file to store invoice in
    invoice_date: datetime,
    bill_period_start: datetime,
    bill_period_end: datetime,
    sender: str,
    customer: str,
    bill_amt:  float,
    gal_saved: str,              # gallons saved during billing period
    bill_rate_per_gal: float,    # rate charged per gallon of fuel saved 
    retail_rate_per_gal: float,  # 
    fuel_value: float,
    graph_billing_period: PIL,
    graph_historical_period: PIL,
):
    # building the elements/building blocks of the complete invoice. 
    # set in order in which they will be added to the page object 
    building_page = [
        #build_title(), 
        build_invoice_dates(
            invoice_date=invoice_date,
            bill_period_start=bill_period_start,
            bill_period_end=bill_period_end
        ), 
        table_spacing(),
        build_address_header(),
        build_address_information(
            sender=sender,
            customer=customer
        ),
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
        #build_historical_graph_header(),
        build_graph_images(
            graph_month=graph_billing_period, 
            graph_history=graph_historical_period
        )
    ]
    
    for element in building_page:
        page_layout.add(element)

    #page_layout.add(Image(one_month_graph()))

    with open(f"{file_name}", "wb") as pdf_file_handle:
        PDF.dumps(pdf_file_handle, pdf)

    return (
        print('',end='\n'), 
        print('   Invoice successfully created', end='\n'), 
        print('----------------------------------')
        )

