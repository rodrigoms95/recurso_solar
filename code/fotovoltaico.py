# Obtiene las variables DNI, UVHI, y P_mp.

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
path_d = ( f"{internal}/{name}/qgrid/{name}_{i}.nc" )
path_r = ( f"{internal}/{name}/fotovoltaico/{name}_{i}.nc" )

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
    #ds["Sx"] = cos(ds["Declination"])*cos(ds["lon_subs"]-ds["lon"])
    #ds["Sy"] = ( cos(ds["lat"])*sin(ds["Declination"])
    #    - sin(ds["lat"])*cos(ds["Declination"])
    #    *cos(ds["lon_subs"]-ds["lon"]) )
    ds["Sz"] = ( sin(ds[dims[1]])*sin(ds["Declination"])
        - cos(ds[dims[1]])*cos(ds["Declination"])
        *cos(ds["lon_subs"]-ds[dims[2]]) )
    ds = ds.drop_vars( "lon_subs" )
    # Ángulo del cénit solar.
    ds["Zenith_Angle"] = acos(ds["Sz"])
    ds = ds.drop_vars( "Sz" )
    # Ángulo acimutal solar.
    ds["Azimuth_Angle"] = acos( ( sin(ds["Declination"])
        - cos(ds["Zenith_Angle"])*sin(ds[dims[1]]) )
    / ( sin(ds["Zenith_Angle"])*cos(ds[dims[1]]) ) )
    ds["Azimuth_Angle"] = ds["Azimuth_Angle"].where(
        ds["Hour_Angle"] < 0, 360 - ds["Azimuth_Angle"] )
    ds = ds.drop_vars( ["Declination", "Hour_Angle"] )
    # Masa de aire.
    ds["Air_Mass"] = ( 1/(cos(ds["Zenith_Angle"])
        + 0.15/(93.885 - ds["Zenith_Angle"])**1.253 )
        * ds["Pressure"]/101325 )
    ds["Air_Mass"] = ds["Air_Mass"].where( ds["Zenith_Angle"] < 85.5, 0 )
    # Extraterrestrial radiation factor.
    # Extraterrestrial radiation.
    ds = ds.drop_vars( ["Day_Angle"] )

    # Modelo de Pérez de Cielo Difuso.
    azimuth_A = 180
    # Ángulo entre el panel y el sol.
    ds["Angle_of_Incidence"] = acos(
        cos(ds["Zenith_Angle"])*cos(ds[dims[1]])
        + sin(ds["Zenith_Angle"])*sin(ds[dims[1]])
        *cos(ds["Azimuth_Angle"]-azimuth_A) )
    #ds = ds.drop_vars( "Azimuth_Angle" )
    # Diffuse Horizontal Radiation.
    ds["DHI"] = ds["GHI"] - ds["DNI"] * cos(ds["Zenith_Angle"])
    ds["DHI"] = ds["DHI"].where(ds["DHI"]>0, 0.001)
    K = 5.535e-6
    # Perez clearness bins.
    ds["bins"] = 0
    ds["bins"] = ds["bins"].where( ds["DHI"] == 0.001,
        ( (ds["DHI"]+ds["DNI"])/ds["DHI"] + K*ds["Zenith_Angle"]**3 )
        / ( 1 + K*ds["Zenith_Angle"]**3 ) )
    ds["DHI"] = ds["DHI"].where(ds["DHI"]>0.001, 0)
    ds["epsilon"] = ds["bins"   ].where( ds["bins"] < 6.200, 8 )
    ds["epsilon"] = ds["epsilon"].where( 
        ~( (ds["bins"]>4.500) & (ds["bins"]<6.200) ), 7 )
    ds["epsilon"] = ds["epsilon"].where( 
        ~( (ds["bins"]>2.600) & (ds["bins"]<4.500) ), 6 )
    ds["epsilon"] = ds["epsilon"].where( 
        ~( (ds["bins"]>1.950) & (ds["bins"]<2.600) ), 5 )
    ds["epsilon"] = ds["epsilon"].where( 
        ~( (ds["bins"]>1.500) & (ds["bins"]<1.950) ), 4 )
    ds["epsilon"] = ds["epsilon"].where( 
        ~( (ds["bins"]>1.230) & (ds["bins"]<1.500) ), 3 )
    ds["epsilon"] = ds["epsilon"].where( 
        ~( (ds["bins"]>1.065) & (ds["bins"]<1.500) ), 2 )
    ds["epsilon"] = ds["epsilon"].where( ds["bins"] > 1.065, 1 )
    Perez = pd.read_csv("code/Perez.csv", index_col = "bin" )
    ds = ds.drop_vars( "bins" )
    # Extraterrestrial radiation.
    Ea = 1367
    # Coeficientes.
    ds["Delta"] = ds["DHI"] * ds["Air_Mass"] / Ea
    ds = ds.drop_vars( "Air_Mass" )
    for i in Perez.index:
        for j in Perez.columns:
            ds[j] = ds["epsilon"].where(
                ~(ds["epsilon"] == i), Perez.loc[i, j] )
    ds = ds.drop_vars( "epsilon" )
    ds["F1"] = ( ds["f11"] + ds["f12"]*ds["Delta"]
        + np.radians(ds["Zenith_Angle"])*ds["f13"] )
    ds = ds.drop_vars( ["f11", "f12", "f13"] )
    ds["F1"] = ds["F1"].where( ds["F1"] > 0, 0 )
    #ds["F1"] = ds["F1"].where( ds["Zenith_Angle"] > 0, 0 )
    ds["F2"] = ( ds["f21"] + ds["f22"]*ds["Delta"]
        + np.radians(ds["Zenith_Angle"])*ds["f23"] )
    ds = ds.drop_vars( ["f21", "f22", "f23", "Delta"])#, "Zenith_Angle"] )
    ds["a"] = cos(ds["Angle_of_Incidence"])
    ds["a"] = ds["a"].where( ds["a"] > 0, 0 )
    #ds["b"] = cos(ds["Angle_of_Incidence"])
    ds["b"] = cos(ds["Zenith_Angle"])
    ds["b"] = ds["b"].where( ds["b"] > cos(85), cos(85) )
    #ds["b"] = ds["b"].where( ds["b"] > 0, cos(85) )
    # Radiación difusa.
    ds["I_d"] = ( ds["DHI"] * ( (1-ds["F1"]) * ((1+cos(ds[dims[1]]))/2)
        + ds["F1"]*ds["a"]/ds["b"] + ds["F2"]*sin(ds[dims[1]]) ) )
    ds = ds.drop_vars( ["F1", "F2", "a", "b"])#, "DHI"] )
    # Radiación directa.
    ds["I_b"] = ds["DNI"] * cos(ds["Angle_of_Incidence"])
    ds["I_b"] = ds["I_b"].where( ds["Angle_of_Incidence"] >= 90, 0 )
    #ds = ds.drop_vars( "Angle_of_Incidence" )
    # Radiación total en el panel.
    ds["POA"] = ds["I_b"] + ds["I_d"]
    #ds = ds.drop_vars( ["I_b", "I_d"] )

    # NOCT Cell Temperature Model.
    T_NOCT    = 44 # °C
    # Datos de Panel Canadian Solar 550 W
    # Modelo: HiKu6 Mono PERC CS6W-550
    I_mp      = 13.2 # A
    V_mp      = 41.7 # V
    A_m       = 1.134*2.278 # m^2
    eff_ref   = I_mp * V_mp / (1000 * A_m)
    tau_alpha = 0.9
    # Ajuste de viento.
    #v = 0.61 # Dos pisos.
    v = 0.51 # Un piso.
    # Ajuste de montaje.
    T_adj = 2   + T_NOCT # Building integrated,
    # greater than 3.5 in, or groud/rack mounted
    #T_adj = 2  + T_NOCT # 2.5 to 3.5 in
    #T_adj = 6  + T_NOCT # 1.5 to 2.5 in
    #T_adj = 11 + T_NOCT # 0.5 to 1.5 in
    #T_adj = 18 + T_NOCT # less than 0.5 in
    # Temperatura de la celda.
    ds["Cell_Temperature"] = ( ds["Temperature"]
        + ds["POA"] / 800 * (T_adj-20)
        * (1-eff_ref/tau_alpha) * ( 9.5 / (5.7+3.8*v*ds["Wind Speed"]) ) )

    # Simple efficiency module model.
    # Eficiencia por temperatura.
    eff_T = -0.34
    # Pérdidas del sistema.
    eff_n = [ "Soiling", "Shading", "Snow", "Mismatch",
        "Wiring", "Connections", "Light_Induced_Degradation",
        "Nameplate_Rating", "Age", "Availability" ]
    eff = np.array( [0.98, 0.97, 1, 0.98, 0.98,
        0.995, 0.985, 0.99, 1, 0.97] ).prod()
    # Eficiencia del inversor.
    eff_inv = 0.96
    # Eficiencia del sistema.
    eff_sys = eff_ref * eff_inv * eff
    # DC to AC Size Ratio.
    DC_AC = 1.2
    # Inverter size.
    inv_P = I_mp * V_mp / DC_AC
    # Potencia generada en AC.
    ds["P_mp"] = ( ds["POA"]*eff_sys*A_m *
        ( 1 + eff_T/100 * (ds["Cell_Temperature"]-25) ) )
    ds["P_mp"] = ds["P_mp"].where( ds["P_mp"] < inv_P, inv_P
        ).astype(np.float32).transpose(dims[0], dims[1], dims[2])
    # El resultando es la generación por cada kWp.
    ds["P_mp"] = ds["P_mp"] * 1000 / ( I_mp * V_mp )
    ds = ds.drop_vars( ["Cell_Temperature"])#, "POA"] )

    # Reordenamos el Dataset.
    ds["P_mp"] = ds["P_mp"].assign_attrs( units = "W" )

    # Guardamos el archivo.
    ds.to_netcdf(path_r, mode = "w" )