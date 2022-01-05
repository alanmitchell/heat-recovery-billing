# Borb Imports
from os import path
from pathlib import Path
from typing import Text
import PIL
from borb.pdf.canvas.color.color import HexColor
from borb.pdf.canvas.layout.table.fixed_column_width_table import FixedColumnWidthTable as FixedTable
from borb.pdf.canvas.layout.table.table import Table
from borb.pdf.canvas.layout.text.paragraph import Paragraph
from borb.pdf.canvas.layout.layout_element import Alignment
from borb.pdf.canvas.layout.image.image import Image
# Other modules
from datetime import datetime
from decimal import Decimal

from test_data import one_month_graph


def build_title() -> Table:
    table_title = FixedTable(number_of_columns=1, number_of_rows=1)
    table_title.add(Paragraph("INVOICE", font="Helvetica-Bold", font_size=24, font_color=HexColor("1a1aff"),
                                text_alignment=Alignment.LEFT))

    table_title.set_padding_on_all_cells(Decimal(2), Decimal(2), Decimal(20), Decimal(2))  
    table_title.no_borders()

    return table_title


def build_invoice_dates(
    invoice_date: datetime, # invoice date, Python date/time
    bill_period_start: datetime, # Start of billing period, date/time
    bill_period_end: datetime,   # Start of billing period, date/time
    ) -> Table:

    table_000 = FixedTable(
        number_of_rows=4, 
        number_of_columns=3, 
        column_widths=[Decimal(1.6), Decimal(1.65), Decimal(0.95)]
    )

    # row 1
    table_000.add(Paragraph('INVOICE', font_size=18, font_color=HexColor("1a1aff"), font="Helvetica-Bold"))
    table_000.add(Paragraph(' '))
    table_000.add(Paragraph(' '))

    # row 2
    table_000.add(Paragraph(' '))
    table_000.add(Paragraph(
        'Invoice Date:', 
        font="Helvetica-Bold", 
        horizontal_alignment=Alignment.RIGHT, 
        font_size=11
    ))
    table_000.add(Paragraph(
        invoice_date.strftime('%B %d, %Y'), 
        horizontal_alignment=Alignment.RIGHT,
        font_size=11
    ))

    #row 3
    table_000.add(Paragraph(' '))
    table_000.add(Paragraph(
        'Start of Billing Period:', 
        font="Helvetica-Bold", 
        horizontal_alignment=Alignment.RIGHT,
        font_size=11
    ))
    table_000.add(Paragraph(
        bill_period_start.strftime('%B %d, %Y'), 
        horizontal_alignment=Alignment.RIGHT,
        font_size=11
    ))

    # row 4
    table_000.add(Paragraph(' '))
    table_000.add(Paragraph(
        'End of Billing Period:', 
        font="Helvetica-Bold", 
        horizontal_alignment=Alignment.RIGHT,
        font_size=11
    ))
    table_000.add(Paragraph(
        bill_period_end.strftime('%B %d, %Y'), 
        horizontal_alignment=Alignment.RIGHT,
        font_size=11
    ))
    
    # Format cells
    table_000.set_padding_on_all_cells(
        padding_top=1, 
        padding_bottom=3, 
        padding_left=2, 
        padding_right=2
    )
    table_000.no_borders()

    return table_000


def table_spacing() -> Table:
    table_space = FixedTable(number_of_rows=1, number_of_columns=1, background_color=None)
    table_space.add(Paragraph(" ", font_size=7))

    # formatting cells
    table_space.set_padding_on_all_cells(1,1,1,1)
    table_space.no_borders()

    return table_space


def build_address_header() -> Table:
    header = FixedTable(
        number_of_rows=1,
        number_of_columns=2,
        background_color=HexColor('cecece')
    )

    header.add(Paragraph(
        'Bill From',
        font="Helvetica-Bold",
        font_size=11,
        vertical_alignment=Alignment.TOP
    ))
    header.add(Paragraph(
        'Bill To',
        font="Helvetica-Bold",
        font_size=11,
        vertical_alignment=Alignment.TOP
    ))

    header.set_padding_on_all_cells(0,1,4,1)
    header._border_bottom
    header._border_right

    return header


def build_address_information(
    sender: dict,           # name & address info in a dictionary of the invoice sender
    customer: dict,          # name & address info dictionary of customer
    ) -> FixedTable:



    'city' 
    'state' 
    'zip' 
    'phone' 

    #  Create table size to match dict size
    rows_needed = len(customer.keys()) -1
    table_001 = FixedTable(number_of_rows=rows_needed, number_of_columns=2)
	
    # create contct names
    table_001.add(Paragraph(
        text=sender['contact_name'], 
        font_size=11
    ))
    table_001.add(Paragraph(
        text=customer['contact_name'],
        font_size=11
    ))   

    # create organization names
    table_001.add(Paragraph(
        text=sender['organization'], 
        font_size=11
    ))
    table_001.add(Paragraph(
        text=customer['organization'],
        font_size=11
    ))   

    # Create address and builidng unit/office titles
    table_001.add(Paragraph(text=sender['address1'],
        font_size=11
    ))

    table_001.add(Paragraph(
        text=customer['address1'],
        font_size=11
    ))   

    table_001.add(Paragraph(
        text=sender['address2'],
        font_size=11
    ))
    table_001.add(Paragraph(
        text=customer['address2'],
        font_size=11
    ))   
  
    # Create city, state zip fomatting
    table_001.add(Paragraph(
        text=f"{sender['city']}, {sender['state']} {sender['zip']}" ,
        font_size=11
    ))
    table_001.add(Paragraph(
        text=f"{customer['city']}, {customer['state']} {customer['zip']}",
        font_size=11
    ))   

    # create phone numbers
    table_001.add(Paragraph(
        text=sender['phone'], 
        font_size=11
    ))
    table_001.add(Paragraph(
        text=customer['phone'],
        font_size=11
    ))   
  

    for i in range(2):
        table_001.add(Paragraph(text=" ", font_size=4))


    table_001.set_padding_on_all_cells(Decimal(2), Decimal(2), Decimal(2), Decimal(2))    		
    table_001.no_borders()
    return table_001


