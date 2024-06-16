# Corrección de cuantiles empírica.

import os
import sys

import numpy as np
import pandas as pd

import xarray as xr

i = sys.argv[1]
v = sys.argv[2]
internal = sys.argv[3]
name_d = sys.argv[4]
name_m = sys.argv[5]
dims = ["time", "lat", "lon"]

# Observado.
path_d    = f"{internal}/{name_d}/vars/{v}/{name_d}_{i}.nc"
# Modelo histórico.
path_m    = f"{internal}/{name_m}/vars/{v}/{name_m}_{i}.nc"
#path_f    = "../temp/WRF_2040_regrid_CHIRPS_days_cdf.nc"
path_res  = f"{internal}/{name_m}/map_res/{v}/{name_m}_{i}.nc"
path_map  = f"{internal}/{name_m}/qmap/{v}/{name_m}_{i}.nc"
#path_fmap = "../temp/WRF_2040_regrid_CHIRPS_days_qmap.nc"

sum = True

with xr.open_dataset(path_m) as ds_m:
    with xr.open_dataset(path_d) as ds_d:
        #with xr.open_dataset(path_f) as ds_f:

            df_d = ds_d.to_dataframe().reorder_levels(dims).sort_index()
            df_m = ds_m.to_dataframe().reorder_levels(dims).sort_index()
            #df_f = ds_f.to_dataframe().reorder_levels(**dims).sort_index()
            #df_f["map"] = None
            df_m["map"] = None
            if sum: df_m["diff_sum"] = None
            else: df_m["diff_div"] = None

            latitude = df_d.index.get_level_values(
                dims[1] ).unique().sort_values()
            longitude = df_d.index.get_level_values(
                dims[2] ).unique().sort_values()

            for lat in latitude:
                for lon in longitude:
                    df_xs_m = df_m.loc[ (slice(None), lat, lon),
                        df_m.columns ].sort_values("q_model")
                    df_xs_d = df_d.loc[ (slice(None), lat, lon),
                        df_d.columns ].sort_values("q_model")
                    df_xs_m["map"] = np.interp( df_xs_m["q_model"].values,
                        df_xs_d["q_model"].values, df_xs_d[v].values )
                    df_xs_m["map"] = df_xs_m["map"].where(df_xs_m["map"]>0, 0)
                    if sum:
                        df_xs_m["diff_sum"] = df_xs_m["map"] - df_xs_m[v]
                    else:
                        df_xs_m["diff_div"] = df_xs_m["map"] / df_xs_m[v]
                    df_m.loc[ (slice(None), lat, lon), df_m.columns ] = df_xs_m

                    #df_xs_f = df_f.loc[ (slice(None), lat, lon), 
                    #    df_f.columns ].sort_values("q_model")
                    #if sum:
                    #    df_xs_f["map"] = np.interp( df_xs_f["q_model"].values,
                    #    df_xs_m["q_model"].values,
                    #    df_xs_m["diff_sum"].values )
                    #df_xs_f["map"] = df_xs_f["map"] + df_xs_f[v]
                    #else:
                    #    df_xs_f["map"] = np.interp( df_xs_f["q_model"].values,
                    #        df_xs_m["q_model"].values,
                    #        df_xs_m["diff_div"].values )
                    #    df_xs_f["map"] = df_xs_f["map"] * df_xs_f[v]
                    #df_xs_f["map"] = df_xs_f["map"].where(df_xs_f["map"]>0, 0)
                    #df_f.loc[ (slice(None), lat, lon), df_f.columns ] = df_xs_f

            ds_map = df_m.to_xarray()
            ds_m["map"] = ( dims, ds_map["map"].values )
            if sum:
                ds_m["diff_sum"] = ( dims, ds_map["diff_sum"].values )
            else:
                ds_m["diff_div"] = ( dims, ds_map["diff_div"].values )
            ds_m.to_netcdf( path_res )
            ds_m[["map"]].rename( {"map": v} ).to_netcdf( path_map )

            #ds_fmap = df_f.to_xarray()
            #ds_f["map"] = ( dims, ds_fmap["map"].values )
            #ds_f[["map"]].rename( {"map": v} ).to_netcdf( path_fmap )