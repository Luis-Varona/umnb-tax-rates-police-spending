# %%
import os

import polars as pl
from xlsxwriter import Workbook


# %%
def main():
    dir_used = 'data_final'
    source = os.path.join(dir_used, 'data_master.xlsx')
    dest = os.path.join(dir_used, 'data_final.xlsx')
    
    categories = ['bgt_revs', 'bgt_exps', 'cmp_data', 'tax_base']
    columns = ["Year",
               "Municipality",
               "Average Tax Rate (CMP)",
               "Police Exp./Capita (EXP)",
               "Tax Base for Rate/Capita (TAX)",
               "General Government/Capita (EXP)",
               "Fire Protection/Capita (EXP)",
               "Water Cost Transfer/Capita (EXP)",
               "Emergency Measures/Capita (EXP)",
               "Other Protection/Capita (EXP)",
               "Transportation/Capita (EXP)",
               "Environmental Health/Capita (EXP)",
               "Public Health/Capita (EXP)",
               "Environmental Dev./Capita (EXP)",
               "Recreation & Cultural/Capita (EXP)",
               "Debt Costs/Capita (EXP)",
               "Transfers/Capita (EXP)",
               "Deficits/Capita (EXP)",
               "Total Non-Police Exp./Capita (EXP)",
               "Unconditional Grant/Capita (REV)",
               "Other Gov. Services/Capita (REV)",
               "Sale of Services/Capita (REV)",
               "Own-Source/Capita (REV)",
               "Conditional Transfers/Capita (REV)",
               "Other Transfers/Capita (REV)",
               "Biennial Surplus/Capita (REV)",
               "Total Non-Warrant Rev./Capita (REV)",
               "Latest Census Pop. (CMP)",
               "Provider_PPSA",
               "Provider_Municipal"]
    column_maps = get_column_maps()
    dfs = {cat: pl.read_excel(source,
                              sheet_name=cat,
                              columns=list(column_maps[cat].keys()))
           .rename(column_maps[cat])
           for cat in categories}
    muni_list = set(dfs[categories[0]].to_series(1))
    
    if any(set(dfs[cat].to_series(1)) != muni_list for cat in categories[1:]):
        raise RuntimeError("Municipalities are not the same across datasets.")
    
    provider_map = dict(zip(*pl.read_excel(source, sheet_name='pol_prov')))
    join_cols = ["Year", "Municipality"]
    df_final = (dfs[categories[0]]
                .join(dfs[categories[1]], join_cols)
                .join(dfs[categories[2]], join_cols)
                .join(dfs[categories[3]], join_cols)
                .with_columns(pl.col("Municipality")
                              .replace(provider_map)
                              .alias("Provider"))
                .to_dummies("Provider")
                .with_columns(pl.col("Municipality")
                              .replace(provider_map)
                              .alias("Provider"))
                .with_columns((pl.col("Police (EXP)")
                               / pl.col("Latest Census Pop. (CMP)"))
                              .alias("Police Exp./Capita (EXP)"))
                .with_columns((pl.col("Tax Base for Rate (TAX)")
                               / pl.col("Latest Census Pop. (CMP)"))
                              .alias("Tax Base for Rate/Capita (TAX)"))
                .with_columns((pl.col("General Government (EXP)")
                               / pl.col("Latest Census Pop. (CMP)"))
                              .alias("General Government/Capita (EXP)"))
                .with_columns((pl.col("Fire Protection (EXP)")
                               / pl.col("Latest Census Pop. (CMP)"))
                              .alias("Fire Protection/Capita (EXP)"))
                .with_columns((pl.col("Water Cost Transfer (EXP)")
                               / pl.col("Latest Census Pop. (CMP)"))
                              .alias("Water Cost Transfer/Capita (EXP)"))
                .with_columns((pl.col("Emergency Measures (EXP)")
                               / pl.col("Latest Census Pop. (CMP)"))
                              .alias("Emergency Measures/Capita (EXP)"))
                .with_columns((pl.col("Other Protection (EXP)")
                               / pl.col("Latest Census Pop. (CMP)"))
                              .alias("Other Protection/Capita (EXP)"))
                .with_columns((pl.col("Transportation (EXP)")
                               / pl.col("Latest Census Pop. (CMP)"))
                              .alias("Transportation/Capita (EXP)"))
                .with_columns((pl.col("Environmental Health (EXP)")
                               / pl.col("Latest Census Pop. (CMP)"))
                              .alias("Environmental Health/Capita (EXP)"))
                .with_columns((pl.col("Public Health (EXP)")
                               / pl.col("Latest Census Pop. (CMP)"))
                              .alias("Public Health/Capita (EXP)"))
                .with_columns((pl.col("Environmental Dev. (EXP)")
                               / pl.col("Latest Census Pop. (CMP)"))
                              .alias("Environmental Dev./Capita (EXP)"))
                .with_columns((pl.col("Recreation & Cultural (EXP)")
                               / pl.col("Latest Census Pop. (CMP)"))
                              .alias("Recreation & Cultural/Capita (EXP)"))
                .with_columns((pl.col("Debt Costs (EXP)")
                               / pl.col("Latest Census Pop. (CMP)"))
                              .alias("Debt Costs/Capita (EXP)"))
                .with_columns((pl.col("Transfers (EXP)")
                               / pl.col("Latest Census Pop. (CMP)"))
                              .alias("Transfers/Capita (EXP)"))
                .with_columns((pl.col("Deficits (EXP)")
                               / pl.col("Latest Census Pop. (CMP)"))
                              .alias("Deficits/Capita (EXP)"))
                .with_columns((pl.col("General Government/Capita (EXP)")
                              + pl.col("Fire Protection/Capita (EXP)")
                              + pl.col("Water Cost Transfer/Capita (EXP)")
                              + pl.col("Emergency Measures/Capita (EXP)")
                              + pl.col("Other Protection/Capita (EXP)")
                              + pl.col("Transportation/Capita (EXP)")
                              + pl.col("Environmental Health/Capita (EXP)")
                              + pl.col("Public Health/Capita (EXP)")
                              + pl.col("Environmental Dev./Capita (EXP)")
                              + pl.col("Recreation & Cultural/Capita (EXP)")
                              + pl.col("Debt Costs/Capita (EXP)")
                              + pl.col("Transfers/Capita (EXP)")
                              + pl.col("Deficits/Capita (EXP)"))
                              .alias("Total Non-Police Exp./Capita (EXP)"))
                .with_columns((pl.col("Unconditional Grant (REV)")
                               / pl.col("Latest Census Pop. (CMP)"))
                              .alias("Unconditional Grant/Capita (REV)"))
                .with_columns((pl.col("Other Gov. Services (REV)")
                               / pl.col("Latest Census Pop. (CMP)"))
                              .alias("Other Gov. Services/Capita (REV)"))
                .with_columns((pl.col("Sale of Services (REV)")
                               / pl.col("Latest Census Pop. (CMP)"))
                              .alias("Sale of Services/Capita (REV)"))
                .with_columns((pl.col("Own-Source (REV)")
                               / pl.col("Latest Census Pop. (CMP)"))
                              .alias("Own-Source/Capita (REV)"))
                .with_columns((pl.col("Conditional Transfers (REV)")
                               / pl.col("Latest Census Pop. (CMP)"))
                              .alias("Conditional Transfers/Capita (REV)"))
                .with_columns((pl.col("Other Transfers (REV)")
                               / pl.col("Latest Census Pop. (CMP)"))
                              .alias("Other Transfers/Capita (REV)"))
                .with_columns((pl.col("Biennial Surplus (REV)")
                               / pl.col("Latest Census Pop. (CMP)"))
                              .alias("Biennial Surplus/Capita (REV)"))
                .with_columns((pl.col("Unconditional Grant/Capita (REV)")
                               + pl.col("Other Gov. Services/Capita (REV)")
                               + pl.col("Sale of Services/Capita (REV)")
                               + pl.col("Own-Source/Capita (REV)")
                               + pl.col("Conditional Transfers/Capita (REV)")
                               + pl.col("Other Transfers/Capita (REV)")
                               + pl.col("Biennial Surplus/Capita (REV)"))
                              .alias("Total Non-Warrant Rev./Capita (REV)"))
                .select(columns))
    
    with Workbook(dest) as workbook:
        df_final.write_excel(workbook,
                             header_format={'bold': True}, autofit=True)


