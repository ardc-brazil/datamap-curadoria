# ##################### IMPORTS ####################

import argparse
import pathlib
import numpy as np
import json
from datetime import datetime
from netCDF4 import Dataset
import os
import sys
import utils.fig_utils as utils
import warnings
warnings.filterwarnings("ignore")


# ##################### ARGUMENTS ######################

# Create the parser
JOSS_parser = argparse.ArgumentParser(
    prog="JOSS_gen_figures",
    description="Generate figures for JOSS netCDF files",
    epilog="Developed by: Thomas Pougy and Alan Calheiros"
)

# Add the arguments
JOSS_parser.add_argument("-v", "--version", action="version", version="%(prog)s 0.1")

JOSS_parser.add_argument(
    "-s",
    "--standard",
    action="store_true",
    default=None,
    help="Executes the script for all .nc files inside the data_figures input folder and exit",
)
JOSS_parser.add_argument(
    "-l",
    "--list",
    action="store_true",
    default=None,
    help="Executes the script for files listed in the files_figures.txt file specified ate input/JOSS folder and exit. The file.txt must have only the file name (without path) of the files in each line.",
)
JOSS_parser.add_argument(
    "-p",
    "--png",
    action="store_true",
    default=None,
    help="Generates only the .png files.",
)
JOSS_parser.add_argument(
    "-d",
    "--date",
    action="store",
    default=None,
    help="Expect exporting date in format -d dd/mm/YYYY ou --date dd/mm/YYYY. Read all data inside the data input folder and extract the data for the date specified.",
)
JOSS_parser.add_argument(
    "-i",
    "--input",
    action="store",
    default=None,
    help="Path to the input folder containing the data files",
)
# Execute the parse_args() method
args = JOSS_parser.parse_args()

if args.date:
    try:
        export_date = datetime.strptime(args.date.strip(), "%d/%m/%Y")
    except Exception:
        JOSS_parser.error("Bad date format, see --help for further information")
else:
    export_date = args.date

# check if there is at least one action requested
if args.standard is None and args.list is None and args.date is None:
    JOSS_parser.error("No action requested, see --help to further information")

if args.standard is not None and args.list is not None:
    JOSS_parser.error("Invalid action requested, see --help to further information")

if args.standard is not None and args.date is not None:
    JOSS_parser.error("Invalid action requested, see --help to further information")

if args.date is not None and args.list is not None:
    JOSS_parser.error("Invalid action requested, see --help to further information")

# ##################### SCRIPT #####################


path_input = pathlib.Path(args.input) if args.input else pathlib.Path.cwd().joinpath("input")
path_input_support = path_input.joinpath("support")

path_output = path_input.joinpath("output")
path_output_fig = path_output.joinpath("figures")
path_input_data = path_output.joinpath("netCDF")


# reading auxiliar data
with open(path_input_support.joinpath("variables_info.json"), "r") as xfile:
    variables_info_file = xfile.read()
variables_info = json.loads(variables_info_file)

with open(path_input_support.joinpath("netCDF_info_ARM.json"), "r") as xfile:
    netCDF_info_file = xfile.read()
netCDF_info = json.loads(netCDF_info_file)

# reading all file names in folder or list
EXT = ".nc"
if args.standard:
    print("Executing script in standard mode")
    print("")
    files = [
        path_input_data.joinpath(file)
        for file in os.listdir(path_input_data)
        if file.endswith(EXT)
    ]
elif args.list:
    print("Executing script in list mode")
    print("")
    files = np.loadtxt(path_input_support.joinpath("files_figures.txt"), dtype=str)
    if len(files.shape) == 0:
        files = files.reshape(1)
    files = [path_input_data.joinpath(file) for file in files]
elif args.date:
    print("Executing script in date mode")
    print("")
    files = [
        path_input_data.joinpath(file)
        for file in os.listdir(path_input_data)
        if file.endswith(EXT)
    ]
    #find the date from export_date in the file name considering the format YYYYMMDD in the file name:
    files = [file for file in files if export_date.strftime("%Y%m%d") in file.name]
else:
    print("ERRO. please, check if the arguments are rights")
    quit()

# check if there is at least one file to process
if len(files) == 0:
    print("ERRO. No file to process")
    quit()

if args.png:
    print("Executing script in png mode. Only PNG files are included in the output")

for file in files:
    print("Generating figures for file {}".format(file.name))
    output_folder = path_output_fig.joinpath(str(file.name)[:-3])
    pathlib.Path(output_folder).mkdir(parents=True, exist_ok=True)

    file_data = Dataset(file, "r")
    time_index_file_data = [
        datetime.utcfromtimestamp(x)
        for x in file_data["time_offset"][:] + file_data["base_time"][:]
    ]

    fig_metadata = {"disdrometer": "RD-80", "site": "Atto-Campina"}

    list_variables_1D = ["rain_rate", "radar_reflectivity", "liq_water"]

    for var in list_variables_1D:
        print("\tFigure for variable {}".format(var))
        #convert missing values to NaN
        var_data = np.array(file_data[var][:])
        missing_value = file_data[var].missing_value
        var_data[var_data == missing_value] = np.nan
        utils.gen_fig_1D(
            var_data,
            time_index_file_data,
            netCDF_info["variables"][var]["short_name"],
            netCDF_info["variables"][var]["units"],
            fig_metadata,
            output_folder,
            args.png,
        )

    if not args.png:
        print("\tFigure for variable {}".format("Rain Rate and NDropxDi"))
        rain_data = np.array(file_data['rain_rate'][:])
        missing_value = file_data['rain_rate'].missing_value
        rain_data[rain_data == missing_value] = np.nan
        nd_data = np.array(file_data['num_drop_density'][:])
        missing_value = file_data['num_drop_density'].missing_value
        nd_data[nd_data == missing_value] = np.nan

        utils.gen_fig_NDropxDi(
            time_index_file_data,
            rain_data,
            variables_info["drop_mean_diam"],
            nd_data,
            fig_metadata,
            output_folder,
        )
