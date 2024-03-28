# Stop at first error.
set -e

path_0="temp/quantile_vars/"
path_d="temp/vars_days/"
path_m="temp/vars_months/"
path_t="temp/temp/"

vars=("Pressure" "Relative_Humidity" "Wind_Direction" )
rvars=("UVHI" "DNI" "GHI")
for v in "${vars[@]}"
do
    echo "$v"
    p="$path_0$v/*"
    for file in $p
    do
        fname="${file##*/}"
        cdo -s chname,time,XTIME "$path_0$v/$fname" "$path_t$fname"
        cdo -s ymonmean "$path_t$fname" "$path_m$v/$fname"
        cdo -s daymean "$path_t$fname" "$path_d$v/$fname"
        rm -r -f "$path_t$fname"
    done
done

for v in "${rvars[@]}"
do
    echo "$v"
    p="$path_0$v/*"
    for file in $p
    do
        fname=${file##*/}
        cdo -s chname,time,XTIME "$path_0$v/$fname" "$path_t$fname"
        cdo -s monsum "$path_t$fname" "$path_m$v/$fname"
        cdo -s daysum "$path_t$fname" "$path_d$v/$fname"
        rm -r -f "$path_t$fname"
    done
done

echo "Temperature"
p="$path_0""Temperature/*"
for file in $p
do
    fname=${file##*/}
    cdo -s chname,time,XTIME "$path_0""Temperature/$fname" "$path_t$fname"

    cdo -s monmean "$path_t$fname" "$path_m""Temperature/$fname"

    cdo -s daymean "$path_t$fname" "$path_d""T_mean/$fname"
    cdo -s daymax "$path_t$fname" "$path_d""T_max/$fname"
    cdo -s daymin "$path_t$fname" "$path_d""T_min/$fname"

    cdo -s setname,T_mean "$path_d""T_mean/$fname" "$path_t$fname"
    mv -f "$path_t$fname" "$path_d""T_mean/$fname"
    cdo -s setname,T_max "$path_d""T_max/$fname" "$path_t$fname"
    mv -f "$path_t$fname" "$path_d""T_max/$fname"
    cdo -s setname,T_min "$path_d""T_min/$fname" "$path_t$fname"
    mv -f "$path_t$fname" "$path_d""T_min/$fname"

    rm -r -f "$path_t$fname"
done

echo "Dew_Point"
p="$path_0""Dew_Point/*"
for file in $p
do
    fname=${file##*/}
    cdo -s chname,time,XTIME "$path_0""Dew_Point/$fname" "$path_t$fname"

    cdo -s monmean "$path_t$fname" "$path_m""Dew_Point/$fname"

    cdo -s daymean "$path_t$fname" "$path_d""Dp_mean/$fname"
    cdo -s daymax "$path_t$fname" "$path_d""Dp_max/$fname"
    cdo -s daymin "$path_t$fname" "$path_d""Dp_min/$fname"

    cdo -s setname,Dp_mean "$path_d""Dp_mean/$fname" "$path_t$fname"
    mv -f "$path_t$fname" "$path_d""Dp_mean/$fname"
    cdo -s setname,Dp_max "$path_d""Dp_max/$fname" "$path_t$fname"
    mv -f "$path_t$fname" "$path_d""Dp_max/$fname"
    cdo -s setname,Dp_min "$path_d""Dp_min/$fname" "$path_t$fname"
    mv -f "$path_t$fname" "$path_d""Dp_min/$fname"

    rm -r -f "$path_t$fname"
done

echo "Wind_Speed"
p="$path_0""Wind_Speed/*"
for file in $p
do
    fname=${file##*/}
    cdo -s chname,time,XTIME "$path_0""Wind_Speed/$fname" "$path_t$fname"

    cdo -s monmean "$path_t$fname" "$path_m""Wind_Speed/$fname"

    cdo -s daymean "$path_t$fname" "$path_d""W_mean/$fname"
    cdo -s daymax "$path_t$fname" "$path_d""W_max/$fname"

    cdo -s setname,W_mean "$path_d""W_mean/"$fname "$path_t$fname"
    mv -f "$path_t$fname" "$path_d""W_mean/$fname"
    cdo -s setname,W_max "$path_d""W_max/$fname" "$path_t$fname"
    mv -f "$path_t$fname" "$path_d""W_max/$fname"

    rm -r -f "$path_t$fname"
done