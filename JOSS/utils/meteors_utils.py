import netCDF4
import xarray as xr
import json
import datetime
import numpy as np
import pandas as pd
import os


# def read_files_meteors(netcdf_files, columns):
#     # data is a list of dataframes containg the data from each file
#     data = [
#         xr.open_dataset(file)
#         for file in netcdf_files
#     ]

#     # all data receives the data from all files and sorteb by index (datestamp)
#     all_data = xr.concat(data, dim="time")
    
#     return all_data

# Functions to create required variables and metadata in dataset

def get_files_from_folder(folder_path):
    files_list = []
    for file in os.listdir(folder_path):
        if file.endswith(".nc"):
            files_list.append(os.path.join(folder_path, file))
    return files_list

def create_lat_var_in_dataset(dataset):
    latitude_value = dataset['latitude'].values.item()       
    dataset['lat'] = ((), latitude_value)        
    lat_metadata = {
        "short_name": "Latitude",
        "long_name": "North Latitude",
        "units": "degree_N",
        "datatype": "float32",
        "id": -9999,
        "value": latitude_value,
        "dimensions": ("time"),
        "missing_value": -9999,
        "valid_min": -9999,
        "valid_max": -9999,
        "ancillary_variables": -9999
    }    
    dataset['lat'].attrs.update(lat_metadata)
    
def create_time_var_in_dataset(dataset):
    time_values = dataset['time'].values
    time_metadata = {
        "short_name": "Time",
        "long_name": "Time",
        "units": "days since 2002-01-01",
        "datatype": "float64",
        "id": -9999,
        "value": -9999,
        "dimensions": ("time"),
        "missing_value": -9999,
        "valid_min": -9999,
        "valid_max": -9999,
        "ancillary_variables": "time_bounds"
    }
    dataset['time'] = (('time',), time_values)
    dataset['time'].attrs.update(time_metadata)

def create_lon_var_in_dataset(dataset):
    longitude_value = dataset['longitude'].values.item()       
    dataset['lon'] = ((), longitude_value)        
    lon_metadata = {
        "short_name": "Longitude",
        "long_name": "East Longitude",
        "units": "degree_E",
        "datatype": "float32",
        "id": -9999,
        "value": longitude_value,
        "dimensions": ("time"),
        "missing_value": -9999,
        "valid_min": -9999,
        "valid_max": -9999,
        "ancillary_variables": -9999
    }    
    dataset['lon'].attrs.update(lon_metadata)

def create_time_bounds_var_in_dataset(dataset):
    time = dataset['time']
    time_values = pd.to_datetime(time.values)

    # Calculando os limites de tempo (time_bounds). Aqui, estamos definindo time_bounds para cada dia
    # O limite inferior é a data do dia, e o limite superior é o dia seguinte
    time_bounds = np.array([
        [t, t + np.timedelta64(1, 'D')] for t in time_values
    ])

    time_bounds_metadata = {
    "short_name": -9999,
    "long_name": "Time bounds",
    "datatype": "float64",
    "id": -9999,  
    "dimensions": ("time","bound"),
    "missing_value": -9999,
    "valid_min": -9999,
    "valid_max": -9999,
    "coordinates": "time",
    "ancillary_variables": -9999
    }
    dataset['time_bounds'] = (('time', 'bound'), time_bounds)
    dataset['time_bounds'].attrs.update(time_bounds_metadata)

def create_times_vars_in_dataset(dataset):
    start_date = datetime.datetime.strptime(dataset['time'].values[0], '%Y-%m-%d') 
    epoch = datetime.datetime(1970, 1, 1)
    # The .total_seconds method is called on the timedelta object to get the difference in seconds
    base_time_seconds = int((start_date - epoch).total_seconds()) 
    base_time_metadata = {
        "short_name": start_date.strftime("%Y-%m-%d"),
        "long_name": "Base time in Epoch",
        "units": "seconds since 1970-1-1 0:00:00 0:00",
        "datatype": "int64",
        "id": -9999,
        "value": base_time_seconds,
        "dimensions": (),
        "missing_value": -9999,
        "valid_min": -9999,
        "valid_max": -9999,
        "ancillary_variables": "time_offset"
    }

    num_days = (dataset['time'].size)  # Número de dias, baseado na dimensão do tempo
    time_offset = np.arange(num_days) * 86400  # 86400 seconds in a day
    time_offset_metadata = {
        "short_name": "Time offset",
        "long_name": "Time offset from base_time",
        "units": f"seconds since {start_date.strftime('%Y-%m-%d %H:%M:%S')} 0:00",
        "datatype": "float64",
        "id": -9999,
        "value": -9999,
        "dimensions": ("time"),
        "missing_value": -9999,
        "valid_min": -9999,
        "valid_max": -9999,
        "ancillary_variables": "base_time"
    }

    dataset['base_time'] = ((), base_time_seconds)
    dataset['base_time'].attrs.update(base_time_metadata)
    dataset['time_offset'] = (('time',), time_offset)
    dataset['time_offset'].attrs.update(time_offset_metadata)

