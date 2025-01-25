import base64
import os

import google.generativeai as genai
import requests
import streamlit as st
from dotenv import load_dotenv
from googletrans import Translator
from PIL import Image

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GPT_API_KEY"))

# Sensor and plant data
sensor_pins = {
    "temperature": "V0",
    "soil_moisture": "V1",
    "humidity": "V2",
    "fertilizer_pump": "V3",
    "irrigation_pump": "V4",
}
optimal_conditions = {
    "pepper": {
        "temperature": (25, 30),
        "soil_moisture": (50, 70),
        "humidity": (60, 75),
    },
    "groundnut": {
        "temperature": (20, 28),
        "soil_moisture": (40, 60),
        "humidity": (50, 70),
    },
    "tomato": {
        "temperature": (22, 28),
        "soil_moisture": (60, 80),
        "humidity": (65, 80),
    },
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

# Translator setup
translator = Translator()


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
        url = f"http://api.weatherapi.com/v1/current.json?key={os.getenv('WEATHER_API_KEY')}&q={lga}&aqi=no"
        response = requests.get(url)
        response.raise_for_status()
        weather_data = response.json()
        condition = weather_data["current"]["condition"]["text"]
        return {
            "temperature": weather_data["current"]["temp_c"],
            "condition": condition,
            "emoji": weather_emojis.get(condition, "🌤️"),
            "humidity": weather_data["current"]["humidity"],
        }
    except Exception as e:
        return {"error": str(e)}


# Translate text using Google Translator
def translate_text(text, language):
    lang_codes = {"English": "en", "Yoruba": "yo", "Igbo": "ig", "Hausa": "ha"}
    target_lang = lang_codes.get(language, "en")
    return translator.translate(text, dest=target_lang).text


# Control pumps through Blynk
def control_pump(pump_pin):
    try:
        requests.get(
            f"{os.getenv('BLYNK_URL')}update?token={os.getenv('BLYNK_TOKEN')}&pin={pump_pin}&value=1"
        )
        return "Pump activated successfully."
    except Exception as e:
        return str(e)


# Soil analysis using Gemini
def analyze_soil(sensor_data, language):
    prompt = f"Analyze the soil with temperature={sensor_data.get('temperature')}°C, soil moisture={sensor_data.get('soil_moisture')}%, and humidity={sensor_data.get('humidity')}%. Identify any issue, its possible cause, and suggest one solution in {language}."
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)
    return response.text if response.text else "Analysis failed."


# Plant image analysis using Gemini
def analyze_plant(image_path, language):
    with open(image_path, "rb") as img_file:
        img_content = base64.b64encode(img_file.read()).decode("utf-8")
    prompt = f" Analyze this plant image and summarize your findings:Identify the disease (if any) affecting the plant.State one possible cause of the disease.Recommend a solution (includin what can be used to treat it).. Provide the response in {language}."
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(
        [{"mime_type": "image/jpeg", "data": img_content}, prompt]
    ).text
    return response if response else "Analysis failed."


# Reusable function to render cards
def render_card(title, content):
    return f"""
    <div style="
        background-color: white; 
        color: black; 
        border: 2px solid black; 
        border-radius: 10px; 
        padding: 20px; 
        margin-bottom: 20px;
        box-shadow: 5px 5px 15px rgba(0, 0, 0, 0.3);
    ">
        <h3 style="text-align: center;">{title}</h3>
        <p style="text-align: center;">{content}</p>
    </div>
    """


