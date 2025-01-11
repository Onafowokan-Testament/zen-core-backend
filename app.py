import os

import matplotlib.pyplot as plt
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
    st.set_page_config(
        page_title="Farm-Tech Growth Analysis", page_icon="🌱", layout="wide"
    )

    # Sidebar title and description
    st.sidebar.title("Farm-Tech Growth Monitoring")
    st.sidebar.subheader("Monitor your plant environment efficiently!")

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

    # Show optimal values in Cards
    st.markdown(
        f"""
    <style>
        .card {{
            padding: 20px;
            border-radius: 10px;
            background-color: #e3f9e5;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            margin-bottom: 15px;
        }}
        .card h3 {{
            color: #2d6a4f;
        }}

        .card p{{
            color:  #2d6a4f
        }}
    </style>
    <div class="card">
        <h3>Optimal Temperature Range: {temp_min}°C - {temp_max}°C</h3>
        <p>Ideal temperature range for {plant_name} to thrive.</p>
    </div>
    <div class="card">
        <h3>Optimal Humidity Range: {humidity_min}% - {humidity_max}%</h3>
        <p>Ideal humidity levels for {plant_name} to thrive.</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Fetch sensor data
    st.subheader("Fetching sensor data...")

    sensor_data = fetch_sensor_data()

    # Show sensor data in a modern way (using Card-style layout)
    temperature = (
        f"{sensor_data['temperature']:.2f} °C"
        if sensor_data["temperature"] is not None
        else "No data available"
    )
    humidity = (
        f"{sensor_data['humidity']:.2f}%"
        if sensor_data["humidity"] is not None
        else "No data available"
    )

    st.markdown(
        f"""
        <div class="card">
            <h3>Temperature (°C)</h3>
            <p>{temperature}</p>
        </div>
        <div class="card">
            <h3>Humidity (%)</h3>
            <p>{humidity}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Analyzing sensor data
    st.subheader("Analyzing sensor data...")

    analysis = analyze_data(sensor_data, optimal_values)

    for sensor, result in analysis.items():
        color = "green" if "out of range" not in result else "red"
        st.markdown(
            f"""
        <div style="background-color: {color}; color: white; padding: 10px; border-radius: 10px; margin-bottom: 15px;">
            <h4>{sensor.capitalize()}</h4>
            <p>{result}</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Optionally, add some interactive plots using Matplotlib
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot([20, 25, 30, 35], label="Temperature Variation", color="#4caf50")
    ax.set_title("Temperature Over Time")
    ax.set_xlabel("Time")
    ax.set_ylabel("Temperature (°C)")
    ax.legend()

    st.pyplot(fig)


# Run the Streamlit app
if __name__ == "__main__":
    app()
