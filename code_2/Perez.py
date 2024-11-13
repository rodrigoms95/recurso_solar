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

print("Perez diffuse irradiance model")

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
    ).sortby("points")[["ghi", "dhi"]].chunk({"points": 10000})
ds_2 = xr.open_dataset(f"{dir_r}full_disc_physical_solar_2022.nc",
   ).sortby("points")[["Zenith_Angle", "Air_Mass"]].chunk({"points": 10000})
ds = xr.merge([ds_1, ds_2])

# Modelo de Pérez de Cielo Difuso para calcular 
# la radiación en un plano inclinado
# Diffuse Horizontal Radiation.
ds["dni"] = ((ds["ghi"] - ds["dhi"]) /
    cos(ds["Zenith_Angle"])).clip(min = 0).astype(np.float32)
ds["dhi"] = ds["dhi"].astype(np.float32).clip(min = 0.001)
ds = ds.drop_vars("ghi")
K = 5.535e-6
# Perez clearness bins.
ds["k_zenith"] = K*ds["Zenith_Angle"]**3
ds["bins"] = 0
ds["bins"] = ds["bins"].where( ds["dhi"] == 0,
    ( (ds["dhi"]+ds["dni"])/ds["dhi"] + ds["k_zenith"] )
    / (1+ds["k_zenith"]) ).astype(np.float32)
ds = ds.drop_vars("k_zenith")
ds["dhi"] = ds["dhi"].where(ds["dhi"]>0.001, 0).astype(np.float32)
ds["epsilon"] = xr.where( (ds["bins"]>6.200),
    8, ds["bins"] ).astype(np.float32)
ds["epsilon"] = xr.where( (ds["bins"]>4.500)
    & (ds["bins"]<6.200), 7, ds["epsilon"] ).astype(np.float32)
ds["epsilon"] = xr.where( (ds["bins"]>2.600)
    & (ds["bins"]<4.500), 6, ds["epsilon"] ).astype(np.float32)
ds["epsilon"] = xr.where((ds["bins"]>1.950)
    & (ds["bins"]<2.600), 5, ds["epsilon"] ).astype(np.float32)
ds["epsilon"] = xr.where( (ds["bins"]>1.500)
    & (ds["bins"]<1.950), 4, ds["epsilon"] ).astype(np.float32)
ds["epsilon"] = xr.where( (ds["bins"]>1.230)
    & (ds["bins"]<1.500), 3, ds["epsilon"] ).astype(np.float32)
ds["epsilon"] = xr.where( (ds["bins"]>1.065)
    & (ds["bins"]<1.500), 2, ds["epsilon"] ).astype(np.float32)
ds["epsilon"] = xr.where( (ds["bins"]<1.065),
    1, ds["epsilon"] ).astype(np.float32)
Perez = pd.read_csv("../files/Perez.csv", index_col = "bin")
ds = ds.drop_vars("bins")
# Extraterrestrial radiation.
Ea = 1367
# Coeficientes
ds["Delta"] = (ds["dhi"] * ds["Air_Mass"] / Ea).astype(np.float32)
ds = ds.drop_vars("Air_Mass")
for j in Perez.columns:
    ds[j] = 0.0
    for i in Perez.index:
        ds[j] = ds[j].where(ds["epsilon"] != i,
        Perez.loc[i, j]).astype(np.float32)
    ds[j]
ds = ds.drop_vars("epsilon")
ds["F1"] = ( ds["f11"] + ds["f12"]*ds["Delta"]
    + np.radians(ds["Zenith_Angle"])*ds["f13"]
    ).clip(max = 0).astype(np.float32)
ds = ds.drop_vars(["f11", "f12", "f13"])
ds["F2"] = ( ds["f21"] + ds["f22"]*ds["Delta"]
    + np.radians(ds["Zenith_Angle"])*ds["f23"] ).astype(np.float32)
ds = ds.drop_vars(["f21", "f22", "f23", "Delta", "dhi"])

delayed_obj = ds.to_netcdf(f"{dir_r}full_disc_Perez_2022.nc", compute = False)
with ProgressBar(): results = delayed_obj.compute()