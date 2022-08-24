'''
Ubidots-Python-API-Client-Test-HTTP
By A.J. Brown
24 Aug 2022

Help doc for HTTP and Ubidots:
https://docs.ubidots.com/v1.6/reference/get-variable-data
https://industrial.api.ubidots.com/api/v1.6/devices/<device_label>/<variable_label>/values


This script is designed to pull data from Ubidots servers for streamlined data
analysis. This initial test script will use low-cost temperature and relative
humidity sensors deployed in sugar beet fields to monitor cercospora risk.
'''
import pandas as pd
import requests
import random
import time

from io import StringIO

# Master device name dictionary with API labels
deviceID_dict = {'AWQP_Cercospora_7':'e00fce68e24f0a8925c92b4b',
                 'AWQP_Cercospora_4':'e00fce680eb2a2c6230fd025',
                 'AWQP_Cercospora_3':'e00fce6811c5d10c70de529b',
                 'AWQP_Cercospora_2':'e00fce68b726e54b0dda1a5d'}
                 
# Global variables
ENDPOINT = 'industrial.api.ubidots.com'
DEVICE_NAME  = 'AWQP_Cercospora_7'
DEVICE_LABEL = deviceID_dict[DEVICE_NAME]
VARIABLE_LABEL = 't' # temp. in celcius
TOKEN = '' # Place API token here
HEADERS = {"X-Auth-Token": TOKEN}
DELAY = 1 # Delay in seconds

def get_var(url=ENDPOINT, device=DEVICE_LABEL, variable=VARIABLE_LABEL,
            token=TOKEN, last_values=500):
    try:
        url = "http://{}/api/v1.6/devices/{}/{}/values/"\
              "?page_size={}".format(url,
                                     device,
                                     variable,
                                     last_values)
        #url = http://{}/api/v1.6/devices/{}/{}/values/?page_size={}&format=csv
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
        #print("[INFO] Results:")
        print (req.text)
    except Exception as e:
        print("[ERROR] Error posting, details: {}".format(e))
    return req.text

def get_var_df(url=ENDPOINT, device=DEVICE_LABEL, variable=VARIABLE_LABEL,
            token=TOKEN, last_values=500):
    try:
        url = "http://{}/api/v1.6/devices/{}/{}/values/"\
              "?page_size={}&format=csv".format(url,
                                                device,
                                                variable,
                                                last_values)
        #url = http://{}/api/v1.6/devices/{}/{}/values/?page_size={}&format=csv
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
        print("[INFO] Results:")
        #print (req.text)
    except Exception as e:
        print("[ERROR] Error posting, details: {}".format(e))

    return pd.read_csv(StringIO(req.text), sep=',')

def validate_token(device_id=DEVICE_LABEL, token=TOKEN):
    print("Validating token for " + device_id)

    headers = {
        "X-Auth-Token": token
    }

    resp = requests.get(f"https://industrial.ubidots.com/api/v2.0/devices/{device_id}/variables/", headers=headers)

    if (resp.ok):
        print(f"Token {token} for {device_id} validated.")
    else:
        print(f"Token {token} for {device_id} failed validation with {resp.status_code}")

    return resp.ok

def get_device_token(device_id=DEVICE_LABEL):
    print("Getting device token for " + device_id)

    resp = requests.get(f"https://industrial.api.ubidots.com/api/v1.6/datasources/{device_id}/tokens", headers=HEADERS).json()

    return resp["results"][0]["token"]

def get_all_devices():
    devices = []

    next = "https://industrial.api.ubidots.com/api/v2.0/devices/"

    while next:
        print("Making request to " + next)
        data = requests.get(next, headers=HEADERS).json()
        next = data["next"]
        devices.extend(data["results"])

    return devices

def list_devices(token = TOKEN):
    devices = get_all_devices()
    for device in devices:
        token = get_device_token(device["id"])
        validate_token(device["id"], token)

if __name__ == '__main__':
    while True:
        get_var()
        time.sleep(DELAY)
