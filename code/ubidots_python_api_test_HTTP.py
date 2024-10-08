'''
Ubidots-Python-API-Client-Test-HTTP
By A.J. Brown
24 Aug 2022
Updated: 4 Jan 2023

This script is designed to pull data from Ubidots servers for streamlined data
analysis.

Help doc for HTTP and Ubidots:
https://docs.ubidots.com/v1.6/reference/http # <<< version 1.6
https://docs.ubidots.com/reference/welcome # <<< version 2.0

Help doc for device types:
https://help.ubidots.com/en/articles/2129204-device-types

Please note that a mix of 1.6 and 2.0 are utilized in this doc as 2.0 is
currently under development at Ubidots. Eventually, a full shift to 2.0 will
be integrated.
'''
# TODO: Make script into class?
# TODO: make a function to download all data for a group of devices and all vars
# NOTE: looks like HEADERS doesn't get passed all the way from get_type_data() to _get_device_vars()
import config # <<< this is the config file for the Ubidots API
import pandas as pd
import os
import requests
import time
from datetime import datetime, timedelta
from functools import reduce
from io import StringIO

# Global variables
ENDPOINT = 'industrial.api.ubidots.com'
DEVICE_NAME  = '' # must manually define using ubidots 'name' device attribute
DEVICE_LABEL = '' # must manually define using ubidots device 'id' attribute
DEVICE_TYPE = "low-cost-water-sampler" # other option is 'pile-temp-and-cercospora-monitor'
VARIABLE_LABEL = '' # must manually define using ubidots variable 'id' attribute
TOKEN = config.TOKEN # Place API token in config.py file
HEADERS = {"X-Auth-Token": TOKEN} # must manually change after defining TOKEN #, "Content-Type": "application/json"}
DELAY = 1 # Delay in seconds

def calculate_last_values(start_time = "2024-01-01 00:00:00", 
                          interval_minutes = 5) -> int:
    """
    Calculate the number of data points collected from a specified start datetime until now, 
    given a collection interval.
    
    Parameters:
        start_time (str): The start time in "YYYY-MM-DD HH:MM:SS" format.
        interval_minutes (int): The time interval between each data point in minutes.

    Returns:
        int: The number of data points collected within the specified range.
    """
    # Convert the input string to a datetime object for the start time
    start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    
    # Get the current time
    now = datetime.now()
    
    # Calculate the total duration between the start datetime and now
    total_duration = now - start_dt
    
    # Calculate the number of intervals within the total duration
    interval_duration = timedelta(minutes=interval_minutes)
    data_point_count = total_duration // interval_duration
    
    # Add one more point to count the starting data point
    return data_point_count + 1

LAST_VALUES = calculate_last_values() # <<< this is the number of data points to collect

def get_all_type_var_ids_and_location(device_type = DEVICE_TYPE,
                                    headers=HEADERS,
                                    unl_export = False
                                    ):
    '''
    Collects the ids of all variables for a specified device type, as well as the latitue and longitutude.
    This is for convenient delivery of API ids for further data collection by us or others (e.g., UNL).
    :param device_type: device type label as indicated in Ubidots; can also be found in individual device properties
    :param headers: http headers to use when making HTTP query (see Global variables)
    :return: pandas.core.frame.DataFrame containing variable ids and location for all devices of specified type
    '''
    # get list of all devices containing only name, id, and properties
    device_df = get_all_devices_df(headers=headers)[['name','id','properties']]
    # convert properties from dict to df
    properties_df = device_df['properties'].apply(pd.Series)
    # get the locations from the device properties
    locations_df = properties_df['_location_fixed'].apply(pd.Series)
    # merge df's back together for clean stratification
    clean_df = device_df.join(properties_df)[['_device_type','name','id']]
    clean_df = clean_df.join(locations_df)[['_device_type','lat','lng','name','id']]
    # select only devices of specified type
    type_df = clean_df[clean_df['_device_type'] == device_type]
    dfs = []
    for i,j in enumerate(type_df['id']):
        name = type_df.iloc[i]['name']
        df = get_device_vars_df(device_id=j, headers=headers)
        df['name'] = name
        dfs.append(df)

    # get vars and ids in long format
    type_vars_df = pd.concat(dfs).reset_index(drop=True)
    # pivot to wide format
    pivot_df = type_vars_df.pivot(
        index='name', columns='label', values='id').reset_index()
    # merge with lat/lng columns from type_df dataframe
    pivot_df_wLocations = pivot_df.merge(type_df[['name','lat','lng']], on='name', how='left') 

    if unl_export == True:
        # drop all columns except for those needed for UNL: 'name', 'rh', 't', 'lat', 'lng'
        unl_df = pivot_df_wLocations[['name', 'rh', 't', 'lat', 'lng']]
        # get timestanmp and generate file name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = os.path.join(os.getcwd(), f'unl_export_{timestamp}.csv')
        # export to csv
        unl_df.to_csv(f'{output_filename}', index=False)
    
    return pivot_df_wLocations

