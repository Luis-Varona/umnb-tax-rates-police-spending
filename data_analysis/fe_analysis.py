# %%
import os

import polars as pl

from linearmodels.compat.statsmodels import Summary
from linearmodels.panel.model import PanelOLS
from linearmodels.panel.results import PanelResults


# %%
SOURCE_DIR = os.path.join('..', 'data_pipeline', 'data_final')
DEST_DIR = 'fe_results'


# %%
DEP_VAR = "AvgTaxRate"
INDEP_VARS = ["PolExpCapita",
              "OtherExpCapita",
              "OtherRevCapita",
              "PolExpCapita:Provider_MPSA",
              "PolExpCapita:Provider_Muni",
              "TaxBaseCapita"]
LOG_VARS = ["AvgTaxRate", "TaxBaseCapita"]


# %%
GROUP_COL = "Municipality"
TIME_COL = "Year"

FORMULA = f"{DEP_VAR} ~ {' + '.join(INDEP_VARS)} + EntityEffects"
FORMULA_LOG = FORMULA

for var in LOG_VARS:
    FORMULA_LOG = FORMULA_LOG.replace(var, f"log_{var}")


# %%
def main():
    source = os.path.join(SOURCE_DIR, 'data_final.xlsx')
    dest = os.path.join(DEST_DIR, 'model_summary.txt')
    dest_log = os.path.join(DEST_DIR, 'model_summary_log.txt')
    os.makedirs(DEST_DIR, exist_ok=True)
    
    df = pl.read_excel(source)
    model, result = fit_model(df)
    model_log, result_log = fit_model(df, left_log=True)
    
    write_model_summary(result.summary, dest)
    write_model_summary(result_log.summary, dest_log)


# %%
def fit_model(
    df: pl.DataFrame, *, left_log: bool = False
) -> tuple[PanelOLS, PanelResults]:
    df_pandas = df.to_pandas()
    df_pandas.set_index([GROUP_COL, TIME_COL], inplace=True)
    
    formula = FORMULA_LOG if left_log else FORMULA
    model = PanelOLS.from_formula(formula, df_pandas)
    result = model.fit(cov_type='clustered', cluster_entity=True)
    
    return model, result

def write_model_summary(summary: Summary, dest: str) -> None:
    if os.path.exists(dest):
        os.remove(dest)
    
    with open(dest, 'x') as file:
        file.write(summary.as_text())


# %%
if __name__ == "__main__":
    wd = os.getcwd()
    os.chdir(os.path.dirname(__file__))
    
    try:
        main()
    finally:
        os.chdir(wd)