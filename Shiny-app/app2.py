import pandas as pd
import altair as alt
import geopandas as gpd
from shiny import App, Inputs, render, ui, reactive
from shinywidgets import render_widget, output_widget


# Load the GeoJSON data and deposit data
geo_data = gpd.read_file("Data/raw/peru_departamental_simple.geojson")
an10 = pd.read_csv("Data/processed/an10_final.dsv", sep="|")
rep4b2 = pd.read_csv("Data/processed/rep4b2_final.dsv", sep="|")
an03 = pd.read_csv("Data/processed/an03_final.dsv", sep="|")


# Preprocess an10 data
an10['YearMonth'] = an10['Date'].astype(str).str[:7]

an10_aggregated = an10.groupby(['YearMonth', 'Region'], as_index=False).agg({
    'Deposits': lambda x: x.sum() / 1_000_000,  # Convert to millions
    'Loans': lambda x: x.sum() / 1_000_000     # Convert to millions
})

an10_aggregated = an10_aggregated[an10_aggregated['YearMonth'] >= '2019-01']

# Merge GeoDataFrame with deposit data on region column
an10_geo_data = geo_data.merge(
    an10_aggregated, left_on="NOMBDEP", right_on="Region", how="left")

date_options = sorted(an10_geo_data['YearMonth'].unique())


# Preprocess rep4b2 data
rep4b2['YearMonth'] = rep4b2['Date'].astype(str).str[:7]

rep4b2_aggregated = rep4b2.groupby(
    ['YearMonth', 'industry_category'], as_index=False)['Loans'].sum()
rep4b2_aggregated = rep4b2_aggregated.sort_values(
    by='Loans', ascending=False)  # Sort by loan value

rep4b2_aggregated = rep4b2_aggregated[rep4b2_aggregated['YearMonth'] >= '2019-01']

# Preprocess an03 data
an03['YearMonth'] = an03['Date'].astype(str).str[:7]

an03_aggregated = an03.groupby(['YearMonth', 'FI_TYPE', 'LOAN_TYPE', 'industry_cat'], as_index=False).agg({
    'Loans': lambda x: x.sum() / 1_000_000,
    'Loans_new': lambda x: x.sum() / 1_000,
    'Debtors': lambda x: x.sum() / 1_000
})

an03_aggregated = an03_aggregated[an03_aggregated['YearMonth'] >= '2019-01']

# Building the UI

# Step 1: Function to create unique sidebars


def create_sidebar(page):
    return
    ui.sidebar(
        ui.input_select(
            f"selected_date_{page}",
            "Select Date (Month-Year):",
            choices=date_options,
            selected=date_options[0]
        ),
        ui.input_checkbox(
            f"include_lima_{page}",
            "Include Lima",
            value=True
        )
    )


# Step 2: Page By Region
page_by_region = ui.page_fluid(
    ui.h1("Financial Inclusion by Region"),
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_select(
                "selected_date_region",
                "Select Date (Month-Year):",
                choices=date_options,
                selected=date_options[0]
            ),
            ui.input_checkbox(
                "include_lima_region",
                "Include Lima",
                value=True
            )
        ),
        ui.layout_column_wrap(
            3,  # Three boxes in one row
            ui.value_box(
                title="Sum of Loans (Millions)",
                value=ui.output_text("sum_loans_region"),
                full_screen=True
            ),
            ui.value_box(
                title="Sum of Deposits (Millions)",
                value=ui.output_text("sum_deposits_region"),
                full_screen=True
            ),
            ui.value_box(
                title="Number of Financial Institutions",
                value=ui.output_text("num_financial_institutions_region"),
                full_screen=True
            )
        ),
        ui.layout_columns(
            ui.column(
                12,
                ui.card(
                    ui.card_header("Loans Map"),
                    output_widget("map_plot_loans_region")
                )
            ),
            ui.column(
                12,
                ui.card(
                    ui.card_header("Deposits Map"),
                    output_widget("map_plot_deposits_region")
                )
            )
        )
    )
)

