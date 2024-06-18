# Obtiene las variables DNI y UVHI.

import os
import sys

import numpy as np
import pandas as pd

import xarray as xr

i = sys.argv[1]
internal = sys.argv[2]
name = sys.argv[3]

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
path_d = ( f"{internal}/grid/{name}_{i}.nc" )
path_r = ( f"{internal}/radiacion/{name}_{i}.nc" )

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
    # Coeficientes.
    ds["A"] = ( -5.743 + 21.77*ds["Kt"]
        - 27.49*ds["Kt"]**2 + 11.56*ds["Kt"]**3 )
    ds["A_1"] = ( 0.512 - 1.56*ds["Kt"]
        + 2.286*ds["Kt"]**2 - 2.222*ds["Kt"]**3 )
    ds["A"] = ds["A"].where( ds["Kt"] > 0.6, ds["A_1"] )
    ds = ds.drop_vars( "A_1" )
    ds["B"] = ( 41.4 - 118.5*ds["Kt"]
        + 66.05*ds["Kt"]**2 + 31.9*ds["Kt"]**3 )
    ds["B_1"] = 0.37 + 0.962*ds["Kt"]
    ds["B"] = ds["B"].where( ds["Kt"] > 0.6, ds["B_1"] )
    ds = ds.drop_vars( "B_1" )
    ds["C"] = ( -47.01 + 184.2*ds["Kt"]
        - 222*ds["Kt"]**2 + 73.81*ds["Kt"]**3 )
    ds["C_1"] = -0.28 + 0.932*ds["Kt"] - 2.048*ds["Kt"]**2
    ds["C"] = ds["C"].where( ds["Kt"] > 0.6, ds["C_1"] )
    ds = ds.drop_vars( "C_1" )
    # Delta Kn.
    ds["D_Kn"] = ds["A"] + ds["B"] * np.exp( ds["C"] * ds["Air_Mass"] )
    ds = ds.drop_vars( ["A", "B", "C"] )
    # Direct beam atmospheric transmittance under clear-sky conditions.
    ds["Knc"] = ( 0.866 - 0.122*ds["Air_Mass"] + 0.0121*ds["Air_Mass"]**2
        - 0.000653*ds["Air_Mass"]**3 + 0.000014*ds["Air_Mass"]**4 )
    # Radiación normal directa.
    ds["DNI"] = ds["I_tr"] * ( ds["Knc"] - ds["D_Kn"] )
    ds["DNI"] = ds["DNI"].where( ds["Kt"] > 0, 0
        ).where( ds["DNI"] > 0, 0 ).where( ds["GHI"] > 0, 0
        ).astype(np.float32).transpose(dims[0], dims[1], dims[2])
    ds = ds.drop_vars( ["Knc", "D_Kn", "I_tr"] )

    # UVHI (UVA + UVB) from GHI (Foyo-Moreno et al., 1998).
    ds["a"] = ( -0.851 + 0.433*np.exp(-(ds["Air_Mass"]-0.97)/1.85)
        +0.118*np.exp(-(ds["Air_Mass"]-0.97)/1.86) )
    ds["b"] = 0.610 + 0.271*np.exp(-(ds["Air_Mass"]-1.05)/1.62)
    ds["Kt"] = ds["Kt"].where( ds["Kt"] > 0, 0.00001 )
    ds["UVHI"] = ( ds["I_etr_uv"]
        * np.exp( ds["a"] + ds["b"]*np.log(ds["Kt"]) ) )
    ds["UVHI"] = ds["UVHI"].where( ds["Air_Mass"] > 0, 0
        ).where( ds["UVHI"] > 0, 0 ).where( ds["GHI"] > 0, 0
        ).astype(np.float32).transpose(dims[0], dims[1], dims[2])
    ds = ds.drop_vars( ["a", "b", "Kt", "I_etr_uv", "Air_Mass" ] )

    # Reordenamos el Dataset.
    ds["UVHI"] = ds["UVHI"].assign_attrs( units = "W m-2" )
    ds["DNI"] = ds["DNI"].assign_attrs( units = "W m-2" )

    # Guardamos el archivo.
    ds.to_netcdf(path_r, mode = "w" )