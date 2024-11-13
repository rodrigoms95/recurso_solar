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

dir_r = "/datos/rodr/temp/recurso_solar/duck_curve/"
ds_1 = xr.open_dataset(f"{dir_r}full_disc_irradiance_2022.nc",
   ).sortby("points")[["dhi"]].chunk({"points": 2000})
ds_2 = xr.open_dataset(f"{dir_r}full_disc_physical_solar_2022.nc",
   ).sortby("points")[["cos_zenith", "Zenith_Angle"]].chunk({"points": 2000})
ds_3 = xr.open_dataset(f"{dir_r}full_disc_track_solar_2022.nc",
   ).sortby("points")[track_AOI + track_tilt].chunk({"points": 2000})
ds_4 = xr.open_dataset(f"{dir_r}full_disc_Perez_2022.nc",
   ).sortby("points")[["dni", "F1", "F2"]
    ].chunk({"points": 2000})
ds = xr.merge([ds_1, ds_2, ds_3, ds_4])

# Modelo de Pérez de Cielo Difuso para calcular 
# la radiación en un plano inclinado
# Iteramos para cada caso
for i in range(len(cases)):
    # Radiación difusa.
    ds["cos_tilt"] = ((1+cos(ds[track_tilt[i]]))/2).astype(np.float32)
    ds["cos_AOI"] = cos(ds[track_AOI[i]]).astype(np.float32)
    ds["I_d"] = (ds["dhi"] * ( (1-ds["F1"])*ds["cos_tilt"]
        + ds["F1"]*ds["cos_AOI"].clip(max = 0)
        /ds["cos_zenith"].clip(max = cos(85))
        + ds["F2"]*sin(ds[track_tilt[i]])) 
        ).where(ds["Zenith_Angle"] < 87.5,
        ds["dhi"] * ds["cos_tilt"]
        ).where(ds["Zenith_Angle"] < 90, 0).astype(np.float32)
    # Radiación directa.
    ds["I_b"] = (ds["dni"] * ds["cos_AOI"]).where(
        ds[track_AOI[i]] < 90, 0).astype(np.float32)
    ds = ds.drop_vars([track_AOI[i], track_tilt[i]])
    # Radiación total en el panel.
    ds[track_POA[i]] = (ds["I_b"] + ds["I_d"]).astype(np.float32)
    ds = ds.drop_vars(["I_b", "I_d", "cos_tilt", "cos_AOI"])

ds = ds.drop_vars(["F1", "F2", "cos_zenith", "Zenith_Angle", "dhi", "dni"])
delayed_obj = ds.to_netcdf(f"{dir_r}full_disc_POA_2022.nc", compute = False)
with ProgressBar(): results = delayed_obj.compute()
