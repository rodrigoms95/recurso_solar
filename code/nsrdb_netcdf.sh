# Une todos los CSV de NSRDB en un NetCDF.

# Stop at first error.
set -e

name="NSRDB"
path_nsrdb="results/"$name"/*"
path_temp="temp/"
path_netcdf=$path_temp"NetCDF/"
output="results/"$name".nc"
y_i=1998
y_f=2022

echo
echo "Convirtiendo de CSV a NetCDF..."
echo

# Limpiamos los datos temporales.
rm -r -f $path_temp
mkdir -p $path_netcdf

# Convertimos cada conjunto de CSV en NetCDF.
for file in $path_nsrdb; do
    echo "Procesando coordenadas ${file##*/}..."
    python code/nsrdb_netcdf.py $file $y_i $y_f
done

# Unimos todos los NetCDF.
echo
echo "Uniendo todas las coordenadas..."
cdo -O -s collgrid $path_netcdf"*" $output

# Obtenemos el promedio.
echo
echo "Obteniendo los promedios..."
cdo -s ymonmean $output $path_temp$name"_mean.nc"
cdo -s ymonsum $output $path_temp$name"_sum.nc"
python code/mean.py $name $y_i $y_f

echo
echo "Conversión terminada."
echo

# Limpiamos los datos temporales.
rm -r -f $path_temp