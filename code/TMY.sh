# Une todos los CSV de NSRDB en un NetCDF.

# Stop at first error.
set -e

path_netcdf="temp/NetCDF"
output="results/NSRDB_TMY.nc"
y_i=1998
y_f=2022

echo
echo "Generación de NetCDF con datos TMY..."
echo

# Limpiamos los datos temporales.
rm -r -f $path_netcdf
mkdir -p $path_netcdf

echo "Generando archivos TMY..."
python code/TMY.py $y_i $y_f

# Unimos todos los NetCDF.
echo
echo "Uniendo todas las coordenadas..."
cdo -O -s collgrid $path_netcdf"/*" $output

echo
echo "Generación de TMY terminada."
echo

# Limpiamos los datos temporales.
#rm -r -f $path_netcdf