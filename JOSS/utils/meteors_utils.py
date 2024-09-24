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
        "id": float('nan'),
        "value": latitude_value,
        "dimensions": ("time"),
        "missing_value": float('nan'),
        "valid_min": float('nan'),
        "valid_max": float('nan'),
        "ancillary_variables": float('nan')
    }    
    dataset['lat'].attrs.update(lat_metadata)

def create_lon_var_in_dataset(dataset):
    longitude_value = dataset['longitude'].values.item()       
    dataset['lon'] = ((), longitude_value)        
    lon_metadata = {
        "short_name": "Longitude",
        "long_name": "East Longitude",
        "units": "degree_E",
        "datatype": "float32",
        "id": float('nan'),
        "value": longitude_value,
        "dimensions": ("time"),
        "missing_value": float('nan'),
        "valid_min": float('nan'),
        "valid_max": float('nan'),
        "ancillary_variables": float('nan')
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
    "short_name": float('nan'),
    "long_name": "Time bounds",
    "datatype": "float64",
    "id": float('nan'),  
    "value": time_bounds,
    "dimensions": ("time","bound"),
    "missing_value": float('nan'),
    "valid_min": float('nan'),
    "valid_max": float('nan'),
    "coordinates": "time",
    "ancillary_variables": float('nan')
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
        "id": float('nan'),
        "value": base_time_seconds,
        "dimensions": (),
        "missing_value": float('nan'),
        "valid_min": float('nan'),
        "valid_max": float('nan'),
        "ancillary_variables": "time_offset"
    }

    num_days = (dataset['time'].size)  # Número de dias, baseado na dimensão do tempo
    time_offset = np.arange(num_days) * 86400  # 86400 seconds in a day
    time_offset_metadata = {
        "short_name": "Time offset",
        "long_name": "Time offset from base_time",
        "units": f"seconds since {start_date.strftime('%Y-%m-%d %H:%M:%S')} 0:00",
        "datatype": "float64",
        "id": float('nan'),
        "value": float('nan'),
        "dimensions": ("time"),
        "missing_value": float('nan'),
        "valid_min": float('nan'),
        "valid_max": float('nan'),
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
        print(var.dims)
        return {
            "short_name": var.attrs.get("short_name", float('nan')),
            "standard_name": var.attrs.get("standard_name", float('nan')),
            "long_name": var.attrs.get("long_name", float('nan')),
            "units": "days since 2000-01-01" if var.name == "time_bounds" else var.attrs.get("units", float('nan')),
            "datatype": str(var.dtype),
            "id": float('nan'),  
            "value": float('nan'),  
            "missing_value": var.attrs.get("missing_value", float('nan')),
            "valid_min": var.min().item() if var.min().notnull() else float('nan'),
            "valid_max": var.max().item() if var.max().notnull() else float('nan'), 
            "ancillary_variables": var.attrs.get("ancillary_variables", float('nan')),
            "dimensions": var.dims  
        }

def create_and_update_metadata_in_json(dataset, base_json_path, final_json_path):
    with open(base_json_path, "r") as json_file:
        metadados_base = json.load(json_file)
    
    metadados_dimensoes = {dim: extract_dims_for_metadata(dataset,dim) for dim in dataset.dims}
    
    metadados_variaveis = {var_name: extract_vars_for_metadata(dataset[var_name]) for var_name in dataset.data_vars}

    #Update base JSON with new dimensions and variables
    metadados_base["dimensions"] = metadados_dimensoes
    
    if "variables" not in metadados_base:
        metadados_base["variables"] = metadados_variaveis
    else:
        metadados_base["variables"].update(metadados_variaveis)

    with open(final_json_path, "w") as f:
        json.dump(metadados_base, f, indent=4)

    # print(json.dumps(metadados_base, indent=4))

def create_and_update_metadata_in_dataset(dataset, json_path, output_path):
   with open(json_path, 'r') as f:
    metadados = json.load(f)

    if 'global_attributes' in metadados:
        for attr_name, attr_value in metadados['global_attributes'].items():
            dataset.attrs[attr_name] = attr_value['long_name']
        

    for var_name, var_metadata in metadados['variables'].items():
        if (var_name in dataset.data_vars) and (var_name != "time_bounds"):
            for key, value in var_metadata.items():
                if key == 'missing_value':
                    dataset[var_name].attrs['missing_value'] = float('nan')  # Atualiza valor ausente
                else:
                    dataset[var_name].attrs[key] = value
                    
                  
    for dim_name, dim_metadata in metadados['dimensions'].items():
        if dim_name in dataset.dims:
            for key, value in dim_metadata.items():
                dataset[dim_name].attrs[key] = value


    if 'time' in dataset.dims:
        time_dim = dataset['time']
        time_length = len(time_dim)
        print(1)
        if time_length > 1:
            print(2)
            # Se houver mais de uma data na dimensão time, usar o intervalo (início - fim)
            start_date = pd.to_datetime(time_dim.values[0]).strftime('%Y%m%d')
            print(start_date)
            end_date = pd.to_datetime(time_dim.values[-1]).strftime('%Y%m%d')
            print(4)
            nome_arquivo = f'{output_path}/meteors_metadata_timeseries_{start_date}_{end_date}.nc'
            # print(f"{nome_arquivo}")

        else:
            # Se houver apenas uma data, usar essa data
            single_date = pd.to_datetime(time_dim.values[0]).strftime('%Y%m%d')
            nome_arquivo = f'{output_path}/meteors_metadata_0_05deg_{single_date}.nc'
    print(dataset)
    try:
        dataset.to_netcdf(nome_arquivo)
        print(f"Arquivo salvo como {nome_arquivo}")
    except Exception as e:
        print(f"Ocorreu um erro: {e}. O arquivo {nome_arquivo} não foi salvo.")