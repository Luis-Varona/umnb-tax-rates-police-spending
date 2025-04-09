# umnb-tax-rates-police-spending

[![PEP8](https://img.shields.io/badge/code%20style-pep8-orange.svg)](https://www.python.org/dev/peps/pep-0008/)

A fixed-effects two-stage least squares regression analysis of municipal tax
rates on police spending, conducted for the Union of Municipalities of New
Brunswick (UMNB). Annual Government of New Brunswick (GNB) data from
2000&#x2013;2004 and 2006&#x2013;2018 on budget expenditures & revenue,
comparative demographics, and tax bases is integrated into the model. (2024
policing provider data is mapped backwards to municipal jurisdictions from
previous years.) The instrument variable used in the 2SLS regression is
obtained from occassional Statistics Canada census data on median household
income and interpolated to the years of interest.

The final data used for analysis is in the
[data_pipeline/data_final/data_final.xlsx](data_pipeline/data_final/data_final.xlsx)
workbook. Further details regarding the data pipeline process can be found at
[data_pipeline/README.md](data_pipeline/README.md), and a data summary can be
found at [data_summary/data_summary.pdf](data_summary/data_summary.pdf). The
official data report is at
[data_report/data_report.pdf](data_report/data_report.pdf).

(The final report in collaboration with the UMNB yet to be completed.)