def get_type_data(device_type = DEVICE_TYPE,
                  headers=HEADERS,
                  last_values = LAST_VALUES,
                  export_csv = False):
    '''
    Collects all variable data from all devices of a specified type, returns as single dataframe
    with variables and  as columns, all organized by timestamp.
    :param device_type: device type label as indicated in Ubidots; can also be found in individual device properties
    :param headers: http headers to use when making HTTP query (see Global variables)
    :param last_values: number that designates how many of the most recent values to return in the dataframe
    :return: pandas.core.frame.DataFrame containing variable values plus timestamps for single device
    '''
    # get list of all devices containing only name, id, and properties
    device_df = get_all_devices_df(headers=headers)[['name','id','properties']]
    # convert properties from dict to df
    properties_df = device_df['properties'].apply(pd.Series)
    # merge df's back together for clean stratification
    clean_df = device_df.join(properties_df)[['_device_type','name','id']]
    # select only devices of specified type
    type_df = clean_df[clean_df['_device_type'] == device_type]
    dfs = []
    for i,j in enumerate(type_df['id']):
        name = type_df.iloc[i]['name']
        df = get_device_data(device_id=j,
                             last_values=last_values,
                             headers=headers)
        df['name'] = name
        dfs.append(df)

    type_data_df = pd.concat(dfs).reset_index(drop=True)
    # print confirmation message with beginning and end timestamps using warning colors from bcolors class below
    print(f'\033[93mData collection complete for {device_type} devices.\033[0m')
    # print start timestamp by finding the minimum timestamp in the dataframe
    print(f"Start timestamp: {type_data_df['Human readable date (UTC)'].min()}")
    # print end timestamp by finding the maximum timestamp in the dataframe
    print(f"End timestamp: {type_data_df['Human readable date (UTC)'].max()}")

    # export to csv with timestamp
    if export_csv == True:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = os.path.join(os.getcwd(), f'{device_type}_export_{timestamp}.csv')
        type_data_df.to_csv(f'{output_filename}', index=False)
        print(f'\033[1mExported data to {output_filename}.\033[0m')

    return type_data_df

def get_device_data(device_id=DEVICE_LABEL, headers=HEADERS, last_values=LAST_VALUES):
    '''
    Collects all variable data from specified device and returns DataFrame
    with variables as columns, all merged by timestamp.
    :param device_id: individual device label as created by Ubidots
    :param headers: http headers to use when making HTTP query (see Global variables)
    :param last_values: number that designates how many of the most recent values to return in the dataframe
    :return: pandas.core.frame.DataFrame containing variable values plus timestamps for single device
    '''
    print("Headers = " + str(headers))
    dfs = []
    for i in get_device_vars_df(device_id=device_id, headers=headers)['id']:
        print(i)
        df = get_var_df(url=ENDPOINT,
                        device_id=device_id,
                        variable=i,
                        headers=headers,
                        last_values=last_values)
        dfs.append(df)
        #print(dfs)
    merged_df = reduce(lambda left, right:     # Merge DataFrames in list
                       pd.merge(left , right,
                                on = ['Timestamp','Human readable date (UTC)',
                                      'Context'],
                                how = "outer"),
                       dfs)
    print('Done.')
    return merged_df

