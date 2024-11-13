# Calcula los elementos físicos de la radiación solar que dependen de la
# ubicación y del tiempo.

import pandas as pd
import numpy as np
import xarray as xr
from dask.diagnostics import ProgressBar

# Funciones trigonométricas.
def sin(x) : return np.sin(np.radians(x))
def cos(x) : return np.cos(np.radians(x))
def tan(x) : return np.tan(np.radians(x))
def asin(x): return np.arcsin(x) * 180/np.pi
def acos(x): return np.arccos(x) * 180/np.pi
def atan(x): return np.arctan(x) * 180/np.pi

print("Calculando elementos físicos solares")

# Cargamos datos.
dir_d = "/datos/rodr/temp/recurso_solar/duck_curve/"
ds = pd.read_csv(f"{dir_d}conus_points.csv", index_col = 0)[
    ["latitude", "longitude", "REGION", "timezone",
    "potential_solar_park_zones", "built_surface"]
    ].to_xarray().rename({"index": "points"}).chunk({"points": 20000})
ds["time"] = pd.date_range("2022-01-01", "2023-01-01", freq = "1h")[:-1]

lat = ds["latitude"]
lon = ds["longitude"]
# Eccentric anomaly of the earth in its orbit around the sun.
ds["Day_Angle"] = (6.283185 * (ds["time"].dt.dayofyear-1)/365
    ).astype(np.float32)
# Declinación.
ds["Declination"] = ((0.006918 - 0.399912 * np.cos(ds["Day_Angle"])
    + 0.070257*np.sin(ds["Day_Angle"]) - 0.006758*np.cos(2*ds["Day_Angle"])
    + 0.000907*np.sin(2*ds["Day_Angle"]) - 0.002697*np.cos(3*ds["Day_Angle"])
    + 0.001480*np.sin(3*ds["Day_Angle"])) * 180/np.pi).astype(np.float32)
# Ecuación del tiempo.
ds["Time_Equation"] = ((0.000075 + 0.001868*np.cos(ds["Day_Angle"])
    - 0.032077*np.sin(ds["Day_Angle"]) - 0.014615*np.cos(2*ds["Day_Angle"])
    -0.040849*np.sin(2*ds["Day_Angle"])) * 229.18).astype(np.float32)
ds = ds.drop_vars("Day_Angle")
# Longitud del punto subsolar.
ds["lon_subs"] = -15 * (ds["time"].dt.hour + ds["Time_Equation"]/60
    ).astype(np.float32)
# Posiciones del analema solar.
# cos zenith = Sz
ds["cos_zenith"] = (sin(lat)*sin(ds["Declination"])
    - cos(lat)*cos(ds["Declination"])
    * cos(ds["lon_subs"]-lon)).astype(np.float32)
ds = ds.drop_vars(["lon_subs"])
# Ángulo del cénit solar.
ds["Zenith_Angle"] = acos(ds["cos_zenith"]).astype(np.float32)
ds["Zenith_Angle"] = ds["Zenith_Angle"] + xr.where((ds["Zenith_Angle"]==0)
    | (ds["Zenith_Angle"]==180), 0.01, 0).astype(np.float32)
ds["sin_zenith"] = sin(ds["Zenith_Angle"])
# Ángulo horario.
ds["Hour_Angle"] = (15 * (ds["time"].dt.hour - 12 - ds["Time_Equation"]/60
    + lon/15)).astype(np.float32)
ds["Hour_Angle"] = xr.where(ds["Hour_Angle"]<-180,
    360+ds["Hour_Angle"], ds["Hour_Angle"])
ds["Hour_Angle"] = xr.where(ds["Hour_Angle"]>180,
    ds["Hour_Angle"]-360, ds["Hour_Angle"])
ds = ds.drop_vars("Time_Equation")
# Ángulo acimutal solar.
ds["Azimuth_Angle"] = acos(((ds["sin_zenith"]*sin(lat)
    - sin(ds["Declination"])) / (ds["sin_zenith"]*cos(lat))
    ).clip(-1, 1)).astype(np.float32)
ds["Azimuth_Angle"] = (180 + ds["Azimuth_Angle"]
    * xr.where(ds["Hour_Angle"]<=0, -1, 1)).astype(np.float32)
ds = ds.drop_vars(["Declination", "Hour_Angle"])
# Masa de aire.
ds["Air_Mass"] = xr.where(ds["Zenith_Angle"] > 90, 0, 1/(ds["cos_zenith"]
    + 0.50572/(96.07995 - ds["Zenith_Angle"].clip(max = 90))**1.6364)
    ).astype(np.float32)

delayed_obj = ds.transpose("points", "time").to_netcdf(
    f"{dir_d}full_disc_physical_solar_2022.nc", compute = False)
with ProgressBar(): results = delayed_obj.compute()