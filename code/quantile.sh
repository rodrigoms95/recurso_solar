# Une todos los CSV de NSRDB en un NetCDF.

# Stop at first error.
set -e

# Datos originales.
name_1="NSRDB"
# Datos para corrección de cuantiles
name_2="NSRDB_2"
path_1="results/"$name_1".nc"
path_2="results/"$name_2".nc"
path_temp="temp/"
path_netcdf=$path_temp"NetCDF/"
output_1="results/"$name_1"_mapped.nc"
output_2="results/"$name_1"_quantiles.nc"
y_i=2006
y_f=2022

echo
echo "Corrección de cuantiles"
echo

# Limpiamos los datos temporales.
rm -r -f $path_temp
mkdir -p $path_netcdf

latitud=("19.41" "19.45")
longitud=("-99.14" "-99.18")

echo "Haciendo corrección de cuantiles..."
echo
for lat in ${latitud[@]}; do
    for lon in ${longitud[@]}; do
        echo "Procesando coordenadas "$lat"°"$lon"°..."
        cdo -s sellonlatbox,$lon,$lon,$lat,$lat $path_1 $path_netcdf$name_1"_"$lat"_"$lon".nc"
        cdo -s sellonlatbox,$lon,$lon,$lat,$lat $path_2 $path_netcdf$name_2"_"$lat"_"$lon".nc"
        python code/quantile.py $name_1 $name_2 $lat $lon
        rm -r -f $path_netcdf$name_1"_"$lat"_"$lon".nc"
        rm -r -f $path_netcdf$name_2"_"$lat"_"$lon".nc"
    done
done

# Unimos todos los NetCDF.
echo
echo "Uniendo todas las coordenadas..."
cdo -O -s collgrid $path_netcdf"*_mapped.nc" $output_1
cdo -O -s collgrid $path_netcdf"*_quantiles.nc" $output_2

# Obtenemos el promedio.
echo
echo "Obteniendo los promedios..."
cdo -s ymonmean $output_1 $path_temp$name_1"_mapped_mean.nc"
cdo -s ymonsum $output_1 $path_temp$name_1"_mapped_sum.nc"
python code/mean.py $name_1"_mapped" $y_i $y_f

echo
echo "Corrección de cuantiles terminada."
echo

# Limpiamos los datos temporales.
rm -r -f $path_temp