# %%
def get_column_maps() -> dict[str, dict[str, str]]:
    return {
        'bgt_exps': {
            "Year": "Year",
            "Municipality": "Municipality",
            "General Government": "General Government (EXP)",
            "Police": "Police (EXP)",
            "Fire Protection": "Fire Protection (EXP)",
            "Water Cost Transfer": "Water Cost Transfer (EXP)",
            "Emergency Measures": "Emergency Measures (EXP)",
            "Other Protection Services": "Other Protection (EXP)",
            "Transportation": "Transportation (EXP)",
            "Environmental Health": "Environmental Health (EXP)",
            "Public Health": "Public Health (EXP)",
            "Environmental Development": "Environmental Dev. (EXP)",
            "Recreation & Cultural": "Recreation & Cultural (EXP)",
            "Debt Costs": "Debt Costs (EXP)",
            "Transfers": "Transfers (EXP)",
            "Deficits": "Deficits (EXP)",
            "Total Expenditures": "Total Expenditures (EXP)",
        },
        'bgt_revs': {
            "Year": "Year",
            "Municipality": "Municipality",
            "Warrant": "Warrant (REV)",
            "Unconditional Grant": "Unconditional Grant (REV)",
            "Services to Other Governments": "Other Gov. Services (REV)",
            "Sale of Services": "Sale of Services (REV)",
            "Own-Source Revenue": "Own-Source (REV)",
            "Conditional Transfers": "Conditional Transfers (REV)",
            "Other Transfers": "Other Transfers (REV)",
            "Biennial Surplus": "Biennial Surplus (REV)",
            "Total Revenue": "Total Revenue (REV)",
        },
        'cmp_data': {
            "Year": "Year",
            "Municipality": "Municipality",
            "Latest Census Population": "Latest Census Pop. (CMP)",
            "Average Tax Rate": "Average Tax Rate (CMP)",
        },
        'tax_base': {
            "Year": "Year",
            "Municipality": "Municipality",
            "Total Tax Base for Rate": "Tax Base for Rate (TAX)",
        },
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