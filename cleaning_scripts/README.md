# cleaning_scripts

Contains Python scripts used in the data cleaning process. Each script prefaced
with an underscore (`_`) is a helper script to be called by the main
executable, `cleaning_scripts/clean_all_data.py`. Unprocessed data is taken
from the `data_xlsx` directory, and output files are saved in `data_clean`.
