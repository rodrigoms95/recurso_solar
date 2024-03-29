# Modifica las variables de WRF para poder hacer el mapeo de cuantiles.

import numpy as np
import pandas as pd

import xarray as xr
import os

# Cargamos el archivo.
path_d = "data/WRF_miroc_1985_2014/"
path_r = "temp/quantile_prep/"
path_v = "temp/quantile_vars/"

files = os.listdir(path_d)
if ".DS_Store" in files: files.remove(".DS_Store")
f = files[0]

with xr.open_dataset( path_d + f ) as ds:

    # Creamos las variables.
    ds["Wind_Speed"] = np.sqrt( np.square(ds["U10"])
        + np.square(ds["V10"]) ).astype(np.float32)
    ds["Wind_Direction"] = ( np.arctan2(ds["V10"], ds["U10"])
        * 180/np.pi - 90 )
    ds["Wind_Direction"] = ds["Wind_Direction"].where(
        ds["Wind_Direction"] > 0, ds["Wind_Direction"] + 360
        ).astype(np.float32)
    ds = ds.drop_vars( ["U10", "V10"] )
    ds["T_C"] = ds["T2"] - 273.15
    ds["Pvs"] = 611.21*np.exp( ( 18.678 - ds["T_C"]/234.5 )
        * ( ds["T_C"]/(257.14+ds["T_C"]) ) )
    ds = ds.drop_vars( "T_C" )
    ds["Q2"] = ds["Q2"].where( ds["Q2"] > 0.0001, 0.0001 )
    ds["Relative_Humidity"] = ( 100 * ds["Q2"] * 461.4/286.9
        * ( ds["PSFC"]/ds["Pvs"] - 1 ) )
    ds["Relative_Humidity"] = ds["Relative_Humidity"].where(
        ds["Relative_Humidity"] < 100, 100 ).astype(np.float32)
    ds = ds.drop_vars( ["Q2", "Pvs"] )

    # Reordenamos el Dataset.
    ds["Wind_Speed"] = ds["Wind_Speed"].assign_attrs( units = "m/s" )
    ds["Relative_Humidity"] = ds[ "Relative_Humidity"
        ].assign_attrs( units = "%" )
    ds["Wind_Direction"] = ds ["Wind_Direction"
        ].assign_attrs( units = "degrees" )
    ds = ds.rename_vars( { "T2": "Temperature",
        "PSFC": "Pressure", "SWDOWN": "GHI" } )

    # Guardamos el archivo.
    ds.to_netcdf( path_r + f, mode = "w" )

    # Guardamos las variables individuales.
    vars = ["Temperature", "Pressure", "Relative_Humidity",
        "Wind_Speed", "Wind_Direction", "GHI"]
    for v in vars:
        ds[[v]].to_netcdf( path_v + v + "/" + f, mode = "w" )