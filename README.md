# umnb-tax-rates-police-spending

[![Build Status](https://github.com/Luis-Varona/umnb-tax-rates-police-spending/actions/workflows/pylint.yml/badge.svg?branch=main)](https://github.com/Luis-Varona/umnb-tax-rates-police-spending/actions/workflows/pylint.yml?query=branch%3Amain)
[![PEP8](https://img.shields.io/badge/code%20style-pep8-orange.svg)](https://www.python.org/dev/peps/pep-0008/)

A correlated random-effects regression analysis of the impact of municipal
police spending on tax rates, conducted for the Union of Municipalities of New
Brunswick (UMNB). Annual Government of New Brunswick (GNB) data from
2000&#x2013;2004 and 2006&#x2013;2018 on budget expenditures & revenue,
comparative demographics, and tax bases is integrated into the model. (2024
policing provider data is mapped backwards to municipal jurisdictions from
previous years.)

The final data used for analysis is in the
[data_final.xlsx](data_pipeline/data_final/data_final.xlsx)
workbook, produced by the
[clean_to_final.py](data_pipeline/clean_to_final.py) script. Further
details regarding the data pipeline process can be found at
[data_pipeline/README.md](data_pipeline/README.md), and a data summary can be
found at [data_summary/data_summary.md](data_summary/data_summary.md).

(The final data analysis is yet to be completed.)
