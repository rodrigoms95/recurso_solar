# Une todos los CSV de NSRDB en un NetCDF.

# Stop at first error.
set -e

# Datos originales.
# Datos para corrección de cuantiles
name="NSRDB_4km"
path_data="~/Datos/NSRDB/$name"
internal="~/temp/recurso_solar/$name"
path_csv="CSV"
path_netcdf="NetCDF"
path_netcdf_m="NetCDF_m"
path_netcdf_n="NetCDF_n"

printf "\nConversión de CSV a NetCDF"

# Limpiamos los datos temporales.
mkdir -p "$internal/$path_netcdf"
mkdir -p "$internal/$path_netcdf_m"
mkdir -p "$internal/$path_netcdf_n"
mkdir -p "$internal/$path_csv"

if [ ! -f "$path_data.nc" ]; then
    # Unimos los años en un solo archivo.
    printf "\n\nUniendo archivos de años..."
    python code/nsrdb_mergetime.py "$path_data" "$internal/$path_csv"

    # Convertimos cada conjunto de CSV en NetCDF.
    python code/nsrdb_netcdf.py "$internal/$path_csv" "$internal/$path_netcdf"

    # Unimos todos los NetCDF.
    echo "\n\nUniendo todas las coordenadas..."
    for i in {18..19}; do
        for j in {0..9}; do

            k=97
            for l in {2..9}; do
                if [ ! -f "$internal/$path_netcdf_m/$i.$j""_$k.$l.nc" ]; then
                    printf "\n\nUniendo $i.$j""°N $k.$l""°W..."
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
    done

    i=20
    for j in {0..6}; do

        k=97
        for l in {2..9}; do
            if [ ! -f "$internal/$path_netcdf_m/$i.$j""_$k.$l.nc" ]; then
                printf "\n\nUniendo $i.$j""°N $k.$l""°W..."
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

    printf "\n\n$name"" unido."
fi

lat=$(cdo griddes "$path_data.nc" | awk 'NR==7{print $3}')
directory="grid"
mkdir -p "$internal/$directory"

if [ ! -f "$internal/$directory/$name""_$((lat-1)).nc" ]; then
    printf "\n\nGenerando malla..."
    for ((i=0;i<lat;i++)); do
        printf "\nProcesando malla $((i+1))/$lat"
        if [ ! -f "$internal/$directory/"$name"_$i.nc" ]; then
            python code/tot_grid.py "$i" "$internal" "$name" 
        fi
    done
fi

#vars=("Pressure" "Temperature" "Wind Speed" "DNI" "GHI" "UVHI")
vars=("${(@s[ ])$(cdo showname $internal/$directory/"$name"_0.nc)}")
if [ ! -f "$internal/${vars[1]}/$name""_$((lat-1)).nc" ]; then
    printf "\n\nCalculando cuantiles..."
    for v in "${vars[@]}"; do; mkdir -p "$internal/vars/$v"; done
    for ((i=0;i<lat;i++)); do
        printf "\n\nProcesando malla $((i+1))/$lat"
        if [ ! -f "$internal/vars/$v/"$name"_$i.nc" ]; then
            python code/cdf_wrf.py "$i" "$internal" "$name" "$directory"
        fi
    done
fi