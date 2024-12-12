# Obtenemos malla de puntos

import xarray as xr
import geopandas as gpd
import h5pyd
import pandas as pd
import numpy as np

# Descargamos malla con HSDS
with h5pyd.File("/nrel/nsrdb/current/nsrdb_2022.h5") as f:
    meta = pd.DataFrame(f['meta'][...])
points = meta[ (meta["country"]==b"Mexico")
    | (meta["state"].isin([b"Texas", b"California", b"Nevada"]))
    ].sort_values(["latitude", "longitude"])

# Regiones eléctricas
dir_d = "/home/rodr/Datos/recurso_solar/"
dir_r = "/home/rodr/temp/recurso_solar/net_load/"
regiones_p = f"{dir_d}Mapas/Electric_regions"
regiones = gpd.read_file(regiones_p)
# Vemos en qué región cae cada punto
print("Determinando región de cada punto")
points["geometry"] = gpd.points_from_xy(
    points["longitude"], points["latitude"])
points = gpd.GeoDataFrame(points, crs = 4326)
points["REGION"] = np.nan
for row in regiones.itertuples():
    points["MASK_REG"] = points.within(row.geometry)
    points["REGION"] = points["REGION"].where(
        ~points["MASK_REG"], row.ID_NUMBER )
points = points.dropna()

points.to_csv(f"{dir_r}nsrdb_points.csv", index = True)
