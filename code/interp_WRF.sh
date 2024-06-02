set -e
for i in {0..5}; do
    echo "WRF_miroc_1985_2014_$i"
	if [ ! -f /Volumes/DATA/temp/temp/WRF/WRF_miroc_1985_2014_2km/years/WRF_miroc_1985_2014_$i.nc ]; then
        cp "/Volumes/DATA/temp/temp/WRF/WRF_miroc_1985_2014/years/WRF_miroc_1985_2014_$i.nc" "temp/WRF_miroc_1985_2014/"
		python code/interp_WRF.py $i
        rm -r "temp/WRF_miroc_1985_2014/WRF_miroc_1985_2014_$i.nc"
        cp "temp/WRF_miroc_1985_2014_2km/WRF_miroc_1985_2014_2km_$i.nc" "/Volumes/DATA/temp/temp/WRF/WRF_miroc_1985_2014_2km/years"
	fi
done