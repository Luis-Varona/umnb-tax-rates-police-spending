# %%
import os

import polars as pl
import polars.selectors as cs
from xlsxwriter import Workbook


# %%
def main():
    source_dir = 'data_clean'
    dest = os.path.join('data_final', 'data_master.xlsx')
    os.makedirs('/'.join(dest.split('/')[:-1]), exist_ok=True)
    
    categories = ['bgt_revs', 'bgt_exps', 'cmp_data', 'tax_base']
    years = list(range(2000, 2004)) + list(range(2006, 2019))
    source_maps = {cat: {year: os.path.join(source_dir,
                                            str(year),
                                            f'GNB{year}_{cat}_clean.xlsx')
                         for year in years}
                   for cat in categories}
    schemas = get_schemas()
    
    concat_dfs = {cat: concat_panels(source_map, schemas[cat])
                  for cat, source_map in source_maps.items()}
    muni_list = concat_dfs['cmp_data'].to_series(1).unique()
    provider_source = os.path.join(source_dir, 'GNB2024_pol_prov_clean.xlsx')
    provider_df = melt_provider_data(provider_source,
                                     schemas['pol_prov'],
                                     muni_list)
    data_master = concat_dfs | {'pol_prov': provider_df}
    
    with Workbook(dest) as workbook:
        for cat, df in data_master.items():
            df.write_excel(workbook, cat,
                           header_format={'bold': True},
                           autofit=True)


# %%
def concat_panels(source_map: dict[int, str],
                 schema: pl.Schema) -> pl.DataFrame:
    return pl.concat(pl.read_excel(source, schema_overrides=schema)
                     .with_columns(pl.lit(year, pl.UInt32).alias("Year"))
                     .select("Year", cs.exclude("Year"))
                     for year, source in source_map.items())


# %%
def melt_provider_data(source: str,
                       schema: pl.Schema,
                       muni_list: pl.Series) -> pl.DataFrame:
    provider_df = pl.read_excel(source, schema_overrides=schema)
    provider_map = {}
    
    for dist in provider_df.select("District").to_series().unique():
        if dist in muni_list:
            providers = (provider_df.filter(pl.col("District") == dist)
                        .to_series(2)
                        .unique())
            
            if len(providers) > 1:
                raise ValueError(f"District {dist} has multiple policing "
                                f"providers: {providers}")
            
            provider_map[dist] = providers[0]
    
    for muni in provider_df.select("Municipality").to_series().unique():
        if muni in muni_list:
            providers = (provider_df.filter(pl.col("Municipality") == muni)
                        .to_series(2)
                        .unique())
            
            if len(providers) > 1:
                raise RuntimeError(f"Municipality {muni} has multiple "
                                   f"policing providers: {providers}")
            
            if muni in provider_map and provider_map[muni] != providers[0]:
                raise RuntimeError(f"Municipality {muni} has different "
                                   f"policing providers: {provider_map[muni]} "
                                   f"and {providers[0]}")
            
            provider_map[muni] = providers[0]
    
    provider_map["Sussex Corner"] = provider_map["Sussex"]
    
    if missing_munis := set(muni_list) - provider_map.keys():
        raise RuntimeError("Missing policing provider data for the following "
                           f"municipalities: {missing_munis}")
    
    muni_data, prov_data = zip(*provider_map.items())
    return pl.DataFrame(
        {
            "Municipality": muni_data,
            "Policing Provider": prov_data,
        }
    ).sort("Municipality")


# %%
def get_schemas() -> dict[str, pl.Schema]:
    return {
        'bgt_exps': pl.Schema(
            {
                "Municipality": pl.Utf8,
                "General Government": pl.Float64,
                "Police": pl.Int64,
                "Fire Protection": pl.Int64,
                "Water Cost Transfer": pl.Int64,
                "Emergency Measures": pl.Int64,
                "Other Protection Services": pl.Int64,
                "Transportation": pl.Int64,
                "Environmental Health": pl.Int64,
                "Public Health": pl.Int64,
                "Environmental Development": pl.Int64,
                "Recreation & Cultural": pl.Int64,
                "Debt Costs": pl.Float64,
                "Transfers": pl.Int64,
                "Deficits": pl.Int64,
                "Total Expenditures": pl.Float64,
            }
        ),
        'bgt_revs': pl.Schema(
            {
                "Municipality": pl.Utf8,
                "Warrant": pl.Int64,
                "Unconditional Grant": pl.Int64,
                "Services to Other Governments": pl.Int64,
                "Sale of Services": pl.Int64,
                "Own-Source Revenue": pl.Int64,
                "Conditional Transfers": pl.Int64,
                "Other Transfers": pl.Int64,
                "Biennial Surplus": pl.Int64,
                "Total Revenue": pl.Int64,
            }
        ),
        'cmp_data': pl.Schema(
            {
                "Municipality": pl.Utf8,
                "Latest Census Population": pl.Int64,
                "Penultimate Census Population": pl.Int64,
                "Provincial Kilometrage": pl.Float64,
                "Regional Kilometrage": pl.Float64,
                "Municipal Kilometrage": pl.Float64,
                "Total Kilometrage": pl.Float64,
                "Population/Kilometrage": pl.Float64,
                "Tax Base": pl.Int64,
                "Tax Base/Capita": pl.Float64,
                "Tax Base/Kilometrage": pl.Float64,
                "Total Budget": pl.Int64,
                "Fiscal Capacity": pl.Float64,
                "Average Tax Rate": pl.Float64,
            }
        ),
        'tax_base': pl.Schema(
            {
                "Municipality": pl.Utf8,
                "General Residential Assessment": pl.Int64,
                "Federal Residential Assessment": pl.Int64,
                "Provincial Residential Assessment": pl.Int64,
                "Total Residential Assessment": pl.Int64,
                "General Non-Residential Assessment": pl.Int64,
                "Federal Non-Residential Assessment": pl.Int64,
                "Provincial Non-Residential Assessment": pl.Int64,
                "Total Non-Residential Assessment": pl.Int64,
                "Total Municipal Assessment Base": pl.Int64,
                "Total Municipal Tax Base": pl.Int64,
                "Total Tax Base for Rate": pl.Int64,
            }
        ),
        'pol_prov': pl.Schema(
            {
                "District": pl.Utf8,
                "Municipality": pl.Utf8,
                "Policing Provider": pl.Utf8,
            }
        ),
    }


# %%
if __name__ == '__main__':
    if (wd := os.getcwd()).endswith('clean_to_final'):
        os.chdir('../..')
    elif wd.endswith('helper_scripts'):
        os.chdir('..')
    elif not wd.endswith('data_pipeline'):
        os.chdir('data_pipeline')
    
    try:
        main()
    finally:
        os.chdir(wd)