# Step 3: Page By Industry
page_by_industry = ui.page_fluid(
    ui.h1("Financial Inclusion by Industry"),
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_select(
                "selected_date_industry",
                "Select Date (Month-Year):",
                choices=date_options,
                selected=date_options[0]
            ),
            ui.input_checkbox(
                "include_personal_mortgage_loans",
                "Include Personal/Mortgage Loans",
                value=True
            )
        ),
        ui.layout_column_wrap(
            3,  # Three boxes in one row
            ui.value_box(
                title="Sum of Loans (Millions)",
                value=ui.output_text("sum_loans_industry"),
                full_screen=True
            ),
            ui.value_box(
                title="Num. Debtors (Thousands)",
                value=ui.output_text("sum_debtors_industry"),
                full_screen=True
            ),
            ui.value_box(
                title="Number of Financial Institutions",
                value=ui.output_text("num_financial_institutions_industry"),
                full_screen=True
            )
        ),
        ui.layout_columns(
            ui.column(
                12,
                ui.card(
                    ui.card_header("Total Loans by Industry"),
                    output_widget("loans_by_industry_pie"),
                    width=500,
                    height=400,
                )

            ),
            ui.column(
                12,
                ui.card(
                    ui.card_header(
                        "Number of debtors and the average loan by Industry"),
                    output_widget("scatter_loans_vs_debtors"),
                    width=600,
                    height=400,
                )
            )
        )
    )
)

# Step 4: Main App UI
app_ui = ui.page_navbar(
    ui.nav_panel("By Region", page_by_region),
    ui.nav_panel("By Industry", page_by_industry),
    title="Financial Inclusion Dashboard"
)

# Building the Server Logic


