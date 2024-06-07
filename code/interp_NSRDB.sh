internal="temp"
external="/Volumes/DATA/temp"
for y in {1998..2015}; do
    echo "Año $y..."
    cdo selyear,$y /Volumes/DATA/data/NSRDB_4km.nc $internal/NSRDB_2km_interp/NSRDB_4km_$y.nc
    python code/interp_NSRDB.py $y $internal
    rm -f $internal/NSRDB_2km_interp/NSRDB_4km_$y.nc
    mv $internal/NSRDB_2km_interp/years/NSRDB_2km_interp_$y.nc $external/NSRDB_2km_interp/years
done