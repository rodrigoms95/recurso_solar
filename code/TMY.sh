# Une todos los CSV de NSRDB en un NetCDF.

# Stop at first error.
set -e

name="NSRDB_TMY"
path_temp="temp/"
path_netcdf=$path_temp"NetCDF/"
output="results/"$name".nc"
y_i=1998
y_f=2022

echo
echo "Generación de NetCDF con datos TMY..."
echo

# Limpiamos los datos temporales.
rm -r -f $path_temp
mkdir -p $path_netcdf

echo "Generando archivos TMY..."
python code/TMY.py $y_i $y_f

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
echo "Generación de TMY terminada."
echo

# Limpiamos los datos temporales.
rm -r -f $path_temp