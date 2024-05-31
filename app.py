import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import plotly.express as px

# Add a title and description
st.title('Herbie Sensor Readings')
st.subheader('Welcome to the sensor data dashboard')
st.write('Here you can see the latest sensor readings from the Herbie project.')

# Placeholder for metrics
light_metric = st.empty()
water_metric = st.empty()
soil_moisture_metric = st.empty()
temperature_metric = st.empty()
humidity_metric = st.empty()

# Placeholder for line chart
line_chart_placeholder = st.empty()

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
@st.cache
def fetch_data():
    # Fetch all records from the sheet
    data = sheet.get_all_records()

    # Convert the records to a pandas DataFrame
    df = pd.DataFrame(data)

    df.rename(columns={'TimeString': 'Time'}, inplace=True)

    # Ensure 'TimeString' is datetime and set as index
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

    return df

# Function to calculate differences between the last and new data
def calculate_differences(prev_data, new_data):
    differences = new_data - prev_data
    return differences

# Fetch initial data
prev_data = fetch_data()

# Create real-time line chart
fig_realtime = px.line(prev_data.tail(2000), x=prev_data.index, y=['Light', 'Water', 'Moist', 'Temp', 'Humid'],
                       labels={'value': 'Value', 'index': 'Time'},
                       title='Real-Time Sensor Readings',
                       color_discrete_map={'Light': 'blue', 'Water': 'green', 'Moist': 'red', 'Temp': 'orange', 'Humid': 'purple'},
                       line_dash_sequence=['solid']*5)  # Ensure solid lines for all sensors

# Display line chart
line_chart_placeholder.plotly_chart(fig_realtime, use_container_width=True)

# Update metrics and line chart
def update_metrics_and_chart():
    # Fetch real-time data
    new_data = fetch_data()

    # Calculate differences
    differences = calculate_differences(prev_data, new_data)

    # Update metrics showing differences
    light_metric.metric(label="Light Change", value=differences['Light'].iloc[-1])
    water_metric.metric(label="Water Change", value=differences['Water'].iloc[-1])
    soil_moisture_metric.metric(label="Soil Moisture Change", value=differences['Moist'].iloc[-1])
    temperature_metric.metric(label="Temperature Change", value=differences['Temp'].iloc[-1])
    humidity_metric.metric(label="Humidity Change", value=differences['Humid'].iloc[-1])

    # Update line chart
    fig_realtime = px.line(new_data.tail(2000), x=new_data.index, y=['Light', 'Water', 'Moist', 'Temp', 'Humid'],
                           labels={'value': 'Value', 'index': 'Time'},
                           title='Real-Time Sensor Readings',
                           color_discrete_map={'Light': 'blue', 'Water': 'green', 'Moist': 'red', 'Temp': 'orange', 'Humid': 'purple'},
                           line_dash_sequence=['solid']*5)  # Ensure solid lines for all sensors
    line_chart_placeholder.plotly_chart(fig_realtime, use_container_width=True)

    # Update previous data
    prev_data = new_data

# Execute the update function
update_metrics_and_chart()
