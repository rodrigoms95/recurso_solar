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

print("Seguimiento solar")
print()

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

print("Cargando archivos")
dir_r = "/datos/rodr/temp/recurso_solar/duck_curve/"
ds = xr.open_dataset(f"{dir_r}full_disc_physical_solar_2022.nc",
    chunks = {"time": 24})[["Zenith_Angle", "Azimuth_Angle"]
    + track_tilt + track_azimuth]

# Ángulo de incidencia y valores de método de Pérez
print("Calculando AOI")
for i in range(len(cases)):
    print(f"Calculando {cases[i]}")
    # Ángulo entre el panel y el sol, Angle of Incidence
    ds[track_AOI[i]] = acos((cos(ds["Zenith_Angle"])*cos(ds[track_tilt[i]])
        + sin(ds["Zenith_Angle"])*sin(ds[track_tilt[i]])
        *cos(ds["Azimuth_Angle"]-ds[track_azimuth[i]])
        ).clip(-1, 1)).astype(np.float32).compute()
    ds = ds.drop_vars([track_tilt[i], track_azimuth[i]])
    print(ds.nbytes/1024**3)

ds = ds.drop_vars(["Zenith_Angle", "Azimuth_Angle"])
print("Guardando")
print(ds.nbytes/1024**3)
ds.to_netcdf(f"{dir_r}full_disc_track_solar_2022.nc")