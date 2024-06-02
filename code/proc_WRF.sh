set -e
for i in {0..5}; do
    echo "zzR_zz_Mega0"$i"_Variables_Extraidas"
	if [ ! -f /Volumes/DATA/temp/temp/WRF/WRF_miroc_1985_2014/years/WRF_miroc_1985_2014_$i.nc ]; then
        cp -r "/Volumes/DATA/data/WRF/Miroc6/zzR_zz_Mega0"$i"_Variables_Extraidas" "temp/WRF_miroc_1985_2014/"
		cdo -v -P 2 mergetime "temp/WRF_miroc_1985_2014/zzR_zz_Mega0"$i"_Variables_Extraidas/"* "temp/WRF_miroc_1985_2014/zzR_zz_Mega0"$i"_Variables_Extraidas.nc"
		rm -r "temp/WRF_miroc_1985_2014/zzR_zz_Mega0"$i"_Variables_Extraidas"
		python code/proc_WRF.py $i
		rm -r "temp/WRF_miroc_1985_2014/zzR_zz_Mega0"$i"_Variables_Extraidas.nc"
        mv temp/WRF_miroc_1985_2014/WRF_miroc_1985_2014_$i.nc /Volumes/DATA/temp/temp/WRF/WRF_miroc_1985_2014/years/WRF_miroc_1985_2014_$i.nc
	fi
done