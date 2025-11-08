from prometheus_client import start_http_server, Gauge
import requests, time

# Metrics
temperature = Gauge('weather_temperature_celsius', 'Current temperature in Celsius')
windspeed = Gauge('weather_windspeed_kmh', 'Wind speed in km/h')
winddirection = Gauge('weather_wind_direction', 'Wind direction in degrees')
weathercode = Gauge('weather_code', 'Weather condition code')

def get_weather():
    try:
        # London example (you can change to your city)
        url = "https://api.open-meteo.com/v1/forecast?latitude=51.5&longitude=-0.12&current_weather=true"
        r = requests.get(url, timeout=5)
        data = r.json()
        current = data["current_weather"]

        temperature.set(current["temperature"])
        windspeed.set(current["windspeed"])
        winddirection.set(current["winddirection"])
        weathercode.set(current["weathercode"])

        print(f"Updated: {current['temperature']}°C, wind {current['windspeed']} km/h")

    except Exception as e:
        print("Error fetching weather:", e)

if __name__ == "__main__":
    start_http_server(8000)
    while True:
        get_weather()
        time.sleep(20)
