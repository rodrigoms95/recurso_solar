internal="temp"
cdo seltimestep,1 $internal/NSRDB_4km/NSRDB_4km.nc $internal/NSRDB_2km_interp/NSRDB_4km_0.nc
cdo seltimestep,1 $internal/NSRDB_2km/NSRDB_2km.nc $internal/NSRDB_2km_interp/NSRDB_2km_0.nc
cdo -addc,0.001 -aexpr,"Temperature=Temperature+273.15" -delname,UVHI -selyear,2019/2022 $internal/NSRDB_4km/NSRDB_4km.nc $internal/NSRDB_2km_interp/NSRDB_4km_2019_2022_K.nc
cdo -addc,0.001 -aexpr,"Temperature=Temperature+273.15" -selindexbox,10,-11,11,-12 $internal/NSRDB_2km/NSRDB_2km.nc $internal/NSRDB_2km_interp/NSRDB_2km_K.nc
cdo div NSRDB_2km_interp_K.nc NSRDB_2km_K.nc
python code/interp_NSRDB.py 0 $internal
python code/interp_NSRDB.py "2019_2022_K" $internal
cdo div $internal/NSRDB_2km_interp/NSRDB_2km_K.nc $internal/NSRDB_2km_interp/NSRDB_2km_2019_2022_interp_K.nc $internal/NSRDB_2km_interp/f_int_time.nc