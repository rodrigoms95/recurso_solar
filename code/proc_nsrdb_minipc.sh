set -e

printf "\nProcesamiento de NSRDB."

name="NSRDB_4km"
path_data="datos/rodr/temp/recurso_solar/$name"
internal="../../temp/recurso_solar/$name"

lat=$(cdo griddes "../../temp/recurso_solar/WRF_miroc_1985_2014_4km/years/WRF_miroc_1985_2014_4km_0.nc" | awk 'NR==7{print $3}')
directory="grid"
mkdir -p "$internal/$directory"
if [ ! -f "$internal/$directory/$name""_$((lat-1)).nc" ]; then
    printf "\n\nGenerando malla..."
    for ((i=0;i<lat;i++)); do
        printf "\nProcesando malla $((i+1))/$lat"
        if [ ! -f "$internal/$directory/"$name"_$i.nc" ]; then
            python code/tot_grid.py "$i" "$internal" "$path_data" "$name" 
        fi
    done
fi

read -a vars <<< "$(cdo showname $internal/radiacion/$name""_0.nc)"
if [ ! -f "$internal/${vars[1]}/$name""_$((lat-1)).nc" ]; then
    printf "\n\nCalculando cuantiles..."
    for v in "${vars[@]}"; do; mkdir -p "$internal/vars/$v"; done
    for ((i=0;i<lat;i++)); do
        printf "\n\nProcesando malla $((i+1))/$lat"
        if [ ! -f "$internal/vars/$v/"$name"_$i.nc" ]; then
            python code/cdf_wrf.py "$i" "$internal" "$name" "$directory"
        fi
    done
fi