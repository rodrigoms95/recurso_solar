# Une todos los CSV de NSRDB en un NetCDF.

# Stop at first error.
set -e

# Datos originales.
# Datos para corrección de cuantiles
name="NSRDB_2km"
path_data="../../Datos/NSRDB/$name"
internal="../../temp/recurso_solar/$name"
path_csv="CSV"
path_netcdf="NetCDF"
path_netcdf_m="NetCDF_m"
path_netcdf_n="NetCDF_n"

printf "\nConversión de CSV a NetCDF"

# Limpiamos los datos temporales.
mkdir -p "$internal/$path_netcdf"
mkdir -p "$internal/$path_netcdf/18"
mkdir -p "$internal/$path_netcdf/19"
mkdir -p "$internal/$path_netcdf/20"
mkdir -p "$internal/$path_netcdf_m"
mkdir -p "$internal/$path_netcdf_n"
mkdir -p "$internal/$path_csv"

if [ ! -f "$path_data.nc" ]; then
    # Unimos los años en un solo archivo.
    printf "\n\nUniendo archivos de años...\n"
    python code/nsrdb_mergetime.py "$path_data" "$internal/$path_csv" "$name"

    # Convertimos cada conjunto de CSV en NetCDF.
    python code/nsrdb_netcdf.py "$internal/$path_csv" "$internal/$path_netcdf" "$name"

    # Unimos todos los NetCDF.
    printf "\n\nUniendo todas las coordenadas...\n"
    for i in {18..19}; do
        for j in {0..9}; do

            k=97
            for l in {2..9}; do
                if [ ! -f "$internal/$path_netcdf_m/$i.$j""_$k.$l.nc" ]; then
                    printf "\nUniendo $i.$j""°N $k.$l""°W..."
                    cdo -s -O -P 7 collgrid $internal/$path_netcdf/$i/$i.$j*/$i.$j*$k.$l* $internal/$path_netcdf_m/$i.$j"_"$k.$l.nc
                fi
            done

            for k in {98..99}; do
                for l in {0..9}; do
                    if [ ! -f "$internal/$path_netcdf_m/$i.$j""_$k.$l.nc" ]; then
                        printf "\nUniendo $i.$j""°N $k.$l""°W..."
                        cdo -s -O -P 7 collgrid $internal/$path_netcdf/$i/$i.$j*/$i.$j*$k.$l* $internal/$path_netcdf_m/$i.$j"_"$k.$l.nc
                    fi
                done
            done

            k=100
            for l in {0..4}; do
                if [ ! -f "$internal/$path_netcdf_m/$i.$j""_$k.$l.nc" ]; then
                    printf "\nUniendo $i.$j""°N $k.$l""°W..."
                    cdo -s -O -P 7 collgrid $internal/$path_netcdf/$i/$i.$j*/$i.$j*$k.$l* $internal/$path_netcdf_m/$i.$j"_"$k.$l.nc
                fi
            done
            
            if [ ! -f "$internal/$path_netcdf_n/$i.$j.nc" ]; then
                printf "\nUniendo $i.$j""°N...\n"
                cdo -O -P 1 collgrid $internal/$path_netcdf_m/$i.$j* $internal/$path_netcdf_n/$i.$j.nc
            fi

        done
    done

    i=20
    for j in {0..6}; do

        k=97
        for l in {2..9}; do
            if [ ! -f "$internal/$path_netcdf_m/$i.$j""_$k.$l.nc" ]; then
                printf "\nniendo $i.$j""°N $k.$l""°W..."
                cdo -s -O -P 7 collgrid $internal/$path_netcdf/$i/$i.$j*/$i.$j*$k.$l* $internal/$path_netcdf_m/$i.$j"_"$k.$l.nc
            fi
        done

        for k in {98..99}; do
            for l in {0..9}; do
                if [ ! -f "$internal/$path_netcdf_m/$i.$j""_$k.$l.nc" ]; then
                    printf "\nUniendo $i.$j""°N $k.$l""°W..."
                    cdo -s -O -P 7 collgrid $internal/$path_netcdf/$i/$i.$j*/$i.$j*$k.$l* $internal/$path_netcdf_m/$i.$j"_"$k.$l.nc
                fi
            done
        done

        k=100
        for l in {0..4}; do
            if [ ! -f "$internal/$path_netcdf_m/$i.$j""_$k.$l.nc" ]; then
                printf "\nUniendo $i.$j""°N $k.$l""°W..."
                cdo -s -O -P 7 collgrid $internal/$path_netcdf/$i/$i.$j*/$i.$j*$k.$l* $internal/$path_netcdf_m/$i.$j"_"$k.$l.nc
            fi
        done
        
        if [ ! -f "$internal/$path_netcdf_n/$i.$j.nc" ]; then
            printf "\nUniendo $i.$j""°N..."
            cdo -O -P 1 collgrid $internal/$path_netcdf_m/$i.$j* $internal/$path_netcdf_n/$i.$j.nc
        fi
        
    done

    cdo -P 2 collgrid "$internal/$path_netcdf_n/"* "$internal/$name.nc"

fi

if [ ! -f "$external/$name""_promedio.nc" ]; then
    printf "\n\nCalculando promedio...\n"
    v1="GHI"
    if [ $name -eq "NSRDB_4km" ]; then
        v2="UVHI"
        cdo -L -s -timavg -yearsum -selname,"$v1","$v2" "$internal/$name.nc" "$internal/$name""_promedio.nc"
    else
        cdo -L -s -timavg -yearsum -selname,"$v1" "$internal/$name.nc" "$internal/$name""_promedio.nc"
    fi
fi

printf "\n\n$name"" unido."