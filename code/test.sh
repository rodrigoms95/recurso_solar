# Stop at first error.
set -e

path_0="temp/quantile_vars/"
path_d="temp/vars_months/"

path_0="/Volumes/DATA/temp/quantile_vars/"
path_d="/Volumes/DATA/temp/vars_months/"

vars=("Pressure" "Relative Humidity" "Wind Direction" )
#rvars=("UVHI" "DNI" "GHI")
for v in "${vars[@]}"; do
    p="$path_0$v"
    echo $p
done