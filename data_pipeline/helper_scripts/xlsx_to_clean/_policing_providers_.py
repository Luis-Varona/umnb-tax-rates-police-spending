# %%
import os
import sys

import polars as pl

sys.path.append(os.path.join((WD := os.path.dirname(__file__)),
                             '..',
                             '..',
                             '..'))
from modules.fastexcel_logging import suppress_fastexcel_logging


# %%
SOURCE_DIR = os.path.join(WD, '..', '..', 'data_xlsx')
DEST_DIR = os.path.join(WD, '..', '..', 'data_clean')


# %%
def main():
    source = os.path.join(SOURCE_DIR, 'GNB2024_pol_prov.xlsx')
    dest = os.path.join(DEST_DIR, 'GNB2024_pol_prov_clean.xlsx')
    os.makedirs(DEST_DIR, exist_ok=True)
    
    with suppress_fastexcel_logging():
        (clean_pol_prov_data(get_muni_map(read_provider_data(source)))
         .write_excel(dest, header_format={'bold': True}, autofit=True))


# %%
def read_provider_data(source: str) -> pl.DataFrame:
    return (pl.read_excel(source, columns=[0, 8])
            .filter(pl.nth(0).map_elements(len, pl.Int64) < 81)
            .with_columns(pl.nth(1)
                          .str.slice(0, 4)
                          .str.to_uppercase()
                          .str.replace(r"MUNI|BNPP|KVPF", "Municipal")))


# %%
def get_muni_map(provider_df: pl.DataFrame) -> dict[str, list[tuple]]:
    muni_iter = zip(*provider_df)
    curr_muni, curr_prov = next(muni_iter)
    muni_map: dict[str, list[tuple]] = {curr_muni: []}
    
    for muni, prov in muni_iter:
        if muni == "Florenceville-Bristol TV":
            muni_map[curr_muni].extend([(muni, curr_prov),
                                      ("Florenceville TV", curr_prov),
                                      ("Bristol TV", curr_prov)])
        elif muni == "Fundy Shores":
            curr_muni, curr_prov = muni, prov
            muni_map[curr_muni] = []
        elif curr_muni == "Fundy Shores" and muni != "Fundy-St. Martins":
            muni_map[curr_muni].append((muni, prov))
        elif muni == "Woodstock":
            curr_muni, curr_prov = muni, prov
            muni_map[curr_muni] = []
        elif curr_muni == "Woodstock":
            muni_map[curr_muni].append((muni, prov))
        elif prov is None:
            muni_map[curr_muni].append((muni, curr_prov))
        else:
            curr_muni, curr_prov = muni, prov
            muni_map[curr_muni] = []
    
    return muni_map


# %%
def clean_pol_prov_data(muni_map: dict[str, list[tuple]]) -> pl.DataFrame:
    municipalities = [muni for muni in muni_map for _ in muni_map[muni]]
    districts, providers = zip(*(token for value in muni_map.values()
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
    main()