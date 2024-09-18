import xarray as xr
import json
import act
import numpy as np
import pandas as pd


# Read the JSON file
inpupath='/Users/alancalheiros/data/data_instruments_codes/disdrometers/INPE-data-processing-master/JOSS/input/JOSS/support/'
json_file = inpupath+'netCDF_info_ARM.json'
with open(json_file) as f:
    data = json.load(f)

#find the dimensions and save in an dictionary called dimensions_nc
dimensions_nc={}
for key in data.keys():
    if 'dimensions' in key:
        for dim in data[key].keys():
            dimensions_nc[dim] = data[key][dim]['value'] 

# Create a new empty dataset with dimensions based on for in dimensions_nc
ds = xr.Dataset(coords={dim: np.arange(int(size)) for dim, size in dimensions_nc.items()})

# create the variables in the dataset
for key in data.keys():
    if 'variables' in key:
        for var in data[key].keys():
            if data[key][var]['optional'] == 'True':
                datavalue = 0 if data[key][var]['value'] == 'None' else float(data[key][var]['value'])
                # if if dimensions are different of "empty":
                if data[key][var]['dimensions'] != 'empty':
                    coords = {dimen: np.arange(int(dimensions_nc[dimen])) for dimen in data[key][var]['dimensions']}
                    dims = tuple(dimen for dimen in data[key][var]['dimensions'])
                else:
                    coords = None
                    dims = None
                ds[var] = xr.DataArray(
                data=datavalue,
                coords=coords,
                dims=dims,
                attrs={attr: data[key][var][attr] for attr in data[key][var].keys() if attr != 'dimensions' and attr != 'datatype' and attr != 'value' and data[key][var][attr] != 'empty' and attr != 'optional'}
                )
                # change the datatype of the variable based on the datatype informed in the JSON file
                # if data[key][var]['datatype'] == 'float':
                #     ds[var] = ds[var].astype(np.float32)
                # elif data[key][var]['datatype'] == 'integer':
                #     ds[var] = ds[var].astype(np.int32)
                # elif data[key][var]['datatype'] == 'string':
                #     ds[var] = ds[var].astype(str)
                ds[var].encoding['_FillValue'] = None
    elif 'global attributes' in key:
        for attr in data[key].keys():
            ds.attrs[attr] = data[key][attr]['long_name']

#print(ds['alt'].values)
#ds['base_time'].values = rainrate_data
#ds['alt']=ds['alt'].astype(np.float32)
#ds['alt'].encoding['_FillValue'] = None
# Salva o dataset em um arquivo netCDF
pathout='/Users/alancalheiros/data/data_instruments_codes/disdrometers/INPE-data-processing-master/JOSS/output/JOSS/test/'
ds.to_netcdf(pathout+'netCDF_from_json.nc')

# #-------------------------------------------------------
# rainrate_data = np.random.uniform(low=0, high=150, size=(1440,))
# rainrate_data = rainrate_data.astype(np.float32)
# # Set the start time as the first minute of July 1, 2020
# start_time = pd.Timestamp('2020-07-01 00:00:00', tz='UTC')
# # Create an array of time values as minutes in Julian day
# time_values = (pd.date_range(start_time, periods=1440, freq='T') -
#                pd.Timestamp('2020-01-01', tz='UTC')).total_seconds() / 60.0



# # Create a new empty dataset with dimensions 'time' and 'dropsnumber'
# #ds = xr.Dataset(coords={'time': np.arange(1440), 'dropsnumber': np.arange(20)})
# ds = xr.Dataset(coords={'time': ('time', np.arange(1440)), 'dropsnumber': np.arange(20)})
# ds.time.attrs['units'] = 'minutes since 2020-07-01 00:00:00'
# ds.time.encoding.update({'unlimited': True, 'current_size': len(time_values)})
# ds['time'].attrs['comment'] = 'This is the time dimension'


# # Add a new variable with dimensions 'time' and 'dropsnumber'
# ds['rainrate'] = xr.DataArray(
#     data=None,
#     coords={'time': time_values, 'dropsnumber': np.arange(20)},
#     dims=('time', 'dropsnumber'),
#     attrs={
#         'long_name': 'Rain Rate',
#         'units': 'mm/hr'
#     }
# )

# ds['rainrate'].values = np.random.uniform(low=0, high=150, size=(1440, 20))

# # Create a new variable called 'time'
# ds['time'] = xr.DataArray(
#     data=time_values,
#     coords={'time': time_values},
#     dims=('time',),
#     attrs={
#         'long_name': 'Time',
#         'units': 'minutes since 2020-01-01 00:00:00 UTC'
#     }
# )

# ds['time'].attrs['comment'] = 'This is the time dimension'

# # Save the dataset to a NetCDF file
# ds.to_netcdf(pathout+'rainrate.nc')

