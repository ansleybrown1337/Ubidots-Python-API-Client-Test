import streamlit as st
import os
import sys
from datetime import datetime
from tabulate import tabulate

# Add the 'code' folder to the system path to import the script
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the necessary function from your Python script
from ubidots_python_api_test_HTTP import get_all_type_var_ids_and_location

# Function to format email text
def generate_email_body(df):
    # Generate table in github markdown format
    table_text = tabulate(df, headers="keys", tablefmt="github", showindex=False)
    
    # Email content with proper spacing
    email_body = f"""
Dear Xin and Wei-Zhen,

Please find the selected sensor data for your integration into the UNL CLS Daily Infection Risk Dashboard.

Device Information:
{table_text}

Best regards,
[Your Name]
"""

    return email_body

# Cache the function that fetches the device data to avoid re-running it unnecessarily
@st.cache_data(show_spinner=True)
def fetch_device_data(device_type, headers):
    """Fetch data from Ubidots API and cache the result."""
    return get_all_type_var_ids_and_location(device_type=device_type, headers=headers, unl_export=False)

# Streamlit app code
def main():
    st.title("CSU AWQP Ubidots API Data Retrieval for UNL Delivery")
    # Image under the title
    st.image("https://agsci.colostate.edu/waterquality/wp-content/uploads/sites/160/2024/05/AWQP_horizontalhighres.png", 
             caption="CSU Agricultural Water Quality Program", use_column_width=True)
    st.write("""
        This app allows users to retrieve GPS and variable data from Ubidots devices, 
        and export it for use in the UNL Cercospora Leaf Spot sensor project.
    """)

    # Step 1: Ensure GPS location is correct and set
    st.write("""
        ### Step 1: Use CSU Ubidots to obtain GPS data
        The GPS location of each device can be modified in [CSU Ubidots](https://csuwaterqualitygroup.iot.ubidots.com/) manually.  
        The resulting lat/long values can then be obtained by this tool for each
        respective device if this location is correct and set.

        An instructional video on how to set a location in Ubidots so can be 
        [found here](https://www.loom.com/share/1c19825f15bd4a9e90f333233b1f379b?sid=7f25672c-74b6-4239-a016-52274bf71ec6).             
        """
    )

    # Step 2: Input API token
    st.write("### Step 2: Provide the CSU Ubidots API Key")
    st.write("*Please contact [Ella Stankiewicz](mailto:estankiewicz@westernsugar.com) to obtain the API key.*")
    token = st.text_input("Please enter your Ubidots API token:", type="password")

    if token:
        # Set headers with the provided token
        headers = {"X-Auth-Token": token}
        st.success("API token set! Fetching device data...")

        # Set device type
        device_type = "pile-temp-and-cercospora-monitor"

        try:
            # Use the cached function to fetch data, ensuring it only runs once unless token changes
            df = fetch_device_data(device_type, headers)

            if df.empty:
                st.warning("No devices found. Please check your API token and try again.")
            else:
                st.success("Device data fetched successfully!")
                
                # Filter df columns to only include relevant columns
                df = df[['name', 'rh', 't', 'lat', 'lng']]

                st.write("### Step 3: Select devices")
                
                # Allow users to select devices but do not filter yet
                device_names = df['name'].unique().tolist()  # Get unique device names
                selected_devices = st.multiselect(
                    "Select devices to view using the multi-select dropdown below:", 
                    device_names, 
                    default=None
                )

                # Display the selected devices
                if selected_devices:
                    # Filter the dataframe based on selected devices only after clicking the button
                    filtered_df = df[df['name'].isin(selected_devices)]
                    
                    if filtered_df.empty:
                        st.warning("No data available for the selected devices.")
                    else:
                        # Display filtered data
                        st.write("#### Selected Device Data")
                        st.write(filtered_df)

                        # Button to download the filtered data
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        export_filename = f'unl_export_{timestamp}.csv'

                        # Save the filtered dataframe as CSV
                        filtered_df.to_csv(export_filename, index=False)

                        # Provide a download link for the generated CSV
                        with open(export_filename, "rb") as file:
                            st.download_button(
                                label="Download Filtered CSV",
                                data=file,
                                file_name=export_filename,
                                mime='text/csv'
                            )
                        st.success(f"CSV file '{export_filename}' generated and ready for download!")

                        # Step 4: Instructions for using the app
                        st.markdown("""
                            ### Step 4: Email device information to UNL
                            UNL contacts:
                            - Xin Qiao (xin.qiao@unl.edu)
                            - Wei-Zhen Liang (wei-zhen.liang@unl.edu)
                                    
                            This will allow the UNL team to integrate the data into the UNL
                            [CLS Daily Infection Risk Dashboard](https://phrec-irrigation.com/#/cls_monitoring).
                        """)
                        if st.button("Generate Email to UNL"):
                            email_body_plain = generate_email_body(filtered_df)
                            
                            # Display the email content in a code block for preview
                            st.code(email_body_plain)

                            # URL encode the email body for mailto link
                            email_body_encoded = email_body_plain.replace("\n", "%0A").replace("\t", "%09").replace(" ", "%20")

                            # Create a clickable mailto link
                            mailto_link = f'mailto:xin.qiao@unl.edu,wei-zhen.liang@unl.edu?subject=Device%20Data%20for%20UNL%20CLS%20Dashboard&body={email_body_encoded}'
                            
                            st.markdown(f'[Click here to send email to UNL]({mailto_link})', unsafe_allow_html=True)

                else:
                    st.warning("Please select at least one device to display the data.")

        except Exception as e:
            st.error(f"Error fetching device data: {e}")

if __name__ == "__main__":
    main()
