# Une todos los CSV de NSRDB en un NetCDF.

# Stop at first error.
set -e

# Datos originales.
#name="NSRDB"
# Datos para corrección de cuantiles
name="NSRDB_2km"
path_temp="temp/NSRDB/"
path_nsrdb="$path_temp$name/*"
path_netcdf=$path_temp"NetCDF/"
output="results/$name.nc"
y_i=1998
#y_i=2006
y_f=2022

echo
echo "Conversión de CSV a NetCDF"
echo

# Limpiamos los datos temporales.
rm -r -f $path_temp
mkdir -p $path_netcdf

# Unimos los años en un solo archivo.
echo "Uniendo archivos de años..."
python code/nsrdb_mergetime.py $name $y_i $y_f
echo

# Convertimos cada conjunto de CSV en NetCDF.
for file in $path_nsrdb; do
    base_name=${file%.*}
    echo "Procesando coordenadas ${base_name##*/}..."
    python code/nsrdb_netcdf.py $file $y_i $y_f
done

# Unimos todos los NetCDF.
echo
echo "Uniendo todas las coordenadas..."
cdo -O -s collgrid $path_netcdf"*" $output

# Obtenemos el promedio.
#echo
#echo "Obteniendo los promedios..."
#cdo -s ymonmean $output $path_temp$name"_mean.nc"
#cdo -s ymonsum $output $path_temp$name"_sum.nc"
#python code/mean.py $name $y_i $y_f

echo
echo "Conversión de CSV a NetCDF terminada."
echo

# Limpiamos los datos temporales.
rm -r -f $path_temp