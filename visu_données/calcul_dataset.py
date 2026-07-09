import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sys



provinces_folder = Path("/data/rd_exchange/asauvebois/dataset_biome") # est-ce que je le mets dans la boucle ou est-ce que je crée des dossiers avec l'ajout du biome ?
micronekton_folder = Path("/data/rd_exchange/asauvebois/moy_month")

variables_mnkc= ["mnkc_epi", "mnkc_umeso", "mnkc_lmeso", "mnkc_mumeso", "mnkc_mlmeso", "mnkc_hmlmeso"]


rows = []

for mnkc_file in sorted(micronekton_folder.glob("*_monthly_mean.nc")):

#on va extraire l'année et le mois depuis le nom du fichier
    year_str = mnkc_file.stem.split("_")[0]
    month_str = mnkc_file.stem.split("_")[1]
    print(f"\nTraitement {year_str}-{month_str}...")


#Fichier province correspondant

    prov_file = provinces_folder/f"provinces_Y{year_str}_M{month_str}.nc"

    if not prov_file.exists():
        print(f"   → Province manquante, on passe")
        continue

#on charge les deux datasets

    ds_mnkc = xr.open_dataset(mnkc_file)
    ds_prov = xr.open_dataset(prov_file)
    
    provinces = ds_prov["province"].values
    prov_list = list(set(provinces.flatten()))

#on boucle sur les provinces 
    prov_list = [p for p in set(provinces.flatten()) if not np.isnan(p)]

    for prov_id in prov_list:
        mask = (provinces == prov_id) #true si on est dans cette province
        biome_values = ds_prov["Biome"].values[mask]
        if len(biome_values) == 0:
            continue
        biome_id = ds_prov["Biome"].values[mask][0] #on prend toutes les valeurs de biome où le masque est true, et on prend la première car toutes les cases d'une même province ont le même biome
       
        row = {
            "date": f"{year_str}-{month_str}",
            "prov": prov_id,
            "Biome": biome_id
        }

#Puis on fait la moyenne spatiale de chaque variable sur la province

        for var in variables_mnkc:
            valeur = ds_mnkc[var].where(mask).mean().values
            row[var] = float(valeur)

        rows.append(row)


    ds_mnkc.close()
    ds_prov.close()


#création du Dataset
df_new = pd.DataFrame(rows)
df_new = df.set_index('date')
print(df_new)


df_new.to_csv("/data/rd_exchange/asauvebois/df_micronekton_.csv")