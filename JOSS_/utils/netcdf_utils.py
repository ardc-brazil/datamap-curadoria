from datetime import datetime
import xarray as xr
import numpy as np
import os
import disdrometer_utils as disd


def extract_variables(
    day_data,
    variables_info,
    netCDF_info
):
    print("Extracting variables from the data")
    
    #defining the dimensions and variables of the netCDF file:
    #    "time": "It is always a daily file, please, check the integration_time in variable_info.json",
    #    "drop_avg_class": "check the variable_info.json"
    dimensions={}
    variables={}

    basetime = day_data.index[0].timestamp()
    timeoffset = (day_data.index - datetime(day_data.index[0].year,day_data.index[0].month,day_data.index[0].day,0,0,)).map(lambda x: x.total_seconds()).to_numpy()
    ref_time = timeoffset

    dimensions["time"] = ref_time
    dimensions["drop_avg_class"] = np.array(variables_info["drop_mean_diam"])

    #creating and filling the variables that already have values in the jason file "variables":
    for key in netCDF_info.keys():
        if 'variables' in key:
            for var in netCDF_info[key].keys():
                #check if the variable is optional (False means that the variable is not mandatory):
                if netCDF_info[key][var]['optional'] is True:
                    #checking if the variable has value in the data:
                    if netCDF_info[key][var]['value'] is not None:
                        #filling the variable with the data:
                        variables[var] = netCDF_info[key][var]['value']

    #creating and filling variables manually:
    variables["base_time"] = basetime
    variables["time_offset"] = np.array(timeoffset)
    variables["time"] = np.array(dimensions["time"])
    # for midnight time
    # variables["time"] = datetime(day_data.index[0].year,day_data.index[0].month,day_data.index[0].day,0,0,).timestamp()
    variables["drop_avg_class"] = np.array(dimensions["drop_avg_class"])
    variables["fall_velocity"] = np.array(variables_info["fall_vell"])
    variables["delta_diam"] = np.array(variables_info["delta_diam"])
    variables["num_drop"] = day_data[variables_info["drop_col"]].to_numpy()
    #total number of drops detected in num_drop:
    variables['number_detected_drops'] = np.array(variables["num_drop"].sum(axis=1))
    variables['diam_max'] = np.array(
        disd.get_d_max(
            variables["num_drop"],
            variables_info["drop_mean_diam"]
        )
    )
    variables['diam_min'] = np.array(
        disd.get_d_min(
            variables["num_drop"],
            variables_info["drop_mean_diam"]
        )
    )

    time_interval = day_data['Interval'].to_numpy()

    variables['num_drop_density'] = np.array(
        disd.get_n_d_rd80(
            variables["num_drop"],
            time_interval,
            variables_info["delta_diam"],
            variables_info["fall_vell"]
        )
    )
    variables['rain_rate'] = np.array(
        disd.get_ri_rd80(
            variables["num_drop"],
            time_interval,
            variables_info["drop_mean_diam"],
            variables_info["sensor_area"]
        )
    )
    variables['radar_reflectivity'] = np.array(
        disd.get_zdb(
            disd.get_z_rd80(
                variables["num_drop"],
                time_interval,
                variables_info["drop_mean_diam"],
                variables_info["fall_vell"],
                variables_info["sensor_area"]
            )
        )
    )
    variables['liq_water'] = np.array(
        disd.get_liq_water_rd80(
            variables["num_drop"],
            time_interval,
            variables_info["drop_mean_diam"],
            variables_info["fall_vell"],
            variables_info["sensor_area"]
        )
    )
    variables['energy_flux'] = np.array(
        disd.get_ef(
            disd.get_ek_rd80(
                variables["num_drop"],
                variables_info["drop_mean_diam"],
                variables_info["fall_vell"],
                variables_info["sensor_area"]
            ),
            time_interval
        )
    )
    variables['slope_parameter'] = np.array(
        disd.get_slope(
            variables["liq_water"], 
            disd.get_z_rd80(
                variables["num_drop"],
                time_interval,
                variables_info["drop_mean_diam"],
                variables_info["fall_vell"],
                variables_info["sensor_area"]
            )
        )
    )
    variables['distribution_intercept'] = np.array(
        disd.get_n_0(
            variables["liq_water"],
            disd.get_z_rd80(
                variables["num_drop"],
                time_interval,
                variables_info["drop_mean_diam"],
                variables_info["fall_vell"],
                variables_info["sensor_area"]
            ),
        )
    )

    # ##################### Quality control variables: #####################
    # (1) - qc_number_detected_particles: 0 = good data, 1 = bad data
    variables['qc_number_detected_particles'] = np.array(variables['number_detected_drops'])

    # Set values to 1 where condition 1 is True
    cond1 = (variables['number_detected_drops'] > 0) & (variables['number_detected_drops'] < variables_info["filter_ni"])
    variables['qc_number_detected_particles'][cond1] = 1.
    # Set values to 0 where condition 2 is True
    cond2 = (variables['number_detected_drops'] >= variables_info["filter_ni"])
    variables['qc_number_detected_particles'][cond2] = 0.
    # Set values to 0 where condition 3 is True
    cond3 = (variables['number_detected_drops'] == 0)
    variables['qc_number_detected_particles'][cond3] = 0.

    # (2) - QC for time_interval: if time insterval is longer than integration_time the data will be considered bad
    qc_time_interval = np.where(time_interval > variables_info["integration_time"], 1, 0)
    if np.max(qc_time_interval) == 1:
        print("WARNING: The time interval is longer than the integration time")
        print("The data will be considered bad")
    #variables['qc_time_interval'] = qc_time_interval
    
    # ##################### Checking if the variables are correct: #####################
    #checking if has a missing variables or wrong dimensions between the variables in the json file and the variables that were created manually:
    for key in netCDF_info.keys():
        if 'variables' in key:
            for var in netCDF_info[key].keys():
                if netCDF_info[key][var]['optional'] is True:
                    if var not in variables.keys():
                        print("EXIT: The variable", var, "is mandatory, but it was not found in the data")
                        print("Please, check your variables in the json file and in the code")
                        exit()
                    #checking if the variable has the same dimension as the one in the json file:
                    if netCDF_info[key][var]['dimensions'] is not None:
                        i=0
                        for dim in netCDF_info[key][var]['dimensions']:
                            if dim in dimensions.keys():
                                if len(dimensions[dim]) != variables[var].shape[i]:
                                    print("EXIT: The variable", var, "has a different dimension than the one in the json file")
                                    print("Please, check your variables in the json file and in the code")
                                    exit()
                            i+=1
                        

    return dimensions, variables

