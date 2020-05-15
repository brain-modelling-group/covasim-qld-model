import data
import os

# file path
root = os.path.dirname(os.path.abspath(__file__))
root += "/data"

# create data object
setting = "victoria"
dataobj = data.setup_dataobj(root, "vic-data", setting)
