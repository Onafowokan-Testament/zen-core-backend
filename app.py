import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

BLYNK_TOKEN = os.getenv("BLYNK_TOKEN")
BLYNK_URL = os.getenv("BLYNK_URL")

sensor_pins = {
    "temperature": "V0",
    "humidity": "V1",
}

# Dictionary of plants and their optimal values
plants_requirements = {
    "pepper": {
        "temperature": {"min": 24, "max": 30},
        "humidity": {"min": 60, "max": 70},
    },
    "groundnut": {
        "temperature": {"min": 25, "max": 30},
        "humidity": {"min": 40, "max": 60},
    },
    "tomato": {
        "temperature": {"min": 20, "max": 25},
        "humidity": {"min": 60, "max": 70},
    },
}


# Function to get optimal values for the plant
def get_optimal_values_for_plant(plant_name: str):
    plant_data = plants_requirements.get(plant_name)
    if plant_data:
        return plant_data
    else:
        return {
            "temperature": {"min": 20, "max": 30},
            "humidity": {"min": 50, "max": 70},
        }


# Function to fetch sensor data from Blynk
def fetch_sensor_data():
    sensor_data = {}
    for sensor, pin in sensor_pins.items():
        try:
            response = requests.get(f"{BLYNK_URL}get?token={BLYNK_TOKEN}&pin={pin}")
            response.raise_for_status()
            sensor_data[sensor] = float(response.text)
        except Exception:
            sensor_data[sensor] = None
    return sensor_data


# Function to analyze sensor data
def analyze_data(sensor_data, optimal_values):
    analysis_results = {}
    for sensor, value in sensor_data.items():
        if value is None:
            analysis_results[sensor] = "No data available"
            continue

        optimal_range = optimal_values.get(sensor)
        if optimal_range:
            if optimal_range["min"] <= value <= optimal_range["max"]:
                analysis_results[sensor] = (
                    f"{sensor} is within the optimal range ({optimal_range['min']}–{optimal_range['max']})."
                )
            else:
                analysis_results[sensor] = (
                    f"{sensor} is out of range! Current value: {value}. "
                    f"Expected range: {optimal_range['min']}–{optimal_range['max']}."
                )
        else:
            analysis_results[sensor] = f"No optimal range defined for {sensor}."
    return analysis_results


# Streamlit app
def app():
    st.title("Plant Growth Analysis App")

    # User input for plant selection
    plant_name = st.selectbox("Choose a plant", ["pepper", "groundnut", "tomato"])

    st.subheader(f"Fetching optimal values for {plant_name}...")

    # Fetch optimal values
    optimal_values = get_optimal_values_for_plant(plant_name)

    # Display optimal temperature and humidity using sliders for better interactivity
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Temperature Range (°C)**")
        temp_min = st.slider(
            "Min Temperature",
            min_value=15,
            max_value=35,
            value=optimal_values["temperature"]["min"],
        )
        temp_max = st.slider(
            "Max Temperature",
            min_value=15,
            max_value=35,
            value=optimal_values["temperature"]["max"],
        )

    with col2:
        st.write("**Humidity Range (%)**")
        humidity_min = st.slider(
            "Min Humidity",
            min_value=0,
            max_value=100,
            value=optimal_values["humidity"]["min"],
        )
        humidity_max = st.slider(
            "Max Humidity",
            min_value=0,
            max_value=100,
            value=optimal_values["humidity"]["max"],
        )

    # Show optimal values in cards using columns
    st.write(f"Optimal temperature range: {temp_min}°C - {temp_max}°C")
    st.write(f"Optimal humidity range: {humidity_min}% - {humidity_max}%")

    # Fetch sensor data
    st.subheader("Fetching sensor data...")

    sensor_data = fetch_sensor_data()

    # Display sensor data in cards (using columns)
    st.write("### Sensor Data:")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f"""
            <div style="padding: 10px; background-color: #f0f0f5; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h5 style="color:green">Temperature (°C)</h5>
                <p style="font-size: 24px; color: {'green' if sensor_data['temperature'] and temp_min <= sensor_data['temperature'] <= temp_max else 'red'};">
                    {sensor_data['temperature']:.2f}°C
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div style="padding: 10px; background-color: #f0f0f5; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h5 style="color:green">Humidity (%)</h5>
                <p style="font-size: 24px; color: {'green' if sensor_data['humidity'] and humidity_min <= sensor_data['humidity'] <= humidity_max else 'red'};">
                    {sensor_data['humidity']:.2f}%
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Analyzing sensor data
    st.subheader("Analyzing sensor data...")

    analysis = analyze_data(sensor_data, optimal_values)

    # Display analysis results with colored labels
    st.write("### Analysis:")
    for sensor, result in analysis.items():
        if "out of range" in result:
            st.markdown(f"**{sensor.capitalize()}:** 🚨 {result}")
        else:
            st.markdown(f"**{sensor.capitalize()}:** ✅ {result}")


# Run the Streamlit app
if __name__ == "__main__":
    app()
