# %%
import os
import pickle

import numpy as np
import polars as pl

from linearmodels.panel.model import PanelOLS
from linearmodels.panel.results import PanelResults
from statsmodels.regression.linear_model import OLS


# %%
WD = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(WD, '..', '..', 'data_pipeline', 'data_final')
DEST_DIR = os.path.join(WD, '..', 'fe_2sls_results')
INSTRUMENT_DIR = os.path.join(WD, '..', '..', 'data_iv', 'results')


# %%
DEP_VAR = "AvgTaxRate"
EXOG = ["PolExpCapita", "OtherExpCapita", "OtherRevCapita",
        "PolExpCapita:Provider_MPSA", "PolExpCapita:Provider_Muni"]
ENDOG = "TaxBaseCapita"
FORMULA = f"{DEP_VAR} ~ {' + '.join(EXOG)} + {ENDOG} + EntityEffects"


# %%
GROUP_COL = "Municipality"
TIME_COL = "Year"

INSTRUMENT = "MedHouseInc"
INSTRUMENT_YEARS = list(range(2000, 2021))


# %%
def main():
    source = os.path.join(SOURCE_DIR, 'data_final.xlsx')
    source_instr = os.path.join(INSTRUMENT_DIR, 'muni_map.pkl')
    
    dest_df = os.path.join(DEST_DIR, 'data_2sls.xlsx')
    dest_result = os.path.join(DEST_DIR, 'model_result.pkl')
    dest_summary = os.path.join(DEST_DIR, 'model_summary.txt')
    dest_tex = os.path.join(DEST_DIR, 'model_summary.tex')
    os.makedirs(DEST_DIR, exist_ok=True)
    
    df = first_stage_regress(source, source_instr)
    model, result = fit_model(df)
    
    df.write_excel(dest_df)
    write_model_result(result, dest_result, dest_summary, dest_tex)


# %%
def process_muni_map(muni_map: dict[int, dict]) -> tuple[list, dict]:
    munis = list(muni_map[INSTRUMENT_YEARS[0] + 1].keys())
    incomes = {}
    
    for muni in munis:
        incomes[muni] = np.empty(len(INSTRUMENT_YEARS), np.float64)
        
        for i, year in enumerate(INSTRUMENT_YEARS):
            sub_map = muni_map.get(year + 1)
            incomes[muni][i] = sub_map[muni] if sub_map else np.nan
    
    return munis, incomes

def get_interp_args(incomes: dict[str, np.ndarray]) -> tuple[dict, dict, dict]:
    nans = {muni: np.isnan(income) for muni, income in incomes.items()}
    xs = {muni: np.where(nan)[0] for muni, nan in nans.items()}
    xps = {muni: np.where(~nan)[0] for muni, nan in nans.items()}
    fps = {muni: income[xps[muni]] for muni, income in incomes.items()}
    return xs, xps, fps

def interpolate_instrument_data(
    munis: list, incomes: dict[str, np.ndarray]
) -> pl.DataFrame:
    xs, xps, fps = get_interp_args(incomes)
    
    for muni, income in incomes.items():
        income[xs[muni]] = np.interp(xs[muni], xps[muni], fps[muni])
    
    muni_series = munis * len(INSTRUMENT_YEARS)
    year_series = [year for year in INSTRUMENT_YEARS for _ in munis]
    income_series = [income[t] / 1e5 for t in range(len(INSTRUMENT_YEARS))
                     for income in incomes.values()]
    
    return pl.DataFrame(
        {
            GROUP_COL: muni_series,
            TIME_COL: year_series,
            INSTRUMENT: income_series
        }
    )

def get_instrument_data(source_instr: str) -> pl.DataFrame:
    with open(source_instr, 'rb') as f:
        muni_map = pickle.load(f)
    
    return interpolate_instrument_data(*process_muni_map(muni_map))


# %%
def first_stage_regress(source: str, source_instr: str) -> pl.DataFrame:
    df_instr = get_instrument_data(source_instr)
    df = (pl.read_excel(source)
          .join(df_instr, on=[GROUP_COL, "Year"], how="left"))
    
    iv_model = OLS.from_formula(f"{ENDOG} ~ {INSTRUMENT}", df)
    new_endog = iv_model.fit().predict()
    
    return df.with_columns(pl.Series(new_endog).alias(ENDOG))

def fit_model(df: pl.DataFrame) -> tuple[PanelOLS, PanelResults]:
    df_pandas = df.to_pandas()
    df_pandas.set_index([GROUP_COL, TIME_COL], inplace=True)
    
    model = PanelOLS.from_formula(FORMULA, df_pandas)
    result = model.fit(cov_type='clustered', cluster_entity=True)
    
    return model, result

def write_model_result(
    result: PanelResults, dest_result: str, dest_summary: str, dest_tex: str,
) -> None:
    for dest in {dest_result, dest_summary}:
        if os.path.exists(dest):
            os.remove(dest)
    
    with open(dest_result, 'xb') as file:
        pickle.dump(result, file)
    
    with open(dest_summary, 'x') as file:
        file.write(result.summary.as_text())
    
    with open(dest_tex, 'x') as file:
        file.write(result.summary.as_latex())


# %%
if __name__ == "__main__":
    main()