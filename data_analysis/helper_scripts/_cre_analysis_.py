# %%
import os

import polars as pl
from statsmodels.iolib.summary2 import Summary
from statsmodels.regression.mixed_linear_model \
    import MixedLM, MixedLMResultsWrapper


# %%
WD = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(WD, '..', '..', 'data_pipeline', 'data_final')
DEST_DIR = os.path.join(WD, '..', 'cre_results')


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
    source = os.path.join(SOURCE_DIR, 'data_final.xlsx')
    os.makedirs(DEST_DIR, exist_ok=True)
    
    df = add_mundlak_means(pl.read_excel(source))
    models = {}
    
    for model_id in FORMULAS.keys():
        model, result = fit_model(df, model_id)
        models[model_id] = (model, result)
        
        dest = os.path.join(DEST_DIR, f'model_summary_{model_id}.txt')
        write_model_summary(result.summary(), dest)


# %%
def add_mundlak_means(df: pl.DataFrame) -> pl.DataFrame:
    for var in [DEP_VAR] + INDEP_VARS:
        df = df.with_columns(pl.col(var)
                             .mean()
                             .over(GROUP_COL)
                             .alias(f"{var}_mean"))
    
    return df


# %%
def fit_model(
    df: pl.DataFrame, model_id: str,
) -> tuple[MixedLM, MixedLMResultsWrapper]:
    formula = FORMULAS[model_id]
    group = df.select(GROUP_COL).to_series()
    model = MixedLM.from_formula(formula, df, groups=group)
    result = model.fit(reml=True)
    return model, result


# %%
def write_model_summary(summary: Summary, dest: str) -> None:
    if os.path.exists(dest):
        os.remove(dest)
    
    with open(dest, 'x') as file:
        file.write(summary.as_text())


# %%
if __name__ == "__main__":
    main()


# %%
wd = os.getcwd()
os.chdir(os.path.dirname(__file__))


# %%
source = os.path.join(SOURCE_DIR, 'data_final.xlsx')
df = add_mundlak_means(pl.read_excel(source))
models = {}

for model_id in FORMULAS.keys():
    model, result = fit_model(df, model_id)
    models[model_id] = (model, result)


# %%
results_rstd = models['rstd'][1]
results_indic = models['indic'][1]
results_inter = models['inter'][1]
results_unrstd = models['unrstd'][1]


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