def get_var_df(url=ENDPOINT, device_id=DEVICE_LABEL, variable=VARIABLE_LABEL,
            headers=HEADERS, last_values=LAST_VALUES):
    # tested: good for v1.6 but NOT v2.0
    '''
    Function to generate dataframe of a single variable's values
    :param url: api url for ubidots (see Global variables)
    :param device_id: (not used currently) individual device label as created by Ubidots
    :param variable: individual variable label as created by Ubidots
    :param headers: http headers to use when making HTTP query (see Global variables)
    :param last_values: number that designates how many of the most recent values to return in the dataframe
    :return: pandas.core.frame.DataFrame containing variable values plus timestamps for single device
    '''
    try:
        '''
        # TODO: not working, and I'm not sure why
        url = "https://{}/api/v1.6/devices/{}/{}/values/"\
              "?page_size={}&format=csv".format(url,
                                                device_id,
                                                variable,
                                                last_values)
        '''
        url = "https://{}/api/v1.6/variables/{}/values/"\
              "?page_size={}&format=csv".format(url,
                                                variable,
                                                last_values)
        attempts=0
        status_code = 400
        print(url)
        print("Headers = " + str(headers))
        while status_code >= 400 and attempts < 5:
            print("[INFO] Retrieving data, attempt number: {}".format(attempts))
            req = requests.get(url=url, headers=headers)
            status_code = req.status_code
            attempts += 1
            time.sleep(1)
        #print (req.text)
    except Exception as e:
        print("[ERROR] Error posting, details: {}".format(e))

    return pd.read_csv(StringIO(req.text), sep=',')

def get_all_devices_df(headers=HEADERS):
    #tested: good for v2.0
    '''
    Function to generate dataframe of all Ubidot devices and associated demographic info (not variables).
    Mostly used to find specific device label
    :param device_id: individual device label as created by Ubidots
    :param headers: http headers to use when making HTTP query (see Global variables)
    :return: pandas.core.frame.DataFrame containing list of devices and their properties
    '''
    df = pd.DataFrame(_get_all_devices(headers=headers))
    print('Done.')
    return df

def get_device_vars_df(device_id=DEVICE_LABEL, headers=HEADERS):
    # tested: good for v2.0
    '''
    Function to generate dataframe of a single device's variable names and associated demographic info.
    Mostly used to find variable labels for a specific device
    :param device_id: individual device label as created by Ubidots
    :param headers: http headers to use when making HTTP query (see Global variables)
    :return: pandas.core.frame.DataFrame containing variable info for single device
    '''
    var_df = pd.DataFrame(_get_device_vars(device_id=device_id, headers=headers))
    device_name = var_df.device[0]['name']
    print(f'{bcolors.OKCYAN}Variable dataframe returned for device name:\
            {device_name}{bcolors.ENDC}')
    return var_df

def _get_all_devices(headers=HEADERS):
    # tested: good for v2.0
    '''
    Function to generate list of all Ubidot devices and associated demographic info (not variables).
    :private function (should not need to run, but used in main fxns)
    :param headers: http headers to use when making HTTP query (see Global variables)
    :return: a list of dictionaries (1 dict = 1 device)
    '''
    devices = []
    next = "https://industrial.api.ubidots.com/api/v2.0/devices/"
    while next:
        print("Making request to " + next)
        print("Headers = " + str(headers))
        data = requests.get(next, headers=headers).json()
        next = data["next"]
        devices.extend(data["results"])
    return devices

def _get_device_vars(device_id=DEVICE_LABEL, headers=HEADERS):
    # tested: good for v2.0
    '''
    Function to generate list of a single device's variables and associated demographic info.
    :private function (should not need to run, but used in main fxns)
    :param device_id: individual device label as created by Ubidots
    :param headers: http headers to use when making HTTP query (see Global variables)
    :return: a list of dictionaries (1 dict = 1 device)
    '''
    var_list = []
    next = f"https://industrial.api.ubidots.com/api/v2.0/devices/{device_id}/variables"
    while next:
        print("Making request to " + next)
        print("Headers = " + str(headers))
        data = requests.get(next, headers=headers).json()
        next = data["next"]
        var_list.extend(data["results"])
    return var_list

