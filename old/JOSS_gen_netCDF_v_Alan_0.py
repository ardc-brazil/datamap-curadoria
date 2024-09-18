# ##################### IMPORTS ####################

import argparse
import numpy as np
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os
import gc
import pathlib
import json
import utils
import sys

# ##################### ARGUMENTS ######################

# Create the parser
JOSS_parser = argparse.ArgumentParser(
    prog="JOSS_gen_netCDF",
    description="Processes JOSS raw data files to netCDF files",
    epilog="This program is used to generate netcdf files from the owner format for RD-80 disdrometer"
)

# Add the arguments
JOSS_parser.add_argument("-v", "--version", action="version", version="%(prog)s 0.1")

JOSS_parser.add_argument(
    "-d",
    "--date",
    action="store",
    default=None,
    help="Expect exporting date in format -d dd/mm/YYYY ou --date dd/mm/YYYY. Read all data inside the data input folder",
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
    help="Expect the format of the date contained in file names, use python strftime formats (https://strftime.org/) for input like '%Y%m%d'. Read the files inside the data input folder only for one day before and one day after the date input",
)

# Execute the parse_args() method
args = JOSS_parser.parse_args()

# if args.date is None:
if args.date is None and args.pattern is None:
    export_date = args.date
else:
    try:
        if args.date is None: export_date = datetime.strptime(args.pattern.strip(), "%d/%m/%Y")
        if args.pattern is None: export_date = datetime.strptime(args.date.strip(), "%d/%m/%Y")
    except Exception:
        JOSS_parser.error("Bad date format, see --help to further information")

# check if there is at least one action requested
if args.standard is None and args.list is None and args.pattern is None:
    JOSS_parser.error("No action requested, see --help to further information")

if args.standard is not None and args.list is not None:
    JOSS_parser.error("Invalid action requested, see --help to further information")

if args.standard is not None and args.pattern is not None:
    JOSS_parser.error("Invalid action requested, see --help to further information")

if args.list is not None and args.pattern is not None:
    JOSS_parser.error("Invalid action requested, see --help to further information")

if args.pattern is not None and args.date is not None:
    JOSS_parser.error("Invalid action requested, see --help to further information")

# ##################### SCRIPT #####################

# Folders and files path
path_cwd = pathlib.Path.cwd()

print(path_cwd.name)

if path_cwd.name != "JOSS":
    print(
        "ERRO. Please make sure python current working directory is the /JOSS folder which contains this script"
    )
    print("ERRO. Current working directory is:", path_cwd)
    quit()

path_input = path_cwd.joinpath("input", "JOSS")
path_input_data = path_input.joinpath("data")
path_input_support = path_input.joinpath("support")

path_output = path_cwd.joinpath("output", "JOSS")
path_output_data = path_output.joinpath("netCDF")

# reading auxiliar data
with open(path_input_support.joinpath("variables_info_orig.json"), "r") as xfile:
    variables_info_file = xfile.read()
variables_info = json.loads(variables_info_file)

with open(path_input_support.joinpath("netCDF_info_orig.json"), "r") as xfile:
    netCDF_info_file = xfile.read()
netCDF_info = json.loads(netCDF_info_file)

columns = list(np.loadtxt(path_input_support.joinpath("variables.txt"), dtype=str))

# reading all file names in folder or list
EXT = variables_info["input_file_extension"]
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
    files = np.loadtxt(path_input.joinpath("files.txt"), dtype=str)
    if len(files.shape) == 0:
        files = files.reshape(1)
    files = [path_input_data.joinpath(file) for file in files]
elif args.pattern:
    print("Executing script in pattern mode")
    print("")
    d0 = export_date
    d0 = d0.strftime("%Y%m%d")
    d1 = export_date - relativedelta(days=1)
    d1 = d1.strftime("%Y%m%d")
    d2 = export_date + relativedelta(days=1)
    d2 = d2.strftime("%Y%m%d")
    #ALAN:Essa busca depende do nome do arquivo, então se mudar o nome do arquivo, tem que mudar aqui também
    files = [
        path_input_data.joinpath(file)
        for days in [d1, d0, d2]
        for file in os.listdir(path_input_data)
        if file.find(days) != -1
    ]

# call the fuction that read all files
all_data = utils.read_files(files, columns)

# data processing
while True:

    (export_date, day_data, flag) = utils.get_day_data(
        all_data, export_date, variables_info
    )

    if flag:
        break

    if day_data.shape[0] != 0:

        cdf_filename = (
            "att"
            + "impactdisd"
            + "cam."
            + "b0."
            + day_data.index[0].strftime("%Y%m%d.%H%M%S")
            + ".nc"
        )

        utils.generate_netCDF(
            cdf_filename,
            day_data,
            columns,
            variables_info,
            netCDF_info,
            path_output_data,
        )
        print("")

    if args.date or args.pattern:
        break

    gc.collect()

# end of data processing
print("All data have been processed.")
quit()