def extract_dims_for_metadata(dataset, dim):
    return {
        "length": len(dataset[dim])  
    }
def extract_vars_for_metadata(var):
    # Filter out -9999 values from the dataset
    var = var.where(var != -9999)
    return {
        "short_name": var.attrs.get("short_name", -9999),
        "standard_name": var.attrs.get("standard_name", -9999),
        "long_name": var.attrs.get("long_name", -9999),
        "units": "days since 2002-01-01" if var.name == "time_bounds" else var.attrs.get("units", -9999),
        "datatype": str(var.dtype),
        "id": -9999,  
        "value": -9999,  
        "missing_value": var.attrs.get("missing_value", -9999),
        "valid_min": var.min().item() if var.min().notnull() else -9999,
        "valid_max": var.max().item() if var.max().notnull() else -9999, 
        "ancillary_variables": var.attrs.get("ancillary_variables", -9999),
        "dimensions": var.dims  
    }

def create_and_update_metadata_in_json(dataset, base_json_path, final_json_path):
    with open(base_json_path, "r") as json_file:
        metadados_base = json.load(json_file)
    
    metadados_dimensoes = {dim: extract_dims_for_metadata(dataset, dim) for dim in dataset.dims}
    
    metadados_variaveis = {}
    for var_name in dataset.data_vars:
        var_metadata = extract_vars_for_metadata(dataset[var_name])
        base_metadata = metadados_base.get("variables", {}).get(var_name, {})
        
        # Update base metadata with valid values from netcdf if base metadata value is -9999
        for key, value in var_metadata.items():
            if base_metadata.get(key, -9999) == -9999 and value != -9999:
                base_metadata[key] = value
        
        metadados_variaveis[var_name] = base_metadata

    # Update base JSON with new dimensions and variables
    metadados_base["dimensions"] = metadados_dimensoes
    
    if "variables" not in metadados_base:
        metadados_base["variables"] = metadados_variaveis
    else:
        metadados_base["variables"].update(metadados_variaveis)

    with open(final_json_path, "w") as f:
        json.dump(metadados_base, f, indent=4)

def create_and_update_metadata_in_dataset(dataset, json_path, output_path):
   with open(json_path, 'r') as f:
    metadados = json.load(f)

    if 'global_attributes' in metadados:
        for attr_name, attr_value in metadados['global_attributes'].items():
            dataset.attrs[attr_name] = attr_value['value']
        

    for var_name, var_metadata in metadados['variables'].items():
        if (var_name in dataset.data_vars) and (var_name != "time_bounds"):
            for key, value in var_metadata.items():
                if key == 'missing_value':
                    dataset[var_name].attrs['missing_value'] = -9999  # Update missing value
                else:
                    dataset[var_name].attrs[key] = value
                    
                  
    for dim_name, dim_metadata in metadados['dimensions'].items():
        if dim_name in dataset.dims:
            for key, value in dim_metadata.items():
                dataset[dim_name].attrs[key] = value


    if 'time' in dataset.dims:
        time_dim = dataset['time']
        time_length = len(time_dim)
        if time_length > 1:
            # If there is more than one date in the time dimension, use the range (start - end)
            start_date = pd.to_datetime(time_dim.values[0]).strftime('%Y%m%d')
            end_date = pd.to_datetime(time_dim.values[-1]).strftime('%Y%m%d')
            file_name = f'meteors_metadata_timeseries_{start_date}_{end_date}.nc'
            path_name = f'{output_path}/{file_name}'

        else:
            # If there is only one date, use that date
            single_date = pd.to_datetime(time_dim.values[0]).strftime('%Y%m%d')
            file_name = f'meteors_metadata_0_05deg_{single_date}.nc'
            path_name = f'{output_path}/{file_name}'
            
            
    try:
        dataset.to_netcdf(path_name)
        print(f"File saved as {file_name}")
    except Exception as e:
        print(f"An error occurred: {str(e)}. The file {file_name} was not saved.")