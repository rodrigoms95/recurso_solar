# Calculamos el TMY para todos los puntos.

import os
import sys

import itertools as it

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import scipy.stats as stats
import scipy.interpolate as interp

# Datos.
y_i = sys.argv[1]
y_f = sys.argv[2]
path_d = "results/NSRDB/"
path_r = "temp/NetCDF/"
files = os.listdir(path_d)
if ".DS_Store" in files: files.remove(".DS_Store")
for f in files:
    lat = f[0:5]
    lon = f[-10:-4]
    years  = list( range( int(y_i), int(y_f) + 1) )
    months = list( range(1, 13) )
    columns = [ "Temperature", "Dew Point",
        "Wind Speed", "GHI", "Wind Direction" ]

    # Cargamos el archivo.
    df = pd.read_csv( path_d + f, index_col = "time", parse_dates = True,
        infer_datetime_format = True )

    # Obtenemos la información diaria.
    vnames = [ "GHI", "T_max", "T_min", "T_mean", 
        "Dp_min", "Dp_max", "Dp_mean", "W_max", "W_mean" ]
    df_d = df[ [vnames[0]] ].resample("D").sum()
    df_d[vnames[1]] = df[ "Temperature" ].resample("D").min()
    df_d[vnames[2]] = df[ "Temperature" ].resample("D").max()
    df_d[vnames[3]] = df[ "Temperature" ].resample("D").mean()
    df_d[vnames[4]] = df[ "Dew Point"   ].resample("D").min()
    df_d[vnames[5]] = df[ "Dew Point"   ].resample("D").max()
    df_d[vnames[6]] = df[ "Dew Point"   ].resample("D").mean()
    df_d[vnames[7]] = df[ "Wind Speed"  ].resample("D").max()
    df_d[vnames[8]] = df[ "Wind Speed"  ].resample("D").mean()

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
                    & ( df_d.index.month == m ), [v] ].sort_values( v
                    ).reset_index( drop = True )
                df_my.index = ( df_my.index + 1 ) / df_my.shape[0]
                # Seleccionamos un mes para todos los años y 
                # calculamos su distribución acumulada.
                df_m = df_d.loc[ ( df_d.index.month == 1 ), [v]
                    ].sort_values( v ).reset_index( drop = True
                    ).reset_index().rename( {"index": "CDF_TOT"}, axis = 1 )
                df_m["CDF_TOT"] = ( df_m["CDF_TOT"] + 1 ) / df_m.shape[0]
                # Interpolamos la información para cada año para poder
                # comparar con la información para todos los años.
                df_m["CDF"] = np.interp( df_m[ v ].values,
                    df_my[ v ].values, df_my.index )
                # Calculamos el estadístico de Finkelstein-Schafer
                # como la resta de las dos distribuciones acumuladas.
                fs.loc[y, m] = np.abs( df_m["CDF_TOT"] - df_m["CDF"] ).sum()

            # Ordenamos los estadísticos de menor a
            # mayor y anotamos su año correspondiente.
            fs_t[ m ] = fs[ [m] ].values

        # Reiniciamos los índices y agregamos las tablas a una lista.
        ls_t.append(fs_t)

    # Pesos para la suma del estadístico FS.
    # Método Sandía.
    #weights = np.array( [ [ 12/24, 1/24, 1/24, 2/24, 1/24,
    #    1/24, 2/24, 2/24, 2/24 ] ] ).T
    # Método NSRDB.
    weights = np.array( [ [ 10/24, 1/24, 1/24, 2/24, 1/24,
        1/24, 2/24, 1/24, 1/24 ] ] ).T

    # Aplicamos los pesos, umamos el estadístico de cada año
    # para todas las variables y lo ordenamos de menor a mayor.
    df_t = pd.concat( ls_t,  axis = 0, keys = vnames )
    df_t = ( np.repeat( np.tile(weights, 12),
        int(y_f) - int(y_i) + 1, axis = 0 ) * df_t )
    tot_fs = df_t.groupby( level = 1 ).sum()
    tot_y  = tot_fs.copy()
    for m in months:
        tot_y[ m ]  = tot_fs[ [m] ].sort_values(m).index.values
        tot_fs[ m ] = tot_fs[ [m] ].sort_values(m).values
    tot_fs = tot_fs.reset_index(drop = True)
    tot_y  =  tot_y.reset_index(drop = True)
    tot = pd.concat( [tot_fs, tot_y], axis = 0, keys = ["FS", "year"]
            ).swaplevel(0, 1).sort_index()

    # Unimos los estadísticos para cada variable
    # individual y para todas las variables.
    df_fs = pd.concat( [tot], axis = 0, keys = ["total"] )
    # Aseguramos que el año sea un número entero.
    df_fs.loc[ (slice(None), slice(None), "year") ] = (
        df_fs.loc[ (slice(None), slice(None), "year") ].astype(int) )
    # Hacemos que el índice sea el orden de los datos de 1 a 24.
    df_fs.index = df_fs.index.set_levels( range( 1,
        df_fs.index.get_level_values(1).shape[0] + 1 ), level = 1)


    # Evaluación de la persistencia meteorológica.

    # Función que compara menor o mayor que dependiendo del caso.
    def comp(x):
        if i == 0: return x <= p
        else:      return x >= p

    # Iteramos para el caso der percentil 0.33 y 0.66, 
    # para cada variable y para cada mes.
    #df_run = [ df_d.copy(), df_d.copy() ]
    df_run = [ df_d[ ["GHI", "T_mean"] ].copy(),
        df_d[ ["GHI", "T_mean"] ].copy() ]
    for i in range( len(df_run) ):
        #for v in vnames:
        for v in ["GHI", "T_mean"]:
            for m in months:
                # Seleccionamos un mes para todos los años y 
                # calculamos su distribución acumulada.
                df_m = df_d.loc[ df_d.index.month == m, [v]
                    ].sort_values( v ).reset_index( drop = True
                    ).reset_index().rename( {"index": "CDF_TOT"}, axis = 1 )
                df_m["CDF_TOT"] = ( df_m["CDF_TOT"] + 1 ) / df_m.shape[0]

                # Calculamos el percentil 0.33 o 0.66, según sea el caso.
                p = df_m.loc[ (df_m["CDF_TOT"] <= (i+1)/3 + 1e-3)
                    & (df_m["CDF_TOT"] >= (i+1)/3 - 1e-3), v
                    ].mean()

                # Convertimos las corridas que son menores o exceden
                # el percentil en unos y el resto de valores en ceros.
                df_run[i].loc[ df_d.index.month == m, v ] = np.where(
                    df_d.loc[ ( df_d.index.month == m ), v ].apply(comp),
                    np.ones_like( df_d.loc[ ( df_d.index.month == m ), v ] ),
                    np.zeros_like( df_d.loc[ ( df_d.index.month == m ), v ] ) )
            
    # Unimos las tablas de los dos percentiles.
    df_r = pd.concat( df_run, axis = 1, keys = ["0.33", "0.66"] ).swaplevel(
        0, 1, axis = 1 ).sort_index(axis = 1)

    # Creamos una tabla resumen para las estadísticas de las corridas.
    a = pd.DataFrame( index = years, columns = months )
    b = pd.concat( [a] * 3, axis = 1, keys = ["number", "max", "pass"]
        ).swaplevel(0, 1, axis = 1).sort_index(axis = 1)
    c = pd.concat( [b] * 2, axis = 1, keys = ["0.33", "0.66"]
        ).swaplevel(0, 1, axis = 1).sort_index(axis = 1)
    df_nr = pd.concat( [c] * len(vnames), axis = 1, keys = vnames )

    # Iteramos para cada variable, cada mes, y cada año.   
    for p in ["0.33", "0.66"]:         
        #for v in vnames:
        for v in ["GHI", "T_mean"]:
            for m in months:
                for y in years:
                    # Seleccionamos un mes y un año.
                    a = df_r.loc[ (df_r.index.year == y)
                        & (df_r.index.month == m), (v, p) ]
                    # Obtenemos los datos de las corridas
                    # de unos y eliminamos los ceros.
                    nr = pd.DataFrame( [ (i, len(list(g))) 
                        for i, g in it.groupby(a) ] )
                    nr = nr.where( nr.loc[:, 0] == 1, np.nan ).dropna()
                    # Encontramos la corrida más larga
                    # y contamos la cantidad de corridas.
                    df_nr.loc[y, (v, m, p)] = [
                        nr.loc[:, 1].max(), nr.loc[:, 0].sum(), np.nan ]

        # Calculamos los años que pasan para cada percentil.
        df_nr.loc[:, (slice(None), slice(None), p, "pass")] = ~(
            ( (df_nr.max() == df_nr).loc[
            :, (slice(None), slice(None), p, "max") ] ).values
            + ( (df_nr.max() == df_nr).loc[
            :, (slice(None), slice(None), p, "number") ] ).values )

    # Calculamos los años que hay que desechar por el criterio de persistencia.
    reject = pd.DataFrame( index = years, columns = months )
    for m in months:
        reject.loc[:, m] = df_nr.loc[ :,
            ( slice(None), m, slice(None), "pass" ) ].all(axis = 1)
    reject = reject.where(reject == False, np.nan)


    # Obtenemos la selección final de años para el TMY.

    # Creamos la lista de años para cada mes.
    df_list = pd.DataFrame( columns = ["year"], index = range(1, 13) )

    # Empezamos los años con el menor estadístico FS.
    n = 1
    # Iteramos para cada mes
    for m in range(1, 13):
        # Verificamos si el año pasa o no el criterio de persistencia.
        if not( df_fs.loc[ ("total", n, "year"), m ]
            in reject[m].dropna().index ):
            df_list.loc[m] = df_fs.loc[ ("total", n, "year"), m ]

    # Iteramos para los siguientes 4 valores de FS.
    for n in range(2, 6):
        # Solo iteramos para los meses que no pasaron el
        # criterio de persistencia en el ciclo pasado.
        for m in df_list[ df_list.isnull().any(axis = 1) ].index:
            if not( df_fs.loc[ ("total", n, "year"), m ]
                in reject[m].dropna().index ):
                df_list.loc[m] = df_fs.loc[ ("total", n, "year"), m ]

    # Revisamos si se cubrieron todos los meses con los 5 años seleccionados.
    if df_list.isnull().sum().values[0] > 0:
        print( "Error: no se pudo asignar al menos un mes" )
        
    df_list = df_list.astype(int)

    # Construimos el TMY.  

    # Empezamos el TMY con el año correspondiente al mes 1.
    df_tmy = df[ (df.index.month == df_list.index[0])
        & (df.index.year == df_list.loc[1, "year"]) ].copy()
    df_tmy["year"] = df_list.loc[1, "year"]

    # Agregamos el resto de los meses.
    for row in df_list.loc[2:].itertuples():
        # Seleccionamos el mes del año correspondiente.
        df_m = df[ (df.index.month == row.Index)
            & (df.index.year == row.year) ].copy()
    
        # Suavizamos 6 horas con un spline.
        x   = months
        y_1 = ( list( df_tmy.iloc[-6:, -2].values )
            + list( df_m.iloc[0:6, -2].values ) )
        y_2 = ( list( df_tmy.iloc[-6:, -1].values )
            + list( df_m.iloc[0:6, -1].values ) )
        z_1 = interp.splev( x, interp.splrep( x, y_1, s = 10 ) )
        z_2 = interp.splev( x, interp.splrep( x, y_2, s = 10 ) )
        df_tmy.iloc[-6:, -2] = z_1[0:6]
        df_tmy.iloc[-6:, -1] = z_2[0:6]
        df_m.iloc[  0:6, -2] = z_1[6:]
        df_m.iloc[  0:6, -2] = z_2[6:]

        df_m["year"] = row.year
    
        # Unimos los meses.
        df_tmy = df_tmy.append( df_m )

    # Damos formato a la tabla.
    #df_tmy["year"] = df_tmy["year"].astype(int)
    #df_tmy["month"] = df_tmy.index.month
    #df_tmy["day"] = df_tmy.index.day
    #df_tmy["hour"] = df_tmy.index.hour
    #df_tmy = df_tmy[ ["year", "month", "day", "hour"] + columns
    #    ].reset_index( drop = True )

    # Convertimos a Dataset.
    df_tmy = df_tmy.reset_index()
    df_tmy["lat" ] = float(lat)
    df_tmy["lon"] = float(lon)
    ds = df_tmy.set_index( ["time", "lat", "lon"]
        ).astype( float ).round( decimals = 1 ).to_xarray()
    #ds = df_tmy.set_index( ["lat", "lon", "month", "day", "hour"] ).astype(
    #    float ).round( decimals = 1 ).to_xarray()
    ds["lat"] = ds["lat"].assign_attrs( standard_name = "latitude",
        long_name = "Latitude", units = "degrees" )
    ds["lon"] = ds["lon"].assign_attrs(standard_name = "longitude",
        long_name = "Longitude", units = "degrees" )
    ds["time"] = pd.date_range( "01/01/2001 00:00:00",
        "31/12/2001 23:00:00", freq = "H" )
    ds.to_netcdf(f"{path_r}{lat}_{lon}.nc")