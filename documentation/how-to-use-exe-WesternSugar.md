# How to use the .exe and get Ubidots CLS sensor data for UNL delivery
Created by A.J. Brown <br>
Agricultural Data Scientist<br>
19 July 2024

The `ubidots_python_api_test_HTTP.exe` file was created for easy data delivery to University of Lincoln-Nebraska (UNL) collaborators for piping data from the Colorado State University (CSU) Agricultural Water Quality Program (AWQP) cercospora leaf spot (CLS) sensors to the [UNL-based, CLS website dashboard (PHREC)](https://phrec-irrigation.com/#/cls_monitoring) that calculates daily infection values (DIVs) for Western Sugar (WS) agriculturalists and sugar beet producers.

This document describes the procedure for obtaining the necessary data from CSU AWQP CLS sensors, and delivering it to UNL collaborators for display on the PHREC dashboard. It is intended for CSU and WS employees involved in this collaborative effort.

## Step 1: Use Ubidots to obtain GPS data
Login to the AWQP Ubidots Portal here:
https://csuwaterqualitygroup.iot.ubidots.com/

The GPS location can be modified in Ubidots manually. After getting to your device list, use the Ubidots search bar to find each sensor and click on it to open its details.  On the left side of the sensor page, you will find a "Location" section that has three categories, "Mode", "Latitude", and "Longitude".  Ensure that "Mode" is set to "Manual", then copy and paste the correct lat/long values recorded in step one for each sensor. Alternatively, you can iteractively change the location at the top of the page using the map viewer.

An instructional video on how to do so can be [found here](https://www.loom.com/share/1c19825f15bd4a9e90f333233b1f379b?sid=7f25672c-74b6-4239-a016-52274bf71ec6).

The resulting lat/long values can then be recorded for each respective device if this location is correct.

## Step 2: Run `ubidots_python_api_test_HTTP.exe`
The .exe file was built in python to webscrape the CLS device information that is needed for UNL collaborators to add each device to the PHREC dashboard. **The .exe will only work on Windows PC operating systems (i.e., not Mac or Linux).**

Run the .exe file by double clicking it.  A command prompt window should open.  The command prompt will then output a lot of text (i.e., it shows each sensor that it's trying to reach).  The command window will close when complete.  A new CSV file will be found in the same file location as where the .exe file is stored. This CSV file, usually named something like `unl_export_20240719_101718.csv` contains the necessary columns to send to UNL.

All sensors are listed, so select the ones that need to be to delivered to unl and combine them into their own table:

| Name          | rh                  | t                   | Latitude   | Longitude  |
|---------------|---------------------|---------------------|------------|------------|
| WS27-XLU      | 65d6457c7a715d000bf94dc0 | 65d6457d7a715d000c7d068c | 39.962214  | -102.29798 |
| WS25-F2W      | 65d644066eb306000dee50f9 | 65d644067a7226000bcdb493 | 40.088832  | -104.418673|
| WS19-ECW      | 65c3c37648bb6b000e4e9979 | 65c3c377e858cb000eb4367a | 40.290692  | -104.523564|
| WS48-ABS      | 6644f0dd573ffb000ce2b97f | 6644f0ddb921b4000b90b85d | 40.790072  | -105.072431|
| WS26-5KL      | 65d644ba5ee5f8000c3ec157 | 65d644bb7a7226000c15eb7f | 40.130597  | -105.031846|


## Step 3: Select desired sensor data and email to UNL
The last step is to email the consolidated table to UNL.  As of 19 July 2024, the UNL contacts are Xin Qiao (xin.qiao@unl.edu) and Wei-Zhen Liang (wei-zhen.liang@unl.edu)

Copy/paste your consolidated sensor data table and email it to both Xin and Wei-Zhen.  It is also courteous to cc any relevant WS agriculturalists on the email to let them know that their deployed sensors will be online soon.

## Questions?
Please contact A.J. Brown at Ansley.Brown@colostate.edu