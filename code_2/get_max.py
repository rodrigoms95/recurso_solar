# Obtiene los valores máximos diarios
import os
import sys
import xarray         as xr
import numpy          as np
import pandas         as pd

# Cargamos datos.
scn   = sys.argv[1]
#dir_o = "/home/rodr/buffalo/rodr/WRF/"
dir_o = "/datos/rodr/Datos/WRF_data/"
dir_d = f"{dir_o}{scn}/PV/"
dir_r = f"{dir_o}{scn}/max/"
if not os.path.exists(dir_r): os.mkdir(dir_r)
files = os.listdir(dir_d)
files.sort()

print("Calculando máximos")
for f in files:
    print(f"{f}               ", end = "\r")
    if not os.path.exists(dir_r + f):
        ds = xr.open_dataset(dir_d + f)
        ds["P_mp"] = (ds["P_mp"].astype(np.float64)
            + np.random.randn(*ds["P_mp"].shape) / 1e5)
        var = "P_mp"
        # Generación máxima diaria
        df = ds.resample({"XTIME": "D"}).max().to_dataframe()
        df_2 = ds.to_dataframe()
        # Hora de generación pico
        df_2["hour"] = df_2.index.get_level_values("XTIME").hour.astype(int)
        df_2 = df_2.reset_index()
        df_2["XTIME"] = df_2["XTIME"].dt.date
        df_2 = df_2.set_index(["XTIME", "south_north", "west_east"])
        df["hour"] = df_2[df_2[var].isin(df[var])]["hour"]
        # Pocentaje de generación matutina
        df["perc_morning"] = (
            ds.shift({"XTIME": -7}).resample({"XTIME": "12h"}).sum()
            / ds.shift({"XTIME": -1}).resample({"XTIME": "D"}).sum(
            ).resample({"XTIME": "12h"}).ffill()).resample({"XTIME": "D"}
            ).first().to_dataframe().sort_index()[var].values
        # Guardamos el archivo
        df.to_xarray().set_coords(["XLONG", "XLAT"]
            ).drop_vars(["south_north", "west_east"]
            ).astype(np.float32).to_netcdf(dir_r + f)
print()
print()
