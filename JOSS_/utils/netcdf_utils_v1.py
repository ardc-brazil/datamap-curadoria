from datetime import datetime
import xarray as xr
import pandas as pd
import numpy as np
import os
import disdrometer_utils as disd


def generate_netCDF(
    cdf_filename,
    day_data,
    variables_info,
    netCDF_info,
    path_output_data,
):

    print("Generating netCDF:", cdf_filename)

    # check if file already exists, if true delete
    if os.path.exists(path_output_data.joinpath(cdf_filename)):
        os.remove(path_output_data.joinpath(cdf_filename))
        print("File already exists, overwriting a new one...")

    #------------------------ Create NetCDF from json file ------------------------#
    # Define dimentions:
    #MANUAL
    #    "time": "It is always a daily file, please, check the integration_time in variable_info.json",
    #    "drop_avg_class": "check the variable_info.json"
    basetime = day_data.index[0].timestamp()
    timeoffset = (day_data.index - datetime(day_data.index[0].year,day_data.index[0].month,day_data.index[0].day,0,0,)).map(lambda x: x.total_seconds()).to_numpy()
    ref_time = timeoffset

    dimensions_nc={}
    dimensions_nc['time'] = ref_time
    dimensions_nc['drop_avg_class'] = variables_info["drop_mean_diam"]
    
    # Create a new empty dataset with dimensions based on for in dimensions_nc
    ds = xr.Dataset(coords={dim: vec for dim, vec in dimensions_nc.items()})

    # create the variables in the dataset
    for key in netCDF_info.keys():
        if 'variables' in key:
            for var in netCDF_info[key].keys():
                #check if the variable is optional (False means that the variable is not mandatory):
                if netCDF_info[key][var]['optional'] == 'True':
                    #fill datavalue for variables that already have a value in the json file if not fill with 0 to be able to create the dataset:
                    datavalue = 0 if netCDF_info[key][var]['value'] == 'None' else netCDF_info[key][var]['value']
                    #If to check the variables is also a dimensions and fill the datavalue with the dimensions_nc value:
                    if var in dimensions_nc.keys():
                        datavalue = dimensions_nc[var]
                    # define the dimensions and coords of the variables:
                    if netCDF_info[key][var]['dimensions'] != 'empty':
                        coords = {dimen: dimensions_nc[dimen] for dimen in netCDF_info[key][var]['dimensions']}
                        dims = tuple(dimen for dimen in netCDF_info[key][var]['dimensions'])
                    else:
                        coords = None
                        dims = None
                    #fill the dataset with the variables:
                    ds[var] = xr.DataArray(
                    data=datavalue,
                    coords=coords,
                    dims=dims,
                    attrs={attr: netCDF_info[key][var][attr] for attr in netCDF_info[key][var].keys() if attr != 'dimensions' and attr != 'value' and netCDF_info[key][var][attr] != 'empty' and attr != 'optional'}
                    )
                    #change the datatype of the variables that values are not None or are also dimensions_nc:
                    if netCDF_info[key][var]['datatype'] != 'None' or var in dimensions_nc.keys():
                        ds[var] = ds[var].astype(ds[var].datatype)
                        #delete FillValue:
                        ds[var].encoding['_FillValue'] = None
        elif 'global attributes' in key:
            for attr in netCDF_info[key].keys():
                ds.attrs[attr] = netCDF_info[key][attr]['long_name']

    #------------------------ fill netCDF with data ------------------------#
    # fill base time
    ds['base_time'].values = basetime
    ds['base_time'].values = ds['base_time'].values.astype(ds['base_time'].datatype)
    #change the attribute "string" to datetime based on the gregoriam calendar and basetime value
    #only change 0:00 (the last 3 numbers are the time zone) if you are using local time
    ds['base_time'].attrs['string'] = datetime.utcfromtimestamp(basetime).strftime('%Y-%m-%d %H:%M:%S 0:00')

    # time offset:
    ds['time_offset'].values = (
        timeoffset
        .astype(ds['time_offset'].datatype)
    )
    ds['time_offset'].attrs['units'] = datetime.utcfromtimestamp(basetime).strftime('seconds since %Y-%m-%d %H:%M:%S 0:00')

    #define the midnight time based on the day_data index:
    #midnight_time = datetime(day_data.index[0].year,day_data.index[0].month,day_data.index[0].day,0,0,).timestamp()
    #ds['time'].attrs['units'] = datetime.utcfromtimestamp(midnight_time).strftime('seconds since %Y-%m-%d %H:%M:%S 0:00')

    #based on the xr the time is the time_offset plus the midnight time (basetime in my case) that is write directly in the atrribute "units":
    #My midnight time is equal to the basetime
    ds['time'].attrs['units'] = datetime.utcfromtimestamp(basetime).strftime('seconds since %Y-%m-%d %H:%M:%S 0:00')

    #fill fall velocity:
    ds['fall_velocity'].values = variables_info["fall_vell"]
    ds['fall_velocity'].values = ds['fall_velocity'].values.astype(ds['fall_velocity'].datatype)

    #fill delta diameter:
    ds['delta_diam'].values = variables_info["delta_diam"]
    ds['delta_diam'].values = ds['delta_diam'].values.astype(ds['delta_diam'].datatype)

    # Applies the quality control using filters
    # if variables_info["filter_ni"] != "None":
    #     print("FILTERING DATA BASED ON THE MINUMUM NUMBER OF DROPS")
    #     day_data = disd.get_filter_ni(day_data, variables_info["drop_col"], variables_info["filter_ni"])

    #fill number of drops
    ds['num_drop'].values = day_data[variables_info["drop_col"]].to_numpy().astype(ds['num_drop'].datatype)

    #Total number of drops in the sample:
    ds['number_detected_drops'].values = ds['num_drop'].values.sum(axis=1)
    ds['number_detected_drops'].values = ds['number_detected_drops'].values.astype(ds['number_detected_drops'].datatype)

    #fill qc_number_detected_particles with 1 when ds['number_detected_drops'] < variables_info["filter_ni"] or is a NaN and 0 when ds['number_detected_drops'] < variables_info["filter_ni"]:
    ds['qc_number_detected_particles'].values = np.where(
        (ds['number_detected_drops'].values < variables_info["filter_ni"]) |
        np.isnan(ds['number_detected_drops'].values),
        1,
        np.where(
            ds['number_detected_drops'].values >= variables_info["filter_ni"],
            0,
            np.nan
        )
    ).astype(ds['qc_number_detected_particles'].datatype)

    #fill max diameter:
    ds['diam_max'].values = np.array(
        disd.get_d_max(
            day_data[variables_info["drop_col"]],
            variables_info["drop_col"],
            variables_info["drop_mean_diam"]
        )
    ).astype(ds['diam_max'].datatype)

    #fill min diameter:
    ds['diam_min'].values = np.array(
        disd.get_d_min(
            day_data[variables_info["drop_col"]],
            variables_info["drop_col"],
            variables_info["drop_mean_diam"]
        )
    ).astype(ds['diam_min'].datatype)

    #fill num drop density:
    ds['num_drop_density'].values = np.array(
        disd.get_n_d_rd80(
            day_data[['Interval',*variables_info["drop_col"]]],
            variables_info["drop_col"],
            variables_info["delta_diam"],
            variables_info["fall_vell"]
        )
    ).astype(ds['num_drop_density'].datatype)

    #fill rain rate:
    ds['rain_rate'].values = np.array(
        disd.get_ri_rd80(
            day_data[['Interval',*variables_info["drop_col"]]],
            variables_info["drop_col"],
            variables_info["drop_mean_diam"]
        )
    ).astype(ds['rain_rate'].datatype)

    #fill radar reflectivity:
    ds['radar_reflectivity'].values = np.array(
        disd.get_zdb(
            disd.get_z_rd80(
                day_data[['Interval',*variables_info["drop_col"]]],
                variables_info["drop_col"],
                variables_info["drop_mean_diam"],
                variables_info["fall_vell"]
            )
        )
    ).astype(ds['radar_reflectivity'].datatype)

    #fill liquid water content:
    ds['liq_water'].values = np.array(
        disd.get_liq_water_rd80(
                day_data[['Interval',*variables_info["drop_col"]]],
                variables_info["drop_col"],
                variables_info["drop_mean_diam"],
                variables_info["fall_vell"]
        )
    ).astype(ds['liq_water'].datatype)

    #fill energy flux:
    ds['energy_flux'].values = np.array(
        disd.get_ef(
            disd.get_ek_rd80(
                day_data[['Interval',*variables_info["drop_col"]]],
                variables_info["drop_col"],
                variables_info["drop_mean_diam"],
                variables_info["fall_vell"]
            ),
            day_data['Interval'],
        )
    ).astype(ds['energy_flux'].datatype)

    #fill slope of the drop size distribution:
    ds['slope_parameter'].values = np.array(
        disd.get_slope(
            disd.get_liq_water_rd80(
                day_data[['Interval',*variables_info["drop_col"]]],
                variables_info["drop_col"],
                variables_info["drop_mean_diam"],
                variables_info["fall_vell"]
            ),
            disd.get_z_rd80(
                day_data[['Interval',*variables_info["drop_col"]]],
                variables_info["drop_col"],
                variables_info["drop_mean_diam"],
                variables_info["fall_vell"]
            ),
        )
    ).astype(ds['slope_parameter'].datatype)

    #fill distribution intercept parameter:
    ds['distribution_intercept'].values = np.array(
        disd.get_n_0(
            disd.get_liq_water_rd80(
                day_data[['Interval',*variables_info["drop_col"]]],
                variables_info["drop_col"],
                variables_info["drop_mean_diam"],
                variables_info["fall_vell"]
            ),
            disd.get_z_rd80(
                day_data[['Interval',*variables_info["drop_col"]]],
                variables_info["drop_col"],
                variables_info["drop_mean_diam"],
                variables_info["fall_vell"]
            ),
        )
    ).astype(ds['distribution_intercept'].datatype)

    #convert all NaN data in all variables to missing value based on the variable_netCDF_info[var]["missing_value"]]:
    for var in ds.variables:
        #if for variables with missing values attribute:
        if 'missing_value' in ds[var].attrs:
            ds[var].values[np.isnan(ds[var].values)] = ds[var].attrs['missing_value']
            #print("Number of missing values in "+var+" is: "+str(np.count_nonzero(ds[var].values == ds[var].attrs['missing_value'])))


    #remove the attribute 'datatype' from the variables:
    for var in ds.variables:
        if 'datatype' in ds[var].attrs:
            ds[var].attrs.pop('datatype')

    #write the output file in JOSS_CDF (netCDF file), unlimited the time dimension and delete the chunking by using the format 'NETCDF3_CLASSIC':
    ds.to_netcdf(path_output_data.joinpath(cdf_filename),unlimited_dims='time',format='NETCDF3_CLASSIC')

    print("netCDF created")