def _get_var(url=ENDPOINT, device=DEVICE_LABEL, variable=VARIABLE_LABEL,
            token=TOKEN, last_values=LAST_VALUES):
    # tested: good for v1.6 but NOT v2.0
    try:
        '''
        # not working, and I'm not sure why
        url = "https://{}/api/v1.6/devices/{}/{}/values/"\
              "?page_size={}&format=csv".format(url,
                                                device,
                                                variable,
                                                last_values)
        '''
        url = "https://{}/api/v1.6/variables/{}/values/"\
              "?page_size={}".format(url,
                                     variable,
                                     last_values)
        headers = {"X-Auth-Token": token}#, "Content-Type": "application/json"}
        attempts=0
        status_code = 400
        print(url)
        print(headers)
        while status_code >= 400 and attempts < 5:
            print("[INFO] Retrieving data, attempt number: {}".format(attempts))
            req = requests.get(url=url, headers=headers)
            status_code = req.status_code
            attempts += 1
            time.sleep(1)
        #print (req.text)
    except Exception as e:
        print("[ERROR] Error posting, details: {}".format(e))
    return req.text

def _validate_token(device_id=DEVICE_LABEL, token=TOKEN):
    #tested: good for v2.0
    print("Validating token for " + device_id)
    resp = requests.get(f"https://industrial.ubidots.com/api/v2.0/devices/{device_id}/variables/", headers=HEADERS)
    if (resp.ok):
        print(f"Token {token} for {device_id} validated.")
    else:
        print(f"Token {token} for {device_id} failed validation with {resp.status_code}")
    return resp.ok

def _get_device_token(device_id=DEVICE_LABEL):
    # tested: good for v1.6 but NOT v2.0
    print("Getting device token for " + device_id)
    try:
        resp = requests.get(f"https://industrial.api.ubidots.com/api/v1.6/datasources/{device_id}/tokens", headers=HEADERS).json()
        print(resp["results"][0]["token"])
    except Exception as e:
        print("[ERROR] Error posting, details: {}".format(e))
    return resp["results"][0]["token"]

def _list_devices(token = TOKEN):
    # tested: requires mix of v1.6 and v2.0
    # runs into 'list index out of range' error every time it's ran
    devices = _get_all_devices()
    for device in devices:
        token = _get_device_token(device["id"])
        _validate_token(device["id"], token)

class bcolors:
    # https://stackoverflow.com/questions/287871/how-do-i-print-colored-text-to-the-terminal
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

if __name__ == '__main__':
    # Initialization message
    print("Initializing code...")

    # Prompt the user for the API token
    while True:
        TOKEN = input("Please enter your API token: ")
        if TOKEN:
            break
        else:
            print("API token cannot be empty. Please try again.")

    # Set the headers with the provided token
    HEADERS = {"X-Auth-Token": TOKEN}

    # Call the function with the necessary parameters
    lcs_df = get_type_data(device_type = DEVICE_TYPE,
                  headers=HEADERS,
                  last_values = LAST_VALUES,
                  export_csv = True)

    # Display the dataframe (optional)
    print("Dataframe export complete. Resulting CSV can be found in the current working directory (i.e., 'code').")

    # Inform the user that the window will close and add a delay
    print("The window will close in 10 seconds. Please make a note of any information displayed.")
    time.sleep(10)
r'''
How to execute the script from the terminal:

1. Open your terminal (Command Prompt, PowerShell, or any terminal emulator).
2. Navigate to the directory where your script is located. For example:
    cd C:\Users\AJ-CPU\Documents\GitHub\Ubidots-Python-API-Client-Test\code
3. Activate your virtual environment if necessary. For example:
    activate ubidots_exe
4. Run the script using Python. Make sure you have your virtual environment 
   activated if necessary. The command to run the script is:
    python ubidots_python_api_test_HTTP.py
5. You will be prompted to enter your API token. Enter the token and press Enter.

After following these steps, the script will execute, make the request using the
provided token, and print "Dataframe export complete." once the process is 
finished.
'''