def generate_netCDF(
    cdf_filename,
    dimensions_nc,
    variables_nc,
    netCDF_info,
    path_output_data,
):

    print("Generating netCDF:", cdf_filename)

    # check if file already exists, if true delete
    if os.path.exists(path_output_data.joinpath(cdf_filename)):
        os.remove(path_output_data.joinpath(cdf_filename))
        print("File already exists, overwriting a new one...")

    # Create a new empty dataset with dimensions based on dimensions_nc
    ds = xr.Dataset(coords={dim: vec for dim, vec in dimensions_nc.items()})

    # Create the variables and fill them with values from variables_nc
    for key, value in netCDF_info.get('variables', {}).items():
        optional = value.get('optional', False)
        var_data = variables_nc.get(key)

        if var_data is None and optional:
            print("WARNING: The variable", key, "is optional, but it is empty - CHECK THE DATA")
            var_data = 0

        dimensions = value.get('dimensions', [])
        coords = {dim: dimensions_nc[dim] for dim in dimensions} if dimensions else None

        attrs = {attr: attr_value for attr, attr_value in value.items()
                 if attr not in ['dimensions', 'value', 'optional'] and attr_value is not None}
            
        ds[key] = xr.DataArray(
            data=var_data,
            coords=coords,
            dims=dimensions,
            attrs=attrs
        )

    # Set global attributes
    for attr, attr_value in netCDF_info.get('global attributes', {}).items():
        ds.attrs[attr] = attr_value['long_name']

    # Convert time-related attributes to datetime
    basetime = datetime.utcfromtimestamp(ds['base_time'].values.astype(netCDF_info['variables']['base_time']['datatype']))
    basetime_string = basetime.strftime('%Y-%m-%d %H:%M:%S 0:00')

    ds['base_time'].attrs['string'] = basetime_string
    ds['time_offset'].attrs['units'] = 'seconds since '+basetime_string
    ds['time'].attrs['units'] = 'seconds since '+basetime_string  #My midnight time is equal to the basetime, if not, use the line below:
    #ds['time'].attrs['units'] = 'seconds since '+datetime.utcfromtimestamp(basetime).strftime('%Y-%m-%d 00:00:00 0:00')

    # Convert: 2)  NaN values to missing values and 2) DATATYPE to the one in the json file
    for var in ds.variables:
        missing_value = ds[var].attrs.get('missing_value')
        if missing_value is not None:
            #print("The variable", var, "has", np.count_nonzero(np.isnan(ds[var].values)), "missing values")
            ds[var].values[np.isnan(ds[var].values)] = float(missing_value)
        if netCDF_info['variables'][var].get('datatype') is not None:
            ds[var] = ds[var].astype(netCDF_info['variables'][var]['datatype'])
            ds[var].encoding['_FillValue'] = None
            if missing_value is not None:
                missing_value = ds[var].dtype.type(missing_value)
                ds[var].attrs['missing_value'] = missing_value
        ds[var].attrs.pop('datatype', None)

    #write the output file in JOSS_CDF (netCDF file), unlimited the time dimension and delete the chunking by using the format 'NETCDF3_CLASSIC':
    ds.to_netcdf(path_output_data.joinpath(cdf_filename),unlimited_dims='time',format='NETCDF3_CLASSIC')

    print("netCDF created")

