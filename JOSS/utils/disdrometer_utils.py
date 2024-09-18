import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import math
import warnings
warnings.filterwarnings("ignore")

# FUNCTIONS TO READ THE FILES

def read_files_rd80(files, columns):
    joss_date_parser = lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S")

    # data is a list of dataframes containg the data from each file
    data = [
        pd.read_csv(
            file,
            sep="\s",
            header=None,
            names=columns,
            skiprows=[0],
            index_col=[0],
            parse_dates=[[0, 1]],
            date_parser=joss_date_parser,
            decimal=",",
            dtype={"RI": np.float64, "RA": np.float64, "RAT": np.float64},
            engine="python",
        )
        for file in files
    ]

    # all data receives the data from all files and sorteb by index (datestamp)
    all_data = pd.concat(data).sort_index()
    # Remove duplicate index (datestamp) and keep the first one
    all_data = all_data[~all_data.index.duplicated(keep="first")]
    
    return all_data


def get_day_data(all_data, export_date, variables_info):

    # last date of the data
    aux_datetime = all_data.index[-1] 

    # if export_date is None, the first date of the data is used
    if export_date == None:
        export_date = all_data.index[0]
    
    # start and end date of the day
    start_date = datetime(export_date.year, export_date.month, export_date.day, 0, 0)

    delta = pd.Timedelta(seconds=(86400 - variables_info["integration_time"]))
    end_date = datetime.combine(export_date.date(), datetime.min.time().replace(hour=delta.components.hours, minute=delta.components.minutes, second=delta.components.seconds))
    
    # index with all the dates from the day
    day_idx = pd.date_range(
        start=start_date,
        end=end_date,
        freq=str(variables_info["integration_time"]) + "S",
    )

    # reindex the dataframe with the day index and fill the missing values with NaN
    all_data = all_data.reindex(day_idx, fill_value=np.nan)

    # return dataframe with one day data, the next day to be exported and a boolean to break the loop
    return (
        export_date + timedelta(days=1),
        all_data.loc[start_date:end_date],
        start_date > aux_datetime,
    )

# FUNCTIONS TO CALCULATE THE FILTERS IN DATA

def get_filter_ni(data, drop_col, min_ni):

    ni = data[drop_col].sum(axis=1)
    invalid_indices = np.where(ni < min_ni)[0]
    if len(invalid_indices) > 0:
        data.iloc[invalid_indices] = np.nan 

    return data

# FUNCTIONS TO CALCULATE THE VARIABLES

def get_ri_rd80(drop_sizes,interval, drop_diam,sensor_area):

    # calculate the "constant" based on the interval (it can change!)
    c = (np.pi/6.) * (3.6/(10.**3.))
    inv_interval = 1 / (sensor_area * interval)

    # extract drop sizes and diameters as NumPy arrays: times x raindrop classes
    diameters = np.tile(np.array(drop_diam), drop_sizes.shape[0]).reshape(drop_sizes.shape[0],drop_sizes.shape[1])

    # perform the calculation using array operations
    rain_rate = c * inv_interval * np.sum(drop_sizes * np.power(diameters, 3), axis=1)

    return rain_rate


# def get_ra(ri_data, t):
#     return [rain_rate * t / 3600 for rain_rate in ri_data]


# def get_rat(ra_data):
#     return [sum(ra_data[0:i]) for i in range(len(ra_data))]


def get_liq_water_rd80(drop_sizes, interval, drop_diam, fall_vell, sensor_area):
    
    # calculate the "constant" based on the interval (it can change!)
    c = (np.pi/6.)
    inv_interval = 1 / (sensor_area * interval)

    # extract drop sizes and diameters as NumPy arrays: times x raindrop classes
    diameters = np.tile(np.array(drop_diam), drop_sizes.shape[0]).reshape(drop_sizes.shape[0],drop_sizes.shape[1])
    vel = np.tile(np.array(fall_vell), drop_sizes.shape[0]).reshape(drop_sizes.shape[0],drop_sizes.shape[1])

    # perform the calculation using array operations
    liq_water = c *  inv_interval * np.sum((drop_sizes/vel) * np.power(diameters, 3), axis=1)

    return liq_water/1000.

