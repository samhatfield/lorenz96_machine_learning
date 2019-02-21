import numpy as np
from netCDF4 import Dataset
from numerical_model.qg_constants import qg_constants as const


def setup_output(output_file, start_date):
    nx, ny = int(const.nx), int(const.ny)
    d1, d2 = float(const.d1), float(const.d2)

    # Define NetCDF dataset to store all output
    dataset = Dataset(output_file, "w", format="NETCDF4_CLASSIC")

    # Define dimensions
    dataset.createDimension("time", None)
    dataset.createDimension("i", nx)
    dataset.createDimension("j", ny)
    dataset.createDimension("lev", 2)

    # Define dimension variables
    timevar = dataset.createVariable("time", np.int32, ("time",))
    ivar    = dataset.createVariable("i",    np.int32, ("i",))
    jvar    = dataset.createVariable("j",    np.int32, ("j",))
    levvar  = dataset.createVariable("lev",  np.int32, ("lev"))

    # Set time units
    timevar.setncatts({"units": f"minutes since {start_date:%Y-%m-%dT%H:%M:%SZ}"})

    # Define multidimensional variables
    dataset.createVariable("pv",  np.float32, ("time", "lev", "j", "i"))
    dataset.createVariable("psi", np.float32, ("time", "lev", "j", "i"))
    dataset.createVariable("u",   np.float32, ("time", "lev", "j", "i"))
    dataset.createVariable("v",   np.float32, ("time", "lev", "j", "i"))

    # Assign values to non-unlimited dimensions
    ivar[:]   = np.array([i for i in range(nx)], dtype=np.int32)
    jvar[:]   = np.array([j for j in range(ny)], dtype=np.int32)
    levvar[:] = np.array([d1, d2])

    dataset.close()


def output(output_file, start_date, date, time_index, pv, 𝛙, u, v):
    # Append latest data along time dimension
    dataset = Dataset(output_file, "a", format="NETCDF4_CLASSIC")
    dataset["time"][time_index]      = (date - start_date).total_seconds()/60.0
    dataset["pv"][time_index,:,:,:]  = np.transpose(pv[:,:,:])
    dataset["psi"][time_index,:,:,:] = np.transpose(𝛙[:,:,:])
    dataset["u"][time_index,:,:,:]   = np.transpose(u[:,:,:])
    dataset["v"][time_index,:,:,:]   = np.transpose(v[:,:,:])
    dataset.close()
