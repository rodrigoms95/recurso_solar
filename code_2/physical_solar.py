# Calcula los elementos físicos de la radiación solar que dependen de la
# ubicación y del tiempo.

import pandas as pd
import numpy as np
import xarray as xr

# Funciones trigonométricas.
def sin(x) : return np.sin(np.radians(x))
def cos(x) : return np.cos(np.radians(x))
def tan(x) : return np.tan(np.radians(x))
def asin(x): return np.arcsin(x) * 180/np.pi
def acos(x): return np.arccos(x) * 180/np.pi
def atan(x): return np.arctan(x) * 180/np.pi

print("Calculando elementos físicos solares")
print()

# Cargamos datos.
print("Cargando tabla de puntos")
dir_d = "/home/rodr/temp/recurso_solar/duck_curve/"
points = pd.read_csv(f"{dir_d}/conus_points.csv", index_col = 0)
points = points[points["REGION"].notnull()]
points["REGION"] = points["REGION"].astype(np.int16)
print("Creando xarray Dataset")
ds = points[["latitude", "longitude", "elevation", "timezone", "REGION",
    "potential_solar_park_zones", "built_surface"]
    ].to_xarray().rename({"index": "points"})
ds["time"] = pd.date_range("2022-01-01", "2023-01-01", freq = "1h")[:-1]
ds = ds.chunk(time = 24)
print("Calculando presión")
ds["Pressure"] = (1013.25 * (1 - 0.0065/288.15*ds["elevation"]) ** 5.25588
    ).astype(np.float32)
ds = ds.drop_vars("elevation")

# Convertimos a fecha.
print()
print("Calculando posición solar")
print("Calculando día y hora")
ds["hour"] = (ds["time"].dt.hour + ds["time"].dt.minute/60).astype(
    np.float32).chunk(time = 24).compute()
ds["dayofyear"] = ds["time"].dt.dayofyear.astype(
    np.int16).chunk(time = 24).compute()
TZ = ds["timezone"]
lat = ds["latitude"]
lon = ds["longitude"]
# Eccentric anomaly of the earth in its orbit around the sun.
print("Calculando ángulo diario")
ds["Day_Angle"] = (6.283185 * ( ds["dayofyear"] - 1 ) / 365
    ).astype(np.float32).chunk(time = 24).compute()
# Declinación.
print("Calculando declinación")
ds["Declination"] = ((0.006918 - 0.399912 * np.cos(ds["Day_Angle"])
    + 0.070257*np.sin(ds["Day_Angle"])
    - 0.006758*np.cos(2*ds["Day_Angle"])
    + 0.000907*np.sin(2*ds["Day_Angle"])
    - 0.002697*np.cos(3*ds["Day_Angle"])
    + 0.00148*np.sin(3*ds["Day_Angle"])) * 180/np.pi
    ).astype(np.float32).chunk(time = 24).compute()
# Ecuación del tiempo.
print("Calculando ecuación del tiempo")
ds["Time_Equation"] = ((0.000075 + 0.001868*np.cos(ds["Day_Angle"])
    - 0.032077*np.sin(ds["Day_Angle"])
    - 0.014615*np.cos(2*ds["Day_Angle"])
    -0.040849*np.sin(2*ds["Day_Angle"])) * 229.18
    ).astype(np.float32).chunk(time = 24).compute()
# Longitud del punto subsolar.
print("Calculando longitud del punto subsolar")
ds["lon_subs"] = -15 * (ds["hour"] - TZ
    + ds["Time_Equation"]/60
    ).astype(np.float32).chunk(time = 24).compute()
# Posiciones del analema solar.
print("Calculando posición del analema solar")
ds["Sz"] = (sin(lat)*sin(ds["Declination"])
    - cos(lat)*cos(ds["Declination"])
    *cos(ds["lon_subs"]-lon)
    ).astype(np.float32).chunk(time = 24).compute()
ds = ds.drop_vars(["lon_subs"])
# Factor b de Pérez
print("Calculando Pérez b")
ds["b"] = ds["Sz"].clip(max = cos(85))
# Ángulo del cénit solar.
print("Calculando ángulo del cénit solar")
ds["Zenith_Angle"] = acos(ds["Sz"]).astype(np.float32)
ds["Zenith_Angle"] = ds["Zenith_Angle"] + xr.where(
    (ds["Zenith_Angle"]==0) | (ds["Zenith_Angle"]==180),
    0.01, 0).astype(np.float32).chunk(time = 24).compute()
