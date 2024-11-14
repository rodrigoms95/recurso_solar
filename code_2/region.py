import xarray as xr
import pandas as pd
import numpy as np
from dask.diagnostics import ProgressBar

dir_r = "/datos/rodr/temp/recurso_solar/duck_curve/"
points = pd.read_csv(f"{dir_r}conus_points.csv").rename( columns = 
    {"Unnamed: 0": "points"}).set_index("points")[["latitude", "longitude",
    "timezone", "REGION", "potential_solar_park_zones", "built_surface"]
    ].to_xarray()
ds_0 = xr.open_dataset(f"{dir_r}full_disc_PV_2022.nc").chunk({"time": 2000})
ds = xr.merge([ds_0, points])

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

# Ponderamos la producción fotovoltaica

# Para generación distribuida ponderamos con el área construida
prod_n_dist = [f"{x}_distributed" for x in prod_n]
ds[prod_n_dist] = (ds[prod_n] * ds["built_surface"]).astype(np.float32)
# Podemos forzar a que la producción distribuida siempre sea hacia el sur
#for v in prod_n_dist[1:]: ds[v] = ds[prod_n_dist[0]]

# Para parques solares ponderamos con las líneas de transmisión
prod_n_centr = [f"{x}_central" for x in prod_n]
ds[prod_n_centr] = ds[prod_n].where(ds["potential_solar_park_zones"]
    ).astype(np.float32)

# Promediamos la generación por región
ds_c = ds.groupby("REGION").mean()
# Datos agregados para generación
# Agrupamiento longitudinal
ds_i = ds.where(ds["REGION"].isin([1, 2, 4, 5, 6, 14, 19]))
ds_i["REGION"] = ds_i["REGION"].where(ds_i["REGION"] == 22, 22)
ds_c_2 = ds_i.groupby("REGION").mean()
# Agrupamiento latitudinal
ds_i = ds.where(ds["REGION"].isin([1, 2, 10, 11, 12, 13]))
ds_i["REGION"] = ds_i["REGION"].where(ds_i["REGION"] == 23, 23)
ds_c_3 = ds_i.groupby("REGION").mean()
# Agrupamiento total
ds_i["REGION"] = ds["REGION"].where(ds["REGION"] == 24, 24)
ds_c_4 = ds_i.groupby("REGION").mean()
ds_c = xr.concat([ds_c, ds_c_2, ds_c_3, ds_c_4], "REGION")
ds_c["REGION"] = ds_c["REGION"].astype(int)

# Para generación distribuida ponderamos con el área construida
a = ds[["built_surface", "REGION"]].groupby("REGION").sum().to_dataframe()
a.loc[24] = a.sum()
a.loc[22] = a.loc[[1, 2, 4, 5, 6, 14, 19]].sum()
a.loc[23] = a.loc[[1, 2, 10, 11, 12, 13]].sum()
b = ds[["built_surface", "REGION"]].groupby("REGION").count().to_dataframe()
b.loc[24] = b.sum()
b.loc[22] = b.loc[[1, 2, 4, 5, 6, 14, 19]].sum()
b.loc[23] = b.loc[[1, 2, 10, 11, 12, 13]].sum()
ds_c["sum_built_surface"] = a.sort_index().to_xarray()["built_surface"]
ds_c["count_built_surface"] = b.sort_index().to_xarray()["built_surface"]
ds_c[prod_n_dist] = (ds_c[prod_n_dist] * ds_c["count_built_surface"]
    / ds_c["sum_built_surface"])

# Unimos toda la producción
prod_n_total = [f"{x}_total" for x in prod_n]
for i, v in enumerate(prod_n_total): ds_c[v] = (
    (ds_c[prod_n_dist[i]] + ds_c[prod_n_centr[i]])/2).astype(np.float32)

delayed = ds_c.to_netcdf(f"{dir_r}full_disc_region_2022.nc", compute = False)
with ProgressBar(): result = delayed.compute()
