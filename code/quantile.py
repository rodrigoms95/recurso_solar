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
path_r = [ f"{path_temp}{names[1]}_{lat}_{lon}_{x}.nc"
    for x in ["mapped", "quantiles"] ]

df_d = xr.open_dataset( f"{path_d[0]}" ).to_dataframe(
    ).reset_index().drop( ["lon", "lat"], axis = 1 ).set_index("time")
df_r = xr.open_dataset( f"{path_d[1]}" ).to_dataframe(
    ).reset_index().drop( ["lon", "lat"], axis = 1 ).set_index("time")

# Creamos DataFrames de apoyo.
df_m = df_r.copy()
df_q = pd.DataFrame( index = np.linspace( 1/df_r.shape[0], 1, df_r.shape[0] ),
    columns = df_r.columns )
df_q = df_q.rename_axis("CDF", axis = 0)
df = [df_m, df_q]

# Inicializamos las variables como 0.
df_m[ ["GHI", "DNI"] ] = 0

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
    df_i["CDF"] = np.linspace( 1/df_i.shape[0], 1, df_i.shape[0] )
    df_j["CDF"] = np.linspace( 1/df_j.shape[0], 1, df_j.shape[0] )

    # Interpolamos los valores de la distribución origen a la destino.
    df_j["Map"] = np.interp( df_j["CDF"], df_i["CDF"],
        df_i[v] ).round( decimals = 2 )
    df_j["quantile"] =  df_j["Map"] - df_j[v]
    df_j = df_j.set_index("time").sort_index()
    # Reordenamos los valores.
    df_m.loc[ df_j.index, v ] = df_j["Map"]
    # Guardamos el mapeo de cuantiles para la corrida futura.
    df_j = df_j.set_index("CDF").sort_index()
    if v in ["DNI", "GHI"]:
          q = np.interp( df_q.index, df_j.index, df_j["quantile"].values )
    else: q = df_j["quantile"].values
    df_q[v] = q
    
# Nos aseguramos que los datos estén dentro de su rango.
df_m["Relative Humidity"] = df_m["Relative Humidity"].where(
    df_m["Relative Humidity"] > 0, 0 )
df_m["Relative Humidity"] = df_m["Relative Humidity"].where(
    df_m["Relative Humidity"] < 100, 100 )
df_m["Wind Direction"] = df_m["Wind Direction"].where(
    df_m["Wind Direction"] < 360, df_m["Wind Direction"] - 360 )
df_m["Wind Speed"] = df_m["Wind Speed"].where( df_m["Wind Speed"] > 0 , 0 )
df_m["GHI"] = df_m["GHI"].where( df_m["GHI"] > 0 , 0 )
df_m["DNI"] = df_m["DNI"].where( df_m["DNI"] > 0 , 0 )

# Convertimos a Dataset.
var = ["time", "CDF"]
for i in range(len(df)):
    df[i]["lat"] = float(lat)
    df[i]["lon"] = float(lon)
    ds = df[i].reset_index().set_index( [var[i], "lat", "lon"]
        ).astype( float ).round( decimals = 2 ).to_xarray()
    ds["lat"] = ds["lat"].assign_attrs( standard_name = "latitude",
        long_name = "Latitude", units = "degrees" )
    ds["lon"] = ds["lon"].assign_attrs(standard_name = "longitude",
        long_name = "Longitude", units = "degrees" )
    ds["time"] = pd.date_range( "01/01/2006 00:00:00",
        "31/12/2022 23:00:00", freq = "H" )
    ds.to_netcdf( path_r[i] )