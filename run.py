import os
import setup

# file path
root = os.path.dirname(os.path.abspath(__file__))

# create data object
setting = 'victoria'
file_name = 'vic-data'
setup.setup(root, file_name, setting)
