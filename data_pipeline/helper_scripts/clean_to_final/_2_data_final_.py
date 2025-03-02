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
                .drop("Provider_PPSA"))
    
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
            "Total Tax Base for Rate": "Total Tax Base for Rate (TAX)",
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