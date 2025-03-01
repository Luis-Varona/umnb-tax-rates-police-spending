# %%
import logging
import os
import polars as pl
from xlsxwriter import Workbook


# %%
def main():
    source = 'data_raw/GNB2024_pol_prov.xlsx'
    dest = 'data_clean/GNB2024_pol_prov_clean.xlsx'
    os.makedirs('/'.join(dest.split('/')[:-1]), exist_ok=True)
    
    logger = logging.getLogger('fastexcel.types.dtype')
    default_level = logger.getEffectiveLevel()
    logger.setLevel(logging.ERROR)
    
    try:
        with Workbook(dest) as workbook:
            (clean_pol_prov_data(get_mun_map(read_provider_data(source)))
             .write_excel(workbook,
                          header_format={'bold': True}, autofit=True))
    finally:
        logger.setLevel(default_level)


# %%
def read_provider_data(source: str) -> pl.DataFrame:
    return (pl.read_excel(source, columns=[0, 8])
            .filter(pl.nth(0).map_elements(len, pl.Int64) < 81)
            .with_columns(pl.nth(1)
                          .str.slice(0, 4)
                          .str.to_uppercase()
                          .str.replace(r"MUNI|BNPP|KVPF", "Municipal")))


# %%
def get_mun_map(provider_df: pl.DataFrame) -> dict[str, list[tuple]]:
    mun_iter = zip(*provider_df)
    curr_mun, curr_prov = next(mun_iter)
    mun_map: dict[str, list[tuple]] = {curr_mun: []}
    
    for mun, prov in mun_iter:
        if mun == "Florenceville-Bristol TV":
            mun_map[curr_mun].extend([(mun, curr_prov),
                                      ("Florenceville TV", curr_prov),
                                      ("Bristol TV", curr_prov)])
        elif mun == "Fundy Shores":
            curr_mun, curr_prov = mun, prov
            mun_map[curr_mun] = []
        elif curr_mun == "Fundy Shores" and mun != "Fundy-St. Martins":
            mun_map[curr_mun].append((mun, prov))
        elif mun == "Woodstock":
            curr_mun, curr_prov = mun, prov
            mun_map[curr_mun] = []
        elif curr_mun == "Woodstock":
            mun_map[curr_mun].append((mun, prov))
        elif prov is None:
            mun_map[curr_mun].append((mun, curr_prov))
        else:
            curr_mun, curr_prov = mun, prov
            mun_map[curr_mun] = []
    
    return mun_map


# %%
def clean_pol_prov_data(mun_map: dict[str, list[tuple]]) -> pl.DataFrame:
    municipalities = [mun for mun in mun_map for _ in mun_map[mun]]
    districts, providers = zip(*(token for value in mun_map.values()
                                 for token in value))
    
    return (pl.DataFrame(
        {
            "District": districts,
            "Municipality": municipalities,
            "Policing Provider": providers,
        }
    )
            .filter(pl.col("District").str.contains(r"\s(C|TV|V)$"))
            .with_columns(pl.col("District")
                          .str.replace(r"\s(C|TV|V)$",
                                       "")
                          .str.replace(r"^Baker Brook$",
                                       "Baker-Brook")
                          .str.replace(r"^Cambridge Narrows$",
                                       "Cambridge-Narrows")
                          .str.replace(r"^Neguac",
                                       "Néguac")
                          .str.replace(r"^Plaster Rocker$",
                                       "Plaster Rock")
                          .str.replace(r"^Saint-Anne$",
                                       "Sainte-Anne-de-Madawaska")
                          .str.replace(r"^Saint-François$",
                                       "Saint-François-de-Madawaska")
                          .str.replace(r"^Ste-Marie-St-Raphael$",
                                       "Sainte-Marie-Saint-Raphaël")
                          .str.replace(r"^Tracadie$",
                                       "Tracadie-Sheila")
                          .str.replace(r"^Eel Riv.*",
                                       "Eel River Crossing")
                          .str.replace(r"^Grand-Sault.*",
                                       "Grand Falls/Grand-Sault")
                          .str.replace(r"^Nackawic.*",
                                       "Nackawic"))
            .with_columns(pl.col("Municipality")
                          .str.replace(r"^Tracadie$",
                                       "Tracadie-Sheila")
                          .str.replace(r"^Grand-Sault.*",
                                       "Grand Falls/Grand-Sault")
                          .str.replace(r"^Nackawic.*",
                                       "Nackawic")))


# %%
if __name__ == '__main__':
    if (wd := os.getcwd()).endswith('cleaning_scripts'):
        os.chdir('..')
    
    try:
        main()
    finally:
        os.chdir(wd)