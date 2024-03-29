# Calculamos el TMY para todos los puntos.
import os

import numpy as np
import pandas as pd

import xarray as xr

import scipy.interpolate as interp

months = np.arange(1, 13)
m_d = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
vars = ["Temperature", "Pressure", "Wind_Speed",
    "Wind_Direction", "Relative_Humidity" ]

# Cargamos el archivo.
path_d = "temp/radiacion/"
path_y = "temp/TMY_years/"
path_r = "temp/TMY/"

TZ = -6

files = os.listdir(path_d)
files.sort()
if ".DS_Store" in files: files.remove(".DS_Store")
f = files[0]

# Abrimos la lista de años.
with xr.open_dataset( path_y + f ) as ds_y:
    # Abrimos los datos para todos los años.
    with xr.open_dataset( path_d + f,
        drop_variables = "Dew_Point" ) as ds:
        # Recorremos de UTC a tiempo local.
        ds["XTIME"] = ds.indexes["XTIME"].shift(TZ, "h")
        # Quitamos los 29 de febrero.
        ds = ds.sel( {"XTIME": ~( (ds["XTIME"].dt.month == 2)
            & (ds["XTIME"].dt.day == 29) ) } )
        # Creamos la variable de año.
        ds["Year"] = ds["Temperature"].astype(np.int32).copy()
        # Creamos un Dataset de solo un año.
        ds_tmy = ds.isel({"XTIME": slice(0, 8760)}).copy()
        ds_tmy["XTIME"] = pd.date_range( "01/01/2001 00:00:00",
            "31/12/2001 23:00:00", freq = "h" )

        # Iteramos para todas las celdas.
        for lat in ds["south_north"].values:
            for lon in ds["west_east"].values:
                # Iteramos para todos los meses.
                for m in months:
                    # Obtenemos el año que corresponde al mes
                    # y asignamos esa información al TMY.
                    y = ds_y.loc[ {"south_north": [lat],
                        "west_east": [lon], "Month": [m]} ].to_array()
                    ds_m = ds.loc[ {"XTIME": ( ds["XTIME"].dt.month.isin(m)
                        & ds["XTIME"].dt.year.isin(y) ),
                        "south_north": [lat], "west_east": [lon]} ]
                    ds_m["Year"] = ds_m["XTIME"].dt.year
                    ds_m["XTIME"] = ds_tmy.loc[ { "XTIME":
                        ds_tmy["XTIME"].dt.month.isin(m) } ]["XTIME"]
                    ds_tmy.loc[ {"XTIME": ds_tmy["XTIME"].dt.month.isin(m),
                        "south_north": [lat], "west_east": [lon]} ] = ds_m
                    
                # Suavizamos 6 horas con un spline.
                for m in months[:-1]:
                    # Iteramos para todas las variables
                    # menos las de radiación.
                    for v in vars:
                        ds_i = ds_tmy.loc[ { "XTIME": ( ( 
                            ds_tmy["XTIME"].dt.month.isin([m])
                            &  ds_tmy["XTIME"].dt.day.isin([m_d[m-1]])
                            &  ds_tmy["XTIME"].dt.hour.isin(range(18, 24)) )
                            | ( ds_tmy["XTIME"].dt.month.isin([m+1])
                            &  ds_tmy["XTIME"].dt.day.isin([1])
                            & ds_tmy["XTIME"].dt.hour.isin(range(0, 6)) ) ),
                            "south_north": lat, "west_east": lon } ][v]
                        ds_i = interp.splev( months,
                            interp.splrep( months, ds_i.values ) )

        # Guardamos el archivo.         
        ds_tmy.to_netcdf(path_r + f)