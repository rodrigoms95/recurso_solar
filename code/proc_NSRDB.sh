set -e

name="NSRDB_4km"
path_data="/Volumes/DATA/data/$name"
external="/Volumes/DATA/temp/$name"
internal="temp/$name"

lat=$(cdo griddes "/Volumes/DATA/temp/WRF_miroc_1985_2014_4km/years/WRF_miroc_1985_2014_4km_0.nc" | awk 'NR==7{print $3}')
directory="grid"
mkdir -p "$external/$directory"
mkdir -p "$internal/$directory"
if [ ! -f "$external/$directory/$name""_$((lat-1)).nc" ]; then
    printf "\n\nGenerando malla...\n"
    rsync "$path_data.nc" "$internal/$name.nc"
    for ((i=0;i<lat;i++)); do
        printf " Procesando malla $((i+1))/$lat\r"
        if [ ! -f "$external/$directory/"$name"_$i.nc" ]; then
            python code/tot_grid.py "$i" "$internal" "$internal" "$name"
            mv "$internal/$directory/"$name"_$i.nc" "$external/$directory"
        fi
    done
fi
rm -f "$internal/$name.nc"

vars=("Pressure" "Temperature" "Wind Speed" "DNI" "GHI" "UVHI")
#vars=("${(@s[ ])$(cdo showname $external/$directory/"$name"_0.nc)}")
if [ ! -f "$external/${vars[1]}/$name""_$((lat-1)).nc" ]; then
    printf "\n\nCalculando cuantiles...\n"
    for v in "${vars[@]}"; do
        mkdir -p "$internal/vars/$v"
        mkdir -p "$external/vars/$v"
    done
    for ((i=0;i<lat;i++)); do
        printf " Procesando malla $((i+1))/$lat\r"
        if [ ! -f "$external/vars/$v/"$name"_$i.nc" ]; then
            rsync "$external/$directory/"$name"_$i.nc" "$internal/$directory/"$name"_$i.nc"
            python code/cdf_wrf.py "$i" "$internal" "$name" "$directory"
            rm -f "$internal/$directory/"$name"_$i.nc"
            for v in "${vars[@]}"; do
                mv "$internal/vars/$v/"$name"_$i.nc" "$external/vars/$v"
            done
        fi
    done
fi

printf "\n\nNSRDB procesado.\n"