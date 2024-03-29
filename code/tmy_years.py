# Calculamos el TMY para todos los puntos.
import os

import itertools as it

import numpy as np
import pandas as pd

import xarray as xr

# Cargamos el archivo.
path_d = "temp/vars_days/"
path_r = "temp/TMY_years/"

#perc   = [ "0.25", "0.75" ]
#perc_n = [ 1/4,    3/4    ] 
perc   = [ "0.33", "0.66" ]
perc_n = [ 1/3,    2/3    ] 
#N = 5

# Datos.
months = np.arange(1, 13)
vnames = [ "GHI", "DNI", "T_max", "T_min", "T_mean", 
        "Dp_min", "Dp_max", "Dp_mean", "W_max", "W_mean" ]
path_v = [ f"{path_d}{x}/" for x in vnames ]

files = os.listdir(path_v[0])
if ".DS_Store" in files: files.remove(".DS_Store")
dsets = [ x + files[0] for x in path_v ]
f = files[0]
    
with xr.open_mfdataset( [ x + f for x in path_v ]
    ).drop_dims("bnds") as ds:

    df = ds.to_dataframe()

    latitude = df.index.get_level_values("south_north").unique()
    longitude = df.index.get_level_values("west_east").unique()
    years = df.index.get_level_values("XTIME").year.unique()
    N = years.shape[0]

    mo = np.tile( np.tile( months, len(longitude) ), len(latitude) )
    la = np.tile( np.repeat(latitude, len(months) ), len(longitude) )
    lo = np.repeat( np.repeat(longitude, len(months) ), len(latitude) )
    y = np.zeros_like(mo)

    y_list = pd.DataFrame( [ la, lo, mo, y ] ).T
    y_list.columns = [ "south_north", "west_east", "Month", "Year" ]
    y_list = y_list.set_index( ["south_north",
        "west_east", "Month"] ).sort_index()

    # Iteramos para cada celda.
    for lat in latitude:
        for lon in longitude:
            df_d = df.xs( (lat, lon),
                level = ["south_north", "west_east"] )

            # Cálculo del estadístico Finkelstein-Schafer.

            # Iteramos para cada variable.
            ls_fs = []
            ls_t  = []
            for v in vnames:

                # Creamos los dataframes que usaremos.
                fs = pd.DataFrame( columns = months, index = years )
                fs_y = fs.copy()
                fs_t = fs.copy()

                # Iteramos para cada mes y cada año.
                for m in months:
                    for y in years:
                        # Seleccionamos un mes y un año y
                        # calculamos su distribución acumulada.
                        df_my = df_d.loc[ ( df_d.index.year == y )
                            & ( df_d.index.month == m ), [v]
                            ].sort_values(v).reset_index( drop = True )
                        df_my.index = ( df_my.index + 1 ) / df_my.shape[0]
                        # Seleccionamos un mes para todos los años y 
                        # calculamos su distribución acumulada.
                        df_m = df_d.loc[ ( df_d.index.month == 1 ), [v]
                            ].sort_values(v).reset_index( drop = True
                            ).reset_index().rename(
                            {"index": "CDF_TOT"}, axis = 1 )
                        df_m["CDF_TOT"] = ( ( df_m["CDF_TOT"] + 1 )
                            / df_m.shape[0] )
                        # Interpolamos la información para
                        # cada año para poder comparar con
                        # la información para todos los años.
                        df_m["CDF"] = np.interp( df_m[ v ].values,
                            df_my[ v ].values, df_my.index )
                        # Calculamos el estadístico de
                        # Finkelstein-Schafer como la resta de 
                        # las dos distribuciones acumuladas.
                        fs.loc[y, m] = np.abs(
                            df_m["CDF_TOT"] - df_m["CDF"] ).sum()

                    # Ordenamos los estadísticos de menor a
                    # mayor y anotamos su año correspondiente.
                    fs_t[ m ] = fs[ m ].copy()

                # Reiniciamos los índices y
                # agregamos las tablas a una lista.
                ls_t.append(fs_t)

            # Pesos para la suma del estadístico FS., método NSRDB.
            weights = np.array( [ [ 5/24, 5/24, 1/24, 1/24,
                2/24, 1/24, 1/24, 2/24, 1/24, 1/24 ] ] ).T

            # Aplicamos los pesos, umamos el estadístico de cada año
            # para todas las variables y lo ordenamos de menor a mayor.
            df_t = pd.concat( ls_t,  axis = 0, keys = vnames )
            df_t = ( np.repeat( np.tile(weights, 12),
                years[-1] - years[0] + 1, axis = 0 ) * df_t )
            tot_fs = df_t.groupby( level = 1 ).sum()
            tot_y  = tot_fs.copy()
            for m in months:
                tot_y[m]  = tot_fs[m].sort_values().index.copy()
                tot_fs[m] = tot_fs[m].sort_values().copy()
            tot_fs = tot_fs.reset_index(drop = True)
            tot_y  =  tot_y.reset_index(drop = True)
            tot = pd.concat( [tot_fs, tot_y], axis = 0,
                keys = ["FS", "year"] ).swaplevel(0, 1).sort_index()

            # Unimos los estadísticos para cada variable
            # individual y para todas las variables.
            df_fs = pd.concat( [tot], axis = 0, keys = ["total"] )
            # Hacemos que el índice sea el orden de los datos de 1 a 24.
            df_fs.index = df_fs.index.set_levels( range( 1,
                df_fs.index.get_level_values(1).shape[0] + 1 ), level = 1)


            # Evaluación de la persistencia meteorológica.

            # Función que compara menor o mayor que dependiendo del caso.
            def comp(x):
                if i == 0: return x <= p
                else:      return x >= p

            # Iteramos para el caso del percentil 0.33 y 0.66, 
            # para cada variable y para cada mes.
            #df_run = [ df_d.copy(), df_d.copy() ]
            # solo para las variables GHI y T_mean.
            vars_p = ["GHI", "T_mean"]
            df_run = [ df_d[ vars_p ].copy(), df_d[ vars_p ].copy() ]
            for i in range( len(df_run) ):
                #for v in vnames:
                for v in vars_p:
                    for m in months:
                        # Seleccionamos un mes para todos los años y 
                        # calculamos su distribución acumulada.
                        df_m = df_d.loc[ df_d.index.month == m, [v]
                            ].sort_values( v ).reset_index( drop = True
                            ).reset_index().rename(
                            {"index": "CDF_TOT"}, axis = 1 )
                        df_m["CDF_TOT"] = ( ( df_m["CDF_TOT"] + 1 )
                            / df_m.shape[0] )

                        # Calculamos el percentil
                        # 0.33 o 0.66, según sea el caso.
                        p = df_m.loc[ (df_m["CDF_TOT"] <= perc_n[i] + 1e-3)
                            & (df_m["CDF_TOT"] >= perc_n[i] - 1e-3),
                            v ].mean()

                        # Convertimos las corridas que son
                        # menores o exceden el percentil en  
                        # unos y el resto de valores en ceros.
                        df_run[i].loc[ df_d.index.month == m, v
                            ] = np.where(
                            df_d.loc[
                            (df_d.index.month==m), v ].apply(comp),
                            np.ones_like(
                            df_d.loc[df_d.index.month==m, v] ),
                            np.zeros_like(
                            df_d.loc[df_d.index.month==m, v] ) )
                        
            # Unimos las tablas de los dos percentiles.
            df_r = pd.concat( df_run, axis = 1, keys = perc
                ).swaplevel( 0, 1, axis = 1 ).sort_index(axis = 1)

            # Creamos una tabla resumen para
            # las estadísticas de las corridas.
            a = pd.DataFrame( index = years, columns = months )
            b = pd.concat( [a] * 3, axis = 1,
                keys = ["number", "max", "pass"]
                ).swaplevel(0, 1, axis = 1).sort_index(axis = 1)
            c = pd.concat( [b] * 2, axis = 1, keys = perc
                ).swaplevel(0, 1, axis = 1).sort_index(axis = 1)
            df_nr = pd.concat( [c] * len(vnames),
                axis = 1, keys = vnames )

            # Iteramos para el percentil 0.33 y 0.66.
            for p in perc:
                # Iteramos para cada variable, cada mes, y cada año.
                #for v in vnames:
                # Iteramos para cada GHI y T_mean, cada mes, y cada año.
                for v in vars_p:
                    for m in months:
                        for y in years:
                            # Seleccionamos un mes y un año.
                            a = df_r.loc[ (df_r.index.year == y)
                                & (df_r.index.month == m), (v, p) ]
                            # Obtenemos los datos de las corridas
                            # de unos y eliminamos los ceros.
                            nr = pd.DataFrame( [ (i, len(list(g))) 
                                for i, g in it.groupby(a) ] )
                            nr = nr.where( nr.loc[:, 0] == 1,
                                np.nan ).dropna()
                            # Encontramos la corrida más larga
                            # y contamos la cantidad de corridas.
                            df_nr.loc[y, (v, m, p)] = [
                                nr.loc[:, 1].max(),
                                nr.loc[:, 0].sum(), np.nan ]

                # Calculamos los años que pasan para cada percentil.
                df_nr.loc[:, (slice(None), slice(None), p, "pass")] = ~(
                    ( (df_nr.max() == df_nr).loc[
                    :, (slice(None), slice(None), p, "max") ] ).values
                    + ( (df_nr.max() == df_nr).loc[
                    :, (slice(None), slice(None), p, "number") ] ).values )

            # Para GHI solo se considera p = 0.33.
            df_nr.loc[:, ("GHI", slice(None), perc[1], "pass")] = True

            # Calculamos los años que hay que
            # desechar por el criterio de persistencia.
            reject = pd.DataFrame( index = years, columns = months )
            for m in months:
                reject.loc[:, m] = df_nr.loc[ :,
                    ( slice(None), m, slice(None), "pass" ) ].all(axis = 1)
            reject = reject.where(reject == False, np.nan)

            # El último mes de la corrida de WRF está
            # incompleto por 6 horas, siempre se quita.
            reject.iloc[-1, -1] = False

            # Junio de 1993 está incompleto por 6 horas, siempre se quita.
            reject.loc[1993, 6] = False

            # Obtenemos la selección final de años para el TMY.

            # Creamos la lista de años para cada mes.
            df_list = pd.DataFrame( columns = ["year"], index = months )

            # Empezamos los años con el menor estadístico FS.
            n = 1
            # Iteramos para cada mes
            for m in months:
                # Verificamos si el año pasa o
                # no el criterio de persistencia.
                if not( df_fs.loc[ ("total", n, "year"), m ]
                    in reject[m].dropna().index ):
                    df_list.loc[m] = df_fs.loc[ ("total", n, "year"), m ]

            # Iteramos para los siguientes N valores de FS.
            for n in range(2, N + 1):
                # Solo iteramos para los meses que no pasaron el
                # criterio de persistencia en el ciclo pasado.
                for m in df_list[ df_list.isnull().any(axis = 1) ].index:
                    if not( df_fs.loc[ ("total", n, "year"), m ]
                        in reject[m].dropna().index ):
                        df_list.loc[m] = df_fs.loc[
                            ("total", n, "year"), m ]

            # Revisamos si se cubrieron todos
            # los meses con los 5 años seleccionados.
            #if df_list.isnull().sum().values[0] > 0:
            #    print( "Error: no se pudo asignar al menos un mes" )
                    
            y_list.loc[ (lat, lon) ] = df_list.values

    # Guardamos el archivo.
    ds_yl = y_list.to_xarray()
    ds_yl["Month"] = ds_yl["Month"].astype(np.int32)
    ds_yl["Year"] = ds_yl["Year"].astype(np.int32)
    ds_yl["south_north"] = ds_yl["south_north"].astype(np.int32)
    ds_yl["west_east"] = ds_yl["west_east"].astype(np.int32)
    ds_yl.to_netcdf(path_r + f)