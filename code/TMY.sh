# Stop at first error.
set -e

path_d="/Volumes/DATA/data/WRF_miroc_1985_2014/*"
path_d2="data/WRF_miroc_1985_2014/"
path_c="temp/"
path_r="/Volumes/DATA/temp/"

#for file in $path_d:
#    fname="${file##*/}"
#    echo "$fname"
#
#    cp "$file" "$path_d2$fname"
#
python quantile_model.py
python radiacion_cal.py
python quantile_model.py

bash tmy_prep.sh

python tmy_years.py
python tmy_calc.py
#
#    rsync -a path_c path_r
#    find path_c -type f -exec rm '{}' +