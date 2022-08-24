'''
Ubidots-Python-API-Client-Test
By A.J. Brown
24 Aug 2022

Help doc for ubidots library:
https://pypi.org/project/ubidots/

This script is designed to pull data from Ubidots servers for streamlined data
analysis. This initial test script will use low-cost temperature and relative
humidity sensors deployed in sugar beet fields to monitor cercospora risk.
'''
# Import Ubidots library
from ubidots import ApiClient
## Connect to Ubidots via API token

api = ApiClient(token='')

# Connecting to devices and variables directly
## Calling a specific device datasource
AWQP_Cercospora_7 = api.get_datasource('62f2d9731d84721b5589224f')
variable_list = AWQP_Cercospora_7.get_variables()

## Calling a specific variable
AWQP_Cercospora_7_TempF = api.get_variable('62f2d9c922d44d0a7ce46fb2')
### Saving most recent value in a python variable
last_value = AWQP_Cercospora_7_TempF.get_values(1)[0]['value']
### Getting all the values from the server.
#### WARNING: If your variable has millions of datapoints, then this will take forever or break your code!
all_values = AWQP_Cercospora_7_TempF.get_values()

# Now using a python dict to use device ID's alone to access everything
deviceID_dict = {'AWQP_Cercospora_7':'62f2d9731d84721b5589224f',
                 'AWQP_Cercospora_4':'6287e6751d84721cdfccf9a1',
                 'AWQP_Cercospora_3':'6287e1581d84720fb49b7baf',
                 'AWQP_Cercospora_2':'627d59cd1d847205d7306a78'}
## Define sensor name as variable
deviceName = 'AWQP_Cercospora_7'
## Call datasource
datasource = api.get_datasource(deviceID_dict[deviceName])
## Call variable of interest from list of variables
print(datasource.get_variables())
tempF = datasource.get_variables()[6].get_values()
rh = datasource.get_variables()[3].get_values()
