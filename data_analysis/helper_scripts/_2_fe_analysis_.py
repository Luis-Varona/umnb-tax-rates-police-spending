# %%
import os

import polars as pl

from linearmodels.compat.statsmodels import Summary
from linearmodels.panel.model import PanelOLS
from linearmodels.panel.results import PanelResults


# %%
WD = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(WD, '..', '..', 'data_pipeline', 'data_final')
DEST_DIR = os.path.join(WD, '..', 'fe_results')


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
    source = os.path.join(SOURCE_DIR, 'data_final.xlsx')
    dest = os.path.join(DEST_DIR, 'model_summary.txt')
    os.makedirs(DEST_DIR, exist_ok=True)
    
    df = pl.read_excel(source)
    model, result = fit_model(df)
    
    write_model_summary(result.summary, dest)


# %%
def fit_model(df: pl.DataFrame) -> tuple[PanelOLS, PanelResults]:
    df_pandas = df.to_pandas()
    df_pandas.set_index([GROUP_COL, TIME_COL], inplace=True)
    
    model = PanelOLS.from_formula(FORMULA, df_pandas)
    result = model.fit(cov_type='clustered', cluster_entity=True)
    
    return model, result

def write_model_summary(summary: Summary, dest: str) -> None:
    if os.path.exists(dest):
        os.remove(dest)
    
    with open(dest, 'x') as file:
        file.write(summary.as_text())


# %%
if __name__ == "__main__":
    main()