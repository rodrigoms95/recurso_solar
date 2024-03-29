# Pasamos de valores horarios a diarios y promedios mensuales.

# Stop at first error.
set -e

# Rutas de archivos.
path_0="temp/quantile_vars/"
path_d="temp/vars_days/"
path_m="temp/vars_months/"
path_t="temp/temp/"

# Cálculos de medias.
vars=("Pressure" "Relative_Humidity" "Wind_Direction" )
for v in "${vars[@]}"
do
    #echo "$v"
    p="$path_0$v/*"
    for file in $p
    do
        fname="${file##*/}"
        cdo -s -w daymean "$path_0$v/$fname" "$path_d$v/$fname"
        cdo -s -w ymonmean "$path_0$v/$fname" "$path_m$v/$fname"
    done
done

# Cálculos de variables de radiación.
rvars=("UVHI" "DNI" "GHI" "P_mp")
for v in "${rvars[@]}"
do
    #echo "$v"
    p="$path_0$v/*"
    for file in $p
    do
        fname=${file##*/}
        cdo -s -w daysum "$path_0$v/$fname" "$path_d$v/$fname"
        cdo -s -w ymonsum "$path_0$v/$fname" "$path_m$v/$fname"
        y=$(cdo nyear "$path_0$v/$fname")
        cdo -s divc,$y "$path_m$v/$fname" "$path_t$fname"
        mv -f  "$path_t$fname" "$path_m$v/$fname"
    done
done

# Variables para TMY.

#echo "Temperature"
p="$path_0""Temperature/*"
for file in $p
do
    fname=${file##*/}

    cdo -s -w daymean "$path_0""Temperature/$fname" "$path_d""T_mean/$fname"
    cdo -s -w daymax "$path_0""Temperature/$fname" "$path_d""T_max/$fname"
    cdo -s -w daymin "$path_0""Temperature/$fname" "$path_d""T_min/$fname"

    cdo -s -w ymonmean "$path_0""Temperature/$fname" "$path_m""Temperature/$fname"

    cdo -s -w setname,T_mean "$path_d""T_mean/$fname" "$path_t$fname"
    mv -f "$path_t$fname" "$path_d""T_mean/$fname"
    cdo -s -w setname,T_max "$path_d""T_max/$fname" "$path_t$fname"
    mv -f "$path_t$fname" "$path_d""T_max/$fname"
    cdo -s -w setname,T_min "$path_d""T_min/$fname" "$path_t$fname"
    mv -f "$path_t$fname" "$path_d""T_min/$fname"

done

#echo "Dew_Point"
p="$path_0""Dew_Point/*"
for file in $p
do
    fname=${file##*/}

    cdo -s -w daymean "$path_0""Dew_Point/$fname" "$path_d""Dp_mean/$fname"
    cdo -s -w daymax "$path_0""Dew_Point/$fname" "$path_d""Dp_max/$fname"
    cdo -s -w daymin "$path_0""Dew_Point/$fname" "$path_d""Dp_min/$fname"

    cdo -s -w ymonmean "$path_0""Dew_Point/$fname" "$path_m""Dew_Point/$fname"

    cdo -s -w setname,Dp_mean "$path_d""Dp_mean/$fname" "$path_t$fname"
    mv -f "$path_t$fname" "$path_d""Dp_mean/$fname"
    cdo -s -w setname,Dp_max "$path_d""Dp_max/$fname" "$path_t$fname"
    mv -f "$path_t$fname" "$path_d""Dp_max/$fname"
    cdo -s -w setname,Dp_min "$path_d""Dp_min/$fname" "$path_t$fname"
    mv -f "$path_t$fname" "$path_d""Dp_min/$fname"
done

#echo "Wind_Speed"
p="$path_0""Wind_Speed/*"
for file in $p
do
    fname=${file##*/}

    cdo -s -w daymean "$path_0""Wind_Speed/$fname" "$path_d""W_mean/$fname"
    cdo -s -w daymax "$path_0""Wind_Speed/$fname" "$path_d""W_max/$fname"

    cdo -s -w ymonmean "$path_0""Wind_Speed/$fname" "$path_m""Wind_Speed/$fname"

    cdo -s -w setname,W_mean "$path_d""W_mean/"$fname "$path_t$fname"
    mv -f "$path_t$fname" "$path_d""W_mean/$fname"
    cdo -s -w setname,W_max "$path_d""W_max/$fname" "$path_t$fname"
    mv -f "$path_t$fname" "$path_d""W_max/$fname"

done