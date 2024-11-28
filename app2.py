import pandas as pd
import geopandas as gpd
from shiny import App, render, ui, reactive

# Preload Data
geo_data = gpd.read_file("Data/peru_departamental_simple.geojson")
an10_aggregated = pd.read_csv("Data/an10_aggregated2.dsv", sep = "|")

# Generate list of unique dates for dropdown
date_options = sorted(an10_aggregated['YearMonth'].unique())

# Define UI
app_ui = ui.page_fluid(
    ui.h1("Financial Inclusion in Peru"),
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_select(
                "selected_date", "Select Date (Month-Year):", choices=date_options, selected=date_options[0]
            ),
            ui.input_checkbox("include_lima", "Include Lima", value=True)
        ),
        ui.layout_column_wrap(
            1,
            ui.value_box("Sum of Loans (Millions)", ui.output_text("sum_loans")),
            ui.value_box("Sum of Deposits (Millions)", ui.output_text("sum_deposits")),
        ),
    )
)

# Server logic
def server(input, output, session):
    @reactive.Calc
    def filtered_data():
        return an10_aggregated[an10_aggregated['YearMonth'] == input.selected_date()]

    @output
    @render.text
    def sum_loans():
        total_loans = filtered_data()['Loans'].sum()
        return f"{total_loans:,.2f} M"

    @output
    @render.text
    def sum_deposits():
        total_deposits = filtered_data()['Deposits'].sum()
        return f"{total_deposits:,.2f} M"



app = App(app_ui, server)
