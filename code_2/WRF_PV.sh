# Parar al primer error
set -e

printf "\nCalculando escenarios de generación fotovoltaica\n\n"

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Escenario a calcular
for scn in "2040_2060"; do #"2080_2089" "2040_2060_100PorcUrbano" "2080_2089_100PorcUrbano"; do
    dr=/home/rodr/buffalo/rodr/WRF/$scn/$scn
    printf "\nCalculando generación fotovoltaica para $scn\n"
    # Copiamos los archivos
    printf "Copiando archivos\n"
    mkdir -p $dr
    for zmegalo in /home/rodr/buffalo/SalidasWRF/$scn/*/ ; do
        dd=$zmegalo/Dominio02/variables_2Dimension
        cd $dd
        for j in zSalidaIRainWRF_*.nc; do
            printf "$j                  \r"
            if [ ! -d "/home/rodr/buffalo/rodr/WRF/$scn/data/" ] && [ ! -f "$dr/$j" ]; then
                cp $j $dr/$j
            fi
        done
    done
    printf "\n\n"

    # Sacamos las variables de interés
    python $SCRIPT_DIR/WRF_extract.py $scn
    # Calculamos la generación fotovoltaica
    python $SCRIPT_DIR/WRF_PV.py $scn
    # Obtenemos los máximos
    python $SCRIPT_DIR/get_max.py $scn
    # Unimos el tiempo
    python $SCRIPT_DIR/merge_time.py $scn
    # Calculamos cuantiles
    # python $SCRIPT_DIR/cdf_wrf.py $scn "_PV"
    # python $SCRIPT_DIR/cdf_wrf.py $scn ""
    # Mapeo de cuantiles
    # python $SCRIPT_DIR/quantile_calc.py $scn "_PV"
    # python $SCRIPT_DIR/quantile_calc.py $scn ""
    rm -rf $dr

done

printf "\nCálculo de escenarios de generación fotovoltaica terminado.\n"