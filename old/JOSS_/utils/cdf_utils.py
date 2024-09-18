import xarray as xr
import pandas as pd
import numpy as np
import os
from netCDF4 import Dataset
import disdrometer_utils as disd


def generate_netCDF(
    cdf_filename,
    day_data,
    columns,
    variables_info,
    netCDF_info,
    path_output_data,
):

    print("Generating netCDF:", cdf_filename)

    # check if file already exists, if true delete
    if os.path.exists(path_output_data.joinpath(cdf_filename)):
        os.remove(path_output_data.joinpath(cdf_filename))
        print("File already exists, overwriting a new one...")

    JOSS_CDF = Dataset(path_output_data.joinpath(cdf_filename), "w", format="NETCDF4")

    #------------------------ Create NetCDF from json file ------------------------#
    #find the dimensions and save in an dictionary called dimensions_nc
    dimensions_nc={}
    for key in netCDF_info.keys():
        if 'dimensions' in key:
            for dim in netCDF_info[key].keys():
                dimensions_nc[dim] = netCDF_info[key][dim]['value'] 

    # Create a new empty dataset with dimensions based on for in dimensions_nc
    ds = xr.Dataset(coords={dim: np.arange(int(size)) for dim, size in dimensions_nc.items()})

    # create the variables in the dataset
    for key in netCDF_info.keys():
        if 'variables' in key:
            for var in netCDF_info[key].keys():
                if netCDF_info[key][var]['optional'] == 'True':
                    datavalue = 0 if netCDF_info[key][var]['value'] == 'None' else float(netCDF_info[key][var]['value'])
                    # if if dimensions are different of "empty":
                    if netCDF_info[key][var]['dimensions'] != 'empty':
                        coords = {dimen: np.arange(int(dimensions_nc[dimen])) for dimen in netCDF_info[key][var]['dimensions']}
                        dims = tuple(dimen for dimen in netCDF_info[key][var]['dimensions'])
                    else:
                        coords = None
                        dims = None
                    ds[var] = xr.DataArray(
                    data=datavalue,
                    coords=coords,
                    dims=dims,
                    attrs={attr: netCDF_info[key][var][attr] for attr in netCDF_info[key][var].keys() if attr != 'dimensions' and attr != 'datatype' and attr != 'value' and netCDF_info[key][var][attr] != 'empty' and attr != 'optional'}
                    )
                    ds[var].encoding['_FillValue'] = None
        elif 'global attributes' in key:
            for attr in netCDF_info[key].keys():
                ds.attrs[attr] = netCDF_info[key][attr]['long_name']

    #------------------------ fill netCDF with data ------------------------#
    #fill rain rate:
    ds['rain_rate'].values = np.array(
        disd.get_ri_rd80(
            day_data[['Interval',*variables_info["drop_size"]]],
            variables_info["drop_size"],
            variables_info["drop_class"]
        )
    ).astype("float64")

    #fill number of drops (ALAN: verificar como remover columns[4:24])
    ds['number_of_drops'].values = day_data[columns[4:24]].to_numpy().astype("float64")


    print("netCDF created")

    JOSS_CDF.close()

