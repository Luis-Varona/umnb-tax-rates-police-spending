# %%
import os
import pickle
import sys

import numpy as np
import polars as pl

from linearmodels import OLS
from linearmodels.panel.model import PanelOLS

sys.path.append(os.path.join((WD := os.path.dirname(__file__)),
                             '..', '..', '..'))
from utils import LMResultsWrapper


# %%
WD = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(WD, '..', '..', '..', 'data_pipeline', 'data_final')
DEST_DIR = os.path.join(WD, '..', '..', 'cre_2sls')
INSTRUMENT_DIR = os.path.join(WD, '..', '..', '..', 'data_iv', 'results')


# %%
DEP_VAR = "AvgTaxRate"
INTER_VAR = "PolExpCapita"
NON_INTER_VARS = ["OtherExpCapita", "OtherRevCapita", "TaxBaseCapita"]
INDIC_VARS = ["Provider_MPSA", "Provider_Muni"]
INDEP_VARS = [INTER_VAR] + NON_INTER_VARS

INTER_TERMS = [f"{INTER_VAR}*{var}" for var in INDIC_VARS]
INTER_TERM_MEANS = [f"{INTER_VAR}_mean*{var}" for var in INDIC_VARS]
NON_INTER_VAR_MEANS = [f"{var}_mean" for var in NON_INTER_VARS]

ENDOG = "TaxBaseCapita"
FORMULA = f"{DEP_VAR} ~ {' + '.join
    (INTER_TERMS + NON_INTER_VARS + INTER_TERM_MEANS + NON_INTER_VAR_MEANS)}"


# %%
GROUP_COL = "Municipality"
TIME_COL = "Year"

INSTRUMENT = "MedHouseInc"
INSTRUMENT_YEARS = list(range(2000, 2021))


# %%
def main():
    os.makedirs(DEST_DIR, exist_ok=True)
    source = os.path.join(SOURCE_DIR, 'data_final.xlsx')
    source_instr = os.path.join(INSTRUMENT_DIR, 'muni_map.pkl')
    
    dest_df = os.path.join(DEST_DIR, 'data_cre_2sls.xlsx')
    dest_results1 = os.path.join(DEST_DIR, 'stage1_results.pkl')
    dest_summary1 = os.path.join(DEST_DIR, 'stage1_summary')
    dest_results2 = os.path.join(DEST_DIR, 'stage2_results.pkl')
    dest_summary2 = os.path.join(DEST_DIR, 'stage2_summary')
    
    results1, df = stage1_results_and_data(source, source_instr)
    results2 = stage2_results(df)
    save_all_output(df, results1, results2,
                    dest_df, dest_results1, dest_summary1,
                    dest_results2, dest_summary2)


# %%
def add_mundlak_means(df: pl.DataFrame) -> pl.DataFrame:
    for var in [DEP_VAR] + INDEP_VARS:
        df = df.with_columns(pl.col(var)
                             .mean()
                             .over(GROUP_COL)
                             .alias(f"{var}_mean"))
    
    return df


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


# %%
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
def stage1_results_and_data(source: str, source_instr: str
                            ) -> tuple[LMResultsWrapper, pl.DataFrame]:
    df_instr = get_instrument_data(source_instr)
    df = (add_mundlak_means(pl.read_excel(source))
          .join(df_instr, on=[GROUP_COL, TIME_COL], how="left"))
    
    model = OLS.from_formula(f"{ENDOG} ~ {INSTRUMENT}", df.to_pandas()) # New
    results = model.fit()
    new_endog = results.predict().iloc[:, 0]
    df = df.with_columns(pl.Series(new_endog).alias(ENDOG))
    
    return LMResultsWrapper(results), df

def stage2_results(df: pl.DataFrame) -> LMResultsWrapper:
    df_pandas = df.to_pandas()
    df_pandas.set_index([GROUP_COL, TIME_COL], inplace=True)
    
    model = PanelOLS.from_formula(FORMULA, df_pandas)
    results = model.fit(cov_type='clustered', cluster_entity=True)
    return LMResultsWrapper(results)


# %%
def save_all_output(df: pl.DataFrame,
                    results1: LMResultsWrapper, results2: LMResultsWrapper,
                    dest_df: str,
                    dest_results1: str, dest_summary1: str,
                    dest_results2: str, dest_summary2: str) -> None:
    df.write_excel(dest_df, header_format={'bold': True}, autofit=True)
    results1.save_all_data(dest_results1,
                           f"{dest_summary1}.txt",
                           f"{dest_summary1}.tex")
    results2.save_all_data(dest_results2,
                           f"{dest_summary2}.txt",
                           f"{dest_summary2}.tex")


# %%
if __name__ == '__main__':
    main()