def get_z_rd80(drop_sizes, interval, drop_diam, fall_vell, sensor_area):

    inv_interval = 1 / (sensor_area * interval)

    # extract drop sizes and diameters as NumPy arrays: times (1 day=1440) x raindrop classes (RD80=20)
    diameters = np.tile(np.array(drop_diam), drop_sizes.shape[0]).reshape(drop_sizes.shape[0],drop_sizes.shape[1])
    vel = np.tile(np.array(fall_vell), drop_sizes.shape[0]).reshape(drop_sizes.shape[0],drop_sizes.shape[1])

    # perform the calculation using array operations
    z = inv_interval * np.sum((drop_sizes/vel) * np.power(diameters, 6), axis=1)

    return z  


def get_zdb(z_data):
    zdbz = np.full(z_data.shape, np.nan)
    zdbz[z_data > 0] = 10.0 * np.log10(z_data[z_data > 0])
    zdbz[z_data == 0] = -99.0
    return zdbz

def get_ek_rd80(drop_sizes, drop_diam, fall_vell, sensor_area):

    # calculate the "constant" based on the interval (it can change!)
    c = (np.pi/12.)*(1/sensor_area)*(1/10**6)

    # extract drop sizes and diameters as NumPy arrays: times x raindrop classes
    diameters = np.tile(np.array(drop_diam), drop_sizes.shape[0]).reshape(drop_sizes.shape[0],drop_sizes.shape[1])
    vel = np.tile(np.array(fall_vell), drop_sizes.shape[0]).reshape(drop_sizes.shape[0],drop_sizes.shape[1])

    # perform the calculation using array operations
    ek = c *  np.sum(drop_sizes * np.power(diameters, 3) * np.power(vel, 2), axis=1)

    return ek

# ek_data is the list produced by get_ek() function
def get_ef(ek_data, interval):
    ef=ek_data * (3600/interval)
    return ef

def get_n_0(liq_water_data, z_data):

    c = (1 / np.pi) * (np.power((math.factorial(6) / np.pi), 4 / 3))
    valid_indices = np.where((z_data > 0) & (~np.isnan(z_data)))
    n_0 = np.full(z_data.shape, np.nan)
    n_0[valid_indices] = c * np.power((liq_water_data[valid_indices] / z_data[valid_indices]), 4./3.)
    n_0[z_data == 0] = 0.0    

    return n_0


def get_slope(liq_water_data, z_data):

    c = math.factorial(6) / math.pi
    slope = np.full(z_data.shape, np.nan)
    valid_indices = np.where((z_data > 0) & (~np.isnan(z_data)))
    slope[valid_indices] = np.power(c * (liq_water_data[valid_indices] / z_data[valid_indices]), 1./3.)
    slope[z_data == 0] = 0.0

    return slope


def get_d_max(drop_sizes, drop_diam):

    D_max = [drop_diam[np.where(row > 0)[0][-1]] if np.sum(row) > 0 else 0 if np.sum(row) == 0 else np.nan for row in drop_sizes]
    
    return D_max
    

def get_d_min(drop_sizes, drop_diam):

    D_min = [drop_diam[np.where(row > 0)[0][0]] if np.sum(row) > 0 else 0 if np.sum(row) == 0 else np.nan for row in drop_sizes]
    
    return D_min


def get_n_d_rd80(drop_sizes,interval, delta_diam, fall_vell):

    # extract drop sizes and diameters as NumPy arrays: times x raindrop classes
    delta_diam = np.tile(np.array(delta_diam), drop_sizes.shape[0]).reshape(drop_sizes.shape[0],drop_sizes.shape[1])
    vel = np.tile(np.array(fall_vell), drop_sizes.shape[0]).reshape(drop_sizes.shape[0],drop_sizes.shape[1])
    
    n_d = drop_sizes / ((0.005 * interval[:, np.newaxis]) * (vel * delta_diam))

    return n_d
