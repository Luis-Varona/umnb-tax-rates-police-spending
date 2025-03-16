# %%
import os
from typing import Literal

import polars as pl
import polars.selectors as cs

from statsmodels.iolib.summary2 import Summary
from statsmodels.regression.mixed_linear_model \
    import MixedLM, MixedLMResultsWrapper


# %%
def main():
    print("Not yet fully implemented.")
    
    source = os.path.join('..',
                          'data_pipeline',
                          'data_final',
                          'data_final.xlsx')
    dest_dir = 'cre_results'
    os.makedirs(dest_dir, exist_ok=True)
    
    model_ids = ('base', 'disagg_nec', 'disagg_nrc', 'unrestricted')
    df_all = read_data(source)
    df_dict = mean_and_sep_dataframes(df_all)
    model_dict = {}
    
    for model_id in model_ids:
        model, result = fit_model(df_dict, model_id)
        model_log, result_log = fit_model(df_dict, model_id, left_log=True)
        
        model_dict[model_id] = (model, result)
        model_dict[f"{model_id}_log"] = (model_log, result_log)
        
        dest = os.path.join(dest_dir, f'model_summary_{model_id}.txt')
        dest_log = os.path.join(dest_dir, f'model_summary_{model_id}_log.txt')
        write_model_summary(result.summary(), dest)
        write_model_summary(result_log.summary(), dest_log)


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
               "POP", "MPSA", "MUNI"]
    
    df_all = pl.read_excel(source)
    return (df_all.rename(dict(zip(df_all.columns, columns)))
            .drop(pl.col("POP"))
            .with_columns(pl.col("ATR") / 100)
            .with_columns(~cs.by_name(columns[:3] + columns[-2:]) / 1e5))


# %%
def add_mundlak_means(df: pl.DataFrame) -> pl.DataFrame:
    df_working = df.clone()
    time_varying_vars = [var for var in df.columns if var not in
                         {"year", "municipality", "ATR", "MPSA", "MUNI"}]
    
    for var in time_varying_vars:
        df_working = df_working.with_columns(pl.col(var)
                                             .mean()
                                             .over("municipality")
                                             .alias(f"{var}_mean"))
    
    return df_working


# %%
def mean_and_sep_dataframes(df_all: pl.DataFrame) -> dict[str, pl.DataFrame]:
    vars_dict = {
        'base': ["year", "municipality",
                 "ATR", "PSC", "TBC",
                 "NEC", "NRC",
                 "MPSA", "MUNI"],
        'disagg_nec': ["year", "municipality",
                       "ATR", "PSC", "TBC",
                       "GGS", "FPS", "WCT", "EMS", "OPS",
                       "TRS", "EHS", "PHS", "EDS",
                       "RCS", "DBC", "TRN", "DFC",
                       "NRC", "MPSA", "MUNI"],
        'disagg_nrc': ["year", "municipality",
                       "ATR", "PSC", "TBC", "NEC",
                       "UGR", "OGS", "SOS", "OSR", "CTR",
                       "OTR", "BIS",
                       "MPSA", "MUNI"],
        'unrestricted': [col for col in df_all.columns if col not in
                         {"NEC", "NRC"}],
    }
    
    return {model_id: (add_mundlak_means(df_all.select(columns))
                       .with_columns(pl.col("ATR").log().alias("log_ATR"))
                       .with_columns(pl.col("TBC").log().alias("log_TBC")))
            for model_id, columns in vars_dict.items()}


# %%
def fit_model(df_dict: dict[str, pl.DataFrame],
              model_id: Literal['base',
                                'disagg_nec',
                                'disagg_nrc',
                                'unrestricted'],
              *, left_log: bool = False,
              ) -> tuple[MixedLM, MixedLMResultsWrapper]:
    df = df_dict[model_id]
    
    dep_var = "log_ATR" if left_log else "ATR"
    exclude_var = "TBC" if left_log else "log_TBC"
    indep_vars = [var for var in df.columns if var not in
                  {"year", "municipality", "ATR", "log_ATR", exclude_var}]
    
    formula = f"{dep_var} ~ {' + '.join(indep_vars)}"
    group = df.select("municipality").to_series()
    
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
    if not (wd := os.getcwd()).endswith('data_analysis'):
        os.chdir('data_analysis')
    
    try:
        main()
    finally:
        os.chdir(wd)


# %%
os.chdir('data_analysis')


# %%

source = os.path.join('..', 'data_pipeline', 'data_final', 'data_final.xlsx')
model_ids = ('base', 'disagg_nec', 'disagg_nrc', 'unrestricted')
df_all = read_data(source)
df_dict = mean_and_sep_dataframes(df_all)
model_dict = {}

for model_id in model_ids:
    model, result = fit_model(df_dict, model_id)
    model_log, result_log = fit_model(df_dict, model_id, left_log=True)
    
    model_dict[model_id] = (model, result)
    model_dict[f"{model_id}_log"] = (model_log, result_log)


# %%
results_ur = model_dict['unrestricted'][1]
results_ur_log = model_dict['unrestricted_log'][1]

hypothesis1 = 'GGS = FPS = WCT = EMS = OPS ' \
    '= TRS = EHS = PHS = EDS = RCS = DBC = TRN = DFC'
hypothesis2 = 'UGR = OGS = SOS = OSR = CTR = OTR = BIS'
hypothesis3 = f'({hypothesis1}),  ({hypothesis2})'
hypothesis4 = 'MPSA = MUNI = 0'

f_test_1 = results_ur.f_test(hypothesis1)
f_test_2 = results_ur.f_test(hypothesis2)
f_test_3 = results_ur.f_test(hypothesis3)
f_test_4 = results_ur.f_test(hypothesis4)

f_test_1_log = results_ur_log.f_test(hypothesis1)
f_test_2_log = results_ur_log.f_test(hypothesis2)
f_test_3_log = results_ur_log.f_test(hypothesis3)
f_test_4_log = results_ur_log.f_test(hypothesis4)


# %%
df = df_dict['unrestricted'].drop("MPSA", "MUNI")

dep_var = "log_ATR"
indep_vars = [var for var in df.columns if var not in
              {"year", "municipality", "ATR", "log_ATR", "TBC"}]

formula = f"{dep_var} ~ {' + '.join(indep_vars)}"
group = df.select("municipality").to_series()

model = MixedLM.from_formula(formula, df, groups=group)
result = model.fit(reml=True)
summary = result.summary()

dest = os.path.join('cre_results', 'model_summary.txt')
write_model_summary(summary, dest)


# %%
os.chdir('..')