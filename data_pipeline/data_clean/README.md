# data_pipeline/data_clean

Contains cleaned GNB data on budget expenditures, budget revenues, comparative
demographics, and tax bases from 2000&#x2013;2004 and 2006&#x2013;2018, as well
as policing provider data from 2024. Results from 2005 and 2019&#x2013;2022 is
excluded due to missing/improperly entered data. (We may work with the GNB and
the UMNB to correct this in the future.)

Prior to usage in the data analysis stage, files are first combined and
filtered in the [data_final](../data_final) directory (see
[clean_to_final.py](../clean_to_final.py)).
