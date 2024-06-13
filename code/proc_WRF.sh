set -e

data="/Volumes/DATA/data/WRF/Miroc6"
n=4
dataset="WRF_miroc_1985_2014"
name="$dataset""_$n""km"
external="/Volumes/DATA/temp/$name"
internal="temp/$name"

external_data="/Volumes/DATA/temp/$dataset"
internal_data="temp/$dataset"

printf "Procesando WRF..."

directory="years"
mkdir -p "$internal_data/years"
mkdir -p "$external_data/years"
mkdir -p "$internal/years"
mkdir -p "$external/years"

printf "\n\nUniendo años...\n"
for i in {0..5}; do
    printf " zzR_zz_Mega0"$i"_Variables_Extraidas\r"
	if [ ! -f "$external_data/years/$dataset""_$i.nc" ]; then
        rsync -r "$data/zzR_zz_Mega0$i""_Variables_Extraidas/" "$internal_data/zzR_zz_Mega0"$i"_Variables_Extraidas/"
        cdo -s -P 2 mergetime "$internal_data/zzR_zz_Mega0$i""_Variables_Extraidas/"* "$internal_data/zzR_zz_Mega0"$i"_Variables_Extraidas.nc"
		rm -r -f "$internal_$data/zzR_zz_Mega0"$i"_Variables_Extraidas"
		python code/proc_WRF.py "$i"
		rm -f "$internal_data/zzR_zz_Mega0$i""_Variables_Extraidas.nc"
        mv "$internal_data/$dataset""_$i.nc" "$external_data/$directory/$dataset""_$i.nc"
	fi
done

printf "\n\nInterpolando a "$n" km...\n"
i=0
printf " Generando malla de interpolación...\r"
if [ ! -f "$external/$name""_weights.nc" ]; then
    rsync "$external_data/$directory/"$dataset"_$i.nc" "$internal_$data/$directory/"$dataset"_$i.nc"
    python code/interp_weights.py "$n" "$internal"
    rsync "$internal/$name""_weights.nc" "$external/$name""_weights.nc"	
fi
for i in {0..5}; do
    printf " "$dataset"_$i                        \r"
	if [ ! -f "$external/$directory/$name""_$i.nc" ]; then
        rsync "$external_data/$directory/"$dataset"_$i.nc" "$internal_data/$directory/"$dataset"_$i.nc"
        python code/interp_WRF.py "$i" "$n" "$internal" "$dataset"
        rm -f "$internal_data/$directory/"$dataset"_$i.nc"
        rsync "$internal/$directory/$name""_$i.nc" "$external/$directory"
	fi
done
rsync "$external/$directory/$name""_$i.nc" "$internal/$directory"

lat=$(cdo griddes "$external/$directory/$name""_0.nc" | awk 'NR==7{print $3}')

directory="grid"
mkdir -p "$internal/$directory"
mkdir -p "$external/$directory"
if [ ! -f "$external/$directory/$name""_$((lat-1)).nc" ]; then
    printf "\n\nUniendo años y generando malla en WRF...\n"
    for ((i=0;i<lat;i++)); do
        printf " Procesando malla $((i+1))/$lat\r"
        if [ ! -f "$external/$directory/$name""_$i.nc" ]; then
            python code/year2grid.py "$i" "$internal" "$name"
            mv "$internal/$directory/$name""_$i.nc" "$external/$directory"
        fi
    done
fi
rm -f "$internal/years/"*

directory="radiacion"
mkdir -p "$internal/$directory"
mkdir -p "$external/$directory"
if [ ! -f "$external/$directory/$name""_$((lat-1)).nc" ]; then
    printf "\n\nCalculando radiación...\n"
    for ((i=0;i<lat;i++)); do
        printf " Procesando malla $((i+1))/$lat\r"
        if [ ! -f "$external/$directory/$name""_$i.nc" ]; then
            rsync "$external/grid/$name""_$i.nc" "$internal/grid/$name""_$i.nc"
            python code/radiacion.py "$i" "$internal" "$name"
            rm -f "$internal/grid/$name""_$i.nc"
            mv "$internal/$directory/$name""_$i.nc" "$external/$directory"
        fi
    done
fi

#vars=("${(@s[ ])$(cdo showname $external/radiacion/$name""_0.nc)}")
vars=("Pressure" "Temperature" "Wind Speed" "DNI" "GHI" "UVHI")
if [ ! -f "$external/${vars[1]}/$name""_$((lat-1)).nc" ]; then
    printf "\n\nCalculando cuantiles en WRF...\n"
    for v in "${vars[@]}"; do
        mkdir -p "$internal/vars/$v"
        mkdir -p "$external/vars/$v"
    done
    for ((i=0;i<lat;i++)); do
        printf " Procesando malla $((i+1))/$lat\r"
        if [ ! -f "$external/vars/$v/$name""_$i.nc" ]; then
            rsync "$external/$directory/$name""_$i.nc" "$internal/$directory/$name""_$i.nc"
            python code/cdf_wrf.py "$i" "$internal" "$name" "$directory"
            rm -f "$internal/$directory/$name""_$i.nc"
            for v in "${vars[@]}"; do
                mv "$internal/vars/$v/$name""_$i.nc" "$external/vars/$v"
            done
        fi
    done
fi

directory="promedio"
mkdir -p "$internal/$directory"
mkdir -p "$external/$directory"
v1="GHI"
v2="UVHI"
if [ ! -f "$external/$name""_$directory.nc" ]; then
    printf "\n\nObteniendo promedios en $name...\n"
    for ((i=0;i<lat;i++)); do
        printf " Procesando malla $((i+1))/$lat\r"
        if [ ! -f "$external/$directory/$name""_$i.nc" ]; then
            rsync "$external/radiacion/$name""_$i.nc" "$internal/radiacion/$name""_$i.nc"
            if [ ! -f "$internal/$directory/$name""_$i.nc" ]; then
                cdo -L -s -timavg -yearsum -selname,"$v1","$v2" "$internal/radiacion/$name""_$i.nc" "$internal/$directory/$name""_$i.nc"
                rm -f "$internal/radiacion/$name""_$i.nc"
            fi
        fi
    done
    if [ ! -f "$internal/$name""_$directory.nc" ]; then
        cdo -s collgrid "$internal/$directory/"* "$internal/$name""_$directory.nc"
        rm -f "$internal/$directory/"*
    fi
    rsync "$internal/$name""_$directory.nc" "$external/$name""_$directory.nc"
fi

printf "\n\n WRF procesado.\n"