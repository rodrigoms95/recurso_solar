df = pd.read_csv( name, index_col = "XTIME", parse_dates = True ).reset_index()

# Convertimos a Dataset.
df["XLAT" ] = float(lat)
df["XLONG"] = float(lon)
df["south_north"] = 0
df["west_east"  ] = 0
ds = df.set_index( ["XTIME", "south_north", "west_east"]
        ).astype(float).to_xarray()
ds["XLAT"] = ds["XLAT"].isel( { "XTIME": 0 } )
ds["XLONG"] = ds["XLONG"].isel( { "XTIME": 0 } )
ds["XTIME"] = ds["XTIME"].assign_attrs( standard_name = "time",
        axis = "T", #bounds = "XTIME_bnds"
        )
ds["XLAT"] = ds["XLAT"].assign_attrs(
    standard_name = "latitude", long_name = "latitude",
    units = "degree_north", _CoordinateAxisType= "Lat" )
ds["XLONG"] = ds["XLONG"].assign_attrs(
        standard_name = "longitude", long_name = "longitude",
        units = "degree_east", _CoordinateAxisType= "Lon" )
ds = ds.set_coords( ["XLAT", "XLONG"] )
ds.to_netcdf( f"temp/NSRDB_prep/NetCDF/{lat}_{lon}.nc" )