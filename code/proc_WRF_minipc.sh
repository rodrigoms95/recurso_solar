set -e

data="/datos/rodr/Datos/WRF/Miroc6"
n=4
dataset="WRF_miroc_1985_2014"
name="$dataset""_$n""km"
internal="~/temp/recurso_solar/$name"

internal_data="~/temp/recurso_solar/$dataset"

printf "\nProcesando WRF..."

directory="years"
mkdir -p "$internal_data/years"
mkdir -p "$internal/years"

printf "\n\nUniendo años..."
for i in {0..5}; do
    printf "\nzzR_zz_Mega0"$i"_Variables_Extraidas"
	if [ ! -f "$internal_data/years/$dataset""_$i.nc" ]; then
        cdo -s -P 2 mergetime "$data/zzR_zz_Mega0$i""_Variables_Extraidas/"* "$internal_data/zzR_zz_Mega0"$i"_Variables_Extraidas.nc"
		python code/proc_WRF.py "$i"
	fi
done

printf "\n\nInterpolando a "$n" km..."
i=0
printf "\nGenerando malla de interpolación..."
if [ ! -f "$internal/$name""_weights.nc" ]; then
    python code/interp_weights.py "$n" "$internal"
fi
for i in {0..5}; do
    printf "\n$dataset""_$i"
	if [ ! -f "$internal/$directory/$name""_$i.nc" ]; then
        python code/interp_WRF.py "$i" "$n" "$internal" "$dataset"
	fi
done

lat=$(cdo griddes "$internal/$directory/$name""_0.nc" | awk 'NR==7{print $3}')

directory="grid"
mkdir -p "$internal/$directory"
if [ ! -f "$internal/$directory/$name""_$((lat-1)).nc" ]; then
    printf "\n\nUniendo años y generando malla en WRF..."
    for ((i=0;i<lat;i++)); do
        printf "\nProcesando malla $((i+1))/$lat"
        if [ ! -f "$internal/$directory/$name""_$i.nc" ]; then
            python code/year2grid.py "$i" "$internal" "$name"
        fi
    done
fi

directory="radiacion"
mkdir -p "$internal/$directory"
if [ ! -f "$internal/$directory/$name""_$((lat-1)).nc" ]; then
    printf "\n\nCalculando radiación..."
    for ((i=0;i<lat;i++)); do
        printf "\nProcesando malla $((i+1))/$lat"
        if [ ! -f "$internal/$directory/$name""_$i.nc" ]; then
            python code/radiacion.py "$i" "$internal" "$name"
        fi
    done
fi

vars=("${(@s[ ])$(cdo showname $internal/radiacion/$name""_0.nc)}")
if [ ! -f "$internal/${vars[1]}/$name""_$((lat-1)).nc" ]; then
    printf "\n\nCalculando cuantiles en WRF..."
    for v in "${vars[@]}"; do; mkdir -p "$internal/vars/$v"; done
    for ((i=0;i<lat;i++)); do
        printf "\n\nProcesando malla $((i+1))/$lat"
        if [ ! -f "$internal/vars/$v/$name""_$i.nc" ]; then
            python code/cdf_wrf.py "$i" "$internal" "$name" "$directory"
        fi
    done
fi

directory="promedio"
mkdir -p "$internal/$directory"
v1="GHI"
v2="UVHI"
if [ ! -f "$internal/$name""_$directory.nc" ]; then
    printf "\n\nObteniendo promedios en $name..."
    for ((i=0;i<lat;i++)); do
        printf "\nProcesando malla $((i+1))/$lat"
        if [ ! -f "$internal/$directory/$name""_$i.nc" ]; then
            cdo -L -s -timavg -yearsum -selname,"$v1","$v2" "$internal/radiacion/$name""_$i.nc" "$internal/$directory/$name""_$i.nc"
        fi
    done
    if [ ! -f "$internal/$name""_$directory.nc" ]; then
        cdo -s collgrid "$internal/$directory/"* "$internal/$name""_$directory.nc"
    fi
fi

printf "\n\nWRF procesado.\n"