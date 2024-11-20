# Calcula los el seguimiento solar.

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

print("Seguimiento solar")

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

dir_r = "/datos/rodr/temp/recurso_solar/duck_curve/"
ds = xr.open_dataset(f"{dir_r}full_disc_physical_solar_2022.nc",
    chunks = {"points": 20000})[["latitude", "longitude", "Zenith_Angle",
    "Azimuth_Angle", "cos_zenith", "sin_zenith"]]

lat = ds["latitude"]
lon = ds["longitude"]
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
    * sin(ds["Azimuth_Angle"] - azimuth_tracker))).astype(np.float32)
ds[track_azimuth[3]] = 90
ds[track_azimuth[3]] = ds["1_track_Azimuth"
    ].where(ds["Azimuth_Angle"]<180, 270).astype(np.float32)
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
ds = ds.drop_vars(["latitude", "longitude"])

# Ángulo de incidencia
for i in range(len(cases)):
    # Ángulo entre el panel y el sol, Angle of Incidence
    ds[track_AOI[i]] = acos((ds["cos_zenith"]*cos(ds[track_tilt[i]])
        + ds["sin_zenith"]*sin(ds[track_tilt[i]])
        *cos(ds["Azimuth_Angle"]-ds[track_azimuth[i]])
        ).clip(-1, 1)).astype(np.float32)
ds = ds.drop_vars(["Zenith_Angle", "Azimuth_Angle",
    "cos_zenith", "sin_zenith"])

delayed_obj = ds.to_netcdf(f"{dir_r}full_disc_track_solar_2022.nc",
    compute = False)
with ProgressBar(): results = delayed_obj.compute()