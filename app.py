import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import plotly.express as px
import time
from PIL import Image
import webview

# Add an image to the top of Streamlit app
st.image('mqdc-idyllias-logo.png', use_column_width=True)

# Add a title to Streamlit app
st.title('Herbie Sensor Readings')
st.subheader('Welcome to the sensor data dashboard')
st.write('Here you can see the latest sensor readings from the Herbie project.')

# Path to JSON key file
SERVICE_ACCOUNT_FILE = 'herbie_key.json'

# Define the scope
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Authenticate with the JSON key file
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

# Open the Google Sheet by name
spreadsheet = client.open("HerbieData")

# Select the specific sheet within the Google Sheet
sheet = spreadsheet.worksheet("Forestias-0001")

# Function to fetch data from Google Sheet and preprocess it
def fetch_data():
    # Fetch all records from the sheet
    data = sheet.get_all_records()

    # Convert the records to a pandas DataFrame
    df = pd.DataFrame(data)

    # Rename columns to match desired names
    df.rename(columns={'TimeString': 'Time', 'Temp': 'Temperature', 'Moist': 'Soil Moisture', 'Humid': 'Humidity'}, inplace=True)

    # Ensure 'Time' is datetime and set as index
    df['Time'] = pd.to_datetime(df['Time'])
    df.set_index('Time', inplace=True)

    # Drop unwanted columns
    unwanted_columns = ['Herbie_ID']
    df.drop(columns=unwanted_columns, inplace=True, errors='ignore')

    # Select data starting from index 17302 (if exists)
    if len(df) > 17302:
        df = df.iloc[17302:]

    # Fill NaN values with 0
    df = df.fillna(0)

    # Convert all columns to numeric
    df = df.apply(pd.to_numeric, errors='coerce')

    print("DataFrame columns after renaming and processing:", df.columns)

    return df

# Function to create line chart
def create_line_chart(df, title):
    fig = px.line(df, x=df.index, y=['Light', 'Water', 'Soil Moisture', 'Temperature', 'Humidity'],
                  labels={'value': 'Value', 'index': 'Time'},
                  title=title,
                  color_discrete_map={'Light': 'blue', 'Water': 'green', 'Soil Moisture': 'red', 'Temperature': 'orange', 'Humidity': 'purple'},
                  line_dash_sequence=['solid']*5)  # Ensure solid lines for all sensors
    return fig

# Create placeholders for metrics and line charts
metric_placeholder = st.empty()  # Placeholder for metrics
realtime_placeholder = st.empty()
hourly_placeholder = st.empty()

# Continuous loop to update metrics and line charts
while True:
    # Fetch real-time data
    df = fetch_data()

    if not df.empty:
        # Check if all required columns are present
        required_columns = ["Light", "Water", "Soil Moisture", "Temperature", "Humidity"]
        if all(col in df.columns for col in required_columns):
            # Get the latest values
            latest_data = df.iloc[-1]
            previous_data = df.iloc[-2]

            # Display metrics for the latest values and their changes
            with metric_placeholder.container():
                st.metric(label="Light", value=latest_data["Light"], delta=latest_data["Light"] - previous_data["Light"])
                st.metric(label="Water", value=latest_data["Water"], delta=latest_data["Water"] - previous_data["Water"])
                st.metric(label="Soil Moisture", value=latest_data["Soil Moisture"], delta=latest_data["Soil Moisture"] - previous_data["Soil Moisture"])
                st.metric(label="Temperature", value=latest_data["Temperature"], delta=latest_data["Temperature"] - previous_data["Temperature"])
                st.metric(label="Humidity", value=latest_data["Humidity"], delta=latest_data["Humidity"] - previous_data["Humidity"])

        # Create real-time line chart
        fig_realtime = create_line_chart(df.tail(2000), 'Real-Time Sensor Readings')
        realtime_placeholder.plotly_chart(fig_realtime, use_container_width=True)

        # Resample data to hourly intervals and calculate the mean value
        df_hourly_avg = df.resample('H').mean()

        # Create hourly line chart
        fig_hourly = create_line_chart(df_hourly_avg, 'Average Hourly Sensor Readings')
        hourly_placeholder.plotly_chart(fig_hourly, use_container_width=True)

    # Pause briefly before fetching new data and updating the charts
    time.sleep(5)  # Adjust the pause duration as needed

def reload(window):
    while True:
        time.sleep(5)
        window.load_url('idyllias-demo.streamlit.app/')
        
if __name__ == '__main__':
    window = webview.create_window('Herbie', 'idyllias-demo.streamlit.app/')

    webview.start(reload, window, http_server=True)
