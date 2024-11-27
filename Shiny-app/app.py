import pandas as pd
import altair as alt
import geopandas as gpd
from shiny import App, ui, reactive
from shinywidgets import render_widget, output_widget

# Load the GeoJSON data and deposit data
geo_data = gpd.read_file("../Data/raw/peru_departamental_simple.geojson")
an10 = pd.read_csv("../Data/processed/an10_final.dsv", sep="|")
rep4b2 = pd.read_csv("../Data/processed/rep4b2_final.dsv", sep="|")

# Preprocess an10 data
an10['YearMonth'] = an10['Date'].astype(str).str[:7]
an10_aggregated = an10.groupby(['YearMonth', 'Region'], as_index=False).agg({
    'Deposits': 'sum',
    'Loans': 'sum'
})

# Preprocess rep4b2 data
rep4b2['YearMonth'] = rep4b2['Date'].astype(str).str[:7]
rep4b2_aggregated = rep4b2.groupby(
    ['YearMonth', 'industry_category'], as_index=False)['Loans'].sum()
rep4b2_aggregated = rep4b2_aggregated.sort_values(
    by='Loans', ascending=False)  # Sort by loan value

# Merge GeoDataFrame with deposit data on region column
an10_geo_data = geo_data.merge(
    an10_aggregated, left_on="NOMBDEP", right_on="Region", how="left")

# Generate list of unique dates for dropdown
date_options = sorted(an10_geo_data['YearMonth'].unique())

# Define UI for Shiny app add a input_sidebar ( ui.sidebar (data slicer and checkbox))

# Preprocess and categorize data (code for data preprocessing here as in previous example)

# Define UI for Shiny app with sidebar
app_ui = ui.page_fluid(
    ui.h1("Financial Inclusion in Peru"),

    # Sidebar layout for date selection and checkbox
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_select("selected_date", "Select Date (Month-Year):",
                            choices=date_options, selected=date_options[0]),
            ui.input_checkbox("include_lima", "Include Lima", value=True)
        ),

        # Main content layout with full-width cards, maps, and bar plot
        ui.layout_columns(
            # Top Cards showing total Loans and Deposits
            ui.column(
                6,
                ui.card(
                    ui.card_header("Sum of Loans (Millions)"),
                    # Placeholder for sum of loans
                    ui.output_text("sum_loans"),
                    full_screen=True
                )
            ),
            ui.column(
                6,
                ui.card(
                    ui.card_header("Sum of Deposits (Millions)"),
                    # Placeholder for sum of deposits
                    ui.output_text("sum_deposits"),
                    full_screen=True
                )
            )
        ),
        # Maps for Deposits and Loans
        ui.layout_columns(
            ui.column(
                6,
                output_widget("map_plot_deposits")
            ),
            ui.column(
                6,
                output_widget("map_plot_loans")
            )
        ),
        # Bar plot for Loans by Industry Category
        ui.card(
            ui.card_header("Total Loans by Industry Category"),
            output_widget("bar_plot_loans_by_industry"),
            full_screen=True
        )
    )
)

# Define server logic


def server(input, output, session):
    @reactive.Calc
    def filtered_an10():
        # Filter the data based on the selected date
        selected_data = an10_geo_data[an10_geo_data['YearMonth']
                                      == input.selected_date()]

        # Check the state of the include_lima checkbox and filter out Lima if not selected
        if not input.include_lima():
            selected_data = selected_data[selected_data['NOMBDEP'] != "LIMA"]

        return selected_data

    @reactive.Calc
    def filtered_rep4b2():
        # Filter the industry data based on the selected date
        selected_date = input.selected_date()
        return rep4b2_aggregated[rep4b2_aggregated['YearMonth'] == selected_date]

    @output
    @ui.output_text
    def sum_loans():
        # Calculate total loans for display in the card
        total_loans = filtered_an10()['Loans'].sum(
        ) / 1_000_000  # Convert to millions
        return f"{total_loans:,.2f} M"

    @output
    @ui.output_text
    def sum_deposits():
        # Calculate total deposits for display in the card
        total_deposits = filtered_an10()['Deposits'].sum(
        ) / 1_000_000  # Convert to millions
        return f"{total_deposits:,.2f} M"

    @output
    @render_widget
    def map_plot_deposits():
        data = filtered_an10()

        # Create Altair map chart for Deposits
        map_chart = alt.Chart(data).mark_geoshape().encode(
            color=alt.Color('Deposits:Q', title='Total Deposits',
                            scale=alt.Scale(scheme='blues')),
            tooltip=[alt.Tooltip('NOMBDEP:N', title='Region'), alt.Tooltip(
                'Deposits:Q', title='Deposits')]
        ).project(type='mercator').properties(width=250, height=300)

        return map_chart

    @output
    @render_widget
    def map_plot_loans():
        data = filtered_an10()

        # Create Altair map chart for Loans
        map_chart = alt.Chart(data).mark_geoshape().encode(
            color=alt.Color('Loans:Q', title='Total Loans',
                            scale=alt.Scale(scheme='reds')),
            tooltip=[alt.Tooltip('NOMBDEP:N', title='Region'),
                     alt.Tooltip('Loans:Q', title='Loans')]
        ).project(type='mercator').properties(width=250, height=300)

        return map_chart

    @output
    @render_widget
    def bar_plot_loans_by_industry():
        data = filtered_rep4b2()

        # Create Altair bar chart for Loans by industry category
        bar_chart = alt.Chart(data).mark_bar().encode(
            y=alt.Y('industry_category:N', sort='-x',
                    title="Industry Category"),
            x=alt.X('Loans:Q', title="Total Loans (Millions)",
                    axis=alt.Axis(format=',.0f')),
            tooltip=[alt.Tooltip('industry_category:N', title='Industry'), alt.Tooltip(
                'Loans:Q', title='Total Loans')]
        ).properties(width=500, height=400)

        return bar_chart

# Run the app
app = App(app_ui, server)