# Streamlit App
def app():
    st.set_page_config(
        page_title="🌱 Zen-Core-Tech Monitoring", page_icon="🌿", layout="wide"
    )

    # Language selection modal
    language = st.sidebar.selectbox(
        "Choose your language", ["English", "Yoruba", "Igbo", "Hausa"]
    )

    # Function to translate all text dynamically
    def t(text):
        return translate_text(text, language)

    # Title
    st.markdown(
        f"<h1 style='text-align: center;'>{t('🌱 Zen Core Tech Growth Monitoring')}</h1>",
        unsafe_allow_html=True,
    )

    # Weather Data Section
    lga = st.text_input(t("Enter LGA for weather details"), "Lagos")
    weather_data = fetch_weather(lga)
    if "error" not in weather_data:
        # Display weather data in 3 columns
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(
                render_card(
                    t("Temperature"),
                    f"<b>{t('Temperature')}:</b> {weather_data['temperature']}°C",
                ),
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                render_card(
                    t("Weather Condition"),
                    f"<b>{t('Condition')}:</b> {t(weather_data['condition'])} {weather_data['emoji']}",
                ),
                unsafe_allow_html=True,
            )
        with col3:
            st.markdown(
                render_card(
                    t("Humidity"),
                    f"<b>{t('Humidity')}:</b> {weather_data['humidity']}%",
                ),
                unsafe_allow_html=True,
            )
    else:
        st.error(t(weather_data["error"]))

    # Optimal Conditions Section
    plant_name = st.selectbox(
        t("Choose a plant to monitor"), ["pepper", "groundnut", "tomato"]
    )
    optimal = optimal_conditions[plant_name]

    # Display optimal conditions in 3 columns
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            render_card(
                t(f"Optimal {t('Temperature')} for {plant_name.capitalize()}"),
                f"<b>{t('Temperature')}:</b> {optimal['temperature'][0]}°C - {optimal['temperature'][1]}°C",
            ),
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            render_card(
                t(f"Optimal {t('Soil Moisture')} for {plant_name.capitalize()}"),
                f"<b>{t('Soil Moisture')}:</b> {optimal['soil_moisture'][0]}% - {optimal['soil_moisture'][1]}%",
            ),
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            render_card(
                t(f"Optimal {t('Humidity')} for {plant_name.capitalize()}"),
                f"<b>{t('Humidity')}:</b> {optimal['humidity'][0]}% - {optimal['humidity'][1]}%",
            ),
            unsafe_allow_html=True,
        )

    # Real-Time Sensor Data Section
    sensor_data = fetch_sensor_data()
    st.markdown(
        render_card(
            t("Temperature"),
            f"<b>{t('Temperature')}:</b> {sensor_data.get('temperature')}°C",
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        render_card(
            t("Soil Moisture"),
            f"<b>{t('Soil Moisture')}:</b> {sensor_data.get('soil_moisture')}%",
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        render_card(
            t("Humidity"), f"<b>{t('Humidity')}:</b> {sensor_data.get('humidity')}%"
        ),
        unsafe_allow_html=True,
    )

    # Soil Analysis Button
    if st.button(t("Analyze Soil")):
        soil_analysis = analyze_soil(sensor_data, language)
        st.markdown(
            render_card(t("Soil Analysis"), soil_analysis), unsafe_allow_html=True
        )

    # Pump Control Section
    st.markdown(f"### {t('Pump Control')}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button(t("Activate Irrigation")):
            message = control_pump(sensor_pins["irrigation_pump"])
            st.success(t(message))
    with col2:
        if st.button(t("Activate Fertigation")):
            message = control_pump(sensor_pins["fertilizer_pump"])
            st.success(t(message))

    # Plant Image Analysis Section
    uploaded_image = st.file_uploader(
        t("Upload an image of your plant"), type=["jpg", "jpeg", "png"]
    )
    if uploaded_image:
        img = Image.open(uploaded_image)
        st.image(img, caption=t("Uploaded Plant Image"), use_column_width=True)
        if st.button(t("Analyze Plant")):
            img_path = f"temp_image.{uploaded_image.type.split('/')[-1]}"
            img.save(img_path)
            plant_analysis = analyze_plant(img_path, language)
            os.remove(img_path)
            st.markdown(
                render_card(t("Plant Analysis"), plant_analysis), unsafe_allow_html=True
            )


if __name__ == "__main__":
    app()
