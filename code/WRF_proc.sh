set -e

echo "Uniendo años..."
for i in {0..5}; do
    echo "zzR_zz_Mega0"$i"_Variables_Extraidas"
	if [ ! -f "/Volumes/DATA/temp/temp/WRF/WRF_miroc_1985_2014/years/WRF_miroc_1985_2014_$i.nc" ]; then
        cp -r "/Volumes/DATA/data/WRF/Miroc6/zzR_zz_Mega0"$i"_Variables_Extraidas" "temp/WRF_miroc_1985_2014/"
		cdo -v -P 2 mergetime "temp/WRF_miroc_1985_2014/zzR_zz_Mega0"$i"_Variables_Extraidas/"* "temp/WRF_miroc_1985_2014/zzR_zz_Mega0"$i"_Variables_Extraidas.nc"
		rm -r "temp/WRF_miroc_1985_2014/zzR_zz_Mega0"$i"_Variables_Extraidas"
		python code/proc_WRF.py $i
		rm -r "temp/WRF_miroc_1985_2014/zzR_zz_Mega0"$i"_Variables_Extraidas.nc"
        mv temp/WRF_miroc_1985_2014/WRF_miroc_1985_2014_$i.nc /Volumes/DATA/temp/temp/WRF/WRF_miroc_1985_2014/years/WRF_miroc_1985_2014_$i.nc
	fi
done

echo
echo "Interpolando a 2km..."
for i in {0..5}; do
    echo "WRF_miroc_1985_2014_$i"
	if [ ! -f "/Volumes/DATA/temp/temp/WRF/WRF_miroc_1985_2014_2km/years/WRF_miroc_1985_2014_2km_$i.nc" ]; then
        cp "/Volumes/DATA/temp/temp/WRF/WRF_miroc_1985_2014/years/WRF_miroc_1985_2014_$i.nc" "temp/WRF_miroc_1985_2014/"
		python code/interp_WRF.py $i
        rm -r "temp/WRF_miroc_1985_2014/WRF_miroc_1985_2014_$i.nc"
        cp "temp/WRF_miroc_1985_2014_2km/WRF_miroc_1985_2014_2km_$i.nc" "/Volumes/DATA/temp/temp/WRF/WRF_miroc_1985_2014_2km/years"
	fi
done

echo 
echo "Uniendo años y generando malla..."
for i in {0..5}; do
    echo "Procesando malla $i/8"
    if [ ! -f "/Volumes/DATA/temp/temp/WRF/WRF_miroc_1985_2014_2km/grid/WRF_miroc_1985_2014_2km_$i.nc" ]; then
        python code/year2grid.py $i
        mv "temp/WRF_miroc_1985_2014_2km_$i.nc" "/Volumes/DATA/temp/temp/WRF/WRF_miroc_1985_2014_2km/grid"
    fi
done

rm -r temp/WRF_miroc_1985_2014_2km/*

echo 
echo "Calculando DNI..."
for i in {0..8}; do
    echo "Procesando malla $i/8"
    if [ ! -f "/Volumes/DATA/temp/temp/WRF/WRF_miroc_1985_2014_2km/radiacion/WRF_miroc_1985_2014_2km_$i.nc" ]; then
        cp "/Volumes/DATA/temp/temp/WRF/WRF_miroc_1985_2014_2km/grid/WRF_miroc_1985_2014_2km_$i.nc" "temp/WRF_miroc_1985_2014_2km/"
        python code/radiacion_2km.py $i
        rm -f "temp/WRF_miroc_1985_2014_2km/WRF_miroc_1985_2014_2km_$i.nc"
        mv "temp/WRF_miroc_1985_2014_2km_$i.nc" "/Volumes/DATA/temp/temp/WRF/WRF_miroc_1985_2014_2km/radiacion"
    fi
done