# %%
import os
import pickle

import matplotlib.pyplot as plt
import numpy as np
import polars as pl
import polars.selectors as cs
import seaborn as sns


# %%
os.chdir(os.path.dirname(__file__))
SOURCE_DIR = os.path.join('..', 'data_analysis', 'fe_2sls_results')


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
def get_indic(token: str) -> str:
      indic = token.rsplit('_')[-1]
      return next((v for k, v in INDIC_MAP.items() if indic == k), indic)


# %%
source_2sls = os.path.join(SOURCE_DIR, 'data_2sls.xlsx')
source_result = os.path.join(SOURCE_DIR, 'model_result.pkl')


# %%
df = (pl.read_excel(source_2sls, columns=COLUMNS)
      .with_columns(pl.col(COLS_SCALE1) * SCALE1, pl.col(COLS_SCALE2) * SCALE2)
      .with_columns(cs.by_dtype(pl.Float64) - cs.by_dtype(pl.Float64).mean()
                    .over(pl.col(GROUP_COL)),
                    (pl.lit(1) - pl.sum_horizontal(INDICS_IN)).alias(INDIC_EX))
      .with_columns((pl.col(col) * pl.col(INDEP_VAR))
                    .alias(f"{INDEP_VAR}:{col}")
                    for col in INDICS_IN)
      .with_columns(pl.when(pl.col(col) == 1)
                    .then(pl.lit(col).str.extract(r'([^_]+$)'))
                    .alias(col)
                    for col in INDICS_ALL)
      .with_columns(pl.coalesce(pl.col(f'^{prefix}_.+$')).alias(prefix).str.replace(k, v)
                    for k, v in INDIC_MAP.items()
                    for prefix in dict.fromkeys(col.rsplit('_', maxsplit=1)[0]
                                                for col in INDICS_ALL))
      .drop(INDICS_ALL))


# %%
result = pickle.load(open(source_result, "rb"))
params = result.params * SCALE1 / SCALE2

params_indic = params[:0]
new_key = get_indic(INDIC_EX)
params_indic[new_key] = params[INDEP_VAR]

for col in INDICS_IN:
      key = f"{INDEP_VAR}:{col}"
      new_key = get_indic(col)
      params_indic[new_key] = params[INDEP_VAR] + params[key]


# %%
start = df.select(INDEP_VAR).min().item()
stop = df.select(INDEP_VAR).max().item()
num = 1000

x = np.linspace(start, stop, num)
ys = {indic: param * x
      for indic, param in zip(params_indic.index, params_indic)}


# %%
df_control = df.clone()

for var in CONTROL_VARS:
    df_control = (df_control
                  .with_columns(pl.col(DEP_VAR) - pl.col(var) * params[var]))

# %%
dest = 'main_regress.png'

sns.set_theme(rc={'figure.figsize': (8, 6)})
plt.figure()
plot = sns.scatterplot(df_control,
                       x=INDEP_VAR, y=DEP_VAR,
                       hue=HUE_VAR,hue_order = map(get_indic, INDICS_ALL),
                       alpha=0.8, s = 25)
plot.set_title("FE-2SLS Regression of NB Municipal Tax Rates " \
      "on Police Spending",
               fontsize = 14)
plot.set(xlabel=f"${INDEP_VAR}_{{it}} - \overline{{{INDEP_VAR}}}_i$  " \
      "(CAD/person)",
         ylabel=f"${DEP_VAR}_{{it}} - \overline{{{DEP_VAR}}}_i$  " \
               "(%)\n(adjusted for controls)")

for indic, y in ys.items():
      sns.lineplot(x=x, y=y, label=indic, lw=2, legend=False)

plt.savefig(dest, dpi=300, bbox_inches='tight')
plt.close()