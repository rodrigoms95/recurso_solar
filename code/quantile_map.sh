set -e

observed="NSRDB_4km"
model="WRF_miroc_1985_2014_4km"
external="/Volumes/DATA/temp"
internal="temp"

printf "\nRealizando mapeo de cuantiles...\n"

lat=$(cdo griddes "$external/$model/years/$model""_0.nc" | awk 'NR==7{print $3}')
#vars=("${(@s[ ])$(cdo showname $external/radiacion/$name""_0.nc)}")
vars=("Pressure" "Temperature" "Wind Speed" "DNI" "GHI" "UVHI")
if [ ! -f "$external/$model/map/$v/$model""_$((lat-1)).nc" ]; then
    for v in "${vars[@]}"; do
        mkdir -p "$internal/$model/map_res/$v"
        mkdir -p "$internal/$model/qmap/$v"
        mkdir -p "$internal/$model/qgrid/$v"
        mkdir -p "$external/$model/map_res/$v"
        mkdir -p "$external/$model/qmap/$v"
        mkdir -p "$external/$model/qgrid/$v"
    done
    for ((i=0;i<lat;i++)); do
        printf " Procesando malla $((i+1))/$lat\r"
        for v in "${vars[@]}"; do
            if [ ! -f "$external/$model/qmap/$v/$model""_$i.nc" ]; then
                rsync "$external/$observed/vars/$v/$observed""_$i.nc" "$internal/$observed/vars/$v/$observed""_$i.nc"
                rsync "$external/$model/vars/$v/$model""_$i.nc" "$internal/$model/vars/$v/$model""_$i.nc"
                python code/quantile_calc.py $i $v $internal $observed $model
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
    
# Calcular P_mp

# Unir todo.
#if [ ! -f "$external/$model/$model""_qmap.nc" ]; then
#            cdo -s -P 2 collgrid "$internal/$model/qmap/$v/"* "$internal/$model/qmap/$model""_$v.nc"
#            mv -r "$internal/$model/qmap/$model""_$v.nc" "$external/$model/qmap/$model""_$v.nc"
#            rm -f "$internal/$model/qmap/$v/"*
#        fi
#    done
#    rsync "$external/$model/qmap/"*".nc" "$internal/$model/qmap/"*".nc"
#    cdo -s -P 2 merge "$internal/$model/qmap/"*".nc" "$internal/$model/$model""_qmap.nc"
#    mv "$internal/$model/$model""_qmap.nc" "$external/$model/$model""_qmap.nc"
#    rm -f "$internal/$model/qmap/"*".nc"
#fi

#Promedios.
#v1="GHI"
#v2="UVHI"
#v3="P_mp"
#cdo -L -s -timavg -yearsum -selname,"$v1","$v2" "$internal/radiacion/$name""_$i.#nc" "$internal/$directory/$name""_$i.nc"

printf "\n\nMapeo de cuantiles terminado...\n"