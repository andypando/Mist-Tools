# Mist-Tools
Collection of Python Scripts that use a tkinter UI to perform tasks not available in Mist Portal utilizing Mist API calls

These have all been tested with Python 3.12.10

You will also need to install the requests library using:
```
python -m pip install requests
```

The first time you use one of the scripts, you can save your Org ID and API Token and as long as all scripts are executed
from the same folder, they will look for org.conf and load these for you.

## AP Rename

Allows the bulk renaming of APs from a .csv file, a task that is usually performed when turning up a new site. Your .csv file
should just have 2 columns, AP MAC and AP Name. It will iterate through the .csv and for each AP, if it is not assigned to the
site it will move it there, and then change it's name. If an AP in your list is already assigned to a site that is different
from the selected site it skips it. It logs each AP in the .csv so you know if it skips an entry for any reason.
