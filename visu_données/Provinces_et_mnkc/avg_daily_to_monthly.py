import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sys


## On calcule les moyennes mensuelles des données journalières


root = Path("/sortref/system/rea/glo_bgc/microrys12/microrys3/GLOBAL_MULTIYEAR_BGC_001_033/cmems_mod_glo_bgc_my_0.083deg-lmtl_P1D-i")
output = Path("/data/rd_exchange/asauvebois/moy_month")
output.mkdir(parents=True, exist_ok=True)



for year_dir in sorted(root.iterdir()):
    if not year_dir.is_dir():
        continue

    #if int(year_dir.name) > 2000:  # ← stop après 2000
        #continue

    print(f"\nAnnée : {year_dir.name}")
    
    for month_dir in sorted(year_dir.iterdir()):
        if not month_dir.is_dir():
            continue
        print(f"   Mois : {month_dir.name}")
        
        outfile = output/ f"{year_dir.name}_{month_dir.name}_monthly_mean.nc" 
        
        if outfile.exists():
        # Vérifier que le fichier n'est pas vide
            ds_check = xr.open_dataset(outfile)
            total = ds_check['mnkc_epi'].size
            nans = int(ds_check['mnkc_epi'].isnull().sum().values)
            ds_check.close()
        
            if nans == total:  # fichier vide → on le recrée
                print(f"   → fichier vide, on recrée")
                outfile.unlink()  # supprime le fichier
            else:
                print(f"   → déjà traité, on passe")
                continue
        
        files = sorted(month_dir.glob("*.nc"))
        if len(files) == 0:
                continue
            
        ds = xr.open_mfdataset(
                files,
                combine="by_coords",
                chunks={} 
            )
        monthly_mean = ds.mean(dim="time", skipna=True).compute()
        monthly_mean.to_netcdf(outfile)
        ds.close()