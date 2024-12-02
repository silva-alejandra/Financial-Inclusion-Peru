# Financial Inclusion Analysis in Peru

## Overview

This project aims to analyze the state of financial inclusion in Peru, focusing on the challenges and opportunities within a centralized financial system. Economic activities in Peru are largely concentrated in Lima, creating disparities in financial access for other regions. This project examines how loans and deposits have evolved over time, with particular attention to the impact of COVID-19 on financial activity, and explores the geographical and industry-specific distribution of financial services. The objective is to provide insights into expanding financial inclusion, especially for small and medium enterprises (SMEs), in order to drive economic growth and reduce regional inequalities.

## Objectives

1. **Financial Inclusion Evolution**: To examine how financial inclusion has evolved over the years, specifically evaluating the impact of the COVID-19 pandemic.
2. **Geographical and Sectoral Analysis**: To analyze the evolution of financial inclusion across regions in Peru and by economic sectors, highlighting areas with opportunities for improved access to credit.
3. **Policy Implications**: To provide recommendations for improving financial inclusion and enhancing economic resilience, particularly outside Lima.

## Data Sources

- **AN3 and AN10v3**: Data related to loans and deposits from Peru's Financial Stability Authority.
- **ENTIDAD and UBIGEO**: Dimensional tables categorizing financial institutions and providing geographical context.
- **GeoJSON Files**: Spatial data used for mapping the regional distribution of loans and deposits in Peru.


## Methodology

1. **Data Processing**: Datasets were loaded, cleaned, and merged to create a cohesive dataset for analysis. Fields like dates were standardized, and key variables were translated into English for better understanding.
2. **Data Analysis**: Data was analyzed using Python and Altair, with Shiny dashboards used for visualization. The analysis focused on identifying trends in loan and deposit growth, geographical concentration, and changes during the COVID-19 pandemic.
3. **Visualization**: The results were visualized through dynamic dashboards, highlighting key metrics such as loan distribution by region and industry.

## Results

- **Growth Before Pandemic**: Prior to the pandemic, total loans were increasing steadily, driven by growing access to credit for SMEs and expanding economic activities. Growth rates were higher compared to more mature financial systems, which is typical for developing economies like Peru.
- **COVID-19 Impact**: The pandemic led to a significant contraction in loans, with a decline of over 40%. This contraction reflected the economic downturn and increased risk aversion among financial institutions. Government interventions, like the "Reactiva Peru" program, provided liquidity to businesses and led to a rebound in loans by 2021.
- **Geographical Disparities**: The analysis highlighted a high concentration of loans and deposits in Lima, with other regions lagging in financial inclusion. The Shiny dashboard created for this project allows users to visualize the evolution of loans and deposits by region and industry.

## Dashboard

This project includes an interactive Shiny dashboard to help visualize financial inclusion across different regions and industries in Peru. The dashboard has two main pages:

1. **By Region**: Users can explore loans and deposits by region using a time slider. The dashboard includes maps to show the geographical distribution of financial activities and metrics that provide an overview of financial inclusion at the regional level.

2. **By Industry**: Users can filter data by industry and view metrics such as total loans, number of debtors, and the average loan per debtor. Visualizations include pie charts and scatter plots to help understand industry-specific trends.

## Limitations

- **Data Limitations**: The analysis relies on available data from financial institutions and does not capture informal lending or microfinance activities, which could be significant in Peru.
- **Temporal Constraints**: The analysis focuses on data from 2012 onwards. A more extensive historical dataset could provide deeper insights into long-term trends.
- **Regional Disparities**: The analysis highlights regional disparities but does not delve into the structural factors contributing to these differences, which may require more comprehensive socioeconomic data.

## Future Steps

1. **Incorporate Additional Metrics**: Future work could include metrics such as credit-to-GDP ratios to provide better context for comparing financial inclusion across regions and industries.
2. **Longitudinal Analysis**: Conducting a longitudinal study to assess the impact of policies over a longer time frame could provide insights into the effectiveness of financial interventions.
3. **Policy Recommendations**: Develop targeted recommendations to enhance credit access for SMEs and improve financial inclusion in underserved areas.

## Requirements

- **Python 3.12**
- **Packages**: `pandas`, `altair`, `geopandas`, `shiny`
- **Data Files**: Place all required data files (`exportAN3`, `exportAN10v3`, `exportENTIDAD`, `exportUBIGEO`, GeoJSON) in the `Data/raw` directories.

## Installation and Usage

1. **Clone the Repository**: 
   ```bash
   git clone <repository_url>
   cd Financial-Inclusion-Peru
   ```
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the Shiny Dashboard**:
   ```bash
   shiny run Shiny-app/app.py
   ```

## Authors

- Alejandra Silva

## Acknowledgments

- **University of Chicago Harris School of Public Policy** for their support and resources.
- **Peru's Financial Stability Authority and Central Bank of Peru** for providing data used in this analysis.


