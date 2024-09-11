import pathlib
import os
import numpy as np
path_cwd = pathlib.Path.cwd()
path_input = path_cwd.joinpath("input", "JOSS")
path_input_data = path_input.joinpath("data")
print(path_input_data)
files = [
        path_input_data.joinpath(file)
        for file in os.listdir(path_input_data)
        if file.endswith(".trf")
    ]
#print(files)


names=['A','B','C','D']
list_names= [
    i
    for i in names
]
print(list_names)

#concatenate the list of the list in names
list_names= [name for name in names]

