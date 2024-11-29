# une los archivos a lo largo de la variable XTIME
import os
import sys
import xarray as xr
import pandas as pd
from dask.diagnostics import ProgressBar

# Rutas
scn    = sys.argv[1]
#dir_o  = "/home/rodr/buffalo/rodr/WRF/"
dir_o = "/datos/rodr/Datos/WRF_data/"
dir_d1 = f"{dir_o}{scn}/data/"
dir_d2 = f"{dir_o}{scn}/PV/"
dir_d3 = f"{dir_o}{scn}/max/"
dir_r  = f"/datos/rodr/Datos/WRF/{scn}/"
if not os.path.exists(dir_r): os.mkdir(dir_r)

if scn=="NSRDB":
    coords = ("time", "lat", "lon")
    dims = ("time", "lat", "lon")
else:
    coords = ("XTIME", "XLAT", "XLONG")
    dims = ("XTIME", "south_north", "west_east")

# Cargamos archivos y unimos
ds_1       = None
ds_2       = None
ds_3       = None
print("Uniendo Datos temporales")
if not os.path.exists(f"{dir_r}{scn}.nc"):
    ds_1 = xr.open_mfdataset(f"{dir_d1}*.nc").sortby(coords[0])
    ds_1_mean = ds_1.drop_vars("GHI").mean(coords[0])
    ds_1_mean["GHI"] = ds_1["GHI"].resample(
        {coords[0]: "YE"}).sum().mean(coords[0])
    ds_1_month = ds_1.drop_vars("GHI").groupby(ds_1[coords[0]].dt.month).mean()
    ds_1_month_h = ds_1["GHI"].resample({coords[0]: "ME"}).sum()
    ds_1_month["GHI"] = ds_1_month_h.groupby(
        ds_1_month_h[coords[0]].dt.month).mean()
    ds_1_day = ds_1.drop_vars("GHI").groupby(
        ds_1[coords[0]].dt.dayofyear).mean()
    ds_1_day_h = ds_1["GHI"].resample({coords[0]: "D"}).sum()
    ds_1_day["GHI"] = ds_1_day_h.groupby(
        ds_1_day_h[coords[0]].dt.dayofyear).mean()
    ds_1_hour = ds_1.drop_vars("GHI").groupby(ds_1[coords[0]].dt.hour).mean()
    ds_1_hour["GHI"] = ds_1["GHI"].groupby(ds_1[coords[0]].dt.hour).mean()
    month_hour_idx = pd.MultiIndex.from_arrays(
        [ds_1[coords[0]].dt.month.values, ds_1[coords[0]].dt.hour.values])
    ds_1_h = ds_1.copy()
    ds_1_h.coords["month_hour"] = (coords[0], month_hour_idx)
    ds_1_hour_month = ds_1_h.drop_vars("GHI").groupby("month_hour").mean()
    ds_1_hour_month["GHI"] = ds_1_h[["GHI"]].groupby(
        "month_hour").mean()["GHI"]
    ds_1_hour_month = ds_1_hour_month.unstack("month_hour").rename(
        {"XTIME_level_0": "month", "XTIME_level_1": "hour"})
if not os.path.exists(f"{dir_r}{scn}_PV.nc"):
    ds_2 =  xr.open_mfdataset(f"{dir_d2}*.nc").sortby(coords[0])
    ds_2_mean    = ds_2.resample({coords[0]: "YE"}).sum().mean(coords[0])
    ds_2_month_h = ds_2.resample({coords[0]: "ME"}).sum()
    ds_2_month   = ds_2_month_h.groupby(
        ds_2_month_h[coords[0]].dt.month).mean()
    ds_2_day_h   = ds_2.resample({coords[0]: "D"}).sum()
    ds_2_day     = ds_2_day_h.groupby(
        ds_2_day_h[coords[0]].dt.dayofyear).mean()
    ds_2_hour    = ds_2.groupby(ds_2[coords[0]].dt.hour).mean()
    month_hour_idx = pd.MultiIndex.from_arrays(
        [ds_2[coords[0]].dt.month.values, ds_2[coords[0]].dt.hour.values])
    ds_2_h = ds_2.copy()
    ds_2_h.coords["month_hour"] = (coords[0], month_hour_idx)
    ds_2_hour_month  = ds_2_h.groupby("month_hour").mean()
    ds_2_hour_month = ds_2_hour_month.unstack("month_hour").rename(
        {"XTIME_level_0": "month", "XTIME_level_1": "hour"})
if not os.path.exists(f"{dir_r}{scn}_max.nc"):
    ds_3 = xr.open_mfdataset(f"{dir_d3}*.nc").sortby(coords[0])
    ds_3_mean  = ds_3.mean(coords[0])
    ds_3_month = ds_3.groupby(ds_3[coords[0]].dt.month).mean()
    ds_3_day   = ds_3.groupby(ds_3[coords[0]].dt.dayofyear).mean()

# Calculamos y guardamos
with ProgressBar():
    if not ds_1 is None:
        print("Datos")
        ds_1.to_netcdf(f"{dir_r}{scn}.nc")
        print("Promedio")
        ds_1_mean.to_netcdf(f"{dir_r}{scn}_mean.nc")
        print("Promedio mensual")
        ds_1_month.to_netcdf(f"{dir_r}{scn}_month.nc")
        print("Promedio diario")
        ds_1_day.to_netcdf(f"{dir_r}{scn}_day.nc")
        print("Promedio horario")
        ds_1_hour.to_netcdf(f"{dir_r}{scn}_hour.nc")
        print("Promedio horario - mensual")
        ds_1_hour_month.to_netcdf(f"{dir_r}{scn}_hour_month.nc")
        print()
    if not ds_2 is None:
        print("Generación")
        ds_2.to_netcdf(f"{dir_r}{scn}_PV.nc")
        print("Promedio")
        ds_2_mean.to_netcdf(f"{dir_r}{scn}_PV_mean.nc")
        print("Promedio mensual")
        ds_2_month.to_netcdf(f"{dir_r}{scn}_PV_month.nc")
        print("Promedio diario")
        ds_2_day.to_netcdf(f"{dir_r}{scn}_PV_day.nc")
        print("Promedio horario")
        ds_2_hour.to_netcdf(f"{dir_r}{scn}_PV_hour.nc")
        print("Promedio horario - mensual")
        ds_2_hour_month.to_netcdf(f"{dir_r}{scn}_PV_hour_month.nc")
        print()
    if not ds_3 is None:
        print("Máximos")
        ds_3.to_netcdf(f"{dir_r}{scn}_max.nc")
        print("Promedio")
        ds_3_mean.to_netcdf(f"{dir_r}{scn}_max_mean.nc")
        print("Promedio mensual")
        ds_3_month.to_netcdf(f"{dir_r}{scn}_max_month.nc")
        print("Promedio diario")
        ds_3_day.to_netcdf(f"{dir_r}{scn}_max_day.nc")
        print()