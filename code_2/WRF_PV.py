# Calcula los la producción fotovoltaica

import os
import sys
import pandas as pd
import numpy as np
import xarray as xr
from dask.diagnostics import ProgressBar

# Funciones trigonométricas.
def sin(x) : return np.sin(np.radians(x))
def cos(x) : return np.cos(np.radians(x))
def tan(x) : return np.tan(np.radians(x))
def asin(x): return np.arcsin(x) * 180/np.pi
def acos(x): return np.arccos(x) * 180/np.pi
def atan(x): return np.arctan(x) * 180/np.pi

# Cargamos datos.
scn   = sys.argv[1]
dir_o = "/home/rodr/buffalo/rodr/WRF/"
dir_d = f"{dir_o}{scn}/data/"
dir_r = f"{dir_o}{scn}/PV/"
if not os.path.exists(dir_r): os.mkdir(dir_r)
files = os.listdir(dir_d)
files.sort

print("Calculando generación fotovoltaica")
for f in files:
    print(f"{f}               ", end = "\r")
    if not os.path.exists(dir_r + f):
        ds = xr.open_dataset(dir_d + f)

        lat = ds["XLAT"]
        lon = ds["XLONG"]
        # Orientación del panel
        array_tilt = lat
        array_azimuth = 180
        # Eccentric anomaly of the earth in its orbit around the sun.
        ds["Day_Angle"] = (6.283185 * (ds["XTIME"].dt.dayofyear-1)/365
            ).astype(np.float32)
        # Declinación.
        ds["Declination"] = ((0.006918 - 0.399912 * np.cos(ds["Day_Angle"])
            + 0.070257*np.sin(ds["Day_Angle"])
            - 0.006758*np.cos(2*ds["Day_Angle"])
            + 0.000907*np.sin(2*ds["Day_Angle"])
            - 0.002697*np.cos(3*ds["Day_Angle"])
            + 0.001480*np.sin(3*ds["Day_Angle"]))
            * 180/np.pi).astype(np.float32)
        # Ecuación del tiempo.
        ds["Time_Equation"] = ((0.000075 + 0.001868*np.cos(ds["Day_Angle"])
            - 0.032077*np.sin(ds["Day_Angle"])
            - 0.014615*np.cos(2*ds["Day_Angle"])
            - 0.040849*np.sin(2*ds["Day_Angle"])) * 229.18).astype(np.float32)
        # Longitud del punto subsolar.
        ds["lon_subs"] = -15 * (ds["XTIME"].dt.hour + ds["Time_Equation"]/60
            ).astype(np.float32)
        # Posiciones del analema solar.
        # cos zenith = Sz
        ds["cos_zenith"] = (sin(lat)*sin(ds["Declination"])
            - cos(lat)*cos(ds["Declination"]) * cos(ds["lon_subs"]-lon)
            ).transpose("XTIME", "south_north", "west_east").astype(np.float32)
        ds = ds.drop_vars(["lon_subs"])
        # Ángulo del cénit solar.
        ds["Zenith_Angle"] = acos(ds["cos_zenith"]).astype(np.float32)
        ds["Zenith_Angle"] = ds["Zenith_Angle"] + xr.where(
            (ds["Zenith_Angle"]==0) | (ds["Zenith_Angle"]==180),
            0.01, 0).astype(np.float32)
        ds["sin_zenith"] = sin(ds["Zenith_Angle"])
        # Ángulo horario.
        ds["Hour_Angle"] = (15 * (ds["XTIME"].dt.hour
            - 12 - ds["Time_Equation"]/60 + lon/15)).astype(np.float32)
        ds["Hour_Angle"] = xr.where(ds["Hour_Angle"]<-180,
            360+ds["Hour_Angle"], ds["Hour_Angle"])
        ds["Hour_Angle"] = xr.where(ds["Hour_Angle"]>180,
            ds["Hour_Angle"]-360, ds["Hour_Angle"])
        ds = ds.drop_vars("Time_Equation")
        # Ángulo acimutal solar.
        ds["Azimuth_Angle"] = acos(((ds["sin_zenith"]*sin(lat)
            - sin(ds["Declination"])) / (ds["sin_zenith"]*cos(lat))
            ).clip(-1, 1)).astype(np.float32)
        ds["Azimuth_Angle"] = (180 + ds["Azimuth_Angle"]
            * xr.where(ds["Hour_Angle"]<=0, -1, 1)).astype(np.float32)
        ds = ds.drop_vars(["Declination", "Hour_Angle"])
        # Masa de aire.
        ds["Air_Mass"] = xr.where(
            ds["Zenith_Angle"] > 90, 0, 1/(ds["cos_zenith"]
            + 0.50572/(96.07995 - ds["Zenith_Angle"].clip(max = 90))**1.6364)
            ).astype(np.float32)
        # Extraterrestrial radiation factor.
        ds["F_etr"] = (cos(ds["Zenith_Angle"]) * 
            ( 1.00011 + 0.034221*np.cos(ds["Day_Angle"])
            + 0.00128*np.sin(ds["Day_Angle"])
            + 0.000719*np.cos(2*ds["Day_Angle"])
            + 0.000077*np.sin(2*ds["Day_Angle"])))
        # Extraterrestrial radiation.
        I_cs   = 1367 # W m-2.
        ds["I_tr"] = I_cs   * ds["F_etr"]
        ds = ds.drop_vars(["Day_Angle", "F_etr"])

        # NREL DISC Model: DNI from GHI (Maxwell, 1987).
        # Effective global horizontal transmittance.
        ds["Kt"] = ds["GHI"] / ds["I_tr"]
        ds["Kt"] = ds["Kt"].where(ds["Kt"] < 1, 1
            ).where( ds["Air_Mass"] > 0, 0).astype(np.float32)
        ds["Kt_2"] = (ds["Kt"] ** 2).astype(np.float32)
        ds["Kt_3"] = (ds["Kt"] ** 3).astype(np.float32)
        # Coeficientes.
        ds["A"] = (-5.743 + 21.77*ds["Kt"]
            - 27.49*ds["Kt_2"] + 11.56*ds["Kt_3"]).where(ds["Kt"] > 0.6,
            (0.512 - 1.56*ds["Kt"] + 2.286*ds["Kt_2"] - 2.222*ds["Kt_3"])
            ).astype(np.float32)
        ds["B"] = (41.4 - 118.5*ds["Kt"] + 66.05*ds["Kt_2"] + 31.9*ds["Kt_3"]
            ).where(ds["Kt"] > 0.6, 0.37 + 0.962*ds["Kt"]).astype(np.float32)
        ds["C"] = (-47.01 + 184.2*ds["Kt"] - 222*ds["Kt_2"] + 73.81*ds["Kt_3"]
            ).where(ds["Kt"] > 0.6,  -0.28 + 0.932*ds["Kt"] - 2.048*ds["Kt_2"]
            ).astype(np.float32)
        ds = ds.drop_vars(["Kt_2", "Kt_3"])
        # Delta Kn.
        ds["D_Kn"] = (ds["A"] + ds["B"] * np.exp(ds["C"] * ds["Air_Mass"])
            ).astype(np.float32)
        ds = ds.drop_vars(["A", "B", "C"])
        # Direct beam atmospheric transmittance under clear-sky conditions.
        ds["Knc"] = (0.866 - 0.122*ds["Air_Mass"] + 0.0121*ds["Air_Mass"]**2
            - 0.000653*ds["Air_Mass"]**3 + 0.000014*ds["Air_Mass"]**4
            ).astype(np.float32)
        # Radiación normal directa.
        ds["DNI"] = ds["I_tr"] * (ds["Knc"] - ds["D_Kn"]
            ).where(ds["Kt"] > 0, 0)
        ds["DNI"] = ds["DNI"].where( ds["DNI"] > 0, 0
            ).astype(np.float32)
        ds = ds.drop_vars(["Knc", "D_Kn", "I_tr", "Kt"])

        # Modelo de Pérez de Cielo Difuso para calcular 
        # la radiación en un plano inclinado
        # Ángulo entre el panel y el sol, Angle of Incidence
        ds["AOI"] = acos((ds["cos_zenith"]*cos(array_tilt)
            + ds["sin_zenith"]*sin(array_tilt)
            * cos(ds["Azimuth_Angle"]-array_azimuth)
            ).clip(-1, 1)).astype(np.float32)
        ds = ds.drop_vars("sin_zenith")
        # Diffuse Horizontal Radiation.
        ds["DHI"] = ds["GHI"] - ds["DNI"] * cos(ds["Zenith_Angle"])
        ds["DHI"] = ds["DHI"].where(ds["DHI"]>0, 0.001)
        K = 5.535e-6
        # Perez clearness bins.
        ds["k_zenith"] = K*ds["Zenith_Angle"]**3
        ds["bins"] = 0
        ds["bins"] = ds["bins"].where( ds["DHI"] == 0,
            ( (ds["DHI"]+ds["DNI"])/ds["DHI"] + ds["k_zenith"] )
            / (1+ds["k_zenith"]) ).astype(np.float32)
        ds = ds.drop_vars("k_zenith")
        ds["DHI"] = ds["DHI"].where(ds["DHI"]>0.001, 0).astype(np.float32)
        ds["epsilon"] = xr.where( (ds["bins"]>6.200),
            8, ds["bins"] ).astype(np.float32)
        ds["epsilon"] = xr.where( (ds["bins"]>4.500)
            & (ds["bins"]<6.200), 7, ds["epsilon"] ).astype(np.float32)
        ds["epsilon"] = xr.where( (ds["bins"]>2.600)
            & (ds["bins"]<4.500), 6, ds["epsilon"] ).astype(np.float32)
        ds["epsilon"] = xr.where((ds["bins"]>1.950)
            & (ds["bins"]<2.600), 5, ds["epsilon"] ).astype(np.float32)
        ds["epsilon"] = xr.where( (ds["bins"]>1.500)
            & (ds["bins"]<1.950), 4, ds["epsilon"] ).astype(np.float32)
        ds["epsilon"] = xr.where( (ds["bins"]>1.230)
            & (ds["bins"]<1.500), 3, ds["epsilon"] ).astype(np.float32)
        ds["epsilon"] = xr.where( (ds["bins"]>1.065)
            & (ds["bins"]<1.500), 2, ds["epsilon"] ).astype(np.float32)
        ds["epsilon"] = xr.where( (ds["bins"]<1.065),
            1, ds["epsilon"] ).astype(np.float32)
        Perez = pd.read_csv(f"{os.path.dirname(__file__)}/../files/Perez.csv", index_col = "bin")
        ds = ds.drop_vars("bins")
        # Extraterrestrial radiation.
        Ea = 1367
        # Coeficientes
        ds["Delta"] = (ds["DHI"] * ds["Air_Mass"] / Ea).astype(np.float32)
        ds = ds.drop_vars("Air_Mass")
        for j in Perez.columns:
            ds[j] = 0.0
            for i in Perez.index: ds[j] = ds[j].where(ds["epsilon"] != i,
                Perez.loc[i, j]).astype(np.float32)
        ds = ds.drop_vars("epsilon")
        ds["F1"] = ( ds["f11"] + ds["f12"]*ds["Delta"]
            + np.radians(ds["Zenith_Angle"])*ds["f13"]
            ).clip(max = 0).astype(np.float32)
        ds = ds.drop_vars(["f11", "f12", "f13"])
        ds["F2"] = ( ds["f21"] + ds["f22"]*ds["Delta"]
            + np.radians(ds["Zenith_Angle"])*ds["f23"] ).astype(np.float32)
        ds = ds.drop_vars(["f21", "f22", "f23", "Delta"])
        # Radiación difusa.
        ds["cos_tilt"] = ((1+cos(array_tilt))/2).astype(np.float32)
        ds["cos_AOI"] = cos(ds["AOI"]).astype(np.float32)
        ds["I_d"] = (ds["DHI"] * ( (1-ds["F1"])*ds["cos_tilt"]
            + ds["F1"]*ds["cos_AOI"].clip(max = 0)
            /ds["cos_zenith"].clip(max = cos(85)) + ds["F2"]*sin(array_tilt)) 
            ).where(ds["Zenith_Angle"] < 87.5, ds["DHI"] * ds["cos_tilt"]
            ).where(ds["Zenith_Angle"] < 90, 0).astype(np.float32)
        ds = ds.drop_vars(["DHI", "cos_tilt", "F1", "F2",
            "cos_zenith", "Zenith_Angle"])
        # Radiación directa.
        ds["I_b"] = (ds["DNI"] * ds["cos_AOI"]).where(
            ds["AOI"] < 90, 0).astype(np.float32)
        ds = ds.drop_vars("AOI")
        # Radiación total en el panel.
        ds["POA"] = (ds["I_b"] + ds["I_d"]).astype(np.float32)
        ds = ds.drop_vars(["I_b", "I_d", "cos_AOI", "DNI", "Azimuth_Angle"])

        # NOCT Cell Temperature Model
        T_NOCT    = 44 # °C
        # Datos de Panel Canadian Solar 550 W
        # Modelo: HiKu6 Mono PERC CS6W-550
        I_mp      = 13.2 # A
        V_mp      = 41.7 # V
        A_m       = 1.134*2.278 # m^2
        eff_ref   = I_mp * V_mp / (1000 * A_m)
        tau_alpha = 0.9
        # Ajuste de viento.
        #v = 0.61 # Dos pisos.
        v = 0.51 # Un piso.
        # Ajuste de montaje.
        T_adj = 2   + T_NOCT # Building integrated,
        # greater than 3.5 in, or ground/rack mounted
        #T_adj = 2  + T_NOCT # 2.5 to 3.5 in
        #T_adj = 6  + T_NOCT # 1.5 to 2.5 in
        #T_adj = 11 + T_NOCT # 0.5 to 1.5 in
        #T_adj = 18 + T_NOCT # less than 0.5 in
        # Temperatura de la celda
        ds["Cell_Temperature"] = ( ds["Temperature"]
            + ds["POA"] * (T_adj-20) / 800 * (1-eff_ref/tau_alpha)
            * (9.5/(5.7+3.8*v*ds["Wind_speed"])) ).astype(np.float32)

        # Simple efficiency module model
        # Eficiencia por temperatura
        eff_T = -0.34
        # Pérdidas del sistema
        eff_n = [ "Soiling", "Shading", "Snow", "Mismatch",
            "Wiring", "Connections", "Light_Induced_Degradation",
            "Nameplate_Rating", "Age", "Availability" ]
        eff = np.array( [0.98, 0.97, 1, 0.98, 0.98,
            0.995, 0.985, 0.99, 1, 0.97] ).prod()
        # Eficiencia del inversor
        eff_inv = 0.96
        # Eficiencia del sistema
        eff_sys = eff_ref * eff_inv * eff
        # DC to AC Size Ratio
        DC_AC = 1.1
        # Inverter size
        inv_P = I_mp * V_mp / DC_AC

        # Potencia generada en AC
        ds["P_mp"] = (ds["POA"]*eff_sys*A_m *
            ( 1 + eff_T/100 * (ds["Cell_Temperature"]-25) )
            ).astype(np.float32)
        ds["P_mp"] = (ds["P_mp"].where(ds["P_mp"]<inv_P, inv_P)
            / (I_mp*V_mp)).where(ds["GHI"]>0, 0).astype(np.float32)
        # El resultado es la generación por cada kWp.
        ds = ds.drop_vars(["Cell_Temperature", "POA",
            "GHI", "Temperature", "Wind_speed"])

        # Guardamos el archivo
        ds.to_netcdf(dir_r + f)
print()
print()