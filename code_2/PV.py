import xarray as xr
import pandas as pd
import numpy as np
from dask.diagnostics import ProgressBar

# Funciones trigonométricas.
def sin(x) : return np.sin(np.radians(x))
def cos(x) : return np.cos(np.radians(x))
def tan(x) : return np.tan(np.radians(x))
def asin(x): return np.arcsin(x) * 180/np.pi
def acos(x): return np.arccos(x) * 180/np.pi
def atan(x): return np.arctan(x) * 180/np.pi

print("Plane of Array Irradiance")

# Casos a estudiar
cases = [ "south_no_track", "west_no_track", "east_no_track",
    "1_track", "2_track", "bifacial_vertical_west_main",
    "bifacial_vertical_east_main", "bifacial_vertical_west_back",
    "bifacial_vertical_east_back", "bifacial_south_back" 
    ]
# Variables fotovoltaicas por caso
# Inclinación
track_tilt       =   [ f"{x}_Tilt"               for x in cases ]
# Azimuth
track_azimuth    =   [ f"{x}_Azimuth"            for x in cases ]
# Ángulo entre el panel y el sol, Angle of Incidence
track_AOI        =   [ f"{x}_Angle_of_Incidence" for x in cases ]
# Radiación incidente en el panel [W/m^2], Plane of Array Irradiace
track_POA        =   [ f"{x}_POA"                for x in cases ]
# Producción fotovoltaica por kilowatt de capacidad [W/kWp]
track_P_mp       = ( [ f"{x}_P_mp"               for x in cases ]
    + [ "bifacial_vertical_west_P_mp",
        "bifacial_vertical_east_P_mp",
        "bifacial_south_P_mp" ] )
# Producción para cada caso
prod_n           = track_P_mp[0:5] + track_P_mp[10:]
# Factor bifacial
P_bf = [ 1, 1, 1, 1, 1, 1, 1, 0.7, 0.7, 0.7 ]

dir_r = "/datos/rodr/temp/recurso_solar/duck_curve/"
ds_1 = xr.open_dataset(f"{dir_r}full_disc_climate_2022.nc",
   ).sortby("points").chunk({"points": 20000})
print(list(ds_1.keys()))
ds_2 = xr.open_dataset(f"{dir_r}full_disc_POA_2022.nc",
   ).sortby("points").chunk({"points": 20000})
ds_3 = xr.open_dataset(f"{dir_r}full_disc_irradiance_2022.nc",
   ).sortby("points")["ghi"].chunk({"points": 20000})
ds = xr.merge([ds_1, ds_2, ds_3])

# NOCT Cell Temperature Model
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
# greater than 3.5 in, or ground/rack mounted
#T_adj = 2  + T_NOCT # 2.5 to 3.5 in
#T_adj = 6  + T_NOCT # 1.5 to 2.5 in
#T_adj = 11 + T_NOCT # 0.5 to 1.5 in
#T_adj = 18 + T_NOCT # less than 0.5 in
# Iteramos para cada caso
ds["_Cell_Temperature"] = ( (T_adj-20) / 800 * (1-eff_ref/tau_alpha)
    * (9.5/(5.7+3.8*v*ds["wind_speed"])) ).astype(np.float32)
ds = ds.drop_vars("wind_speed")
for i in range(len(cases)):
    # Temperatura de la celda
    ds[cases[i]+"_Cell_Temperature"] = ( ds["air_temperature"]
        + ds[track_POA[i]] * ds["_Cell_Temperature"] ).astype(np.float32)
ds = ds.drop_vars(["air_temperature", "_Cell_Temperature"])

# Simple efficiency module model
# Eficiencia por temperatura
eff_T = -0.34
# Pérdidas del sistema
eff_n = [ "Soiling", "Shading", "Snow", "Mismatch",
    "Wiring", "Connections", "Light_Induced_Degradation",
    "Nameplate_Rating", "Age", "Availability" ]
eff = np.array( [0.98, 0.97, 1, 0.98, 0.98,
    0.995, 0.985, 0.99, 1, 0.97] ).prod()
# Eficiencia del inversor
eff_inv = 0.96
# Eficiencia del sistema
eff_sys = eff_ref * eff_inv * eff
# DC to AC Size Ratio
DC_AC = 1.1
# Inverter size
inv_P = I_mp * V_mp / DC_AC

# Iteramos para cada caso
for i in range(len(cases)):
    # Potencia generada en AC
    ds[track_P_mp[i]] = (P_bf[i] * ds[track_POA[i]]*eff_sys*A_m *
        ( 1 + eff_T/100 * (ds[cases[i]+"_Cell_Temperature"]-25) )
        ).astype(np.float32)
    ds[track_P_mp[i]] = (ds[track_P_mp[i]
        ].where(ds[track_P_mp[i]]<inv_P, inv_P)
        / (I_mp*V_mp)).where(ds["ghi"]>0, 0).astype(np.float32)
    # El resultado es la generación por cada kWp.
    ds = ds.drop_vars([cases[i]+"_Cell_Temperature", track_POA[i]])
ds = ds.drop_vars("ghi")

# Calculamos la producción bifacial total
ds[track_P_mp[10]] = (ds[track_P_mp[5]] + ds[track_P_mp[7]]).astype(np.float32)
ds[track_P_mp[11]] = (ds[track_P_mp[6]] + ds[track_P_mp[8]]).astype(np.float32)
ds[track_P_mp[12]] = (ds[track_P_mp[0]] + ds[track_P_mp[9]]).astype(np.float32)
ds = ds.drop_vars(track_P_mp[5:10])

delayed_obj = ds.to_netcdf(f"{dir_r}full_disc_PV_2022.nc", compute = False)
with ProgressBar(): results = delayed_obj.compute()