def server(input, output, session):
    # By Region
    @reactive.Calc
    def filtered_an10_region():
        selected_data = an10_geo_data[an10_geo_data['YearMonth']
                                      == input.selected_date_region()]
        if not input.include_lima_region():
            selected_data = selected_data[selected_data['NOMBDEP'] != "LIMA"]
        return selected_data

    @output
    @render.text
    def sum_loans_region():
        total_loans = filtered_an10_region()['Loans'].sum()
        return f"{total_loans:,.0f} M"

    @output
    @render.text
    def sum_deposits_region():
        total_deposits = filtered_an10_region()['Deposits'].sum()
        return f"{total_deposits:,.0f} M"

    @output
    @render.text
    def num_financial_institutions_region():
        unique_institutions = an10[an10['YearMonth'] == input.selected_date_region(
        )]['CODIGO_ENTIDAD_ID'].nunique()
        return f"{unique_institutions:,}"

    @output
    @render_widget
    def map_plot_loans_region():
        data = filtered_an10_region()
        map_chart = alt.Chart(data).mark_geoshape().encode(
            color=alt.Color('Loans:Q', title='Total Loans',
                            scale=alt.Scale(scheme='reds')),
            tooltip=[
                alt.Tooltip('NOMBDEP:N', title='Region'),
                alt.Tooltip('Loans:Q', title='Loans', format=',.2f')
            ]
        ).project(type='mercator').properties(
            title=f"Loans by Region in Peru ({input.selected_date_region()})",
            width=280,
            height=350
        )
        return map_chart

    @output
    @render_widget
    def map_plot_deposits_region():
        data = filtered_an10_region()
        map_chart = alt.Chart(data).mark_geoshape().encode(
            color=alt.Color('Deposits:Q', title='Total Deposits',
                            scale=alt.Scale(scheme='blues')),
            tooltip=[
                alt.Tooltip('NOMBDEP:N', title='Region'),
                alt.Tooltip('Deposits:Q', title='Deposits', format=',.2f')
            ]
        ).project(type='mercator').properties(
            title=f"Deposits by Region in Peru ({
                input.selected_date_region()})",
            width=280,
            height=350
        )
        return map_chart

    # By Industry
    @reactive.Calc
    def filtered_an3():
        selected_data = an03_aggregated[an03_aggregated['YearMonth']
                                        == input.selected_date_industry()]
        if not input.include_personal_mortgage_loans():
            selected_data = selected_data[selected_data['industry_cat']
                                          != "Personal/Mortgage loans"]
        return selected_data

    @output
    @render.text
    def sum_loans_industry():
        total_loans = filtered_an3()['Loans'].sum()
        return f"{total_loans:,.0f} M"

    @output
    @render.text
    def sum_debtors_industry():
        total_deposits = filtered_an3()['Debtors'].sum()
        return f"{total_deposits:,.0f} K"

    @output
    @render.text
    def num_financial_institutions_industry():
        unique_institutions = an10[an10['YearMonth'] == input.selected_date_industry(
        )]['CODIGO_ENTIDAD_ID'].nunique()
        return f"{unique_institutions:,}"

    @output
    @render_widget
    def loans_by_industry():
        data = filtered_an3()

        pie_chart = alt.Chart(data).mark_arc().encode(
            theta=alt.Theta('Loans:Q', title="Total Loans"),
            # Sorting categories in descending order
            color=alt.Color('industry_cat:N',
                            title="Industry Category", sort='-x'),
            tooltip=[alt.Tooltip('industry_cat:N', title='Industry'), alt.Tooltip(
                'Loans:Q', title='Total Loans')]
        ).properties(
            title="Total Loans by Industry (Sorted)",
            width=400,  # Adjust the width for better visibility
            height=400  # Adjust the height as needed
        ).sort(alt.EncodingSortField(
            field="Loans",  # Sort by loan amounts
            order="descending"  # Order from highest to lowest
        ))

        return pie_chart

    @output
    @render_widget
    def new_loans_by_industry():
        data = filtered_an3()

        bar_chart = alt.Chart(data).mark_bar().encode(
            y=alt.Y('industry_cat:N', sort='-x', title="Industry Category"),
            x=alt.X('Loans_new:Q', title="Total New Loans"),
            tooltip=[alt.Tooltip('industry_cat:N', title='Industry'), alt.Tooltip(
                'Loans:Q', title='Total Loans')]
        ).properties(
            width=200,
            height=300)
        return bar_chart

    @output
    @render_widget
    def debtors_by_industry():
        data = filtered_an3()
        bar_chart = alt.Chart(data).mark_bar().encode(
            y=alt.Y('industry_cat:N', sort='-x', title="Industry Category"),
            x=alt.X('Debtors:Q', title="Number of debtors"),
            tooltip=[alt.Tooltip('industry_cat:N', title='Industry'), alt.Tooltip(
                'Loans:Q', title='Total Loans')]
        ).properties(
            width=200,
            height=300)
        return bar_chart

    @output
    @render_widget
    def scatter_loans_vs_debtors():
        x_max = 500  # Max for Number of Debtors
        y_max = 500  # Max for Average Loan per Debtor

        data = filtered_an3()
        grouped_data = data.groupby('industry_cat', as_index=False).agg({
            'Loans': 'sum',
            'Debtors': 'sum'
        })
        grouped_data['average_loan_per_debtor'] = grouped_data['Loans'] / \
            grouped_data['Debtors']
        grouped_data = grouped_data[(grouped_data['Debtors'] <= x_max) & (
            grouped_data['average_loan_per_debtor'] <= y_max)]

        scatter_plot = alt.Chart(grouped_data).mark_circle(size=60).encode(
            x=alt.X('Debtors:Q', title="Number of Debtors",
                    scale=alt.Scale(zero=False, domain=[0, x_max])),
            y=alt.Y('average_loan_per_debtor:Q', title="Average Loan per Debtor (in millions)",
                    scale=alt.Scale(zero=False, domain=[0, y_max])),
            color=alt.Color('industry_cat:N', title="Industry Category"),
            tooltip=[
                alt.Tooltip('industry_cat:N', title="Industry"),
                alt.Tooltip(
                    'Debtors:Q', title="Number of Debtors", format=','),
                alt.Tooltip('average_loan_per_debtor:Q',
                            title="Average Loan per Debtor", format=',.2f')
            ]
        ).properties(
            width=250,
            height=250
        )

        return scatter_plot

    @output
    @render_widget
    def loans_by_industry_pie():
        data = filtered_an3()

        loans_by_industry = data.groupby(
            'industry_cat', as_index=False)['Loans'].sum()
        loans_by_industry = loans_by_industry.sort_values(
            by='Loans', ascending=False)

        pie_chart = alt.Chart(loans_by_industry).mark_arc().encode(
            theta=alt.Theta(field="Loans", type="quantitative",
                            title="Total Loans"),
            color=alt.Color(field="industry_cat", type="nominal",
                            title="Industry Category"),
            tooltip=[
                alt.Tooltip('industry_cat:N', title="Industry"),
                alt.Tooltip('Loans:Q', title="Total Loans", format=",")
            ]
        ).properties(
            width=250,
            height=300
        )

        return pie_chart


# Run the app
app = App(app_ui, server)
