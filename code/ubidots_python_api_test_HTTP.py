'''
Ubidots-Python-API-Client-Test-HTTP
By A.J. Brown
24 Aug 2022
Updated: 22 Nov 2022

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
import pandas as pd
import requests
import random
import time
from functools import reduce
from io import StringIO

# Global variables
ENDPOINT = 'industrial.api.ubidots.com'
DEVICE_NAME  = '' # must manually define using ubidots 'name' device attribute
DEVICE_LABEL = '' # must manually define using ubidots 'id' device attribute
VARIABLE_LABEL = '' # must manually define using ubidots 'id' variable attribute
TOKEN = '' # Place API token here
HEADERS = {"X-Auth-Token": TOKEN} # must manually change after defining TOKEN
DELAY = 1 # Delay in seconds

def get_type_data(device_type = 'pile-temp-and-cercospora-monitor',
                    # other type: 'low-cost-water-sampler'
                  last_values = 5000,
                  token = TOKEN):
    # get list of all devices containing only name, id, and properties
    device_df = get_all_devices_df()[['name','id','properties']]
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
                             token=token)
        df['name'] = name
        dfs.append(df)

    return pd.concat(dfs).reset_index(drop=True)

def get_device_data(device_id=DEVICE_LABEL, last_values=5000, token=TOKEN):
    '''
    Collects all variable data from specified device and returns DataFrame
    with variables as columns, all merged by timestamp.
    '''
    dfs = []
    for i in get_device_vars_df(device_id=device_id)['id']:
        print(i)
        df = get_var_df(device=device_id,
                        variable=i,
                        last_values=last_values,
                        token=token)
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

def get_var_df(url=ENDPOINT, device=DEVICE_LABEL, variable=VARIABLE_LABEL,
            token=TOKEN, last_values=5000):
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
              "?page_size={}&format=csv".format(url,
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

    return pd.read_csv(StringIO(req.text), sep=',')

def get_all_devices_df():
    #tested: good for v2.0
    df = pd.DataFrame(_get_all_devices())
    print('Done.')
    return df

def get_device_vars_df(device_id=DEVICE_LABEL):
    # tested: good for v2.0
    var_df = pd.DataFrame(_get_device_vars(device_id=device_id))
    device_name = var_df.device[0]['name']
    print(f'{bcolors.OKCYAN}Variable dataframe returned for device name:\
            {device_name}{bcolors.ENDC}')
    return var_df

def _get_all_devices():
    # tested: good for v2.0
    devices = []
    next = "https://industrial.api.ubidots.com/api/v2.0/devices/"
    while next:
        print("Making request to " + next)
        data = requests.get(next, headers=HEADERS).json()
        next = data["next"]
        devices.extend(data["results"])
    return devices

def _get_device_vars(device_id=DEVICE_LABEL):
    # tested: good for v2.0
    var_list = []
    next = f"https://industrial.api.ubidots.com/api/v2.0/devices/{device_id}/variables"
    while next:
        print("Making request to " + next)
        data = requests.get(next, headers=HEADERS).json()
        next = data["next"]
        var_list.extend(data["results"])
    return var_list

def _get_var(url=ENDPOINT, device=DEVICE_LABEL, variable=VARIABLE_LABEL,
            token=TOKEN, last_values=5000):
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
    while True:
        get_var_df()
        time.sleep(DELAY)
