
import os
import requests

API_KEY = os.environ.get("OPENWEATHER_API_KEY","OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_city_input():
    while True:
        city = input("Enter a city name (or ZIP code, e.g. '10001,us'): ").strip()
        if city:
            return city
        print("  -> City can't be empty. Try again.\n")


def fetch_weather(city):
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"  
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=8)
    except requests.exceptions.Timeout:
        print("Request timed out - check your internet connection and try again.")
        return None
    except requests.exceptions.ConnectionError:
        print("Couldn't reach the weather service. Are you connected to the internet?")
        return None

    if response.status_code == 401:
        print("Invalid API key. Double check the key you registered at openweathermap.org.")
        return None
    elif response.status_code == 404:
        print(f"Couldn't find a city called '{city}'. Check the spelling and try again.")
        return None
    elif response.status_code != 200:
        print(f"Something went wrong (status code {response.status_code}). Try again later.")
        return None

    return response.json()


def celsius_to_fahrenheit(c):
    return (c * 9 / 5) + 32


def display_weather(data):
    city_name = data["name"]
    country = data["sys"]["country"]
    temp_c = data["main"]["temp"]
    temp_f = celsius_to_fahrenheit(temp_c)
    humidity = data["main"]["humidity"]
    description = data["weather"][0]["description"].title()
    wind_speed = data["wind"]["speed"]

    print(f"\nWeather for {city_name}, {country}")
    print("-" * 32)
    print(f"Condition:    {description}")
    print(f"Temperature:  {temp_c:.1f}°C  ({temp_f:.1f}°F)")
    print(f"Humidity:     {humidity}%")
    print(f"Wind speed:   {wind_speed} m/s")


def main():
    print("=== Weather App ===\n")

    if API_KEY == "PASTE_YOUR_API_KEY_HERE":
        print("Heads up: you haven't set your OpenWeatherMap API key yet.")
        print("Either edit API_KEY at the top of this file, or set the")
        print("OPENWEATHER_API_KEY environment variable.\n")

    city = get_city_input()
    data = fetch_weather(city)

    if data:
        display_weather(data)


if __name__ == "__main__":
    while True:
        main()
        again = input("\nCheck another city? (y/n): ").strip().lower()
        if again != "y":
            print("Stay dry out there!")
            break
        print()