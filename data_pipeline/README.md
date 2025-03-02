# data_pipeline

Contains records of the official GNB data at each stage of data processing,
along with the scripts used at each step. The stages of the data pipeline are
as follows:

1. [**data_raw**](data_raw): The raw data, provided directly by the Government
   of New Brunswick.
2. [**data_xlsx**](data_xlsx): The data in `.xlsx` format, converted by
   [raw_to_xlsx.py](raw_to_xlsx.py).
3. [**data_clean**](data_clean): The cleaned data, processed by
   [xlsx_to_clean.py](xlsx_to_clean.py) (and additional helper scripts in
   [helper_scripts/xlsx_to_clean](helper_scripts/xlsx_to_clean)).
4. [**data_final**](data_final): The final data used for analysis, produced by
   [clean_to_final.py](clean_to_final.py) (and additional helper scripts in
   [helper_scripts/clean_to_final](helper_scripts/clean_to_final)).
5. [**data_summary**](data_summary): [Add description later]
6. [**data_analysis**](data_analysis): [Add description later]
