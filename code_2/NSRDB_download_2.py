import urllib.request
import pandas as pd
import numpy as np
import requests
import os
import time
import urllib

y = 2022
interval = "30"
base = "full-disc-download"
attributes = ( "air_temperature,dni,ghi,surface_pressure,wind_speed" )
api_key = "gyt9NnH5zFXLcbeHV8uvPedVOFi2fWnVmIfvFlNS"
leap_year = "true"
utc = "false"
name = "Gustavo+Sanchez"
reason = "academic+research"
affiliation = "UNAM"
email = "rodrigo.munos@atmosfera.unam.mx"
mailing_list = "false"

lat = np.around(np.arange(24.92, 42.02, 0.02), 2)
lon = np.around(np.arange(-124.41, -86.69, 0.02), 2)
X, Y = np.meshgrid(lon, lat)
points = np.array(list(zip(X.flatten(), Y.flatten()))).astype(str)
points = np.array([" ".join(x) for x in points])
mpoints = []
length = int(lon.shape[0]/2)
for i in range(points.shape[0] // length):  mpoints.append(
    "MULTIPOINT(" + ", ".join(points[i*length:(i+1)*length]) + ")")
for wkt in mpoints:
    start = mpoints.index(wkt)*length
    end = (mpoints.index(wkt)+1)*length-1
    if end > len(points): end = len(points)-1
    start_p = points[start].replace(" ", "_")
    end_p = points[end].replace(" ", "_")

    start_lon = f"{float(start_p.split("_")[0])-0.01:.2f}"
    start_lat = f"{float(start_p.split("_")[1])-0.01:.2f}"
    start_p = f"{float(start_lat)+0.01:.2f}_{float(start_lon)+0.01:.2f}"
    end_lon   = f"{float(end_p.split("_")[0])+0.01:.2f}"
    end_lat   = f"{float(end_p.split("_")[1])+0.01:.2f}"
    end_p = f"{float(end_lat)-0.01:.2f}_{float(end_lon)-0.01:.2f}"
    wkt = ( f"POLYGON(({start_lon} {start_lat}, {start_lon} {end_lat}, "
        + f"{end_lon} {end_lat}, {end_lon} {start_lat}, "
        + f"{start_lon} {start_lat}))" )
    wkt.replace(", ", "%2C").replace(" ", "%20")

    wkt = wkt.replace(", ", "%2C").replace(" ", "%20")
    url = ( "https://developer.nrel.gov/api/nsrdb/v2/solar/" +
        f"{base}.json?wkt={wkt}&names={y}&leap_day=" +
        f"{leap_year}&interval={interval}&utc={utc}&full_name=" +
        f"{name}&email={email}&affiliation={affiliation}" +
        f"&mailing_list={mailing_list}&reason={reason}&api_key=" +
        f"{api_key}&attributes={attributes}" )
    url = url.replace(",", "%2C")
    json = requests.get(url).json()

    if json["status"] == 429: raise Exception("Too many requests")
    if json["status"] == 400:
        url = None
        if json["errors"][0][19:] == "User currently owns":
            raise Exception("Too many requests")
    else:
        url = json["outputs"]["downloadUrl"]
        urllib.request.urlretrieve(url,
            f"../../temp/recurso_solar/duck_curve/{i}.zip")
    data = pd.DataFrame(columns = ["status", "downloadURL",
        "start_point", "end_point", "wkt"],
        data = [[json["status"], url, start_p, end_p, wkt]])
    if os.path.exists("../../temp(recurso_solar/duck_curve/NSRDB_json.csv"):
        data = pd.concat([pd.read_csv(
            "../../temp(recurso_solar/duck_curve/NSRDB_json.csv"), data])
    data.to_csv("../results/NSRDB_json.csv", index = False)
    time.sleep(87)