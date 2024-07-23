set -e

observed="NSRDB_4km"
model="WRF_miroc_1985_2014_4km"
internal="temp"

printf "\nCálculo de mapeo de cuantiles y producción fotovoltaica."

lat=$(cdo griddes "$internal/$model/years/$model""_0.nc" | awk 'NR==7{print $3}')
read -a vars <<< "$(cdo showname $internal/$directory/$name""_0.nc)"
mkdir -p "$internal/$model/qgrid"
if [ ! -f "$internal/$model/qmap/${vars[5]}/$model""_$((lat-1)).nc" ]; then
    printf "\n\nRealizando mapeo de cuantiles...\n"
    for v in "${vars[@]}"; do
        mkdir -p "$internal/$model/map_res/$v"
        mkdir -p "$internal/$model/qmap/$v"
    done
    for ((i=0;i<lat;i++)); do
        printf " Procesando malla $((i+1))/$lat\r"
        for v in "${vars[@]}"; do
            if [ ! -f "$internal/$model/qmap/$v/$model""_$i.nc" ]; then
                python code/quantile_calc.py "$i" "$v" "$internal" "$observed" "$model"
            fi
        done
    done
fi

if [ ! -f "$internal/$model/qgrid/$model""_$((lat-1)).nc" ]; then
    printf "\n\nUniendo variables y malla...\n"
    for ((i=0;i<lat;i++)); do
        printf " Procesando malla $((i+1))/$lat\r"
        if [ ! -f "$internal/$model/qgrid/$model""_$i.nc" ]; then
            cdo -s -P 2 merge "$internal/$model/qmap/"*"/$model""_$i.nc" "$internal/$model/qgrid/$model""_$i.nc"
        fi
    done
fi

mkdir -p "$internal/$model/fotovoltaico"
if [ ! -f "$internal/$model/fotovoltaico/$model""_$((lat-1)).nc" ]; then
    printf "\n\nCalculando Producción fotovoltaica...\n"
    for ((i=0;i<lat;i++)); do
        printf " Procesando malla $((i+1))/$lat\r"
        if [ ! -f "$internal/$model/fotovoltaico/$model""_$i.nc" ]; then
            python code/fotovoltaico.py $i $internal $model
        fi
    done
fi

if  [ ! -f "$internal/$model/$model.nc" ]; then
    printf "\n\nUniendo el archivo...\n"
    cdo collgrid "$internal/$model/fotovoltaico/"* "$internal/$model/$model""_qmap.nc"
fi

#Promedios.
printf "\n\nCalculando promedios..\n"
v1="GHI"
v2="UVHI"
v3="P_mp"
if [ ! -f "$internal/$model/$model""_radiacion.nc" ]; then
    printf "\nExtrayendo variables de radiación...\n"
    cdo selname,"$v1","$v2","$v3" "$internal/$model/$model.nc" "$internal/$model/$model""_radiacion.nc"
fi
if [ ! -f "$internal/$model/$model""_radiacion_days.nc" ]; then
    printf "\nCalculando valores diarios...\n"
    cdo daysum "$internal/$model/$model""_radiacion.nc" "$internal/$model/$model""_radiacion_days.nc"
fi
if [ ! -f "$internal/$model/$model""_anual.nc" ]; then
    printf "\nCalculando promedio anual...\n"
    cdo -timmean "$internal/$model/$model""_radiacion_days.nc" "$internal/$model/$model""_anual.nc"
fi
if [ ! -f "$internal/$model/$model""_mensual.nc" ]; then
    printf "\nCalculando promedios mensuales...\n"
    years=$(cdo nyear "$internal/$model/$model""_radiacion.nc")
    cdo -ymonmean "$internal/$model/$model""_radiacion_days.nc" "$internal/$model/$model""_mensual.nc"
fi
mkdir -p "$internal/$model/hours"
if [ ! -f "$internal/$model/$model""_horario.nc" ]; then
    printf "\nCalculando promedios horarios...\n"
    for i in {0..23}; do
        if [ ! -f "$internal/$model/hours/$model""_hora_$i.nc" ]; then
            cdo -L -timmean -selhour,$i "$internal/$model/$model""_radiacion.nc" "$internal/$model/hours/$model""_hora_$i.nc"
        fi
    done
    cdo mergetime "$internal/$model/hours/"* "$internal/$model/$model""_horario.nc"
fi
mkdir -p "$internal/$model/hours_month"
if [ ! -f "$internal/$model/$model""_hora_mensual.nc" ]; then
    printf "\nCalculando promedios horarios mensuales...\n"
    for i in {1..12}; do
        for j in {0..23}; do   
            if [ ! -f "$internal/$model/hours_month/$model""_mes_$i""_hora_$j.nc" ]; then
                cdo -L -timmean -selhour,$j -selmon,$i "$internal/$model/$model""_radiacion.nc" "$internal/$model/hours_month/$model""_mes_$i""_hora_$j.nc"
            fi
        done
    done
    cdo -s mergetime "$internal/$model/hours_month/"* "$internal/$model/$model""_hora_mensual.nc"
fi

printf "\nMapeo de cuantiles terminado...\n"