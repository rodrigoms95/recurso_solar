# Une todos los CSV de NSRDB en un NetCDF.

# Stop at first error.
set -e

path_nsrdb="data/test/NSRDB/*"
path_netcdf="data/test/NetCDF/*"
output="data/test/NSRDB.nc"
y_i=1998
y_f=2022

rm -r -f $path_netcdf

# Convertimos cada conjunto de CSV en NetCDF.
for dir in $path_nsrdb; do
    python code/format.py $dir $y_i $y_f
done

# Unimos todos los NetCDF.
cdo -O collgrid $path_netcdf $output

rm -r -f $path_netcdf