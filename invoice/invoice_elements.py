from os import path
from pathlib import Path
from typing import Text
from datetime import datetime
from decimal import Decimal

from PIL import Image as PIL_Image
from borb.pdf.canvas.color.color import HexColor
from borb.pdf.canvas.layout.table.fixed_column_width_table import FixedColumnWidthTable as FixedTable
from borb.pdf.canvas.layout.table.table import Table
from borb.pdf.canvas.layout.text.paragraph import Paragraph
from borb.pdf.canvas.layout.layout_element import Alignment
from borb.pdf.canvas.layout.image.image import Image

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
        'Prior Reading Date:', 
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
        'Current Reading Date:', 
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

    # add a city/state/zip item to dictionary so we can loop through the keys
    # to add to the document.
    def make_csz(ent):
        csz = f"{ent['city']}, {ent['state']} {ent['zip']}".strip()
        if len(csz) == 1:
            # there is only a comma, so blank it out
            csz = ''
        return csz

    sender['city_st_zip'] = make_csz(sender)
    customer['city_st_zip'] = make_csz(customer)

    # items to put into the table
    items = (
        'contact_name',
        'organization',
        'address1',
        'address2',
        'city_st_zip',
        'phone'
        )

    #  Create table size to match items to display + blank row at bottom
    rows_needed = len(items) + 1
    table_001 = FixedTable(number_of_rows=rows_needed, number_of_columns=2)
	
    for item in items:
        for entity in (sender, customer):
            item_text = entity[item]
            if len(item_text) == 0:
                item_text = ' '     # blank text causes an error
            table_001.add(Paragraph(
                text=item_text,
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
    fuel_value = round(fuel_value, 2)
    bill_amt = round(bill_amt, 2)
    # calculating savings
    savings = fuel_value - bill_amt


    ### Headers and values of invoice Items
    #row 1
    billing_days = (bill_period_end - bill_period_start).total_seconds()/(3600 * 24)
    items_table.add(Paragraph('Days in Billing Period', font_size=10))
    items_table.add(Paragraph(f'{billing_days:.1f} days', text_alignment=Alignment.CENTERED, font_size=10))

    #row 2
    items_table.add(Paragraph('Gallons Saved', text_alignment=Alignment.LEFT, font_size=10))
    items_table.add(Paragraph(text=f'{gal_saved:,.1f} gallons', text_alignment=Alignment.CENTERED, 
        font_size=10))

    # row
    items_table.add(Paragraph('Retail Price per Gallon of Fuel', text_alignment=Alignment.LEFT, font_size=10))
    items_table.add(Paragraph(
        text="${:,.2f} / gallon".format(retail_rate_per_gal), 
        text_alignment=Alignment.CENTERED, 
        font_size=10
    ))

    # row
    items_table.add(Paragraph('Billed Price per Gallon of Fuel', text_alignment=Alignment.LEFT, font_size=10))
    items_table.add(Paragraph(
        text="${:,.2f} / gallon".format(bill_rate_per_gal), 
        text_alignment=Alignment.CENTERED, 
        font_size=10
    ))
 
    #row 3
    items_table.add(Paragraph('Value of Fuel', text_alignment=Alignment.LEFT, font_size=10))
    items_table.add(Paragraph(text="${:,.0f}".format(fuel_value), text_alignment=Alignment.CENTERED, 
        font_size=10))

    #row 4
    items_table.add(Paragraph('Fuel Cost Savings from Use of Waste Heat', text_alignment=Alignment.LEFT, font_size=10))
    items_table.add(Paragraph(
        text="${:,.0f}".format(savings), 
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
    graph_month: PIL_Image,       # graph of fuel use during the month, this will be a PIL.Image
    graph_history: PIL_Image,     # graph of the history of savings, also PIL.Image  
    ) -> Table:
    image_table = FixedTable(number_of_rows=1, number_of_columns=2)
    
    image_table.add(Image(graph_month))
    image_table.add(Image(graph_history))

    image_table.set_padding_on_all_cells(2,2,2,2)
    return image_table
