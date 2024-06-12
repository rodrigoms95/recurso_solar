set -e

external="/Volumes/DATA/temp"
internal="/Volumes/DATA/temp"
n=2
dataset="WRF_miroc_1985_2014"

printf "Procesando WRF..."

printf "\n\nUniendo años...\n"
for i in {0..5}; do
    printf " zzR_zz_Mega0"$i"_Variables_Extraidas\r"
	if [ ! -f "$external/$dataset/years/$dataset""_$i.nc" ]; then
        cdo -s -P 2 mergetime "$internal/$dataset/zzR_zz_Mega0$i""_Variables_Extraidas/"* "$internal/$dataset/zzR_zz_Mega0"$i"_Variables_Extraidas.nc"
		python code/proc_WRF.py $i
	fi
done

printf "\n\nInterpolando a "$n" km...\n"
i=0
directory="years"
printf " "$dataset"_$i\r"
if [ ! -f "$external/$dataset/"$dataset"_"$n"km_weights.nc" ]; then
    python code/interp_weights.py $n $internal
    python code/interp_WRF.py $i $n $internal
fi
for i in {1..5}; do
    printf " "$dataset"_$i\r"
	if [ ! -f "$external/"$dataset"_"$n"km/$directory/"$dataset"_"$n"km_$i.nc" ]; then
        python code/interp_WRF.py $i $n $internal
    fi
done

printf "\n\nUniendo años y generando malla en WRF...\n"
lat=$(cdo griddes "$external/"$dataset"_"$n"km/years/"$dataset"_"$n"km_0.nc" | awk 'NR==7{print $3}')
for ((i=0;i<lat;i++)); do
    printf " Procesando malla $((i+1))/$lat\r"
    if [ ! -f "$external/"$dataset"_"$n"km/grid/"$dataset"_"$n"km_$i.nc" ]; then
        python code/year2grid.py $i $n
    fi
done
rm -f "$internal/"$dataset"_"$n"km/years/"*

lat=$(cdo griddes "$external/"$dataset"_"$n"km/years/"$dataset"_"$n"km_0.nc" | awk 'NR==7{print $3}')
printf "\n\nCalculando radiación...\n"
for ((i=0;i<lat;i++)); do
    printf " Procesando malla $((i+1))/$lat\r"
    if [ ! -f "$external/"$dataset"_"$n"km/radiacion/"$dataset"_"$n"km_$i.nc" ]; then
        python code/radiacion.py $i $n $internal
    fi
done

printf "\n\nCalculando cuantiles en WRF...\n"
#vars=("${(@s[ ])$(cdo showname $external/WRF_miroc_1985_2014_2km/radiacion/WRF_miroc_1985_2014_2km_0.nc)}")
directory="radiacion"
vars=("Pressure" "Temperature" "Wind Speed" "DNI" "GHI" "UVHI")
for v in "${vars[@]}"; do
    mkdir -p "$internal/"$dataset"_"$n"km/vars/$v"
    mkdir -p "$external/"$dataset"_"$n"km/vars/$v"
done
for ((i=0;i<lat;i++)); do
    printf " Procesando malla $((i+1))/$lat\r"
    if [ ! -f "$external/"$dataset"_"$n"km/vars/$v/"$dataset"_"$n"km_$i.nc" ]; then
        python code/cdf_wrf.py $i $n $internal $dataset $directory
    fi
done

v1="GHI"
v2="UVHI"
directory="radiacion"
printf "\n\nObteniendo promedios en $dataset...\n"
for ((i=0;i<lat;i++)); do
    printf " Procesando malla $((i+1))/$lat\r"
    if [ ! -f "$external/"$dataset"_"$n"m/promedio/"$dataset"_"$n"km.nc" ]; then
        if [ ! -f "$internal/"$dataset"_"$n"km/promedio/"$dataset"_"$n"km_$i.nc" ]; then
            cdo -L -s -timavg -yearsum -selname,$v1,$v2 "$internal/"$dataset"_"$n"km/$directory/"$dataset"_"$n"km_$i.nc" "$internal/"$dataset"_"$n"km/promedio/"$dataset"_"$n"km_$i.nc"
        fi
    fi
done
if [ ! -f "$external/"$dataset"_"$n"km/"$dataset"_"$n"km_promedio.nc" ]; then
    if [ ! -f "$internal/"$dataset"_"$n"km/"$dataset"_"$n"km_promedio.nc" ]; then
        cdo -s collgrid "$internal/"$dataset"_"$n"km/promedio/"* "$internal/"$dataset"_"$n"km/"$dataset"_"$n"km_promedio.nc"
    fi
    fi

printf "\n\n WRF procesado.\n"