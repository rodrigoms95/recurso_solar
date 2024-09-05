# Decarga una lista de archivos de NSRDB

# Importamos las librerías
import os
import pandas as pd
import numpy as np

# Carpeta destino
carpeta_destino = "../../Datos/NSRDB_2km_duck/"
# Creamos la subcarpeta
if not os.path.exists(carpeta_destino): os.mkdir(carpeta_destino)

# Coordenadas
# Conjunto de datos 4 km, TMY y quantile map
#lat = np.arange(18.09, 20.69, 0.04)
#lon = np.arange(-100.46, -97.259, 0.04)
# Conjunto de datos 2 km, duck curve 
#lat = np.arange(14.54, 42.02, 0.02)
lat = np.arange(27.42, 42.02, 0.02)
lon = np.arange(-124.41, -86.69, 0.02)

# Años a descargar
# Conjunto de datos 4 km, TMY y quantile map
#years = range(1998, 2023)
# Conjunto de datos 2 km, duck curve 
years = [2022]

# Time interval in minutes
# Conjunto de datos 4 km, TMY y quantile map
#interval = "60"
# Conjunto de datos 2 km, duck curve 
interval = "30"

# base de datos
# Conjunto de datos 4 km, TMY y quantile map
#base = "psm3-2-2-download"
# Conjunto de datos 2 km, duck curve 
base = "full-disc-download"

# Variables a extraer
# Conjunto de datos 4 km, TMY y quantile map
#attributes = ( "air_temperature,dew_point,dni,dhi,ghi,relative_humidity," +
#    "solar_zenith_angle,total_precipitable_water,surface_pressure," + 
#    "surface_albedo,wind_direction,wind_speed,ghuv-280-400,ghuv-295-385" )
# Conjunto de datos 2 km, duck curve 
attributes = ( "air_temperature,dni,ghi,surface_pressure,wind_speed" )

# API key
#api_key = "vGnsS1lJcyC5dRKax0H9QIs5e6ottm05OB3uzRRL"
#api_key = "rzX1wbpMOa9fbeBqDfSk3TRcQSf40Ql7ZDk4t50v"
api_key = "XmMWV5ub8RTjyqBGPsjMtmrizT2LaHlhRrxdxylj"

# Leap year
leap_year = "true"
# Coordinated Universal Time (UTC)
utc = "false"
# Full name
#name = "Ariadna+Porras+Cervantes"
#name = "Rodrigo+Munoz"
name = "Rodrigo+Sanchez"
# Reason for using the NSRDB.
reason = "beta+testing"
# Affiliation
affiliation = "UNAM"
# Email address
#email = "aporrasunam@gmail.com"
#email = "rodrigo.munoz@ingenieria.unam.edu"
email = "rodrigoms95@gmail.com"
# Mailing list
mailing_list = "false"

# Iteramos para cada coordenada
for i in lat:
    print(f"{i:.3f}°N")
    for j in lon:
        # Definimos el nombre de la subcarpeta para cada coordenada
        subcarpeta = f'{i:.2f}_{j:.2f}'
        # Definimos la ruta completa de la subcarpeta que se creará
        ruta = f"{carpeta_destino}{subcarpeta}/"
        # Creamos la subcarpeta
        if not os.path.exists(ruta): os.mkdir(ruta)
        # Iteramos para cada año
        for y in years:
            # Definimos el nombre del archivo CSV
            nombre_archivo = f"{i:.2f}_{j:.2f}_{y}.csv"
            # Definimos la ruta absoluta del archivo
            ruta_archivo = f"{ruta}{nombre_archivo}"
            # Descargamos el archivo si no existe
            if not os.path.exists(ruta_archivo):
                print(ruta_archivo)
                # URL string
                url = ( "https://developer.nrel.gov/api/nsrdb/v2/solar/" +
                    f"{base}.csv?wkt=POINT({j}%20{i})&names={y}&leap_day=" +
                    f"{leap_year}&interval={interval}&utc={utc}&full_name=" +
                    f"{name}&email={email}&affiliation={affiliation}" +
                    f"&mailing_list={mailing_list}&reason={reason}&api_key=" +
                    f"{api_key}&attributes={attributes}" )
                # Descargamos archivo csv del url 
                try:    df = pd.read_csv(url,skiprows=2)
                # Si no es una coordenada válida no descargamos y seguimso
                except: pass
                # Guardamoa archivo CSV en la subcarpeta
                else:
                    df.to_csv(ruta + "/" + nombre_archivo, sep = ",",
                        index = False, encoding = "utf-8" )