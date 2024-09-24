import utils.meteors_utils as meteors
import netCDF4
import xarray as xr
import argparse
import numpy as np
from datetime import datetime, timedelta
import os
import gc
import pathlib
import json


# Create the parser
JOSS_parser = argparse.ArgumentParser(
    prog="JOSS_gen_netCDF",
    description="Processes JOSS raw data files to netCDF files",
    epilog="Developed by: Thomas Pougy and Alan Calheiros",
    formatter_class=argparse.RawDescriptionHelpFormatter
)

# Add the arguments
JOSS_parser.add_argument("-v", "--version", action="version", version="%(prog)s 0.1")

JOSS_parser.add_argument(
    "-d",
    "--date",
    action="store",
    default=None,
    help="Expect exporting date in format -d dd/mm/YYYY ou --date dd/mm/YYYY. Read all data inside the data input folder and extract the data for the date specified.",
)
JOSS_parser.add_argument(
    "-s",
    "--standard",
    action="store_true",
    default=None,
    help="Executes the script for all .trf files inside the data input folder and exit",
)
JOSS_parser.add_argument(
    "-l",
    "--list",
    action="store_true",
    default=None,
    help="Executes the script for files listed in the files.txt file specified ate input/JOSS folder and exit. The file.txt must have only the file name (without path) of the files in each line.",
)
JOSS_parser.add_argument(
    "-p",
    "--pattern",
    action="store",
    default=None,
    help=f"Expect the format of the date contained in file names, use python strftime formats (https://strftime.org/) for input like %%Y%%m%%d. Read the files inside the data input folder only for one day before to one day after the date input",
)

# Execute the parse_args() method
args = JOSS_parser.parse_args()   

# #check if there is at least one action requested

# Define the invalid action combinations
invalid_combinations = [
    (args.standard, args.list),
    (args.standard, args.pattern),
    (args.list, args.pattern),
    (args.pattern, args.date),
]

# Check if at least one action is requested
if all(action is None for action in [args.standard, args.list, args.pattern, args.date]):
    JOSS_parser.error("No action requested, see --help for further information")

# Check for invalid action combinations
if any(action1 is not None and action2 is not None for action1, action2 in invalid_combinations):
    JOSS_parser.error("Invalid action requested, see --help for further information")

# Check if date is used with -s or -l options
if args.date and not (args.standard or args.list):
    JOSS_parser.error("Invalid action requested, date needs to be used with -s or -l, see --help for further information")
    
# Folders and files path
path_cwd = pathlib.Path.cwd()
path_input = path_cwd.joinpath("input")
path_input_data = path_input.joinpath("data_meteors")
path_input_support = path_input.joinpath("support")
print(path_input_data)
print(path_input_support)
path_output_data = path_cwd.joinpath("output", "meteors_netCDF")
print(path_output_data)

if args.standard:
    print("Executing script in standard mode")
    try:
        dataset_input_list = meteors.get_files_from_folder(path_input_data)
        for dataset_path in dataset_input_list:
            try:    
                dataset = xr.open_dataset(dataset_path)
               
                meteors.create_lat_var_in_dataset(dataset)
                
                meteors.create_lon_var_in_dataset(dataset)
              
                meteors.create_time_bounds_var_in_dataset(dataset)
                
                meteors.create_times_vars_in_dataset(dataset)
               
                print(path_input_support.joinpath("metadata_base.json"))
                meteors.create_and_update_metadata_in_json(dataset, path_input_support.joinpath("metadata_base.json"),path_input_support.joinpath("netcdf_meteors_info_atualizado.json"))
                print("6")
                meteors.create_and_update_metadata_in_dataset(dataset, path_input_support.joinpath("netcdf_meteors_info_atualizado.json"), path_output_data)
                print("7")
            except Exception as e:
                print(f"Ocorreu um erro: {e}. Não foi possível processar o arquivo {dataset_path}.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}. Não foi possível listar os caminhos dos arquivos")

print("All data have been processed.")
quit()


