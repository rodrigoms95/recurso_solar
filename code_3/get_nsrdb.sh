# Descarga todos los datos horarios de NSRDB para CAISO, ERCOT, y CENACE

#set -e

for y in "2020" "2019" "2018" "2017" "2016" "2015" "2014" "2013" "2012" "2011" "2010" "2009" "2008" "2007" "2006" "2005" "2004" "2003" "2002" "2001" "2000" "1999" "1998"; do 

    if [ ! -f "/datos/rodr/recurso_solar/net_load/nsrdb_$y.nc" ]; then
        cd /home/rodr/buffalo/rodr/temp
        wget -c https://nrel-pds-nsrdb.s3.amazonaws.com/current/nsrdb_$y.h5

        python /home/rodr/Code/recurso_solar/code_3/h5_nc.py

        rm /home/rodr/buffalo/rodr/temp/nsrdb_$y.h5
        rm -rf /home/rodr/buffalo/trashbox/rodr
    fi
    
done