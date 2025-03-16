# %%
import os

import matplotlib.pyplot as plt
import polars as pl
import polars.selectors as cs
import seaborn as sns

from statsmodels.iolib.summary2 import Summary
from statsmodels.regression.linear_model import OLS, RegressionResultsWrapper


# %%
df = pl.read_excel('data_pipeline/data_final/data_final.xlsx')
df_new = (df.rename({"Average Tax Rate (CMP)": "Tax Rate",
                     "Latest Census Pop. (CMP)": "Population",
                     "Tax Base for Rate/Capita (TAX)": "TBC"}))


# %%
coef = 0.4249

df_comp = (df_new.group_by("Municipality")
           .agg(coef * pl.col("TBC").mean() / 1e5, pl.col("Population").mean())
           .rename({"literal": "product"})
           .with_columns((1 / pl.col("product") - 1).alias("elasticity"))
           .sort("elasticity"))
df_comp.write_excel('data_analysis/elasticity/elasticity.xlsx')