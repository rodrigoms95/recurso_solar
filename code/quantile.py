# Corrección de cuantiles empírica.

import os
import sys

import pandas as pd
import numpy  as np

import xarray as xr

# Rutas de archivos.

names = [ sys.argv[1], sys.argv[2] ]
lat   = sys.argv[3]
lon   = sys.argv[4]

#df_d = xr.open_dataset(f"results/{names[0]}.nc").sel(
#    {"lat": lat, "lon": lon} ).to_dataframe().reset_index(
#    ).drop( ["lat", "lon"], axis = 1 ).set_index("time")

path_temp = "temp/NetCDF/"
path_d = [ f"{path_temp}{names[0]}_{lat}_{lon}.nc",
    f"{path_temp}{names[1]}_{lat}_{lon}.nc" ]
path_r = f"{path_temp}{names[1]}_{lat}_{lon}_quantile.nc"

df_d = xr.open_dataset( f"{path_d[0]}" ).to_dataframe(
    ).reset_index().drop( ["lon", "lat"], axis = 1 ).set_index("time")
df_r = xr.open_dataset( f"{path_d[1]}" ).to_dataframe(
    ).reset_index().drop( ["lon", "lat"], axis = 1 ).set_index("time")

# Creamos un DataFrame de apoyo.
df_q = df_r.copy()
# Iteramos para todas las columnas.
for v in df_d.columns:
    # Ordenamos los valores originales y destino incluyendo el tiempo.
    if v in ["DNI", "GHI"]:
        df_i = df_d[[v]].where( df_d[[v]] > 0, np.nan
            ).dropna().sort_values(v).reset_index()
        df_j = df_r[[v]].where( df_r[[v]] > 0, np.nan
            ).dropna().sort_values(v).reset_index()
    else:
        df_i = df_d[[v]].sort_values(v).reset_index()
        df_j = df_r[[v]].sort_values(v).reset_index()
    # Calculamos la distribución acumulada.
    df_i["CDF"] = np.linspace( 1 / df_i.shape[0] , 1, df_i.shape[0] )
    df_j["CDF"] = np.linspace( 1 / df_j.shape[0] , 1, df_j.shape[0] )

    # Interpolamos los valores de la distribución origen a la destino.
    df_j["Quant"] = np.interp( df_j["CDF"], df_i["CDF"],
        df_i[v] ).round( decimals = 2 )
    # Reordenamos los valores.
    df_q[v] = df_j.sort_values("time").set_index("time").drop( [v, "CDF"],
        axis = 1 ).rename( {"Quant": v}, axis = 1 )
    
df_q["DNI"] = df_q["DNI"].where( df_q["DNI"] > 0, 0 )
df_q["GHI"] = df_q["GHI"].where( df_q["GHI"] > 0, 0 )

# Convertimos a Dataset.
df_q = df_q.reset_index()
df_q["lat" ] = float(lat)
df_q["lon"] = float(lon)
ds = df_q.set_index( ["time", "lat", "lon"]
    ).astype( float ).round( decimals = 2 ).to_xarray()
ds["lat"] = ds["lat"].assign_attrs( standard_name = "latitude",
    long_name = "Latitude", units = "degrees" )
ds["lon"] = ds["lon"].assign_attrs(standard_name = "longitude",
    long_name = "Longitude", units = "degrees" )
ds["time"] = pd.date_range( "01/01/2006 00:00:00",
    "31/12/2022 23:00:00", freq = "H" )
ds.to_netcdf(path_r)