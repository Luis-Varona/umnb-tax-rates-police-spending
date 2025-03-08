# %%
import os

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
               "POP"]
    
    df_orig = pl.read_excel(source).drop(cs.matches(r"^Provider_*"))
    return (df_orig.rename(dict(zip(df_orig.columns, columns)))
            .drop(cs.by_name("NEC", "NRC"))
            .with_columns(pl.col("ATR").log().alias("log_ATR"))
            .with_columns(~cs.by_name(columns[:3]) / 1000))


# %%
def demean_data(df: pl.DataFrame) -> pl.DataFrame:
    df_demeaned = df.clone()
    transform_vars = [var for var in df.columns
                      if var not in {"year", "municipality"}]
    
    for var in transform_vars:
        df_demeaned = (df_demeaned.with_columns(pl.col(var)
                                                - pl.col(var).mean()
                                                .over("municipality")))
    
    return df_demeaned


# %%
def write_model_summary(summary: Summary, dest: str) -> None:
    if os.path.exists(dest):
        os.remove(dest)
    
    with open(dest, 'x') as file:
        file.write(summary.as_text())


# %%
os.chdir('data_analysis')
source = os.path.join('..', 'data_pipeline', 'data_final', 'data_final.xlsx')
dest_dir = 'fe_results'
os.makedirs(dest_dir, exist_ok=True)


# %%
df_orig = read_data(source)
df_demeaned = demean_data(df_orig)
indep_vars = [var for var in df_demeaned.columns
              if var not in {"year", "municipality", "ATR", "log_ATR"}]


# %%
formula = f"ATR ~ {' + '.join(indep_vars)} -1"
formula_log = f"log_ATR ~ {' + '.join(indep_vars)} -1"


# %%
model = OLS.from_formula(formula, df_demeaned)
model_log = OLS.from_formula(formula_log, df_demeaned)

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