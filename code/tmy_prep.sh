# Stop at first error.
set -e

#path_0="temp/quantile_vars/"
#path_d="temp/vars_days/"
#path_m="temp/vars_months/"
path_0="/Volumes/DATA/temp/quantile_vars/"
path_d="/Volumes/DATA/temp/vars_days/"
path_m="/Volumes/DATA/temp/vars_months/"
path_t="/Volumes/DATA/temp/temp/"

vars=("Pressure" "Relative_Humidity" "Wind_Direction" )
rvars=("UVHI" "DNI" "GHI")
for v in "${vars[@]}"
do
    p="$path_0$v/*"
    for file in $p
    do
        fname="${file##*/}"
        echo "$file"
        cdo chname,time,XTIME "$path_0$v/$fname" "$path_t$fname"
        cdo ymonmean "$path_t$fname" "$path_m$v/$fname"
        cdo daymean "$path_t$fname" "$path_d$v/$fname"
        rm -r -f "$path_t$fname"
    done
done

for v in "${rvars[@]}"
do
    p="$path_0$v/*"
    for file in $p
    do
        fname=${file##*/}
        cdo chname,time,XTIME $path_0"$v/"$fname $path_t$fname
        cdo monsum $path_t$fname $path_m"$v/"$fname
        cdo daysum $path_t$fname $path_d"$v/"$fname
        rm -r -f $path_t$fname
    done
done

p="$path_0""Temperature/*"
for file in $p
do
    fname=${file##*/}
    cdo chname,time,XTIME $path_0"Temperature/"$fname $path_t$fname

    cdo monmean $path_t$fname $path_m"Temperature/"$fname

    cdo daymean $path_t$fname $path_d"Mean Temperature/"$fname
    cdo daymax $path_t$fname $path_d"Maximum Temperature/"$fname
    cdo daymin $path_t$fname $path_d"Minimum Temperature/"$fname

    cdo setname,"T_mean" $path_d"Mean Temperature/"$fname $path_d"Mean Temperature/"$fname
    cdo setname,"T_max" $path_d"Maximum Temperature/"$fname $path_d"Maximum Temperature/"$fname
    cdo setname,"T_min" $path_d"Minimum Temperature"$fname $path_d"Minimum Temperature/"$fname

    rm -r -f $path_t$fname
done

p="$path_0""Dew Point/*"
for file in $p
do
    fname=${file##*/}
    cdo chname,time,XTIME $path_0"Dew Point/"$fname $path_t$fname

    cdo monmean $path_t$fname $path_m"Dew Point/"$fname

    cdo daymean $path_t$fname $path_d"Mean Dew Point/"$fname
    cdo daymax $path_t$fname $path_d"Maximum Dew Point/"$fname
    cdo daymin $$path_t$fname $path_d"Minimum Dew Point/"$fname

    cdo setname,"Dp_mean" $path_d"Mean Dew Point/"$fname $path_d"Mean Dew Point/"$fname
    cdo setname,"Dp_max" $path_d"Maximum Dew Point/"$fname $path_d"Maximum Dew Point/"$fname
    cdo setname,"Dp_min" $path_d"Minimum Dew Point"$fname $path_d"Minimum Dew Point/"$fname

    rm -r -f $path_t$fname
done

p="$path_0""Wind Speed/*"
for file in $p
do
    fname=${file##*/}
    cdo chname,time,XTIME $path_0"Wind Speed/"$fname $path_t$fname

    cdo monmean $path_t$fname $path_m"Wind Speed/"$fname

    cdo daymean $path_t$fname $path_d"Mean Wind Speed/"$fname
    cdo daymax $path_t$fname $path_d"Maximum Wind Speed/"$fname

    cdo setname,"W_mean" $path_d"Mean Wind Speed/"$fname $path_d"Mean Wind Speed/"$fname
    cdo setname,"W_max" $path_d"Maximum Wind Speed/"$fname $path_d"Maximum Wind Speed/"$fname

    rm -r -f $path_t$fname
done