ds = ds.drop_vars("Sz")
# Ángulo horario.
print("Calculando ángulo horario")
ds["Hour_Angle"] = (15 * (ds["hour"] - 12 - ds["Time_Equation"]/60
    + ((lon-TZ*15)*4)/60)).astype(np.float32)
ds["Hour_Angle"] = xr.where(ds["Hour_Angle"]<-180,
    360+ds["Hour_Angle"], ds["Hour_Angle"])
ds["Hour_Angle"] = xr.where(ds["Hour_Angle"]>180,
    ds["Hour_Angle"]-360, ds["Hour_Angle"]).chunk(time = 24).compute()
ds = ds.drop_vars(["Time_Equation"])
# Ángulo acimutal solar.
print("Calculando ángulo del acimut solar")
ds["Azimuth_Angle"] = acos(((sin(ds["Zenith_Angle"])*sin(lat)
    - sin(ds["Declination"])) / (sin(ds["Zenith_Angle"])*cos(lat))
    ).clip(-1, 1)).astype(np.float32)
ds["Azimuth_Angle"] = (180 + ds["Azimuth_Angle"]
    * xr.where(ds["Hour_Angle"]<=0, -1, 1)
    ).astype(np.float32).chunk(time = 24).compute()
ds = ds.drop_vars(["Declination", "Hour_Angle"])
# Masa de aire.
print("Calculando masa de aire")
ds["Air_Mass"] = (1/(cos(ds["Zenith_Angle"])
    + 0.15/(93.885 - ds["Zenith_Angle"])**1.253)
    * ds["Pressure"]/1013.25).astype(np.float32)
ds["Air_Mass"] = ds["Air_Mass"].where(ds["Zenith_Angle"] < 85.5, 0
    ).astype(np.float32).chunk(time = 24).compute()
ds = ds.drop_vars(["Day_Angle", "Pressure"])

# Casos de orientación de sistemas fotovoltaico
print("Calculando casos de orientación de sistemas fotovoltaicos")
# Casos a estudiar
cases = [ "south_no_track", "west_no_track", "east_no_track",
    "1_track", "2_track", "bifacial_vertical_west_main",
    "bifacial_vertical_east_main", "bifacial_vertical_west_back",
    "bifacial_vertical_east_back", "bifacial_south_back" ]
# Variables fotovoltaicas por caso
# Inclinación
track_tilt       =   [ f"{x}_Tilt"               for x in cases ]
# Azimuth
track_azimuth    =   [ f"{x}_Azimuth"            for x in cases ]

# Ángulos de orientación de los sistemas
# Orientación del seguidor de un eje
# Asumimos inclinación de 0 grados
azimuth_tracker = 180
# south_no_track
ds[track_azimuth[0]] = 180
ds[track_tilt[0]   ] = lat
# west_no_track
ds[track_azimuth[1]] = 270
ds[track_tilt[1]   ] = lat
# east_no_track
ds[track_azimuth[2]] = 90
ds[track_tilt[2]   ] = lat
# 1_track
ds[track_tilt[3]   ] = np.abs(atan(tan(ds["Zenith_Angle"])
    * sin(ds["Azimuth_Angle"] - azimuth_tracker))
    ).astype(np.float32).chunk(time = 24).compute()
ds[track_azimuth[3]] = 90
ds[track_azimuth[3]] = ds["1_track_Azimuth"
    ].where(ds["Azimuth_Angle"]<180, 270
    ).astype(np.float32).chunk(time = 24).compute()
# 2_track
ds[track_tilt[4]   ] = ds["Zenith_Angle"]
ds[track_azimuth[4]] = ds["Azimuth_Angle"]
# bifacial_vertical_west_main
ds[track_tilt[5]   ] = 90
ds[track_azimuth[5]] = 270
# bifacial_vertical_east_main
ds[track_tilt[6]   ] = 90
ds[track_azimuth[6]] = 90
# bifacial_vertical_west_back
ds[track_tilt[7]   ] = 90
ds[track_azimuth[7]] = 90
# bifacial_vertical_east_back
ds[track_tilt[8]   ] = 90
ds[track_azimuth[8]] = 270
# bifacial_south_back
ds[track_tilt[9]   ] = 90 + lat
ds[track_azimuth[9]] = 0

ds = ds.transpose("points", "time").chunk(time = 24).compute()
ds.to_netcdf(f"{dir_d}full_disc_physical_solar_2022.nc")