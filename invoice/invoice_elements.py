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
    table_title = FixedTable(
        number_of_columns=2, 
        number_of_rows=1,
        column_widths=[Decimal(3.0), Decimal(2.0)],
        )
    table_title.add(
        Image(Path('images/logo.png'), width=Decimal(200), height=Decimal(78))
    )
    table_title.add(Paragraph(
        'Heat Recovery Savings Report', 
        font_size=24, 
        font_color=HexColor("1a1aff"), 
        font="Helvetica-Bold",
        horizontal_alignment=Alignment.RIGHT,
    ))

    table_title.set_padding_on_all_cells(Decimal(2), Decimal(2), Decimal(20), Decimal(2))  
    table_title.no_borders()

    return table_title


def build_dates(
    report_date: datetime, # invoice date, Python date/time
    bill_period_start: datetime, # Start of billing period, date/time
    bill_period_end: datetime,   # Start of billing period, date/time
    user: str,                   # Name of heat user
    utility: str,                # Name of utility supplying heat
    ) -> Table:

    table_000 = FixedTable(
        number_of_rows=3, 
        number_of_columns=4, 
        column_widths=[Decimal(0.9), Decimal(1.1), Decimal(1.1), Decimal(0.95)]
    )

    # row 1
    table_000.add(Paragraph(
        'Building Owner:', 
        font="Helvetica-Bold", 
        #horizontal_alignment=Alignment.RIGHT, 
        font_size=11
    ))
    table_000.add(Paragraph(user, font_size=11))
    table_000.add(Paragraph(
        'Report Date:', 
        font="Helvetica-Bold", 
        horizontal_alignment=Alignment.RIGHT, 
        font_size=11
    ))
    table_000.add(Paragraph(
        report_date.strftime('%B %d, %Y'), 
        horizontal_alignment=Alignment.RIGHT,
        font_size=11
    ))

    #row 2
    table_000.add(Paragraph(
        'Utility:', 
        font="Helvetica-Bold", 
        #horizontal_alignment=Alignment.RIGHT, 
        font_size=11
    ))
    table_000.add(Paragraph(utility, font_size=11))
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

    # row 3
    table_000.add(Paragraph(' '))
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


def build_invoice_amount_due(bill_amt: float) -> Table:
    amount_table = FixedTable(
        number_of_rows=1,
        number_of_columns=2,
        column_widths=[Decimal(2.5),1],
        background_color=HexColor('cecece')
    )
    
    amount_table.add(Paragraph(
        text='Expected payment to Utility for recovered heat',  
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
        text='Report Details',
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
    items_table.add(Paragraph('Days in Reporting Period', font_size=10))
    items_table.add(Paragraph(f'{billing_days:.1f} days', text_alignment=Alignment.CENTERED, font_size=10))

    #row 2
    items_table.add(Paragraph('Gallons of Heating Oil you Saved', text_alignment=Alignment.LEFT, font_size=10))
    items_table.add(Paragraph(text=f'{gal_saved:,.1f} gallons', text_alignment=Alignment.CENTERED, 
        font_size=10))

    # row
    items_table.add(Paragraph('Price you would normally Pay per Gallon of Heating Oil **', text_alignment=Alignment.LEFT, font_size=10))
    items_table.add(Paragraph(
        text="${:,.2f} / gallon".format(retail_rate_per_gal), 
        text_alignment=Alignment.CENTERED, 
        font_size=10
    ))

    # row
    items_table.add(Paragraph('Price Paid for Recovered Heat', text_alignment=Alignment.LEFT, font_size=10))
    items_table.add(Paragraph(
        text="${:,.2f} / gallon equivalent".format(bill_rate_per_gal), 
        text_alignment=Alignment.CENTERED, 
        font_size=10
    ))
 
    #row 3
    items_table.add(Paragraph('Your Avoided Cost of Heating Oil this month', text_alignment=Alignment.LEFT, font_size=10))
    items_table.add(Paragraph(text="${:,.0f}".format(fuel_value), text_alignment=Alignment.CENTERED, 
        font_size=10))

    #row 4
    items_table.add(Paragraph('Your Cost Savings by using Recovered Heat this month', text_alignment=Alignment.LEFT, font_size=10))
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
        text='Daily Savings for Month Reported',
        text_alignment=Alignment.CENTERED,
        font="Helvetica-Bold",
        font_size=11,       
    ))

    header.add(Paragraph(
        text='Last 12 Months',
        text_alignment=Alignment.CENTERED,
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
    
    im_wid = Decimal(230)
    im_ht = Decimal(140)
    image_table.add(Image(graph_month, width=im_wid, height=im_ht))
    image_table.add(Image(graph_history, width=im_wid, height=im_ht))

    image_table.set_padding_on_all_cells(9,3,2,3)
    image_table.no_borders()

    return image_table

def build_notes():
    notes_table = FixedTable(number_of_rows=3, number_of_columns=1)
    notes_table.add(Paragraph(
        text='** From State of Alaska community database.  If this figure is not accurate, email energy@anthc.org with the correct cost per gallon.',
        font_size=10,
    ))
    notes_table.add(Paragraph(text=' '))
    notes_table.add(Paragraph(
        text='This monthly report is intended to show you how much heat recovered from the nearby power plant was used to used to heat your building. It will also show your savings if you had to heat your entire building using your boiler or furnace.',
        font_size=10,
    ))
    notes_table.no_borders()

    return notes_table
