import os

import numpy as np
import pandas as pd

import xarray as xr

path_d = "../temp/quantile_vars/"
path_r = "../temp/quantile_vars_model/"

vars = [ "Pressure", "Relative_Humidity", "Temperature",
    "Wind_Direction", "Wind_Speed", "DNI", "GHI", "UVHI" ]

for v in vars:
    files = os.listdir(path_d)
    if ".DS_Store" in files: files.remove(".DS_Store")

    with xr.open_dataset(path_d + v + "/" + files[0]) as ds:
        df = ds.to_dataframe()
        if v in vars[-3:]: df = df[ df>0 ].dropna()
        latitude = df.index.get_level_values("lat").unique()
        longitude = df.index.get_level_values("lon").unique()
        time = df.index.get_level_values("time").unique()
        df = df.reset_index().set_index(["lat", "lon"]).sort_index()

        df["q_model"] = 0.0
        for lat in latitude:
            for lon in longitude:
                df_c = df.xs( (lat, lon) ).sort_values(v)
                q_model = np.linspace( 1/df_c.shape[0], 1, df_c.shape[0] )
                df_c["q_model"] = q_model
                df.loc[ (lat, lon) ] = df_c

        df = df.reset_index().set_index(
            ["time", "lat", "lon"] ).sort_index()
        df.to_xarray().transpose( "time", "lat", "lon"
            ).to_netcdf(path_r + v + "/" + files[0], mode = "w" )