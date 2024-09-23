import netCDF4
import xarray as xr
import json
import datetime
import numpy as np
import pandas as pd


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

def create_lat_var_in_dataset(dataset):
    latitude_value = dataset['latitude'].values.item()       
    dataset['lat'] = ((), latitude_value)        
    lat_metadata = {
        "short_name": "Latitude",
        "long_name": "North Latitude",
        "units": "degree_N",
        "datatype": "float32",
        "id": float('nan'),
        "optional": True,
        "value": latitude_value,
        "dimensions": (),
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
        "optional": True,
        "value": longitude_value,
        "dimensions": (),
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
    "units": "days since 2000-01-01",
    "datatype": "float64",
    "id": float('nan'),  
    "optional": False,
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
        "optional": True,
        "value": base_time_seconds,
        "dimensions": float('nan'),
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
        "optional": True,
        "value": float('nan'),
        "dimensions": ["time"],
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
        coordenadas = list(var.coords)
        return {
            "short_name": var.attrs.get("short_name", float('nan')),
            "standard_name": var.attrs.get("standard_name", float('nan')),
            "long_name": var.attrs.get("long_name", float('nan')),
            "units": "days since 2000-01-01" if var == "time_bounds" else var.attrs.get("units", float('nan')),
            "datatype": str(var.dtype),
            "id": float('nan'),  
            "optional": float('nan'),  
            "value": float('nan'),  
            "missing_value": var.attrs.get("missing_value", float('nan')),
            "valid_min": var.min().item() if var.min().notnull() else float('nan'),
            "valid_max": var.max().item() if var.max().notnull() else float('nan'),
            "coordinates": coordenadas,  
            "ancillary_variables": var.attrs.get("ancillary_variables", float('nan')),
            "dimensions": var.dims  
        }

def create_and_update_metadata_in_json(dataset, json_path):
    with open(json_path, "r") as json_file:
        metadados_base = json.load(json_file)

    metadados_dimensoes = {dim: extract_dims_for_metadata(dataset,dim) for dim in dataset.dims}
    metadados_variaveis = {var_name: extract_vars_for_metadata(dataset[var_name]) for var_name in dataset.data_vars}

    #Update base JSON with new dimensions and variables
    metadados_base["dimensions"] = metadados_dimensoes
    if "variables" not in metadados_base:
        metadados_base["variables"] = metadados_variaveis
    else:
        metadados_base["variables"].update(metadados_variaveis)

    
    with open("JOSS/input/support/metadata_base_final.json", "w") as f:
        json.dump(metadados_base, f, indent=4)

    print(json.dumps(metadados_base, indent=4))

def create_and_update_metadata_in_dataset(dataset, json_path):
   with open('/content/netcdf_meteors_info_atualizado.json', 'r') as f:
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

    try:
        dataset.to_netcdf('JOSS/output/meteors_output/teste.nc')
    except Exception as e:
        print(f"Ocorreu um erro: {e}, O netcdf não foi salvo")