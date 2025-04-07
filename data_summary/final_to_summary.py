# %%
import os

import polars as pl
from xlsxwriter import Workbook


# %%
def main():
    source = os.path.join('../',
                          'data_pipeline',
                          'data_final',
                          'data_final.xlsx')
    
    dest_by_year = 'data_summary_by_year.xlsx'
    dest_by_stat = 'data_summary_by_stat.xlsx'
    df = pl.read_excel(source)
    
    with Workbook(dest_by_year) as workbook:
        for year, summary_df in get_data_summary_by_year(df).items():
            summary_df.write_excel(workbook, str(year),
                                   header_format={'bold': True}, autofit=True)
    
    with Workbook(dest_by_stat) as workbook:
        for stat, summary_df in get_data_summary_by_stat(df).items():
            summary_df.write_excel(workbook, stat,
                                   header_format={'bold': True}, autofit=True)


# %%
def get_data_summary_by_year(df: pl.DataFrame) -> dict[int, pl.DataFrame]:
    return {year: df.filter(pl.col("Year") == year)
            .drop("Year", "Municipality")
            .describe()
            for year in sorted(df.to_series())}


# %%
def get_data_summary_by_stat(df: pl.DataFrame) -> dict[str, pl.DataFrame]:
    agg_funcs = {
        'count': lambda series: series.count(),
        'null_count': lambda series: series.null_count(),
        'mean': lambda series: series.mean(),
        'std': lambda series: series.std(),
        'min': lambda series: series.min(),
        '25%': lambda series: series.quantile(0.25),
        '50%': lambda series: series.median(),
        '75%': lambda series: series.quantile(0.75),
        'max': lambda series: series.max(),
    }
    
    return {stat: (df.drop("Municipality")
                   .group_by("Year")
                   .agg(func(pl.all()))
                   .sort("Year"))
            for stat, func in agg_funcs.items()}


# %%
if __name__ == '__main__':
    if not (wd := os.getcwd()).endswith('data_summary'):
        os.chdir('data_summary')
    
    try:
        main()
    finally:
        os.chdir(wd)
