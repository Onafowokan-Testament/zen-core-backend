import os

import google.generativeai as genai
import requests
import streamlit as st
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GPT_API_KEY"))

# Sensor and plant data
sensor_pins = {
    "temperature": "V0",
    "humidity": "V1",
}

# Optimal conditions for different plants
optimal_conditions = {
    "pepper": {"temperature_range": "25-30°C", "humidity_range": "60-75%"},
    "groundnut": {"temperature_range": "20-28°C", "humidity_range": "50-70%"},
    "tomato": {"temperature_range": "22-28°C", "humidity_range": "65-80%"},
}

# Emojis for weather conditions
weather_emojis = {
    "Sunny": "☀️",
    "Partly cloudy": "⛅",
    "Cloudy": "☁️",
    "Rain": "🌧️",
    "Thunderstorm": "⛈️",
    "Snow": "❄️",
    "Clear": "🌙",
    "Haze": "🌫️",
    "Fog": "🌁",
    "Mist": "🌫️",
}


# Fetch sensor data from Blynk
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


# Fetch weather data from WeatherAPI
def fetch_weather(lga):
    try:
        # Use the LGA as the location in the API request
        url = f"http://api.weatherapi.com/v1/current.json?key={os.getenv('WEATHER_API_KEY')}&q={lga}&aqi=no"
        response = requests.get(url)
        response.raise_for_status()
        weather_data = response.json()
        condition = weather_data["current"]["condition"]["text"]
        wind_speed = weather_data["current"]["wind_kph"]
        precipitation = weather_data["current"]["precip_mm"]
        humidity = weather_data["current"]["humidity"]
        alert = (
            weather_data.get("alerts", {})
            .get("alert", [{}])[0]
            .get("desc", "No alerts.")
        )
        return {
            "temperature": weather_data["current"]["temp_c"],
            "condition": condition,
            "emoji": weather_emojis.get(condition, "🌤️"),
            "wind_speed": wind_speed,
            "precipitation": precipitation,
            "humidity": humidity,
            "alert": alert,
        }
    except Exception as e:
        return {"error": str(e)}


# Analyze image with Gemini AI
def analyze_image_with_gemini(image):
    model = genai.GenerativeModel(model_name="gemini-1.5-pro")
    prompt = (
        "Analyze the plant image and provide the following:\n"
        "1. Name of the disease visible on the plant\n"
        "2. What causes this disease\n"
        "3. Give just 2 major actions to take to treat or prevent the disease."
    )
    response = model.generate_content([prompt, image])
    return response.text


# Analyze environment with Gemini AI
def analyze_environment_with_gemini(temperature, humidity, plant_name):
    model = genai.GenerativeModel(model_name="gemini-1.5-pro")
    temp_range = optimal_conditions[plant_name]["temperature_range"]
    humidity_range = optimal_conditions[plant_name]["humidity_range"]
    prompt = (
        f"Analyze environment for {plant_name}:\n"
        f"- Current temperature: {temperature}°C\n"
        f"- Current humidity: {humidity}%\n"
        f"- Optimal temperature: {temp_range}\n"
        f"- Optimal humidity: {humidity_range}\n"
        "Provide actionable insights."
    )
    response = model.generate_content([prompt])
    return response.text


