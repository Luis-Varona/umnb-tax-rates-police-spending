# data_pipeline

Contains records of the official GNB data at each stage of data processing,
along with the scripts used at each step. The stages of the data pipeline are
as follows:

1. [**data_raw**](data_raw): The raw data, provided directly by the Government
   of New Brunswick.
2. [**data_xlsx**](data_xlsx): The data in `.xlsx` format, converted by
   [_raw_to_xlsx_.py](helper_scripts/_raw_to_xlsx_.py).
3. [**data_clean**](data_clean): The cleaned data, processed by
   [_xlsx_to_clean_.py](helper_scripts/_xlsx_to_clean_.py).
4. [**data_final**](data_final): The final data used for analysis, produced by
   [_clean_to_final_.py](helper_scripts/_clean_to_final_.py).

The entire data pipeline is run by the main executable, [main.py](main.py).
