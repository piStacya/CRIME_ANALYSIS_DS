# CRIME_ANALYSIS_DS
### Anastassia Käärmann, Helena Angela Kiisler, Kirke Kisand
## Overview
This project explores crime trends across European countries using publicly available data from Eurostat and provides a reproducible exploratory analysis of crime patterns across Europe.

The objective was to apply core data science skills: data cleaning, preprocessing, exploratory analysis, visualization, and interpretation, to produce meaningful insights about crime patterns from mainly 2008–2023, but also using historic data from 1993-2007.

The project uses crime categories defined by the ICCS (International Classification of Crime Statistics) framework, allowing consistent comparison across countries and years.

The analysis also identifies:
- Crime trends over the years for each ICCS category  
- Countries with the highest rates for each crime type  
- Top crime categories for each country

This project is purely descriptive and does not make causal claims.

## Project goals
- Collect and clean multiple Eurostat crime datasets  
- Standardize crime categories using ICCS codes  
- Handle missing values and reporting inconsistencies  
- Perform exploratory data analysis to find:  
  - long-term crime trends  
  - peaks, declines, and anomalies  
  - country-specific crime patterns  
- Present insights visually through clear, interpretable plots  

## Tools and technologies used
- **Python**
- **Pandas** — data manipulation  
- **NumPy** — numerical operations  
- **Matplotlib** — plotting  
- **Seaborn** — visualization support  
- **Jupyter Notebook** — analysis environment 

## Contents
We have conveniently divided our project into multiple directories to make it easier to find the data that we used, the scripts that we wrote to clean the data, the notebooks that we wrote the analysis on different subjects and the assets we both used and created.

- **assets** — This folder contains the images and gif animations that we created and also geographical data we used to plot the maps.
- **data** — This folder contains all of the data that we used. It is divided into subfolders.
  - cleanedDatasets — contains cleaned datasets, changes include: 
    - changing unknown characters to NaN
    - correcting the column names
    - removing rows with too many missing values 
    - replacing both country and region tags with their corresponding names
    - dividing the dataset into subsets for each ICCS category
  - cleanedDatasetsCountryNames — contains cleaned datasets with country names
  - originalDatasets — the original datasets used for cleaning
  - Additional datasets for comparing and having a deeper understanding of the analysis
- **Notebooks** — This folder contains the Jupyter notebooks that we used to perform our analysis.
  - Aastad_ja_kuritööd — Analysing different crime categories over time in Europe. Findind peaks, declines, and anomalies.
  - Riigid_ja_kuritöö_kategooriad — Analysing crime trends for each country. Comparing crime categories over time.
  - Riigid_regioonid_ja_ajalugu — Analysing crime trends in European regions and countries. Comparing different crime categories with historic trends.
- **Scripts** — This folder contains the Python scripts that we used to clean the data.

## Replicating the analysis
To replicate the analysis, follow the steps below:
1. Clone the repository to your local machine.
2. We have already cleaned the data and provided it in the repository. If you want to clean the data yourself, follow the instructions in the scripts folder.
3. Open the desired Jupyter Notebook with the analysis that you want to replicate.
4. Some of the notebooks are divided into sections, each section contains a description of the analysis and the code that was used to perform it.
5. Run the code in the notebook to reproduce the analysis.
6. If anything displays incorrectly or varies widely from the original, please let us know by opening an issue.

## Credits
©EuroGeographics for the administrative boundaries

[Eurostat crime and criminal justice datasets](https://ec.europa.eu/eurostat/web/crime/database)
