# Calculamos el TMY de un NetCDF.

# Stop at first error.
set -e

echo "Procesando archivos TMY..."
echo

# Rutas de archivos.
path_d="/Volumes/DATA/data/WRF_miroc_1985_2014/*"
path_d2="data/WRF_miroc_1985_2014/"
path_t="temp/"
path_r="/Volumes/DATA/temp/"

# Limpieza inicial.
find $path_t ! -type d -delete
rm -r -f $path_d2

# Iteramos para todos las zonas del NetCDF.
for file in $path_d
do
    fname="${file##*/}"
    date
    echo "$fname"

    # Copiamos el archivo del disco duro a la computadora.
    mkdir -p $path_d2
    cp "$file" "$path_d2$fname"

    # Preparamos los archivos para el mapeo de cuantiles.
    python code/quantile_prep.py
    # Calculamos las variables de radiación.
    python code/radiacion_calc.py
    # Calculamos la curva de distribución acumulada del modelo.
    python code/cdf_model.py

    # Obtenemos valores diarios y promedios mensuales.
    bash code/resample.sh

    # Cálculamos los años para el TMY.
    python code/tmy_years.py
    # Obtenemos el TMY.
    python code/tmy_calc.py

    # Copiamos toda la información al disco duro.
    rsync -a $path_t $path_r
    # Borramos los archivos y dejamos las carpetas en la computadora.
    find $path_t ! -type d -delete
    rm -r -f $path_d2

    echo
done

echo "Procesamiento terminado."
echo