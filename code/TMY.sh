# Une todos los CSV de NSRDB en un NetCDF.

# Stop at first error.
set -e

# Datos originales.
name="NSRDB"
# Datos con corrección de cuantiles
#name="NSRDB_quantile"
path_temp="temp/"
path_netcdf=$path_temp"NetCDF/"
path_nsrdb="results/"$name".nc"
output="results/"$name"_TMY.nc"
y_i=1998
y_f=2022

echo
echo "Generación de NetCDF con datos TMY"
echo

# Limpiamos los datos temporales.
rm -r -f $path_temp
mkdir -p $path_netcdf

latitud=("19.41" "19.45")
longitud=("-99.14" "-99.18")

echo "Generando archivos TMY..."
echo
for lat in ${latitud[@]}; do
    for lon in ${longitud[@]}; do
        echo "Procesando coordenadas "$lat"°"$lon"°..."
        cdo -s sellonlatbox,$lon,$lon,$lat,$lat $path_nsrdb $path_netcdf$lat"_"$lon".nc"
        python code/TMY.py $lat $lon $y_i $y_f
        rm -r -f $path_netcdf$lat"_"$lon".nc"
    done
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
echo "Generación de TMY terminada."
echo

# Limpiamos los datos temporales.
rm -r -f $path_temp