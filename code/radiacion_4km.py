# Obtiene las variables DNI.

import os
import sys

import numpy as np
import pandas as pd

import xarray as xr

i = sys.argv[1]
n = sys.argv[2]
internal = sys.argv[3]

# Funciones trigonométricas.
def sin(x): return np.sin(np.radians(x))
def cos(x): return np.cos(np.radians(x))
def asin(x): return np.arcsin(x) * 180/np.pi
def acos(x): return np.arccos(x) * 180/np.pi

dims = ["time", "lat", "lon"]

# Huso horario.
# La información está en UTC.
TZ = 0

# Cargamos el archivo.
path_d = ( f"{internal}/WRF_miroc_1985_2014_{n}km/grid/"
    + f"WRF_miroc_1985_2014_{n}km_{i}.nc" )
path_r = ( f"{internal}/WRF_miroc_1985_2014_{n}km/radiacion/"
    + f"WRF_miroc_1985_2014_{n}km_{i}.nc" )

# Iteramos para todos los archivos.
    
with xr.open_dataset(path_d) as ds:
    
    # Eccentric anomaly of the earth in its orbit around the sun.
    ds["Day_Angle"] = 6.283185 * ( ds[dims[0]].dt.dayofyear - 1 ) / 365
    # Declinación.
    ds["Declination"] = ( ( 0.006918 - 0.399912 * np.cos(ds["Day_Angle"])
        + 0.070257*np.sin(ds["Day_Angle"])
        - 0.006758*np.cos(2*ds["Day_Angle"])
        + 0.000907*np.sin(2*ds["Day_Angle"])
        - 0.002697*np.cos(3*ds["Day_Angle"])
        + 0.00148*np.sin(3*ds["Day_Angle"]) ) * 180/np.pi )
    # Ecuación del tiempo.
    ds["Time_Equation"] = ( ( 0.000075 + 0.001868*np.cos(ds["Day_Angle"])
        - 0.032077*np.sin(ds["Day_Angle"])
        - 0.014615*np.cos(2*ds["Day_Angle"])
        -0.040849*np.sin(2*ds["Day_Angle"])) * 229.18 )
    # Longitud del punto subsolar.
    ds["lon_subs"] = -15 * ( ds[dims[0]].dt.hour - TZ
        + ds["Time_Equation"]/60 )
    # Ángulo horario.
    ds["Hour_Angle"] = ( 15 * ( ds[dims[0]].dt.hour - 12
        - 0.5 + ds["Time_Equation"]/60 + ((ds[dims[2]]-TZ*15)*4)/60 ) )
    ds = ds.drop_vars( "Time_Equation" )
    # Posiciones del analema solar.
    ds["Sz"] = ( sin(ds[dims[1]])*sin(ds["Declination"])
        - cos(ds[dims[1]])*cos(ds["Declination"])
        *cos(ds["lon_subs"]-ds[dims[2]]) )
    ds = ds.drop_vars( "lon_subs" )
    # Ángulo del cénit solar.
    ds["Zenith_Angle"] = acos(ds["Sz"])
    ds = ds.drop_vars( "Sz" )
    ds = ds.drop_vars( ["Declination", "Hour_Angle"] )
    # Masa de aire.
    ds["Air_Mass"] = ( 1/(cos(ds["Zenith_Angle"])
        + 0.15/(93.885 - ds["Zenith_Angle"])**1.253 )
        * ds["Pressure"]/101325 )
    ds["Air_Mass"] = ds["Air_Mass"].where( ds["Zenith_Angle"] < 85.5, 0 )
    # Extraterrestrial radiation factor.
    ds["F_etr"] = ( cos(ds["Zenith_Angle"]) * 
        ( 1.00011 + 0.034221*np.cos(ds["Day_Angle"])
        + 0.00128*np.sin(ds["Day_Angle"])
        + 0.000719*np.cos(2*ds["Day_Angle"])
        + 0.000077*np.sin(2*ds["Day_Angle"]) ) )
    # Extraterrestrial radiation.
    I_cs   = 1367 # W m-2.
    I_uvcs = 78   # W m-2. 
    ds["I_tr"    ] = I_cs   * ds["F_etr"]
    ds["I_etr_uv"] = I_uvcs * ds["F_etr"]
    ds = ds.drop_vars( ["Day_Angle", "F_etr", "Zenith_Angle"] )

    # NREL DISC Model: DNI from GHI (Maxwell, 1987).
    # Effective global horizontal transmittance.
    ds["Kt"] = ds["GHI"] / ds["I_tr"]
    ds["Kt"] = ds["Kt"].where( ds["Kt"] < 1, 1 )
    ds["Kt"] = ds["Kt"].where( ds["Air_Mass"] > 0, 0 )
    ds = ds.drop_vars( [ "I_tr" ] )

    # UVHI (UVA + UVB) from GHI (Foyo-Moreno et al., 1998).
    ds["a"] = ( -0.851 + 0.433*np.exp(-(ds["Air_Mass"]-0.97)/1.85)
        +0.118*np.exp(-(ds["Air_Mass"]-0.97)/1.86) )
    ds["b"] = 0.610 + 0.271*np.exp(-(ds["Air_Mass"]-1.05)/1.62)
    ds["Kt"] = ds["Kt"].where( ds["Kt"] > 0, 0.00001 )
    ds["UVHI"] = ( ds["I_etr_uv"]
        * np.exp( ds["a"] + ds["b"]*np.log(ds["Kt"]) ) )
    ds["UVHI"] = ds["UVHI"].where( ds["Air_Mass"] > 0, 0
        ).astype(np.float32).transpose(dims[0], dims[1], dims[2])
    ds = ds.drop_vars( ["a", "b", "Kt", "I_etr_uv", "Air_Mass" ] )

    # Reordenamos el Dataset.
    ds["UVHI"] = ds["UVHI"].assign_attrs( units = "W m-2" )

    # Guardamos el archivo.
    ds.to_netcdf(path_r, mode = "w" )