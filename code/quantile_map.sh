set -e

observed="NSRDB_4km"
model="WRF_miroc_1985_2014_4km"
external="/Volumes/DATA/temp"
internal="temp"

printf "\nRealizando mapeo de cuantiles...\n"

lat=$(cdo griddes "$external/$model/years/$model""_0.nc" | awk 'NR==7{print $3}')
#vars=("${(@s[ ])$(cdo showname $external/radiacion/$name""_0.nc)}")
vars=("Pressure" "Temperature" "Wind Speed" "DNI" "GHI" "UVHI")
mkdir -p "$external/$model/qgrid"
mkdir -p "$internal/$model/qgrid"
if [ ! -f "$external/$model/map/$v/$model""_$((lat-1)).nc" ]; then
    for v in "${vars[@]}"; do
        mkdir -p "$internal/$model/map_res/$v"
        mkdir -p "$internal/$model/qmap/$v"
        mkdir -p "$internal/$model/qgrid/$v"
        mkdir -p "$external/$model/map_res/$v"
        mkdir -p "$external/$model/qmap/$v"
    done
    for ((i=0;i<lat;i++)); do
        printf " Procesando malla $((i+1))/$lat\r"
        for v in "${vars[@]}"; do
            if [ ! -f "$external/$model/qmap/$v/$model""_$i.nc" ]; then
                rsync "$external/$observed/vars/$v/$observed""_$i.nc" "$internal/$observed/vars/$v/$observed""_$i.nc"
                rsync "$external/$model/vars/$v/$model""_$i.nc" "$internal/$model/vars/$v/$model""_$i.nc"
                python code/quantile_calc.py "$i" "$v" "$internal" "$observed" "$model"
                mv "$internal/$model/map_res/$v/$model""_$i.nc" "$external/$model/map_res/$v/$model""_$i.nc"
                mv "$internal/$model/qmap/$v/$model""_$i.nc" "$external/$model/qmap/$v/$model""_$i.nc"
                rm -f "$internal/$observed/vars/$v/$observed""_$i.nc"
                rm -f "$internal/$model/vars/$v/$model""_$i.nc"
            fi
        done
    done
fi

printf "\n\nUniendo variables y malla...\n"
if [ ! -f "$external/$model/qgrid/$model""_$((lat-1)).nc" ]; then
    for ((i=0;i<lat;i++)); do
        printf " Procesando malla $((i+1))/$lat\r"
        if [ ! -f "$external/$model/qgrid/$model""_$i.nc" ]; then
            rsync -r "$external/$model/qmap/"*"/$model""_$i.nc"  "$internal/$model/qmap/"*"/$model""_$i.nc"
            cdo -s -P 2 merge "$internal/$model/qmap/"*"/$model""_$i.nc" "$internal/$model/qgrid/$model""_$i.nc"
            rsync "$internal/$model/qgrid/$model""_$i.nc" "$external/$model/qgrid/$model""_$i.nc"
            rm -f "$internal/$model/qmap/"*"/$model""_$i.nc"
        fi
    done
done

printf "\n\nCalculando Producción fotovoltaica..\n"
mkdir -p "$internal/$model/fotovoltaico"
mkdir -p "$external/$model/fotovoltaico"
if [ ! -f "$external/$model/fotovoltaico/$model""_$((lat-1)).nc" ]; then
    for ((i=0;i<lat;i++)); do
        printf " Procesando malla $((i+1))/$lat\r"
        if [ ! -f "$external/$model/fotovoltaico/$model""_$i.nc" ]; then
            rsync "$external/$model/qgrid/$model""_$i.nc"  "$internal/$model/qgrid/$model""_$i.nc"
            python code/fotovoltaico.py $i $internal $model
            rsync "$internal/$model/fotovoltaico/$model""_$i.nc"  "$external/$model/fotovoltaico/$model""_$i.nc"
        fi
    done
fi

printf "\n\nUniendo el archivo..\n"
rsync -r "$external/$model/fotovoltaico/"  "$internal/$model/fotovoltaico/"
cdo collgrid "$internal/$model/fotovoltaico/"* "$external/$model/$model.nc"
rm -r -f "$internal/$model/fotovoltaico/"*

#Promedios.
printf "\n\nCalculando promedios..\n"
v1="GHI"
v2="UVHI"
v3="P_mp"
cdo selname,"$v1","$v2","$v3" "$external/$model/$model.nc" "$internal/$model/$model""_radiacion.nc"
cdo -L -s -timavg -yearsum "$internal/$model/$model""_radiacion.nc" "$internal/$model/$model""_anual.nc"
years=$(cdo nyear "$internal/$model/$model""_radiacion.nc")
cdo -L -s -divc,$years -monsum "$internal/$model/$model""_radiacion.nc" "$internal/$model/$model""_mensual.nc"
mkdir -p "$internal/$model/hours"
printf "\n\nUniendo años...\n"
cdo -s -hourmean "$internal/$model/$model""_radiacion.nc" "$internal/$model/$model""_horario.nc"
for i in {1..12}; do
    cdo -s -L -hourmean -selmon,$i "$internal/$model/$model""_radiacion.nc" "$internal/$model/hours/$model""_mensual_$i.nc"
done
cdo -s mergetime "$internal/$model/hours/"* "$internal/$model/$model""_hora_mensual.nc"

printf "\n\nMapeo de cuantiles terminado...\n"