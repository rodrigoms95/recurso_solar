import h5py
import pandas as pd

dir_n = "/home/rodr/buffalo/rodr/Datos/NSRDB/"
dir_p = "/datos/rodr/temp/recurso_solar/duck_curve/"
file_p = f"{dir_p}conus_points.csv"
file_d = f"{dir_n}nsrdb_conus_irradiance_2022.h5"
file_r = f"{dir_p}nsrdb_conus_irradiance_2022_crop.h5"

print("Starting partial copy of dataset")
print()

print("Loading points list")
print()
points = pd.read_csv(file_p, index_col = 0).sort_index().index

with h5py.File(file_d, "r") as f_d:
    with h5py.File(file_r, "w") as f_r:
        print("Copying attributes")
        for b in f_d.attrs:
            print(f"Copying attribute: {b}")
            f_r.attrs[b] = f_d.attrs[b]
        print()
        print("Copying and slicing datasets")
        for a in ["meta", "time_index", "dhi", "ghi"]:
            print(f"Copying and slicing dataset: {a}")
            if a == "meta":
                #f_d.copy(a, f_r)
                f_r.create_dataset(a, data = f_d[a][points],
                    shape = f_d[a][points].shape,
                    dtype = f_d[a].dtype, chunks = f_d[a].chunks,
                    maxshape = f_d[a].maxshape, fillvalue = f_d[a].fillvalue)
            elif a == "time_index":
                f_d.copy(a, f_r)
                #f_r.create_dataset(a, data = f_d[a][::12],
                #    shape = f_d[a][::12].shape,
                #    dtype = f_d[a].dtype, chunks = f_d[a].chunks,
                #    maxshape = f_d[a].maxshape, fillvalue = f_d[a].fillvalue)
            else:
                f_r.create_dataset(a, data = f_d[a][:, points],#[::12, points],
                    shape = f_d[a][:, points].shape,#[::12, points].shape,
                    dtype = f_d[a].dtype, chunks = f_d[a].chunks,
                    maxshape = f_d[a].maxshape, fillvalue = f_d[a].fillvalue)
            for b in f_d[a].attrs: f_r[a].attrs[b] = f_d[a].attrs[b]