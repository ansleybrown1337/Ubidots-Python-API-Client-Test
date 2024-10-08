# Ubidots Python API Client Test
## Branch: Low-Cost IoT Sampler Data Download
By A.J. Brown <br/>
8 Oct 2024 <br/>
Ansley.Brown@colostate.edu

![sugarbeet image](./figs/lcs.jpg)
*Image of the AWQP-developed Low-Cost, IoT Sampler deployed near Fruita, CO.*

## Description

A Python script that downloads Ubidots data via API for streamlined data
analysis.

The CSU Ag Water Quality Program (AWQP) has developed a [low-cost, internet of things (IoT) sampler](https://github.com/CSU-Agricultural-Water-Quality-Program/low-cost-iot-water-sampler) for use in water quality monitoring (henceforth, "LCS"). This sampler is deployed in the field and collects water samples at regular intervals. The data from the LCS is uploaded to Ubidots, a cloud-based data management platform, where it can be accessed and analyzed.

This script is designed to download data from Ubidots using the Ubidots API. The script allows users to specify the device type (in this case, the LCS) and date range for the data they want to download. The script then makes a request to the Ubidots API, retrieves the data, and saves it to a CSV file for archiving and/or further analysis.

## Code

File 1, "ubidots_python_api_test.py", uses the Ubidots API Client module.

File 2, "ubidots_python_api_test_HTTP.py" uses HTTP protocols. **(preferred method)**

## Documentation

In the [documentation folder](./documentation/), you will find instructions on how to run the code via IPython development environment OR terminal (preferred).

### How to Run

How to execute the script from the terminal:

1. Open your terminal (Command Prompt, PowerShell, or any terminal emulator).
2. Navigate to the directory where your script is located. For example:

    `cd C:\Users\AJ-CPU\Documents\GitHub\Ubidots-Python-API-Client-Test\code`
    
3. Activate your virtual environment if necessary. For example:

    `activate playground2`

4. Run the script using Python. Make sure you have your virtual environment 
   activated if necessary. The command to run the script is:

    `python ubidots_python_api_test_HTTP.py`

5. You will be prompted to enter your API token. 

    `Please enter your API token:`

    Enter the token and press Enter.

After following these steps, the script will execute, make the request using the
provided token, and print "Dataframe export complete." once the process is 
finished. The resulting CSV file will contain a list of all CLS sensor device types on Ubidots

## Output

The output folder contains the data downloaded from Ubidots, which will contain all data from all LCS devices in the specified date range. The data is saved in a CSV file format.

## Contact
For more information on this code, or to learn more about the LCS project, please contact me at Ansley.Brown@colostate.edu or visit the AWQP website [here](https://www.csuagwaterquality.com/).
