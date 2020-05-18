import os
import parameters

# file path
root = os.path.dirname(os.path.abspath(__file__))

# create data object
setting = 'victoria'
file_name = 'vic-data'

params = parameters.get_parameters(root, file_name, setting)
