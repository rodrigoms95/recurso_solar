# Une todos los CSV de NSRDB en un NetCDF.

# Stop at first error.
set -e

path_nsrdb="results/NSRDB/*"
path_netcdf="temp/NetCDF"
output="results/NSRDB.nc"
y_i=1998
y_f=2022

echo
echo "Convirtiendo de CSV a NetCDF..."
echo

# Limpiamos los datos temporales.
rm -r -f $path_netcdf
mkdir -p $path_netcdf

# Convertimos cada conjunto de CSV en NetCDF.
for file in $path_nsrdb; do
    echo "Procesando coordenadas ${file##*/}..."
    python code/nsrdb_netcdf.py $file $y_i $y_f
done

# Unimos todos los NetCDF.
echo
echo "Uniendo todas las coordenadas..."
cdo -O -s collgrid $path_netcdf"/*" $output

echo
echo "Conversión terminada."
echo

# Limpiamos los datos temporales.
rm -r -f $path_netcdf