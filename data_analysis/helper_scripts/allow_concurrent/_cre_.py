# TODO: Add instrumentation, F-tests

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
DEST_DIR = os.path.join(WD, '..', '..', 'cre')


# %%
DEP_VAR = "AvgTaxRate"
INTER_VAR = "PolExpCapita"
NON_INTER_VARS = ["OtherExpCapita", "OtherRevCapita", "TaxBaseCapita"]
INDIC_VARS = ["Provider_MPSA", "Provider_Muni"]
INDEP_VARS = [INTER_VAR] + NON_INTER_VARS

INTER_TERMS = [f"{INTER_VAR}*{var}" for var in INDIC_VARS]
INTER_TERM_MEANS = [f"{INTER_VAR}_mean*{var}" for var in INDIC_VARS]
NON_INTER_VAR_MEANS = [f"{var}_mean" for var in NON_INTER_VARS]

FORMULA = f"{DEP_VAR} ~ {' + '.join
    (INTER_TERMS + NON_INTER_VARS + INTER_TERM_MEANS + NON_INTER_VAR_MEANS)}"


# %%
GROUP_COL = "Municipality"
TIME_COL = "Year"


# %%
def main():
    os.makedirs(DEST_DIR, exist_ok=True)
    source = os.path.join(SOURCE_DIR, 'data_final.xlsx')
    dest_results = os.path.join(DEST_DIR, 'results.pkl')
    dest_summary = os.path.join(DEST_DIR, 'summary')
    
    df = add_mundlak_means(pl.read_excel(source))
    fit_model(df).save_all_data(dest_results,
                                f"{dest_summary}.txt",
                                f"{dest_summary}.tex")


# %%
def add_mundlak_means(df: pl.DataFrame) -> pl.DataFrame:
    for var in [DEP_VAR] + INDEP_VARS:
        df = df.with_columns(pl.col(var)
                             .mean()
                             .over(GROUP_COL)
                             .alias(f"{var}_mean"))
    
    return df


# %%
def fit_model(df: pl.DataFrame) -> LMResultsWrapper:
    df_pandas = df.to_pandas()
    df_pandas.set_index([GROUP_COL, TIME_COL], inplace=True)
    
    model = PanelOLS.from_formula(FORMULA, df_pandas)
    result = model.fit(cov_type='clustered', cluster_entity=True)
    return LMResultsWrapper(result)


# %%
if __name__ == '__main__':
    main()
