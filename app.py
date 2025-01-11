import os

import google.generativeai as genai
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GPT_API_KEY"))

# Sensor and plant data
sensor_pins = {
    "temperature": "V0",
    "humidity": "V1",
}

# Optimal conditions for different plants (example)
optimal_conditions = {
    "pepper": {
        "temperature_range": "25-30°C",
        "humidity_range": "60-75%",
    },
    "groundnut": {
        "temperature_range": "20-28°C",
        "humidity_range": "50-70%",
    },
    "tomato": {
        "temperature_range": "22-28°C",
        "humidity_range": "65-80%",
    },
}


# Function to fetch sensor data from Blynk
def fetch_sensor_data():
    sensor_data = {}
    for sensor, pin in sensor_pins.items():
        try:
            response = requests.get(
                f"{os.getenv('BLYNK_URL')}get?token={os.getenv('BLYNK_TOKEN')}&pin={pin}"
            )
            response.raise_for_status()
            sensor_data[sensor] = float(response.text)
        except Exception:
            sensor_data[sensor] = None
    return sensor_data


# Function to generate a dynamic prompt for analysis with concise output and actionable advice
def generate_dynamic_prompt(plant_name, sensor_data):
    optimal_temp_range = optimal_conditions.get(plant_name, {}).get(
        "temperature_range", "No data"
    )
    optimal_humidity_range = optimal_conditions.get(plant_name, {}).get(
        "humidity_range", "No data"
    )

    temperature = sensor_data.get("temperature", "No data")
    humidity = sensor_data.get("humidity", "No data")

    # Construct a detailed prompt for analysis and suggest actions
    prompt = f"""
    Analyze the environment for growing {plant_name}. 
    The optimal temperature range for {plant_name} is {optimal_temp_range} and the optimal humidity range is {optimal_humidity_range}. 
    The current temperature is {temperature}°C and the current humidity is {humidity}%. 
    Based on these conditions, provide a concise summary of the plant's current environment, followed by actionable advice in the form of short bullet points on what the farmer can do to improve the environment.
    Limit the output to a brief summary and 3-5 actionable steps.
    """

    return prompt


# Function to get AI-generated analysis from Gemini without system role
def get_gpt_analysis(plant_name, sensor_data):
    # Start the conversation with initial user and model messages
    chat = genai.GenerativeModel("gemini-1.5-flash").start_chat(
        history=[
            {"role": "user", "parts": f"Tell me how to care for my {plant_name}."},
        ]
    )

    # Generate dynamic prompt for the selected plant
    prompt = generate_dynamic_prompt(plant_name, sensor_data)

    # Send message to the model and get response
    response = chat.send_message(prompt)
    return response.text


# Streamlit app
def app():
    st.set_page_config(
        page_title="Farm-Tech Growth Analysis", page_icon="🌱", layout="wide"
    )

    # Custom CSS for modern design with green farm-tech theme
    st.markdown(
        """
    <style>
        body {
            background-color: #eaf0e0;
            font-family: 'Arial', sans-serif;
            color: #2c3e50;
        }
        .card {
            background-color: #ffffff;
            padding: 20px;
            margin: 15px 0;
            border-radius: 15px;
            box-shadow: 0px 5px 15px rgba(0, 0, 0, 0.1);
        }
        .header-text {
            color: #2c3e50;
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 10px;
        }
        .subheader-text {
            color: #34495e;
            font-size: 1rem;
            margin-bottom: 20px;
        }
        .button {
            background-color: #27ae60;
            color: white;
            padding: 12px 30px;
            border-radius: 8px;
            font-size: 1rem;
            border: none;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        .button:hover {
            background-color: #2ecc71;
        }
        .card p {
            color: #202124;
        }
        .card h3 {
            color: #1e1e1e;
            font-size: 1.2rem;
            font-weight: 500;
        }
        .optimal-values {
            background-color: #d5f5e3;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
            margin-top: 20px;
        }
        .optimal-values h4 {
            color: #2ecc71;
            font-weight: bold;
        }
        .optimal-values p {
            color: #27ae60;
        }
        .insight-card {
            background-color: #ffffff;
            padding: 20px;
            margin: 20px 0;
            border-radius: 15px;
            box-shadow: 0px 5px 15px rgba(0, 0, 0, 0.1);
            color: #2c3e50;
        }
        .insight-card h3 {
            color: #2c3e50;
            font-weight: bold;
        }
        .sensor-cards {
            display: flex;
            justify-content: space-between;
        }
        .sensor-card {
            flex: 1;
            margin-right: 10px;
        }
        .sensor-card:last-child {
            margin-right: 0;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Sidebar title and description
    st.sidebar.title("Farm-Tech Growth Monitoring")
    st.sidebar.subheader("Monitor your plant environment efficiently!")

    # User input for plant selection
    plant_name = st.selectbox("Choose a plant", ["pepper", "groundnut", "tomato"])

    # Fetch sensor data
    st.subheader("Fetching sensor data...")
    sensor_data = fetch_sensor_data()

    # Show sensor data
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

    # Display optimal conditions in a beautiful card layout
    optimal_temp_range = optimal_conditions.get(plant_name, {}).get(
        "temperature_range", "No data"
    )
    optimal_humidity_range = optimal_conditions.get(plant_name, {}).get(
        "humidity_range", "No data"
    )

    st.markdown(
        f"""
        <div class="optimal-values">
            <h4>Optimal Growth Conditions for {plant_name.title()}</h4>
            <p><strong>Temperature Range:</strong> {optimal_temp_range}</p>
            <p><strong>Humidity Range:</strong> {optimal_humidity_range}</p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # Display sensor data in a single row of two cards
    st.markdown(
        f"""
        <div class="sensor-cards">
            <div class="sensor-card card">
                <h3>Temperature (°C)</h3>
                <p><strong>Sensor Reading:</strong> {temperature}</p>
            </div>
            <div class="sensor-card card">
                <h3>Humidity (%)</h3>
                <p><strong>Sensor Reading:</strong> {humidity}</p>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # Button to generate insight
    if st.button("Generate Insight", key="generate_button"):
        # Get GPT analysis
        st.subheader("Analyzing plant environment ...")
        gpt_analysis = get_gpt_analysis(plant_name, sensor_data)

        # Display the analysis in a styled card with improved readability
        st.markdown(
            f"""
            <div class="insight-card">
                <h3>AI Analysis of Plant Environment</h3>
                <p>{gpt_analysis}</p>
            </div>
        """,
            unsafe_allow_html=True,
        )


# Run the Streamlit app
if __name__ == "__main__":
    app()
