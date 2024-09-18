import pandas as pd
import numpy as np
from datetime import datetime
import os
from netCDF4 import Dataset
import disdrometer_utils as disd


def string2ascii_array(string):
    ascii_array = [np.int64(ord(char)) for char in string]
    ascii_array.extend([np.int64(0) for i in range(255 - len(ascii_array))])
    return np.array(ascii_array)


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

    DATA_CDF = Dataset(path_output_data.joinpath(cdf_filename), "w", format="NETCDF4")

    # ######################## DIMENSIONS ##########################

    drop_class = DATA_CDF.createDimension(
        netCDF_info["dimensions"]["drop_class"]["symbol"], variables_info["Number of bins"]
    )

    time = DATA_CDF.createDimension(
        netCDF_info["dimensions"]["time"]["symbol"], day_data.shape[0]
    )

    str_dim = DATA_CDF.createDimension("str_dim", 255)

    # ######################## GLOBAL VARIABLES ###########################

    # variable: description
    description = DATA_CDF.createVariable(
        netCDF_info["global"]["description"]["name"], "u8", ("str_dim",)
    )
    description[:] = string2ascii_array(netCDF_info["global"]["description"]["value"])

    description.shortname = netCDF_info["global"]["description"]["shortname"]
    description.description = netCDF_info["global"]["description"]["description"]
    description.unit = netCDF_info["global"]["description"]["unit"]
    description.datatype = netCDF_info["global"]["description"]["datatype"]
    description.id = netCDF_info["global"]["description"]["id"]
    description.optional = netCDF_info["global"]["description"]["optional"]

    # variable: site_id
    site_id = DATA_CDF.createVariable(netCDF_info["global"]["site_id"]["name"], "u8")
    site_id[:] = np.int64(netCDF_info["global"]["site_id"]["value"])

    site_id.shortname = netCDF_info["global"]["site_id"]["shortname"]
    site_id.description = netCDF_info["global"]["site_id"]["description"]
    site_id.unit = netCDF_info["global"]["site_id"]["unit"]
    site_id.datatype = netCDF_info["global"]["site_id"]["datatype"]
    site_id.id = netCDF_info["global"]["site_id"]["id"]
    site_id.optional = netCDF_info["global"]["site_id"]["optional"]

    # variable: platform_id
    platform_id = DATA_CDF.createVariable(
        netCDF_info["global"]["platform_id"]["name"], "u8"
    )
    platform_id[:] = np.int64(netCDF_info["global"]["platform_id"]["value"])

    platform_id.shortname = netCDF_info["global"]["platform_id"]["shortname"]
    platform_id.description = netCDF_info["global"]["platform_id"]["description"]
    platform_id.unit = netCDF_info["global"]["platform_id"]["unit"]
    platform_id.datatype = netCDF_info["global"]["platform_id"]["datatype"]
    platform_id.id = netCDF_info["global"]["platform_id"]["id"]
    platform_id.optional = netCDF_info["global"]["platform_id"]["optional"]

    # variable: facility_id
    facility_id = DATA_CDF.createVariable(
        netCDF_info["global"]["facility_id"]["name"], "u8"
    )
    facility_id[:] = np.int64(netCDF_info["global"]["facility_id"]["value"])

    facility_id.shortname = netCDF_info["global"]["facility_id"]["shortname"]
    facility_id.description = netCDF_info["global"]["facility_id"]["description"]
    facility_id.unit = netCDF_info["global"]["facility_id"]["unit"]
    facility_id.datatype = netCDF_info["global"]["facility_id"]["datatype"]
    facility_id.id = netCDF_info["global"]["facility_id"]["id"]
    facility_id.optional = netCDF_info["global"]["facility_id"]["optional"]

    # variable: data_level
    data_level = DATA_CDF.createVariable(
        netCDF_info["global"]["data_level"]["name"], "u8"
    )
    data_level[:] = np.int64(netCDF_info["global"]["data_level"]["value"])

    data_level.shortname = netCDF_info["global"]["data_level"]["shortname"]
    data_level.description = netCDF_info["global"]["data_level"]["description"]
    data_level.unit = netCDF_info["global"]["data_level"]["unit"]
    data_level.datatype = netCDF_info["global"]["data_level"]["datatype"]
    data_level.id = netCDF_info["global"]["data_level"]["id"]
    data_level.optional = netCDF_info["global"]["data_level"]["optional"]

    # variable: location_description
    location_description = DATA_CDF.createVariable(
        netCDF_info["global"]["location_description"]["name"], "u8"
    )
    location_description[:] = np.int64(
        netCDF_info["global"]["location_description"]["value"]
    )

    location_description.shortname = netCDF_info["global"]["location_description"][
        "shortname"
    ]
    location_description.description = netCDF_info["global"]["location_description"][
        "description"
    ]
    location_description.unit = netCDF_info["global"]["location_description"]["unit"]
    location_description.datatype = netCDF_info["global"]["location_description"][
        "datatype"
    ]
    location_description.id = netCDF_info["global"]["location_description"]["id"]
    location_description.optional = netCDF_info["global"]["location_description"][
        "optional"
    ]

    variable: datastream
    datastream = DATA_CDF.createVariable(
        netCDF_info["global"]["datastream"]["name"], "u8", ("str_dim",)
    )
    datastream[:] = string2ascii_array(netCDF_info["global"]["datastream"]["value"])

    datastream.shortname = netCDF_info["global"]["datastream"]["shortname"]
    datastream.description = netCDF_info["global"]["datastream"]["description"]
    datastream.unit = netCDF_info["global"]["datastream"]["unit"]
    datastream.datatype = netCDF_info["global"]["datastream"]["datatype"]
    datastream.id = netCDF_info["global"]["datastream"]["id"]
    datastream.optional = netCDF_info["global"]["datastream"]["optional"]

    # variable: samp_interval
    samp_interval = DATA_CDF.createVariable(
        netCDF_info["global"]["sampling_interval"]["name"], "f8"
    )
    samp_interval[:] = np.float64(netCDF_info["global"]["sampling_interval"]["value"])

    samp_interval.shortname = netCDF_info["global"]["sampling_interval"]["shortname"]
    samp_interval.description = netCDF_info["global"]["sampling_interval"][
        "description"
    ]
    samp_interval.unit = netCDF_info["global"]["sampling_interval"]["unit"]
    samp_interval.datatype = netCDF_info["global"]["sampling_interval"]["datatype"]
    samp_interval.id = netCDF_info["global"]["sampling_interval"]["id"]
    samp_interval.optional = netCDF_info["global"]["sampling_interval"]["optional"]

    # variable: avar_interval
    avar_interval = DATA_CDF.createVariable(
        netCDF_info["global"]["averaging_interval"]["name"], "f8"
    )
    avar_interval[:] = np.float64(netCDF_info["global"]["averaging_interval"]["value"])

    avar_interval.shortname = netCDF_info["global"]["averaging_interval"]["shortname"]
    avar_interval.description = netCDF_info["global"]["averaging_interval"][
        "description"
    ]
    avar_interval.unit = netCDF_info["global"]["averaging_interval"]["unit"]
    avar_interval.datatype = netCDF_info["global"]["averaging_interval"]["datatype"]
    avar_interval.id = netCDF_info["global"]["averaging_interval"]["id"]
    avar_interval.optional = netCDF_info["global"]["averaging_interval"]["optional"]

    # variable: serial_number
    serial_number = DATA_CDF.createVariable(
        netCDF_info["global"]["serial_number"]["name"], "u8"
    )
    serial_number[:] = np.int64(netCDF_info["global"]["serial_number"]["value"])

    serial_number.shortname = netCDF_info["global"]["serial_number"]["shortname"]
    serial_number.description = netCDF_info["global"]["serial_number"]["description"]
    serial_number.unit = netCDF_info["global"]["serial_number"]["unit"]
    serial_number.datatype = netCDF_info["global"]["serial_number"]["datatype"]
    serial_number.id = netCDF_info["global"]["serial_number"]["id"]
    serial_number.optional = netCDF_info["global"]["serial_number"]["optional"]

    # variable: calib_date
    calib_date = DATA_CDF.createVariable(
        netCDF_info["global"]["calib_date"]["name"], "u8"
    )
    calib_date[:] = np.datetime64(netCDF_info["global"]["calib_date"]["value"])

    calib_date.shortname = netCDF_info["global"]["calib_date"]["shortname"]
    calib_date.description = netCDF_info["global"]["calib_date"]["description"]
    calib_date.unit = netCDF_info["global"]["calib_date"]["unit"]
    calib_date.datatype = netCDF_info["global"]["calib_date"]["datatype"]
    calib_date.id = netCDF_info["global"]["calib_date"]["id"]
    calib_date.optional = netCDF_info["global"]["calib_date"]["optional"]

    # variable: lat
    lat = DATA_CDF.createVariable(netCDF_info["global"]["lat"]["name"], "u8")
    lat[:] = np.float64(netCDF_info["global"]["lat"]["value"])

    lat.shortname = netCDF_info["global"]["lat"]["shortname"]
    lat.description = netCDF_info["global"]["lat"]["description"]
    lat.unit = netCDF_info["global"]["lat"]["unit"]
    lat.datatype = netCDF_info["global"]["lat"]["datatype"]
    lat.id = netCDF_info["global"]["lat"]["id"]
    lat.optional = netCDF_info["global"]["lat"]["optional"]

    # variable: lon
    lon = DATA_CDF.createVariable(netCDF_info["global"]["lon"]["name"], "u8")
    lon[:] = np.float64(netCDF_info["global"]["lon"]["value"])

    lon.shortname = netCDF_info["global"]["lon"]["shortname"]
    lon.description = netCDF_info["global"]["lon"]["description"]
    lon.unit = netCDF_info["global"]["lon"]["unit"]
    lon.datatype = netCDF_info["global"]["lon"]["datatype"]
    lon.id = netCDF_info["global"]["lon"]["id"]
    lon.optional = netCDF_info["global"]["lon"]["optional"]

    # variable: alt
    alt = DATA_CDF.createVariable(netCDF_info["global"]["alt"]["name"], "u8")
    alt[:] = np.float64(netCDF_info["global"]["alt"]["value"])

    alt.shortname = netCDF_info["global"]["alt"]["shortname"]
    alt.description = netCDF_info["global"]["alt"]["description"]
    alt.unit = netCDF_info["global"]["alt"]["unit"]
    alt.datatype = netCDF_info["global"]["alt"]["datatype"]
    alt.id = netCDF_info["global"]["alt"]["id"]
    alt.optional = netCDF_info["global"]["alt"]["optional"]

    # ######################## TIME VARIABLES ###########################

    # variable: base_time
    base_time = DATA_CDF.createVariable(
        netCDF_info["variables"]["base_time"]["name"], "u8"
    )
    # u8 == 32-bit unsigned integer
    base_time[:] = np.int64(day_data.index[0].timestamp())

    base_time.shortname = netCDF_info["variables"]["base_time"]["shortname"]
    base_time.description = netCDF_info["variables"]["base_time"]["description"]
    base_time.unit = netCDF_info["variables"]["base_time"]["unit"]
    base_time.datatype = netCDF_info["variables"]["base_time"]["datatype"]
    base_time.id = netCDF_info["variables"]["base_time"]["id"]
    base_time.optional = netCDF_info["variables"]["base_time"]["optional"]

    # variable: time_offset
    time_offset = DATA_CDF.createVariable(
        netCDF_info["variables"]["time_offset"]["name"],
        "f8",
        (netCDF_info["dimensions"]["time"]["symbol"],),
    )
    time_offset[:] = (
        (day_data.index - day_data.index[0])
        .map(lambda x: x.total_seconds())
        .to_numpy()
        .astype("float64")
    )

    time_offset.shortname = netCDF_info["variables"]["time_offset"]["shortname"]
    time_offset.description = netCDF_info["variables"]["time_offset"]["description"]
    time_offset.unit = netCDF_info["variables"]["time_offset"]["unit"]
    time_offset.datatype = netCDF_info["variables"]["time_offset"]["datatype"]
    time_offset.id = netCDF_info["variables"]["time_offset"]["id"]
    time_offset.optional = netCDF_info["variables"]["time_offset"]["optional"]

    # Variable: time
    time = DATA_CDF.createVariable(
        netCDF_info["variables"]["time"]["name"],
        "f8",
        (netCDF_info["dimensions"]["time"]["symbol"],),
    )
    time[:] = (
        (
            day_data.index
            - datetime(
                day_data.index[0].year,
                day_data.index[0].month,
                day_data.index[0].day,
                0,
                0,
            )
        )
        .map(lambda x: x.total_seconds())
        .to_numpy()
        .astype("float64")
    )

    time.shortname = netCDF_info["variables"]["time"]["shortname"]
    time.description = netCDF_info["variables"]["time"]["description"]
    time.unit = netCDF_info["variables"]["time"]["unit"]
    time.datatype = netCDF_info["variables"]["time"]["datatype"]
    time.id = netCDF_info["variables"]["time"]["id"]
    time.optional = netCDF_info["variables"]["time"]["optional"]

    # ######################## DATA VARIABLES ###########################

    # Variable: drops_diam
    drops_diam = DATA_CDF.createVariable(
        netCDF_info["variables"]["drops_diam"]["name"],
        "f8",
        (netCDF_info["dimensions"]["drops_diam"]["symbol"],),
    )

    drops_diam.shortname = netCDF_info["variables"]["drops_diam"]["shortname"]
    drops_diam.description = netCDF_info["variables"]["drops_diam"]["description"]
    drops_diam.unit = netCDF_info["variables"]["drops_diam"]["unit"]
    drops_diam.datatype = netCDF_info["variables"]["drops_diam"]["datatype"]
    drops_diam.id = netCDF_info["variables"]["drops_diam"]["id"]
    drops_diam.optional = netCDF_info["variables"]["drops_diam"]["optional"]

    drops_diam[:] = variables_info["drops_diam"]

    # Variable: fall_vell
    fall_vell = DATA_CDF.createVariable(
        netCDF_info["variables"]["fall_vell"]["name"],
        "f8",
        (netCDF_info["dimensions"]["drop_class"]["symbol"],),
    )

    fall_vell.shortname = netCDF_info["variables"]["fall_vell"]["shortname"]
    fall_vell.description = netCDF_info["variables"]["fall_vell"]["description"]
    fall_vell.unit = netCDF_info["variables"]["fall_vell"]["unit"]
    fall_vell.datatype = netCDF_info["variables"]["fall_vell"]["datatype"]
    fall_vell.id = netCDF_info["variables"]["fall_vell"]["id"]
    fall_vell.optional = netCDF_info["variables"]["fall_vell"]["optional"]

    fall_vell[:] = variables_info["fall_vell"]

    # Variable: delta_diam
    delta_diam = DATA_CDF.createVariable(
        netCDF_info["variables"]["delta_diam"]["name"],
        "f8",
        (netCDF_info["dimensions"]["drop_class"]["symbol"],),
    )

    delta_diam.shortname = netCDF_info["variables"]["delta_diam"]["shortname"]
    delta_diam.description = netCDF_info["variables"]["delta_diam"]["description"]
    delta_diam.unit = netCDF_info["variables"]["delta_diam"]["unit"]
    delta_diam.datatype = netCDF_info["variables"]["delta_diam"]["datatype"]
    delta_diam.id = netCDF_info["variables"]["delta_diam"]["id"]
    delta_diam.optional = netCDF_info["variables"]["delta_diam"]["optional"]

    delta_diam[:] = variables_info["delta_diam"]

    # Variable: n
    n = DATA_CDF.createVariable(
        netCDF_info["variables"]["n"]["name"],
        "f8",
        (
            netCDF_info["dimensions"]["time"]["symbol"],
            netCDF_info["dimensions"]["drop_class"]["symbol"],
        ),
    )

    n.shortname = netCDF_info["variables"]["n"]["shortname"]
    n.description = netCDF_info["variables"]["n"]["description"]
    n.unit = netCDF_info["variables"]["n"]["unit"]
    n.datatype = netCDF_info["variables"]["n"]["datatype"]
    n.id = netCDF_info["variables"]["n"]["id"]
    n.optional = netCDF_info["variables"]["n"]["optional"]

    #ALAN: verificar, deixar menos dependente de colunas
    n[:, :] = day_data[columns[4:24]].to_numpy().astype("float64")

    # Variable: d_max
    d_max = DATA_CDF.createVariable(
        netCDF_info["variables"]["d_max"]["name"],
        "f8",
        (netCDF_info["dimensions"]["time"]["symbol"],),
    )

    d_max.shortname = netCDF_info["variables"]["d_max"]["shortname"]
    d_max.description = netCDF_info["variables"]["d_max"]["description"]
    d_max.unit = netCDF_info["variables"]["d_max"]["unit"]
    d_max.datatype = netCDF_info["variables"]["d_max"]["datatype"]
    d_max.id = netCDF_info["variables"]["d_max"]["id"]
    d_max.optional = netCDF_info["variables"]["d_max"]["optional"]

    d_max[:] = np.array(disd.get_d_max(day_data[variables_info["drop_size"]])).astype(
        "float64"
    )

    # Variable: n_d
    n_d = DATA_CDF.createVariable(
        netCDF_info["variables"]["n_d"]["name"],
        "f8",
        (
            netCDF_info["dimensions"]["time"]["symbol"],
            netCDF_info["dimensions"]["drop_class"]["symbol"],
        ),
    )

    n_d.shortname = netCDF_info["variables"]["n_d"]["shortname"]
    n_d.description = netCDF_info["variables"]["n_d"]["description"]
    n_d.unit = netCDF_info["variables"]["n_d"]["unit"]
    n_d.datatype = netCDF_info["variables"]["n_d"]["datatype"]
    n_d.id = netCDF_info["variables"]["n_d"]["id"]
    n_d.optional = netCDF_info["variables"]["n_d"]["optional"]

    n_d[:, :] = np.array(
        disd.get_n_d_rd80(
            day_data[['Interval',*variables_info["drop_size"]]],
            variables_info["drop_size"],
            variables_info["delta_diam"],
            variables_info["fall_vell"]
        )
    ).astype("float64")

    # Variable: rain_rate
    rain_rate = DATA_CDF.createVariable(
        netCDF_info["variables"]["rain_rate"]["name"],
        "f8",
        (netCDF_info["dimensions"]["time"]["symbol"],),
    )

    rain_rate.shortname = netCDF_info["variables"]["rain_rate"]["shortname"]
    rain_rate.description = netCDF_info["variables"]["rain_rate"]["description"]
    rain_rate.unit = netCDF_info["variables"]["rain_rate"]["unit"]
    rain_rate.datatype = netCDF_info["variables"]["rain_rate"]["datatype"]
    rain_rate.id = netCDF_info["variables"]["rain_rate"]["id"]
    rain_rate.optional = netCDF_info["variables"]["rain_rate"]["optional"]

    rain_rate[:] = np.array(
        disd.get_ri_rd80(
            day_data[['Interval',*variables_info["drop_size"]]],
            variables_info["drop_size"],
            variables_info["drop_class"]
        )
    ).astype("float64")


    # Variable: zdb
    zdb = DATA_CDF.createVariable(
        netCDF_info["variables"]["zdb"]["name"],
        "f8",
        (netCDF_info["dimensions"]["time"]["symbol"],),
    )

    zdb.shortname = netCDF_info["variables"]["zdb"]["shortname"]
    zdb.description = netCDF_info["variables"]["zdb"]["description"]
    zdb.unit = netCDF_info["variables"]["zdb"]["unit"]
    zdb.datatype = netCDF_info["variables"]["zdb"]["datatype"]
    zdb.id = netCDF_info["variables"]["zdb"]["id"]
    zdb.optional = netCDF_info["variables"]["zdb"]["optional"]

    zdb[:] = np.array(
        disd.get_zdb(
            disd.get_z_rd80(
                day_data[['Interval',*variables_info["drop_size"]]],
                variables_info["drop_size"],
                variables_info["drop_class"],
                variables_info["fall_vell"]
            )
        )
    ).astype("float64")


    # Variable: liq_water
    liq_water = DATA_CDF.createVariable(
        netCDF_info["variables"]["liq_water"]["name"],
        "f8",
        (netCDF_info["dimensions"]["time"]["symbol"],),
    )

    liq_water.shortname = netCDF_info["variables"]["liq_water"]["shortname"]
    liq_water.description = netCDF_info["variables"]["liq_water"]["description"]
    liq_water.unit = netCDF_info["variables"]["liq_water"]["unit"]
    liq_water.datatype = netCDF_info["variables"]["liq_water"]["datatype"]
    liq_water.id = netCDF_info["variables"]["liq_water"]["id"]
    liq_water.optional = netCDF_info["variables"]["liq_water"]["optional"]

    liq_water[:] = np.array(
        disd.get_liq_water_rd80(
                day_data[['Interval',*variables_info["drop_size"]]],
                variables_info["drop_size"],
                variables_info["drop_class"],
                variables_info["fall_vell"]
        )
    ).astype("float64")


    # Variable: ef
    ef = DATA_CDF.createVariable(
        netCDF_info["variables"]["ef"]["name"],
        "f8",
        (netCDF_info["dimensions"]["time"]["symbol"],),
    )

    ef.shortname = netCDF_info["variables"]["ef"]["shortname"]
    ef.description = netCDF_info["variables"]["ef"]["description"]
    ef.unit = netCDF_info["variables"]["ef"]["unit"]
    ef.datatype = netCDF_info["variables"]["ef"]["datatype"]
    ef.id = netCDF_info["variables"]["ef"]["id"]
    ef.optional = netCDF_info["variables"]["ef"]["optional"]

    ef[:] = np.array(
        disd.get_ef(
            disd.get_ek_rd80(
                day_data[['Interval',*variables_info["drop_size"]]],
                variables_info["drop_size"],
                variables_info["drop_class"],
                variables_info["fall_vell"]
            ),
            day_data['Interval'],
        )
    ).astype("float64")

    # Variable: slope 
    slope = DATA_CDF.createVariable(
        netCDF_info["variables"]["slope"]["name"],
        "f8",
        (netCDF_info["dimensions"]["time"]["symbol"],),
    )

    slope.shortname = netCDF_info["variables"]["slope"]["shortname"]
    slope.description = netCDF_info["variables"]["slope"]["description"]
    slope.unit = netCDF_info["variables"]["slope"]["unit"]
    slope.datatype = netCDF_info["variables"]["slope"]["datatype"]
    slope.id = netCDF_info["variables"]["slope"]["id"]
    slope.optional = netCDF_info["variables"]["slope"]["optional"]

    slope[:] = np.array(
        disd.get_slope(
            disd.get_liq_water_rd80(
                day_data[['Interval',*variables_info["drop_size"]]],
                variables_info["drop_size"],
                variables_info["drop_class"],
                variables_info["fall_vell"]
            ),
            disd.get_z_rd80(
                day_data[['Interval',*variables_info["drop_size"]]],
                variables_info["drop_size"],
                variables_info["drop_class"],
                variables_info["fall_vell"]
            ),
        )
    ).astype("float64")

    # Variable: slope
    n_0 = DATA_CDF.createVariable(
        netCDF_info["variables"]["n_0"]["name"],
        "f8",
        (netCDF_info["dimensions"]["time"]["symbol"],),
    )

    n_0.shortname = netCDF_info["variables"]["n_0"]["shortname"]
    n_0.description = netCDF_info["variables"]["n_0"]["description"]
    n_0.unit = netCDF_info["variables"]["n_0"]["unit"]
    n_0.datatype = netCDF_info["variables"]["n_0"]["datatype"]
    n_0.id = netCDF_info["variables"]["n_0"]["id"]
    n_0.optional = netCDF_info["variables"]["n_0"]["optional"]

    n_0[:] = np.array(
        disd.get_n_0(
            disd.get_liq_water_rd80(
                day_data[['Interval',*variables_info["drop_size"]]],
                variables_info["drop_size"],
                variables_info["drop_class"],
                variables_info["fall_vell"]
            ),
            disd.get_z_rd80(
                day_data[['Interval',*variables_info["drop_size"]]],
                variables_info["drop_size"],
                variables_info["drop_class"],
                variables_info["fall_vell"]
            ),
        )
    ).astype("float64")

    print("netCDF created")

    DATA_CDF.close()
