import utils.meteors_utils as meteors
import xarray as xr
import argparse
import pathlib


# Create the parser
JOSS_parser = argparse.ArgumentParser(
    prog="JOSS_gen_meteors_netCDF",
    description="Processes and create metadata for netCDF files",
    formatter_class=argparse.RawDescriptionHelpFormatter
)

# Add the arguments
JOSS_parser.add_argument("-v", "--version", action="version", version="%(prog)s 0.1")

JOSS_parser.add_argument(
    "-s",
    "--standard",
    action="store_true",
    default=None,
    help="Executes the script for all .trf files inside the data input folder and exit",
)


# Execute the parse_args() method
args = JOSS_parser.parse_args()   

# Check if at least one action is requested
if all(action is None for action in [args.standard]):
    JOSS_parser.error("No action requested, see --help for further information")

# Folders and files path
path_cwd = pathlib.Path.cwd()
path_input = path_cwd.joinpath("input")
path_input_data = path_input.joinpath("data_meteors")
path_input_support = path_input.joinpath("support")
path_output_data = path_cwd.joinpath("output", "meteors_netCDF")

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
                
                meteors.create_time_var_in_dataset(dataset)
               
                meteors.create_and_update_metadata_in_json(dataset, path_input_support.joinpath("metadata_base_meteors.json"),path_input_support.joinpath("netcdf_meteors_info_atualizado.json"))
                meteors.create_and_update_metadata_in_dataset(dataset, path_input_support.joinpath("netcdf_meteors_info_atualizado.json"), path_output_data)
            except Exception as e:
                print(f"An error occurred: {e}. Could not process the file {dataset_path}.")
    except Exception as e:
        print(f"An error occurred: {e}. Could not list the file paths.")

print("All data have been processed.")
quit()


