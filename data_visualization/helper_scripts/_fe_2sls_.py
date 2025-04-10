# %%
import os
import sys
import pickle

import numpy as np
import pandas as pd
import polars as pl
import polars.selectors as cs
import seaborn as sns

sys.path.append(os.path.join((WD := os.path.dirname(__file__)), '..', '..'))
from utils import config_and_save_plot


# %%
SOURCE_DIR = os.path.join(WD, '..', '..', 'data_analysis', 'fe_2sls')


# %%
COLUMNS = ["Year", "Municipality",
           "AvgTaxRate",
           "PolExpCapita", "OtherExpCapita",
           "OtherRevCapita", "TaxBaseCapita",
           "Provider_MPSA", "Provider_Muni"]
GROUP_COL = "Municipality"

INDICS_ALL = ["Provider_PPSA", "Provider_MPSA", "Provider_Muni"]
INDIC_EX = INDICS_ALL[0]
INDICS_IN = INDICS_ALL[1:]
INDIC_MAP = {"Muni": "Municipal"}


# %%
SCALE1 = 100
SCALE2 = 1e5

COLS_SCALE1 = ["AvgTaxRate"]
COLS_SCALE2 = ["PolExpCapita", "OtherExpCapita",
               "OtherRevCapita", "TaxBaseCapita"]


# %%
DEP_VAR = "AvgTaxRate"
INDEP_VAR = "PolExpCapita"
HUE_VAR = "Provider"
CONTROL_VARS = ["OtherExpCapita", "OtherRevCapita", "TaxBaseCapita"]


# %%
NUM_STEPS = 1000

TITLE = "FE-2SLS Regression of NB Municipal Tax Rates on Police Spending"
TITLESIZE = 14
XLABEL = f"${INDEP_VAR}_{{it}} - \overline{{{INDEP_VAR}}}_i$  (CAD/person)"
YLABEL = f"${DEP_VAR}_{{it}} - \overline{{{DEP_VAR}}}_i$  (%)\n" \
    "$\it{(adjusted~for~control~variables)}$"


# %%
def main():
    source_fe_2sls = os.path.join(SOURCE_DIR, 'data_fe_2sls.xlsx')
    source_result = os.path.join(SOURCE_DIR, 'stage2_results.pkl')
    dest = os.path.join(WD, '..', 'fe_2sls.png')
    
    params, params_indic = read_and_process_result(source_result)
    df = read_and_adjust_2sls_data(source_fe_2sls, params)
    x, ys = generate_lobfs(df, params_indic)
    save_regress_plot(df, x, ys, dest)


# %%
def get_indic(token: str) -> str:
    indic = token.rsplit('_')[-1]
    return next((v for k, v in INDIC_MAP.items() if indic == k), indic)


# %%
def read_and_process_result(source_result: str) -> tuple[pd.Series, pd.Series]:
    result = pickle.load(open(source_result, 'rb'))
    params = result.params * SCALE1 / SCALE2
    
    params_indic = params[:0]
    new_key = get_indic(INDIC_EX)
    params_indic[new_key] = params[INDEP_VAR]
    
    for col in INDICS_IN:
        key = f"{INDEP_VAR}:{col}"
        new_key = get_indic(col)
        params_indic[new_key] = params[INDEP_VAR] + params[key]
    
    return params, params_indic


# %%
def read_and_adjust_2sls_data(source_fe_2sls: str,
                              params: pd.Series) -> pl.DataFrame:
    df = (pl.read_excel(source_fe_2sls, columns=COLUMNS)
          .with_columns(pl.col(COLS_SCALE1) * SCALE1,
                        pl.col(COLS_SCALE2) * SCALE2)
          .with_columns(cs.by_dtype(pl.Float64) - cs.by_dtype(pl.Float64)
                        .mean()
                        .over(pl.col(GROUP_COL)),
                        (pl.lit(1) - pl.sum_horizontal(INDICS_IN))
                        .alias(INDIC_EX))
          .with_columns((pl.col(col) * pl.col(INDEP_VAR))
                        .alias(f"{INDEP_VAR}:{col}")
                        for col in INDICS_IN)
          .with_columns(pl.when(pl.col(col) == 1)
                        .then(pl.lit(col).str.extract(r'([^_]+$)'))
                        .alias(col)
                        for col in INDICS_ALL)
          .with_columns(pl.coalesce(pl.col(f'^{prefix}_.+$'))
                        .str.replace(k, v)
                        .alias(prefix)
                        for k, v in INDIC_MAP.items()
                        for prefix in
                        dict.fromkeys(col.rsplit('_', maxsplit=1)[0]
                                      for col in INDICS_ALL))
          .drop(INDICS_ALL))
    
    for var in CONTROL_VARS:
        df = df.with_columns(pl.col(DEP_VAR) - pl.col(var) * params[var])
    
    return df


# %%
def generate_lobfs(df: pl.DataFrame,
                   params_indic: pd.Series) -> tuple[np.ndarray, list]:
    start = df.select(INDEP_VAR).min().item()
    stop = df.select(INDEP_VAR).max().item()
    
    x = np.linspace(start, stop, NUM_STEPS)
    ys = [param * x for param in params_indic]
    return x, ys


# %%
def save_regress_plot(df: pl.DataFrame,
                      x: np.ndarray, ys: list,
                      dest: str) -> None:
    hue_order = [get_indic(col) for col in INDICS_ALL]
    
    with config_and_save_plot(dest):
        plot = sns.scatterplot(df,
                               x=INDEP_VAR, y=DEP_VAR,
                               hue=HUE_VAR, hue_order=hue_order,
                               alpha=0.8, s=25)
        plot.set_title(TITLE, fontsize=TITLESIZE)
        plot.set(xlabel=XLABEL, ylabel=YLABEL)
        
        for y in ys:
            sns.lineplot(x=x, y=y, lw=2, legend=False)


# %%
if __name__ == '__main__':
    main()
