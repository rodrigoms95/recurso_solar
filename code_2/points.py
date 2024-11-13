# Genera la tabla de puntos para el estudio de la curva de pato

import h5pyd
import pandas    as pd
import numpy     as np
import geopandas as gpd
import xarray    as xr
import xesmf     as xe

print("Generando tabla de puntos")
print()

# Descargamos malla con HSDS
print("Descargando malla de CONUS")
with h5pyd.File("/nrel/nsrdb/conus/nsrdb_conus_2022.h5") as f:
    meta = pd.DataFrame(f['meta'][...])
points = meta[ (meta["country"]==b"Mexico")
    | (meta["state"].isin([b"Texas", b"California", b"Nevada"])) ].copy()
points = points[np.where(np.round(points["latitude"]%.06*100)==2, True, False)
    &  np.where(np.round((points["longitude"]-0.01)%.06*100)==2, True, False)
    ].sort_values(["latitude", "longitude"])

# Datos
print("Cargando datos")
# Regiones eléctricas
dir_d = "/home/rodr/Datos/recurso_solar/"
dir_r = "/datos/rodr/temp/recurso_solar/duck_curve/"
regiones_p = f"{dir_d}Mapas/Electric_regions"
regiones = gpd.read_file(regiones_p)
# Líneas de transmisión
transmision_p = f"{dir_d}Mapas/study_region_transmission_lines"
transmision = gpd.read_file(transmision_p).to_crs(6363)
transmision["potential_solar_park_zones"] = transmision.buffer(5000)
transmision = transmision.set_geometry("potential_solar_park_zones")
potential_solar_park_zones = transmision.dissolve(
    ).loc[0, "potential_solar_park_zones"]

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

# Vemos si el punto cae cerca de una línea de transmisión
print("Determinando proximidad a líneas de transmisión")
points["MASK_ZONE"] = points.to_crs(6363).within(potential_solar_park_zones)
points["potential_solar_park_zones"] = np.where(points["MASK_ZONE"], 1, 0)

# Ponderamos la producción fotovoltaica
print("Ponderando producción distribuida")
points_p = points[["latitude", "longitude"]
    ].set_index(["latitude", "longitude"])
ds_p = points_p.to_xarray()
# Cargamos el área construida e interpolamos
dir_m = "/home/rodr/Datos/recurso_solar/Mapas/"
built_n = "GHS_BUILT_S_E2020_GLOBE_R2023A_4326_30ss_V1_0"
built = xr.open_dataset(f"{dir_m}{built_n}/{built_n}.tif"
    ).isel({"band": 0}).drop_vars(["band", "spatial_ref"]).rename(
    {"x": "longitude", "y": "latitude", "band_data": "built_surface"}).sel({
    "longitude": slice(ds_p["longitude"].values.min()-0.06,
        ds_p["longitude"].values.max()+0.06),
    "latitude": slice(ds_p["latitude"].values.max()+0.06,
        ds_p["latitude"].values.min()-0.06)})
built = built.coarsen({"longitude": 6, "latitude": 6}, boundary = "pad").sum()
regridder = xe.Regridder(built, ds_p, method = "bilinear")
ds_p["built_surface"] = regridder(built["built_surface"], keep_attrs = True)
points_p["built_surface"] = ds_p.to_dataframe().sort_values(
    ["latitude", "longitude"])["built_surface"]
points["built_surface"] = points_p["built_surface"].values.astype(np.float32)

# Guardamos el archivo
points.drop(columns = ["geometry", "MASK_REG", "MASK_ZONE"]
    ).to_csv(f"{dir_r}conus_points.csv", index = True)