# une los archivos a lo largo de la variable XTIME
import os
import sys
import xarray as xr
from dask.diagnostics import ProgressBar

# Rutas
scn    = sys.argv[1]
dir_o  = "/home/rodr/buffalo/rodr/WRF/"
dir_d1 = f"{dir_o}{scn}/data/"
dir_d2 = f"{dir_o}{scn}/PV/"
dir_d3 = f"{dir_o}{scn}/max/"
dir_r  = f"/datos/rodr/Datos/WRF/{scn}/"
if not os.path.exists(dir_r): os.mkdir(dir_r)

# Cargamos archivos y unimos
ds_1       = None
ds_2       = None
ds_3       = None
print("Uniendo Datos temporales")
if not os.path.exists(f"{dir_r}{scn}.nc"):
    ds_1 = xr.open_mfdataset(f"{dir_d1}*.nc").sortby("XTIME")
    ds_1_mean = ds_1.drop_vars("GHI").mean("XTIME")
    ds_1_mean["GHI"] = ds_1["GHI"].resample(
        {"XTIME": "YE"}).sum().mean("XTIME")
    ds_1_month = ds_1.drop_vars("GHI").groupby(ds_1["XTIME"].dt.month).mean()
    ds_1_month_h = ds_1["GHI"].resample({"XTIME": "ME"}).sum()
    ds_1_month["GHI"] = ds_1_month_h.groupby(
        ds_1_month_h["XTIME"].dt.month).mean()
    ds_1_day = ds_1.drop_vars("GHI").groupby(ds_1["XTIME"].dt.dayofyear).mean()
    ds_1_day_h = ds_1["GHI"].resample({"XTIME": "D"}).sum()
    ds_1_day["GHI"] = ds_1_day_h.groupby(
        ds_1_day_h["XTIME"].dt.dayofyear).mean()
    ds_1_hour = ds_1.drop_vars("GHI").groupby(ds_1["XTIME"].dt.hour).mean()
    ds_1_hour["GHI"] = ds_1["GHI"].groupby(ds_1["XTIME"].dt.hour).mean()
    ds_1_hour_month = ds_1.drop_vars("GHI").groupby(
        [ds_1["XTIME"].dt.hour, ds_1["XTIME"].dt.month]).mean()
    ds_1_hour_month["GHI"] = ds_1["GHI"].groupby(
        [ds_1["XTIME"].dt.hour, ds_1["XTIME"].dt.month]).mean()
if not os.path.exists(f"{dir_r}{scn}_PV.nc"):
    ds_2 =  xr.open_mfdataset(f"{dir_d2}*.nc").sortby("XTIME")
    ds_2_mean = ds_2.resample({"XTIME": "YE"}).sum().mean("XTIME")
    ds_2_month_h = ds_2.resample({"XTIME": "ME"}).sum()
    ds_2_month = ds_2_month_h.groupby(ds_2_month_h["XTIME"].dt.month).mean()
    ds_2_day_h = ds_2.resample({"XTIME": "D"}).sum()
    ds_2_day = ds_2_day_h.groupby(ds_2_day_h["XTIME"].dt.dayofyear).mean()
    ds_2_hour  = ds_2.groupby(ds_2["XTIME"].dt.hour).mean()
    ds_2_hour_month  = ds_2.groupby([ds_2["XTIME"].dt.hour,
        ds_2["XTIME"].dt.month]).mean()
if not os.path.exists(f"{dir_r}{scn}_max.nc"):
    ds_3 = xr.open_mfdataset(f"{dir_d3}*.nc").sortby("XTIME")
    ds_3_mean  = ds_3.mean("XTIME")
    ds_3_month = ds_3.groupby(ds_3["XTIME"].dt.month).mean()
    ds_3_day   = ds_3.groupby(ds_3["XTIME"].dt.dayofyear).mean()

# Calculamos y guardamos
with ProgressBar():
    if not ds_1 is None:
        print("Datos")
        ds_1.to_netcdf(f"{dir_r}{scn}.nc").compute()
        print("Promedio")
        ds_1_mean.to_netcdf(f"{dir_r}{scn}_mean.nc").compute()
        print("Promedio mensual")
        ds_1_month.to_netcdf(f"{dir_r}{scn}_month.nc").compute()
        print("Promedio diario")
        ds_1_day.to_netcdf(f"{dir_r}{scn}_day.nc").compute()
        print("Promedio horario")
        ds_1_hour.to_netcdf(f"{dir_r}{scn}_hour.nc").compute()
        print("Promedio horario - mensual")
        ds_1_hour_month.to_netcdf(f"{dir_r}{scn}_hour_month.nc").compute()
        print()
    if not ds_3 is None:
        print("Generación")
        ds_2.to_netcdf(f"{dir_r}{scn}_PV.nc").compute()
        print("Promedio")
        ds_2_mean.to_netcdf(f"{dir_r}{scn}_PV_mean.nc").compute()
        print("Promedio mensual")
        ds_2_month.to_netcdf(f"{dir_r}{scn}_PV_month.nc").compute()
        print("Promedio diario")
        ds_2_day.to_netcdf(f"{dir_r}{scn}_PV_day.nc").compute()
        print("Promedio horario")
        ds_2_hour.to_netcdf(f"{dir_r}{scn}_PV_hour.nc").compute()
        print("Promedio horario - mensual")
        ds_2_hour_month.to_netcdf(f"{dir_r}{scn}_PV_hour_month.nc").compute()
        print()
    if not ds_3 is None:
        print("Máximos")
        ds_3.to_netcdf(f"{dir_r}{scn}_max.nc").compute()
        print("Promedio")
        ds_3_mean.to_netcdf(f"{dir_r}{scn}_max_mean.nc").compute()
        print("Promedio mensual")
        ds_3_month.to_netcdf(f"{dir_r}{scn}_max_month.nc").compute()
        print("Promedio diario")
        ds_3_day.to_netcdf(f"{dir_r}{scn}_max_day.nc").compute()
        print()