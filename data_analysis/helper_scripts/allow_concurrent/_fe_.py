# %%
import os
import sys

import polars as pl
from linearmodels.panel.model import PanelOLS

sys.path.append(os.path.join((WD := os.path.dirname(__file__)),
                             '..', '..', '..'))
from utils import LMResultsWrapper


# %%
WD = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(WD, '..', '..', '..', 'data_pipeline', 'data_final')
DEST_DIR = os.path.join(WD, '..', '..', 'fe')


# %%
DEP_VAR = "AvgTaxRate"
INDEP_VARS = ["PolExpCapita",
              "OtherExpCapita",
              "OtherRevCapita",
              "PolExpCapita:Provider_MPSA",
              "PolExpCapita:Provider_Muni",
              "TaxBaseCapita"]
FORMULA = f"{DEP_VAR} ~ {' + '.join(INDEP_VARS)} + EntityEffects"


# %%
GROUP_COL = "Municipality"
TIME_COL = "Year"


# %%
def main():
    os.makedirs(DEST_DIR, exist_ok=True)
    source = os.path.join(SOURCE_DIR, 'data_final.xlsx')
    dest_results = os.path.join(DEST_DIR, 'results.pkl')
    dest_summary = os.path.join(DEST_DIR, 'summary')
    
    df = pl.read_excel(source)
    fit_model(df).save_all_data(dest_results,
                                f"{dest_summary}.txt",
                                f"{dest_summary}.tex")


# %%
def fit_model(df: pl.DataFrame) -> LMResultsWrapper:
    df_pandas = df.to_pandas()
    df_pandas.set_index([GROUP_COL, TIME_COL], inplace=True)
    
    model = PanelOLS.from_formula(FORMULA, df_pandas)
    results = model.fit(cov_type='clustered', cluster_entity=True)
    return LMResultsWrapper(results)


# %%
if __name__ == '__main__':
    main()
