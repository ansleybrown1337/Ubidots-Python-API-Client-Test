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
import requests
import random
import time

# Global variables
ENDPOINT = 'industrial.ubidots.com'
DEVICE_LABEL = 'AWQP_Cercospora_7'
VARIABLE_LABEL = 'Temp (F)'
TOKEN = ''
DELAY = 1 # Delay in seconds

def get_var(url=ENDPOINT, device=DEVICE_LABEL, variable=VARIABLE_LABEL,
            token=TOKEN, last_values=500, start=0, end=1):
    try:
        url = "http://{}/api/v1.6/devices/{}/{}/values/?page_size={}".format(
                                                                    url,
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
        print (req.text)
    except Exception as e:
        print("[ERROR] Error posting, details: {}".format(e))

if __name__ == '__main__':
    while True:
        get_var()
        time.sleep(DELAY)
