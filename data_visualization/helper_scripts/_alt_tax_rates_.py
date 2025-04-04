# %%
import os
import sys
import pickle

import pandas as pd
import polars as pl
import seaborn as sns

sys.path.append(os.path.join((WD := os.path.dirname(__file__)), '..', '..'))
from utils import config_and_save_plot


# %%
SOURCE_DIR = os.path.join(WD, '..', '..', 'data_analysis', 'fe_2sls')


# %%
DEP_VAR = "AvgTaxRate"
INDEP_VAR = "PolExpCapita"
CONTROL_VARS = ["OtherExpCapita", "OtherRevCapita", "TaxBaseCapita"]
INTER_VARS = {
    f"{INDEP_VAR}:Provider_MPSA":
        pl.col(INDEP_VAR) * pl.col("Provider_MPSA"),
    f"{INDEP_VAR}:Provider_Muni":
        pl.col(INDEP_VAR) * pl.col("Provider_Muni"),
}

COLUMNS = ["Year", "Municipality",
           "AvgTaxRate",
           "PolExpCapita", "OtherExpCapita",
           "OtherRevCapita", "TaxBaseCapita",
           "Provider_MPSA", "Provider_Muni"]
GROUP_COL = "Municipality"
TIME_COL = "Year"
DEMEAN_COLS = COLUMNS[3:-2]

PRED1_COL = f"{DEP_VAR}_wPolExp"
PRED2_COL = f"{DEP_VAR}_woPolExp"
YEARS = list(range(2000, 2019, 2))


# %%
SCALE1 = 100
SCALE2 = 1e5

COLS_SCALE1 = ["AvgTaxRate"]
COLS_SCALE2 = ["PolExpCapita", "OtherExpCapita",
               "OtherRevCapita", "TaxBaseCapita"]


# %%
CATS = {
    DEP_VAR: ('solid', "Observed Mean Rate"),
    PRED1_COL: ('dashed', "Predicted (using actual police spending data)"),
    PRED2_COL: ('dashed', "Predicted (using spending levels from 2000)"),
}

TITLE = "NB Tax Rate Progression, Holding Police Spending Constant"
TITLESIZE = 14
YLABEL = "Mean of Municipal Average Tax Rates  (%)"


# %%
def main():
    source_2sls = os.path.join(SOURCE_DIR, 'data_2sls.xlsx')
    source_result = os.path.join(SOURCE_DIR, 'stage2_results.pkl')
    dest = os.path.join(WD, '..', 'alt_tax_rates.png')
    
    result = pickle.load(open(source_result, 'rb'))
    params = result.params * SCALE1 / SCALE2
    df = pred_rates(source_2sls, params)
    
    plot_rates(df, dest)


# %%
def pred_rates(source_2sls: str, params: pd.Series) -> pl.DataFrame:
    df = (pl.read_excel(source_2sls, columns=COLUMNS)
          .with_columns(pl.col(COLS_SCALE1) * SCALE1,
                        pl.col(COLS_SCALE2) * SCALE2)
          .with_columns((pl.col(INDEP_VAR).mean().over(pl.col(GROUP_COL))
                           - pl.col(INDEP_VAR).first().over(pl.col(GROUP_COL)))
                          .alias("Change"))
          .with_columns(pl.col(DEMEAN_COLS) - pl.col(DEMEAN_COLS)
                        .mean()
                        .over(pl.col(GROUP_COL)),
                        pl.col(DEP_VAR)
                        .mean()
                        .over(pl.col(GROUP_COL))
                        .alias(PRED2_COL))
          .with_columns((pl.col(PRED2_COL) + params[INDEP_VAR]
                         * pl.col(INDEP_VAR))
                        .alias(PRED1_COL))
          .with_columns(pl.col(PRED2_COL) - params[INDEP_VAR]
                        * pl.col("Change")))
    
    for col in CONTROL_VARS:
        df = df.with_columns(pl.col(PRED1_COL) + params[col] * pl.col(col),
                             pl.col(PRED2_COL) + params[col] * pl.col(col))
    
    for k, v in INTER_VARS.items():
        df = df.with_columns(pl.col(PRED1_COL) + params[k] * v,
                             pl.col(PRED2_COL) + params[k] * v)
    
    return (df.group_by(TIME_COL)
            .agg(pl.col(DEP_VAR, PRED1_COL, PRED2_COL)
                 .mean())
            .sort(TIME_COL))


# %%
def plot_rates(df: pl.DataFrame, dest: str) -> None:
    with config_and_save_plot(dest):
        plot = sns.scatterplot(df,
                               x=TIME_COL, y=DEP_VAR,
                               alpha=0.8, s=25)
        plot.set_title(TITLE, fontsize=TITLESIZE)
        plot.set(ylabel=YLABEL, xticks=YEARS)
        
        for y, (ls, label) in CATS.items():
            sns.lineplot(df,
                         x=TIME_COL, y=y,
                         ls=ls, label=label)


# %%
if __name__ == '__main__':
    main()