# ##################### IMPORTS ####################

import argparse
import numpy as np
from datetime import datetime, timedelta
import os
import gc
import pathlib
import json
import utils.disdrometer_utils as disd
import utils.netcdf_utils as cdf

# ##################### ARGUMENTS ######################

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
    
if args.date:
    try:
        export_date = datetime.strptime(args.date.strip(), "%d/%m/%Y")
    except Exception:
        JOSS_parser.error("Bad date format, see --help for further information")

if args.pattern:
    try:
        export_date = datetime.strptime(args.pattern.strip(), "%d/%m/%Y")
    except Exception:
        JOSS_parser.error("Bad date format, see --help for further information") 
        

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
    

###################### Defining directories #####################

# Folders and files path
path_cwd = pathlib.Path.cwd()
path_input = path_cwd.joinpath("input")
path_input_data = path_input.joinpath("data")
path_input_support = path_input.joinpath("support")
path_output_data = path_cwd.joinpath("output", "netCDF")

# ##################### reading all file names in folder or list ##################### 

# reading auxiliar data:
with open(path_input_support.joinpath("variables_info.json"), "r") as xfile:
    variables_info_file = xfile.read()
variables_info = json.loads(variables_info_file)

columns = list(variables_info['Columns'])

with open(path_input_support.joinpath("netCDF_info_ARM.json"), "r") as xfile:
    netCDF_info_file = xfile.read()
netCDF_info = json.loads(netCDF_info_file)

# reading data from the equipment:

EXT = variables_info["input_file_extension"]
if args.standard:
    # check if export_date is declared
    if "export_date" not in locals():
        export_date = None
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
    if "export_date" not in locals():
        export_date = None
    if not path_input_support.joinpath("files.txt").exists():
        with open(path_input_support.joinpath("files.txt"), "w") as xfile:
            xfile.write("")
    files = np.loadtxt(path_input_support.joinpath("files.txt"), dtype=str)
    if len(files.shape) == 0:
        files = files.reshape(1)
    files = [path_input_data.joinpath(file) for file in files]
    
elif args.pattern:
    print("Executing script in pattern mode")
    print("")
    export_date = datetime.strptime(args.pattern.strip(), "%d/%m/%Y")
    d0 = export_date.strftime("%Y%m%d")
    d1 = (export_date - timedelta(days=1)).strftime("%Y%m%d")
    d2 = (export_date + timedelta(days=1)).strftime("%Y%m%d")
    # Find the files containing d0, d1, or d2 in the file name
    files = [
        path_input_data.joinpath(file)
        for days in [d1, d0, d2]
        for file in os.listdir(path_input_data)
        if days in file
    ]
    # Remove duplicates
    files = list(dict.fromkeys(files))
    # Sort the list
    files.sort()

# check if there is at least one file to be processed
if len(files) == 0:
    print("No files to be processed")
    quit()

# call the fuction that read all files
all_data = disd.read_files_rd80(files, columns)

# ##################### Generate netcdf file(s) ##################### 
# data processing
while True:

    (export_date, day_data, flag) = disd.get_day_data(all_data, export_date, variables_info)

    if flag:
        break

    if day_data.shape[0] != 0:

        print("Generating netCDF file for", day_data.index[0].strftime("%d/%m/%Y"))
        (dimension_nc,filled_variables) = cdf.extract_variables(day_data,variables_info,netCDF_info)

        cdf_filename = (netCDF_info['global attributes']['datastream']['long_name']+"."+ day_data.index[0].strftime("%Y%m%d.%H%M%S")+".nc")

        cdf.generate_netCDF(
            cdf_filename,
            dimension_nc,
            filled_variables,
            netCDF_info,
            path_output_data
        )
        print("")

    if args.date or args.pattern:
        break

    gc.collect()

# end of data processing
print("All data have been processed.")
quit()
