# %%
import os

import polars as pl


# %%
WD = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(WD, '..', '..', 'data_final')
DEST_DIR = SOURCE_DIR


# %%
CATEGORIES = ['bgt_revs', 'bgt_exps', 'cmp_data', 'tax_base']

COLUMNS = ["Year",
           "Municipality",
           "AvgTaxRate",
           "PolExpCapita",
           "OtherExpCapita",
           "OtherRevCapita",
           "TaxBaseCapita",
           "Provider_MPSA",
           "Provider_Muni",
           "LatestCensusPop"]

COLUMNS_SCALE = ["PolExp",
                 "TotalExp",
                 "TaxRev",
                 "TotalRev",
                 "TaxBase"]

COLUMN_MAPS = {
    "bgt_exps": {
        "Year": "Year",
        "Municipality": "Municipality",
        "Police": "PolExp",
        "Total Expenditures": "TotalExp",
    },
    "bgt_revs": {
        "Year": "Year",
        "Municipality": "Municipality",
        "Warrant": "TaxRev",
        "Total Revenue": "TotalRev",
    },
    "cmp_data": {
        "Year": "Year",
        "Municipality": "Municipality",
        "Latest Census Population": "LatestCensusPop",
        "Average Tax Rate": "AvgTaxRate",
    },
    "tax_base": {
        "Year": "Year",
        "Municipality": "Municipality",
        "Total Tax Base for Rate": "TaxBase",
    },
}


# %%
def main():
    source = os.path.join(SOURCE_DIR, 'data_master.xlsx')
    dest = os.path.join(DEST_DIR, 'data_final.xlsx')
    
    
    dfs = {cat: pl.read_excel(source,
                              sheet_name=cat,
                              columns=list(COLUMN_MAPS[cat].keys()))
           .rename(COLUMN_MAPS[cat]) for cat in CATEGORIES}
    df_final = dfs[CATEGORIES[0]]
    muni_list = set(df_final.to_series(1))
    
    if any(set(dfs[cat].to_series(1)) != muni_list for cat in CATEGORIES[1:]):
        raise RuntimeError("Municipalities are not the same across datasets.")
    
    for cat in CATEGORIES[1:]:
        df_final = (df_final.join(dfs[cat], ["Year", "Municipality"]))
    
    provider_map = dict(zip(*pl.read_excel(source, sheet_name='pol_prov')))
    
    df_final = (df_final
                .with_columns(pl.col("AvgTaxRate") / 100)
                .with_columns(pl.col(COLUMNS_SCALE) / 1e5)
                .with_columns((pl.col("TaxBase") / pl.col("LatestCensusPop"))
                              .alias("TaxBaseCapita"))
                .with_columns((pl.col("PolExp") / pl.col("LatestCensusPop"))
                              .alias("PolExpCapita"))
                .with_columns(((pl.col("TotalExp") - pl.col("PolExp"))
                               / pl.col("LatestCensusPop"))
                              .alias("OtherExpCapita"))
                .with_columns(((pl.col("TotalRev") - pl.col("TaxRev"))
                               / pl.col("LatestCensusPop"))
                              .alias("OtherRevCapita"))
                .with_columns(pl.col("Municipality")
                              .replace(provider_map)
                              .alias("Provider"))
                .to_dummies("Provider")
                .rename({"Provider_Municipal": "Provider_Muni"})
                .select(COLUMNS))
    
    df_final.write_excel(dest, header_format={'bold': True}, autofit=True)


# %%
if __name__ == '__main__':
    main()