def build_invoice_amount_due(bill_amt: float) -> Table:
    amount_table = FixedTable(
        number_of_rows=1,
        number_of_columns=2,
        column_widths=[Decimal(2.5),1],
        background_color=HexColor('cecece')
    )
    
    amount_table.add(Paragraph(
        text='Amount Due',  
        font='Helvetica-Bold',
        font_size=12,
        text_alignment=Alignment.LEFT,
    ))

    bill_amt = round(bill_amt,2)
    
    amount_table.add(Paragraph(
        text="${:,.2f}".format(bill_amt),
        font_size=12,
        font='Helvetica-Bold',
        text_alignment=Alignment.RIGHT, 
    ))

    amount_table.set_padding_on_all_cells(2,2,4,2)
    return amount_table


def build_items_header() -> Table:
    header = FixedTable(
        number_of_rows=1,
        number_of_columns=1,
    )

    header.add(Paragraph(
        text='Invoice Details',
        font="Helvetica-Bold",
        font_size=11,
        vertical_alignment=Alignment.TOP,
    ))

    header.no_borders()
    header.set_padding_on_all_cells(0,1,2,1)  
    return header


def build_item_descriptions(
    gal_saved: float,         # gallons saved during billing period
    bill_amt: float,          # billing amount in $
    fuel_value: float,       # value of fuel saved (what would have been paid).  
    bill_rate_per_gal: float,    # rate charged per gallon of fuel saved 
    retail_rate_per_gal: float,
    bill_period_start: datetime, # Start of billing period, date/time
    bill_period_end: datetime,  # Start of billing period, date/time
    ) -> Table:
    
    items_table = FixedTable(
        number_of_rows=6,
        number_of_columns=2,
        column_widths=[Decimal(2.5),1]
    )

    # rounding currency values to two decimal places
    fuel_value = round(fuel_value,2)
    bill_amt = round(bill_amt,2)
    # calculating savings
    savings = fuel_value - bill_amt


    ### Headers and values of invoice Items
    #row 1
    billing_days = (bill_period_end - bill_period_start).days + 1
    items_table.add(Paragraph('Days in Billing Period', font_size=10))
    items_table.add(Paragraph(str(billing_days), text_alignment=Alignment.CENTERED, font_size=10))

    #row 2
    items_table.add(Paragraph('Gallons Saved', text_alignment=Alignment.LEFT, font_size=10))
    items_table.add(Paragraph(text=f'{round(gal_saved,1)} gal.', text_alignment=Alignment.CENTERED, 
        font_size=10))

    # row
    items_table.add(Paragraph('Retail Price per Gallon of Fuel', text_alignment=Alignment.LEFT, font_size=10))
    items_table.add(Paragraph(
        text="${:,.2f} / gal.".format(retail_rate_per_gal), 
        text_alignment=Alignment.CENTERED, 
        font_size=10
    ))

    # row
    items_table.add(Paragraph('Bill Price per Gallon of Fuel', text_alignment=Alignment.LEFT, font_size=10))
    items_table.add(Paragraph(
        text="${:,.2f} / gal.".format(bill_rate_per_gal), 
        text_alignment=Alignment.CENTERED, 
        font_size=10
    ))
 

    #row 3
    items_table.add(Paragraph('Value of Fuel', text_alignment=Alignment.LEFT, font_size=10))
    items_table.add(Paragraph(text="${:,.2f}".format(fuel_value), text_alignment=Alignment.CENTERED, 
        font_size=10))

    #row 4
    items_table.add(Paragraph('Fuel Savings', text_alignment=Alignment.LEFT, font_size=10))
    items_table.add(Paragraph(
        text="${:,.2f}".format(savings), 
        text_alignment=Alignment.CENTERED,
        font_size=10
    ))

    # formatting table
    items_table.set_padding_on_all_cells(2,2,4,2)
    return items_table


def build_graph_header() -> Table:
    header = FixedTable(
        number_of_rows=1, 
        number_of_columns=2,
        background_color=HexColor('cecece')
    )

    header.add(Paragraph(
        text='Current Billing Period',
        font="Helvetica-Bold",
        font_size=11,       
    ))

    header.add(Paragraph(
        text='Historical Billing Periods',
        font="Helvetica-Bold",
        font_size=11,
    ))

    header.set_padding_on_all_cells(0,1,4,1)
    return header


def build_graph_images(
    graph_month: PIL, # graph of fuel use during the month, this will be a PIL.Image
    graph_history: PIL,     # graph of the history of savings, also PIL.Image  
    ) -> Table:
    image_table = FixedTable(number_of_rows=1, number_of_columns=2)
    
    for pil_img in [graph_month, graph_history]:
        image_table.add(Image(
            pil_img
        ))

    image_table.set_padding_on_all_cells(2,2,2,2)
    return image_table
