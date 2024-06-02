# Une todos los CSV de NSRDB en un NetCDF.

# Stop at first error.
set -e

# Datos originales.
# Datos para corrección de cuantiles
name="NSRDB_4km"
#name="NSRDB_2km"
path_data="/Volumes/DATA/data/$name"
path_temp="/Volumes/DATA/temp/temp/$name"
path_csv="$path_temp/CSV"
path_netcdf="$path_temp/NetCDF"
path_netcdf_m="$path_temp/NetCDF_m"
path_netcdf_n="$path_temp/NetCDF_n"
output="/Volumes/DATA/data/$name.nc"
outdir="results/$name"

echo
echo "Conversión de CSV a NetCDF"
echo

# Limpiamos los datos temporales.
mkdir -p $path_temp
#rm -r -f $path_temp/*
mkdir -p $path_netcdf
mkdir -p $path_netcdf_m
mkdir -p $path_netcdf_n
mkdir -p $path_csv
mkdir -p $outdir

# Unimos los años en un solo archivo.
#echo "Uniendo archivos de años..."
#python code/nsrdb_mergetime.py $path_data $path_csv
#echo

# Convertimos cada conjunto de CSV en NetCDF.
#echo
#python code/nsrdb_netcdf.py $path_csv $path_netcdf
#echo
#rm -r -f $path_csv

# Unimos todos los NetCDF.
echo
echo "Uniendo todas las coordenadas..."
#rm -r -f $output
#rm -r -f $path_netcdf

name="NSRDB_2km"
path_netcdf="NetCDF"
path_netcdf_m="NetCDF_m"
path_netcdf_n="NetCDF_n"
external="/Volumes/DATA/temp/temp/$name"
for i in {18..20}; do
    for j in {0..9}; do
        for k in {97..100}; do
            for l in {0..9}; do

                if [ ! -f $name/$path_netcdf_m/$i.$j"_"$k.$l.nc ]; then
                    echo "Uniendo $i.$j°N $k.$l°W..."
                    cdo -s -O -P 7 collgrid $name/$path_netcdf/$i/$i.$j*/$i.$j*$k.$l* $name/$path_netcdf_m/$i.$j"_"$k.$l.nc
                    rm -r -f $name/$path_netcdf/$i/$i.$j*/$i.$j*$k.$l*
                    cp $name/$path_netcdf_m/$i.$j"_"$k.$l.nc $external/$path_netcdf_m/$i.$j"_"$k.$l.nc
                fi
            
            done
        done
        
        if [ ! -f $name/$path_netcdf_n/$i.$j.nc ]; then
            echo "Uniendo $i.$j°N..."
            cdo -O -P 1 collgrid $name/$path_netcdf_m/$i.$j* $name/$path_netcdf_n/$i.$j.nc
            rm -r -f $name/$path_netcdf_m/$i.$j*
            rm -r -f $name/$path_netcdf/$i/$i.$j*
            cp $name/$path_netcdf_n/$i.$j.nc $external/$path_netcdf_n/$i.$j.nc
            rm -r $name/$path_netcdf_n/$i.$j.nc
        fi
        
    done
done

cdo -P 2 collgrid $name/$path_netcdf_n/* $name/$name.nc



name="NSRDB_4km"
path_netcdf="NetCDF"
path_netcdf_m="NetCDF_m"
path_netcdf_n="NetCDF_n"
external="/Volumes/DATA/temp/temp/$name"
for i in {18..20}; do
    for j in {0..9}; do
        for k in {97..100}; do
            for l in {0..9}; do

                if [ ! -f $name/$path_netcdf_m/$i.$j"_"$k.$l.nc ]; then
                    echo "Uniendo $i.$j°N $k.$l°W..."
                    cdo -s -O -P 7 collgrid $name/$path_netcdf/$i/$i.$j*/$i.$j*$k.$l* $name/$path_netcdf_m/$i.$j"_"$k.$l.nc
                    rm -r -f $name/$path_netcdf/$i/$i.$j*/$i.$j*$k.$l*
                    cp $name/$path_netcdf_m/$i.$j"_"$k.$l.nc $external/$path_netcdf_m/$i.$j"_"$k.$l.nc
                fi
            
            done
        done
        
        if [ ! -f $name/$path_netcdf_n/$i.$j.nc ]; then
            echo "Uniendo $i.$j°N..."
            cdo -O -P 1 collgrid $name/$path_netcdf_m/$i.$j* $name/$path_netcdf_n/$i.$j.nc
            rm -r -f $name/$path_netcdf_m/$i.$j*
            rm -r -f $name/$path_netcdf/$i/$i.$j*
            cp $name/$path_netcdf_n/$i.$j.nc $external/$path_netcdf_n/$i.$j.nc
            rm -r $name/$path_netcdf_n/$i.$j.nc
        fi
        
    done
done



for i in {18..20}; do
    cdo -O -P 1 collgrid $name/$path_netcdf_n/$i* $name/$path_netcdf_l/$i.nc
    rm -r -f $name/$path_netcdf_n/$i*
    cp $name/$path_netcdf_l/$i.nc $external/$path_netcdf_l/$i.nc
done

cdo collgrid $path_netcdf_n/* $output
#rm -r -f $path_netcdf_m
#cdo -s splityear $output "$outdir/$name""_"

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
#rm -r -f $path_temp