# Corrección de cuantiles empírica.
import os
import sys
import numpy as np
import pandas as pd
import xarray as xr

# Cargamos datos.
scn      = sys.argv[1]
scn_hist = "1985_2014"
file     = sys.argv[2]
dir_o    = "/datos/rodr/Datos/WRF/"
dir_d    = f"{dir_o}{scn}/"

# Observado.
path_d    = f"{dir_o}/NSRDB_cdf.nc"
# Modelo histórico.
path_m    = f"{dir_o}{scn_hist}/{scn_hist}{file}_cdf.nc"
path_f    = f"{dir_o}{scn}/{scn}{file}_cdf.nc"
path_res  = f"{dir_o}{scn}/{scn}{file}_mapres.nc"
path_map  = f"{dir_o}{scn}/{scn}{file}_map.nc"
path_fmap = f"{dir_o}{scn}/{scn}{file}_map.nc"

dims = ["XTIME", "south_north", "west_east"]

with xr.open_dataset(path_m,
    chunks = {"south_north": 10, "west_east": 10}) as ds_m:
    with xr.open_dataset(path_d,
        chunks = {"south_north": 10, "west_east": 10}) as ds_d:
        with xr.open_dataset(path_f,
            chunks = {"south_north": 10, "west_east": 10}) as ds_f:

            vars    = ds_m.keys()
            ds_res  = ds_m.drop_vars(vars)
            ds_map  = ds_d.drop_vars(vars)
            ds_fmap = ds_f.drop_vars(vars)

            for v in vars:

                df_d = ds_d.to_dataframe().sort_index(
                    ).drop_vars(["XLAT", "XLONG"])
                df_m = ds_m.to_dataframe().sort_index(
                    ).drop_vars(["XLAT", "XLONG"])
                df_f = ds_f.to_dataframe().sort_index(
                    ).drop_vars(["XLAT", "XLONG"])
                df_f["map"] = None
                df_m["map"] = None
                if sum: df_m["diff_sum"] = None
                else: df_m["diff_div"] = None

                latitude = df_d.index.get_level_values(
                    "south_north" ).unique().sort_values()
                longitude = df_d.index.get_level_values(
                    "west_east" ).unique().sort_values()

                for lat in latitude:
                    for lon in longitude:
                        df_xs_m = df_m.loc[ (slice(None), lat, lon),
                            df_m.columns ].sort_values("q_model")
                        df_xs_d = df_d.loc[ (slice(None), lat, lon),
                            df_d.columns ].sort_values("q_model")
                        df_xs_m["map"] = np.interp( df_xs_m["q_model"].values,
                            df_xs_d["q_model"].values, df_xs_d[v].values )
                        df_xs_m["map"] = df_xs_m["map"
                            ].where(df_xs_m["map"]>0, 0)
                        df_xs_m["diff_sum"] = df_xs_m["map"] - df_xs_m[v]
                        df_m.loc[(slice(None), lat, lon),
                            df_m.columns] = df_xs_m

                        df_xs_f = df_f.loc[ (slice(None), lat, lon), 
                            df_f.columns ].sort_values("q_model")
                        if sum:
                            df_xs_f["map"] = np.interp(
                                df_xs_f["q_model"].values,
                                df_xs_m["q_model"].values,
                                df_xs_m["diff_sum"].values )
                        df_xs_f["map"] = df_xs_f["map"] + df_xs_f[v]
                        df_xs_f["map"] = df_xs_f["map"
                            ].where(df_xs_f["map"]>0, 0)
                        df_f.loc[(slice(None), lat, lon),
                            df_f.columns] = df_xs_f

                ds_res["map"]      = df_m.to_xarray()["map"]
                ds_res["diff_sum"] = df_m.to_xarray()["diff_sum"]
                
                ds_map[v]  = ds_res["map"]
                ds_fmap[v] = df_f.to_xarray()["map"]

            delayed_1 =  ds_res.to_netcdf(path_res,  compute = False)
            delayed_2 =  ds_map.to_netcdf(path_map,  compute = False)
            delayed_3 = ds_fmap.to_netcdf(path_fmap, compute = False)