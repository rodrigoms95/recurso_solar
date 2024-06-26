# Une todos los CSV de NSRDB en un NetCDF.

# Stop at first error.
set -e

# Datos originales.
# Datos para corrección de cuantiles
name="NSRDB_4km"
path_data="/Volumes/DATA/data/$name"
external="/Volumes/DATA/temp/$name"
internal="temp/$name"
path_csv="CSV"
path_netcdf="NetCDF"
path_netcdf_m="NetCDF_m"
path_netcdf_n="NetCDF_n"

echo
echo "Conversión de CSV a NetCDF"
echo

# Limpiamos los datos temporales.
mkdir -p "$external/$path_netcdf"
mkdir -p "$external/$path_netcdf_m"
mkdir -p "$external/$path_netcdf_n"
mkdir -p "$external/$path_csv"

mkdir -p "$internal/$path_netcdf"
mkdir -p "$internal/$path_netcdf_m"
mkdir -p "$internal/$path_netcdf_n"
mkdir -p "$internal/$path_csv"

if [ ! -f "$path_data.nc" ]; then
    # Unimos los años en un solo archivo.
    echo "Uniendo archivos de años..."
    python code/nsrdb_mergetime.py "$path_data" "$external/$path_csv" "$name"
    echo

    # Convertimos cada conjunto de CSV en NetCDF.
    echo
    python code/nsrdb_netcdf.py "$external/$path_csv" "$external/$path_netcdf" "$name"
    echo

    # Unimos todos los NetCDF.
    echo
    echo "Uniendo todas las coordenadas..."
    echo

    for i in {18..19}; do
        rsync -r "$external/NetCDF/$i/" "$internal/$path_netcdf/$i/"
        for j in {0..9}; do

            k=97
            for l in {2..9}; do
                if [ ! -f "$external/$path_netcdf_m/$i.$j""_$k.$l.nc" ]; then
                    echo "Uniendo $i.$j""°N $k.$l""°W..."
                    cdo -s -O -P 7 collgrid $internal/$path_netcdf/$i/$i.$j*/$i.$j*$k.$l* $internal/$path_netcdf_m/$i.$j"_"$k.$l.nc
                    rm -f $internal/$path_netcdf/$i/$i.$j*/$i.$j*$k.$l*
                    rsync $internal/$path_netcdf_m/$i.$j"_"$k.$l.nc $external/$path_netcdf_m/$i.$j"_"$k.$l.nc
                fi
            done

            for k in {98..99}; do
                for l in {0..9}; do
                    if [ ! -f "$external/$path_netcdf_m/$i.$j""_$k.$l.nc" ]; then
                        echo "Uniendo $i.$j""°N $k.$l""°W..."
                        cdo -s -O -P 7 collgrid $internal/$path_netcdf/$i/$i.$j*/$i.$j*$k.$l* $internal/$path_netcdf_m/$i.$j"_"$k.$l.nc
                        rm -f $internal/$path_netcdf/$i/$i.$j*/$i.$j*$k.$l*
                        rsync $internal/$path_netcdf_m/$i.$j"_"$k.$l.nc $external/$path_netcdf_m/$i.$j"_"$k.$l.nc
                    fi
                done
            done

            k=100
            for l in {0..4}; do
                if [ ! -f "$external/$path_netcdf_m/$i.$j""_$k.$l.nc" ]; then
                    echo "Uniendo $i.$j""°N $k.$l""°W..."
                    cdo -s -O -P 7 collgrid $internal/$path_netcdf/$i/$i.$j*/$i.$j*$k.$l* $internal/$path_netcdf_m/$i.$j"_"$k.$l.nc
                    rm -f $internal/$path_netcdf/$i/$i.$j*/$i.$j*$k.$l*
                    rsync $internal/$path_netcdf_m/$i.$j"_"$k.$l.nc $external/$path_netcdf_m/$i.$j"_"$k.$l.nc
                fi
            done
            
            if [ ! -f "$external/$path_netcdf_n/$i.$j.nc" ]; then
                echo "Uniendo $i.$j""°N..."
                rsync $external/$path_netcdf_m/$i.$j* $internal/$path_netcdf_m/
                cdo -O -P 1 collgrid $internal/$path_netcdf_m/$i.$j* $internal/$path_netcdf_n/$i.$j.nc
                rm -f $internal/$path_netcdf_m/$i.$j*
                rsync $internal/$path_netcdf_n/$i.$j.nc $external/$path_netcdf_n/$i.$j.nc
            fi

            rm -r -f $internal/$path_netcdf/$i/$i.$j*/
        done
        rm -r -f "$internal/$path_netcdf/$i/"
    done

    i=20
    rsync -r "$external/NetCDF/$i/" "$internal/$path_netcdf/$i/"
    for j in {0..6}; do

        k=97
        for l in {2..9}; do
            if [ ! -f "$external/$path_netcdf_m/$i.$j""_$k.$l.nc" ]; then
                echo "Uniendo $i.$j""°N $k.$l""°W..."
                cdo -s -O -P 7 collgrid $internal/$path_netcdf/$i/$i.$j*/$i.$j*$k.$l* $internal/$path_netcdf_m/$i.$j"_"$k.$l.nc
                rm -f $internal/$path_netcdf/$i/$i.$j*/$i.$j*$k.$l*
                rsync $internal/$path_netcdf_m/$i.$j"_"$k.$l.nc $external/$path_netcdf_m/$i.$j"_"$k.$l.nc
            fi
        done

        for k in {98..99}; do
            for l in {0..9}; do
                if [ ! -f "$external/$path_netcdf_m/$i.$j""_$k.$l.nc" ]; then
                    echo "Uniendo $i.$j""°N $k.$l""°W..."
                    cdo -s -O -P 7 collgrid $internal/$path_netcdf/$i/$i.$j*/$i.$j*$k.$l* $internal/$path_netcdf_m/$i.$j"_"$k.$l.nc
                    rm -f $internal/$path_netcdf/$i/$i.$j*/$i.$j*$k.$l*
                    rsync $internal/$path_netcdf_m/$i.$j"_"$k.$l.nc $external/$path_netcdf_m/$i.$j"_"$k.$l.nc
                fi
            done
        done

        k=100
        for l in {0..4}; do
            if [ ! -f "$external/$path_netcdf_m/$i.$j""_$k.$l.nc" ]; then
                echo "Uniendo $i.$j""°N $k.$l""°W..."
                cdo -s -O -P 7 collgrid $internal/$path_netcdf/$i/$i.$j*/$i.$j*$k.$l* $internal/$path_netcdf_m/$i.$j"_"$k.$l.nc
                rm -f $internal/$path_netcdf/$i/$i.$j*/$i.$j*$k.$l*
                rsync $internal/$path_netcdf_m/$i.$j"_"$k.$l.nc $external/$path_netcdf_m/$i.$j"_"$k.$l.nc
            fi
        done
        
        if [ ! -f "$external/$path_netcdf_n/$i.$j.nc" ]; then
            echo "Uniendo $i.$j""°N..."
            rsync $external/$path_netcdf_m/$i.$j* $internal/$path_netcdf_m/
            cdo -O -P 1 collgrid $internal/$path_netcdf_m/$i.$j* $internal/$path_netcdf_n/$i.$j.nc
            rm -f $internal/$path_netcdf_m/$i.$j*
            rsync $internal/$path_netcdf_n/$i.$j.nc $external/$path_netcdf_n/$i.$j.nc
        fi
        
        rm -r -f $internal/$path_netcdf/$i/$i.$j*/
    done
    rm -r -f "$internal/$path_netcdf/$i/"

    rsync -r "$external/$path_netcdf_n/" "$internal/$path_netcdf_n/"
    cdo -P 2 collgrid "$internal/$path_netcdf_n/"* "$internal/$name.nc"
    rsync "$internal/$name.nc" "$path_data.nc"
    rm -f "$internal/$path_netcdf_n/"*
fi

if [ ! -f "$external/$name""_promedio.nc" ]; then
    printf "\n\nCalculando promedio...\n"
    rsync "$path_data.nc" "$internal/$name.nc"
    v1="GHI"
    v2="UVHI"
    cdo -L -s -timavg -yearsum -selname,"$v1","$v2" "$internal/$name.nc" "$internal/$name""_promedio.nc"
    rsync "$internal/$name""_promedio.nc" "$external/$name""_promedio.nc"
fi

rm -f "$internal/$name.nc"

echo
    echo "$name"" unido."
    echo