# Streamlit App
def app():
    # Set up page aesthetics
    st.set_page_config(
        page_title="🌱 Farm-Tech Monitoring", page_icon="🌿", layout="wide"
    )

    # Custom CSS for styling
    st.markdown(
        """
    <style>
    body {
        background-color: #ffffff;
        font-family: 'Arial', sans-serif;
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        margin: 0;
    }
    .container {
        width: 90%;
        max-width: 1200px;
    }
    .card {
        background-color: white;
        color: black;
        border-radius: 8px;
        padding: 15px;
        margin: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        height: auto;
        font-size: 14px;
        width: 100%;
        display: inline-block;
        margin-bottom: 20px;
    }
    .header {
        text-align: center;
        margin-bottom: 40px;
    }
    .two-column > div {
        padding: 20px;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Header
    st.markdown(
        "<h1 class='header'>🌱 Farm-Tech Growth Monitoring</h1>", unsafe_allow_html=True
    )

    # Weather data section - FIRST THING NOW
    st.markdown("<h3>Weather Data</h3>", unsafe_allow_html=True)
    lga = st.text_input("Enter LGA for weather details", "Lagos")
    weather_data = fetch_weather(lga)
    if "error" not in weather_data:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(
                f"<div class='card'>"
                f"<b>Temperature:</b> {weather_data['temperature']}°C</div>",
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f"<div class='card'>"
                f"<b>Condition:</b> {weather_data['condition']} {weather_data['emoji']}</div>",
                unsafe_allow_html=True,
            )
        with col3:
            st.markdown(
                f"<div class='card'>"
                f"<b>Humidity:</b> {weather_data['humidity']}%</div>",
                unsafe_allow_html=True,
            )
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                f"<div class='card'>"
                f"<b>Wind Speed:</b> {weather_data['wind_speed']} kph</div>",
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f"<div class='card'>"
                f"<b>Precipitation:</b> {weather_data['precipitation']} mm</div>",
                unsafe_allow_html=True,
            )

        # Display alert if any
        if weather_data["alert"] != "No alerts.":
            st.markdown(
                f"<div class='card' style='background-color: #ffcccb;'>"
                f"<b>Weather Alert:</b> {weather_data['alert']}</div>",
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            f"<div class='card'>{weather_data['error']}</div>", unsafe_allow_html=True
        )

    # Container for the main content
    with st.container():
        # Step 1: Plant Selection
        plant_name = st.selectbox(
            "Choose a plant to monitor",
            ["pepper", "groundnut", "tomato"],
            key="plant_selection",
        )

        # Optimal conditions in two-column layout with smaller cards
        st.markdown("<h3>Optimal Conditions</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                f"<div class='card'>"
                f"<b>Temperature:</b> {optimal_conditions[plant_name]['temperature_range']}</div>",
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f"<div class='card'>"
                f"<b>Humidity:</b> {optimal_conditions[plant_name]['humidity_range']}</div>",
                unsafe_allow_html=True,
            )

        # Real-time sensor data in cards
        st.markdown("<h3>Real-Time Sensor Data</h3>", unsafe_allow_html=True)
        sensor_data = fetch_sensor_data()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(
                f"<div class='card'>"
                f"<b>Temperature:</b> {sensor_data.get('temperature', 'N/A')}°C</div>",
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f"<div class='card'>"
                f"<b>Humidity:</b> {sensor_data.get('humidity', 'N/A')}%</div>",
                unsafe_allow_html=True,
            )

        # Environmental analysis in card
        if sensor_data.get("temperature") and sensor_data.get("humidity"):
            if st.button("Analyze Environment"):
                environment_analysis = analyze_environment_with_gemini(
                    sensor_data["temperature"], sensor_data["humidity"], plant_name
                )
                st.markdown(
                    f"<div class='card'>"
                    f"<b>Environment Analysis:</b><br>{environment_analysis}</div>",
                    unsafe_allow_html=True,
                )

        # Image analysis in full-width card
        st.markdown("<h3>Plant Image Analysis</h3>", unsafe_allow_html=True)
        uploaded_image = st.file_uploader(
            "Upload an image of your plant", type=["jpg", "jpeg", "png"]
        )
        if uploaded_image is not None:
            img = Image.open(uploaded_image)
            st.image(img, caption="Uploaded Plant Image", use_container_width=True)
            if st.button("Analyze Image"):
                image_analysis = analyze_image_with_gemini(img)
                st.markdown(
                    f"<div class='card' style='width: 100%;'>"
                    f"<b>Image Analysis:</b><br>{image_analysis}</div>",
                    unsafe_allow_html=True,
                )


if __name__ == "__main__":
    app()
    app()
