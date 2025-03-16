# %%
import os
import re

import matplotlib.pyplot as plt
import polars as pl
import polars.selectors as cs
import seaborn as sns

from statsmodels.iolib.summary2 import Summary
from statsmodels.regression.linear_model import OLS, RegressionResultsWrapper


# %%
def read_data(source: str) -> pl.DataFrame:
    columns = ["year", "municipality",
               "ATR", "PSC", "TBC",
               "GGS", "FPS", "WCT", "EMS", "OPS",
               "TRS", "EHS", "PHS", "EDS",
               "RCS", "DBC", "TRN", "DFC",
               "NEC",
               "UGR", "OGS", "SOS", "OSR", "CTR",
               "OTR", "BIS",
               "NRC",
               "POP",
               "MPSA", "MUNI"]
    
    df_orig = pl.read_excel(source)
    return (df_orig.rename(dict(zip(df_orig.columns, columns)))
            .drop(pl.col("TBC"), pl.col("NEC"), pl.col("NRC"), pl.col("POP"))
            .with_columns(pl.col("ATR") / 100)
            .with_columns(~cs.by_name(columns[:3] + columns[-2:]) / 1e5)
            .with_columns(pl.col("ATR").log().alias("log_ATR")))

# %%
def demean_data(df: pl.DataFrame) -> pl.DataFrame:
    df_demean = df.clone()
    transform_vars = [var for var in df.columns
                      if var not in {"year", "municipality", "MPSA", "MUNI"}]
    
    for var in transform_vars:
        df_demean = (df_demean.with_columns(pl.col(var) - pl.col(var).mean()
                                            .over("municipality")))
    
    return df_demean


# %%
def write_model_summary(summary: Summary, dest: str) -> None:
    if os.path.exists(dest):
        os.remove(dest)
    
    with open(dest, 'x') as file:
        file.write(summary.as_text())


# %%
os.chdir('data_analysis')
source = os.path.join('..', 'data_pipeline', 'data_final', 'data_final.xlsx')
dest_dir = 'fe_results2'
os.makedirs(dest_dir, exist_ok=True)


# %%
df_orig = read_data(source)
df_demean = demean_data(df_orig)
indep_vars = [var for var in df_demean.columns
              if var not in {"year", "municipality", "ATR", "log_ATR"}]
indep_vars = [re.sub(r"^(MPSA|MUNI)$", r"PSC:\1", var)
              for var in indep_vars]


# %%
formula = f"ATR ~ {' + '.join(indep_vars)} -1"
formula_log = f"log_ATR ~ {' + '.join(indep_vars)} -1"


# %%
model = OLS.from_formula(formula, df_demean)
model_log = OLS.from_formula(formula_log, df_demean)

results = model.fit(reml=True)
results_log = model_log.fit(reml=True)

summary = results.summary()
summary_log = results_log.summary()


# %%
dest = os.path.join(dest_dir, 'model_summary.txt')
dest_log = os.path.join(dest_dir, 'model_summary_log.txt')
write_model_summary(summary, dest)
write_model_summary(summary_log, dest_log)


# %%
os.chdir('..')