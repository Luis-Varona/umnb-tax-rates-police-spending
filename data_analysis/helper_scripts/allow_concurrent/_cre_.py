# %%
import os
import sys

import polars as pl
from statsmodels.regression.mixed_linear_model import MixedLM

sys.path.append(os.path.join((WD := os.path.dirname(__file__)),
                             '..', '..', '..'))
from utils import ModelResults


# %%
WD = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(WD, '..', '..', '..', 'data_pipeline', 'data_final')
DEST_DIR = os.path.join(WD, '..', '..', 'cre')


# %%
DEP_VAR = "AvgTaxRate"
INDEP_VARS = ["PolExpCapita", "OtherExpCapita",
              "OtherRevCapita", "TaxBaseCapita"]
INDEP_VARS += [f"{var}_mean" for var in INDEP_VARS]
INDEP_VARS_INDIC = ["Provider_MPSA", "Provider_Muni"]
INDEP_VARS_INTER = [f"PolExpCapita:{var}" for var in INDEP_VARS_INDIC]


# %%
GROUP_COL = "Municipality"

FORMULAS = {
    'rstd': f"{DEP_VAR} ~ {' + '.join(INDEP_VARS)}",
    'indic': f"{DEP_VAR} ~ {' + '.join(INDEP_VARS + INDEP_VARS_INDIC)}",
    'inter': f"{DEP_VAR} ~ {' + '.join(INDEP_VARS + INDEP_VARS_INTER)}",
    'unrstd': f"{DEP_VAR} ~ " \
        f"{' + '.join(INDEP_VARS + INDEP_VARS_INTER + INDEP_VARS_INDIC)}",
}


# %%
def main():
    os.makedirs(DEST_DIR, exist_ok=True)
    source = os.path.join(SOURCE_DIR, 'data_final.xlsx')
    
    df = add_mundlak_means(pl.read_excel(source))
    
    for model_id in FORMULAS.keys():
        dest_result = os.path.join(DEST_DIR, f"results_{model_id}.pkl")
        dest_summary = os.path.join(DEST_DIR, f"summary_{model_id}")
        model_results = fit_model(df, model_id)
        save_output(model_results, dest_result, dest_summary)


# %%
def add_mundlak_means(df: pl.DataFrame) -> pl.DataFrame:
    for var in [DEP_VAR] + INDEP_VARS:
        df = df.with_columns(pl.col(var)
                             .mean()
                             .over(GROUP_COL)
                             .alias(f"{var}_mean"))
    
    return df


# %%
def fit_model(df: pl.DataFrame, model_id: str) -> ModelResults:
    formula = FORMULAS[model_id]
    group = df.select(GROUP_COL).to_series()
    
    model = MixedLM.from_formula(formula, df, groups=group)
    result = model.fit(reml=True)
    return ModelResults(result, 'statsmodels')


# %%
def save_output(model_results: ModelResults,
                dest_results: str, dest_summary: str) -> None:
    model_results.save_results(dest_results)
    model_results.save_summary(f"{dest_summary}.txt", f"{dest_summary}.tex")


# %%
if __name__ == '__main__':
    main()


# %%
wd = os.getcwd()
os.chdir(os.path.dirname(__file__))


# %%
source = os.path.join(SOURCE_DIR, 'data_final.xlsx')
df = add_mundlak_means(pl.read_excel(source))
results = {}

for model_id in FORMULAS.keys():
    model_results = fit_model(df, model_id)
    results[model_id] = model_results.results


# %%
results_rstd = results['rstd']
results_indic = results['indic']
results_inter = results['inter']
results_unrstd = results['unrstd']


# %%
hypothesis_indic = "Provider_MPSA = 0 = Provider_Muni = 0"
hypothesis_inter = "PolExpCapita:Provider_MPSA = PolExpCapita:Provider_Muni" \
    " = 0"
hypothesis_full = "PolExpCapita:Provider_MPSA = PolExpCapita:Provider_Muni" \
    " = Provider_MPSA = 0 = Provider_Muni = 0"


# %%
ftest1 = results_unrstd.f_test(hypothesis_indic)
ftest2 = results_unrstd.f_test(hypothesis_inter)
ftest3 = results_unrstd.f_test(hypothesis_full)


# %%
ftest4 = results_indic.f_test(hypothesis_indic)
ftest5 = results_inter.f_test(hypothesis_inter)


# %%
os.chdir(wd)
