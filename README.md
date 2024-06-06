# Ubidots Python API Client Test
By A.J. Brown <br/>
24 Aug 2022 <br/>
ansleybrown1337@gmail.com <br/>
Updated: 4 June 2024

## Description

A Python script that downloads ubidots data for streamlined data
analysis.

## Code

File 1, "ubidots_python_api_test.py", uses the Ubidots API Client module.

File 2, "ubidots_python_api_test_HTTP.py" uses HTTP protocols. **(preferred method)**

## Documentation

In the documentation folder, you will find instructions on how to run the code
via IPython development environment OR terminal (preferred).

### How to exectute via terminal
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
finished.

## Output

The output folder contains the data downloaded from Ubidots, which has been cleaned and made ready for providing necessary information to UNL collaborators for the cercospora sensor project between AWQP and Western Sugar.
