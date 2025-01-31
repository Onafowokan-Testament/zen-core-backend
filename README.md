# Zen-Core-Tech Growth Monitoring 🌱

Welcome to the **Zen-Core-Tech Growth Monitoring** application! This Streamlit-based tool is designed to help farmers and agricultural enthusiasts monitor and optimize plant growth conditions. By integrating real-time sensor data, weather information, and AI-powered analysis, this app provides actionable insights to ensure your plants thrive.

---

## Features

- **Real-Time Sensor Data**: Monitor temperature, soil moisture, and humidity from connected sensors.
- **Weather Integration**: Fetch real-time weather data for your local government area (LGA).
- **Optimal Conditions**: View ideal growth conditions for selected plants (pepper, groundnut, tomato).
- **Soil Analysis**: Get AI-powered soil analysis and recommendations.
- **Plant Disease Detection**: Upload plant images for AI-based disease detection and treatment suggestions.
- **Pump Control**: Activate irrigation and fertigation pumps remotely.
- **Multilingual Support**: Available in English, Yoruba, Igbo, and Hausa.

---

## How It Works

1. **Select Language**: Choose your preferred language from the sidebar.
2. **Enter LGA**: Input your local government area to fetch weather data.
3. **Choose Plant**: Select the plant you're monitoring to view its optimal growth conditions.
4. **Monitor Sensor Data**: View real-time data from connected sensors.
5. **Analyze Soil**: Get AI-powered soil analysis and recommendations.
6. **Upload Plant Image**: Detect diseases and receive treatment suggestions.
7. **Control Pumps**: Activate irrigation and fertigation pumps as needed.

---

## Installation

To run this app locally, follow these steps:

### Prerequisites

- Python 3.8 or higher
- Streamlit
- Google Gemini API key (stored in `.env` file)
- Blynk API token (stored in `.env` file)
- WeatherAPI key (stored in `.env` file)

### Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/zen-core-tech-monitoring.git
   cd zen-core-tech-monitoring
   ```

2. **Install the required packages**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your environment variables**:
   Create a `.env` file in the root directory and add your API keys:
   ```plaintext
   GPT_API_KEY=your_gemini_api_key_here
   BLYNK_TOKEN=your_blynk_token_here
   BLYNK_URL=your_blynk_url_here
   WEATHER_API_KEY=your_weatherapi_key_here
   ```

4. **Run the Streamlit application**:
   ```bash
   streamlit run app.py
   ```

---

## Usage

1. Open the app in your browser after running the Streamlit command.
2. Select your preferred language from the sidebar.
3. Enter your local government area (LGA) to fetch weather data.
4. Choose the plant you're monitoring to view its optimal growth conditions.
5. Monitor real-time sensor data and analyze soil conditions.
6. Upload plant images for disease detection and treatment suggestions.
7. Control irrigation and fertigation pumps as needed.

---

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you have any suggestions or improvements.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- [Google Gemini](https://ai.google/) for the powerful AI model.
- [Blynk](https://blynk.io/) for IoT integration.
- [WeatherAPI](https://www.weatherapi.com/) for real-time weather data.
- [Streamlit](https://streamlit.io/) for the easy-to-use web app framework.

---

Feel free to explore the app and optimize your plant growth with Zen-Core-Tech! 🌿✨
