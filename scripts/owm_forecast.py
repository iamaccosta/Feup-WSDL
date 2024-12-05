import requests
import sys
import os
import schedule
import time
from rdflib import Graph, Namespace, Literal, RDF
from rdflib.namespace import XSD
import subprocess

# Your OpenWeatherMap API Key
API_KEY = "3b89c692d961ddb0d96c893a41852dfc"

# OpenWeatherMap API URLs
GEO_API_URL = "http://api.openweathermap.org/geo/1.0/direct"
FORECAST_API_URL = "https://api.openweathermap.org/data/2.5/forecast"

# RDF Namespace
DBPEDIA = Namespace("http://dbpedia.org/resource/")
DBPEDIA_ONT = Namespace("http://dbpedia.org/ontology/")

script = "graphics_forecast.py"

# Function to get latitude, longitude, and country code of the city
def get_coordinates(city_name):
    try:
        params = {"q": city_name, "limit": 1, "appid": API_KEY}
        response = requests.get(GEO_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if data:
            lat = data[0]["lat"]
            lon = data[0]["lon"]
            country_code = data[0]["country"]
            print(f"Coordinates for {city_name}: lat={lat}, lon={lon}, country={country_code}")
            return lat, lon, country_code
        else:
            print(f"No coordinates found for {city_name}.")
            return None, None, None
    except requests.RequestException as e:
        print(f"Error fetching coordinates: {e}")
        return None, None, None

# Function to get the 5-day forecast using latitude and longitude
def get_forecast(lat, lon):
    try:
        params = {"lat": lat, "lon": lon, "appid": API_KEY, "units": "metric"}
        response = requests.get(FORECAST_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        # Parse relevant forecast information
        forecasts = []
        for entry in data["list"]:
            forecast = {
                "datetime": entry["dt_txt"].replace(" ", "T"),  # Ensure ISO 8601 compliance
                "temperature": entry["main"]["temp"],
                "humidity": entry["main"]["humidity"],
                "weather": entry["weather"][0]["description"],
                "wind_speed": entry["wind"]["speed"],
            }
            forecasts.append(forecast)
        print(f"Retrieved {len(forecasts)} forecasts.")
        return forecasts
    except requests.RequestException as e:
        print(f"Error fetching forecast data: {e}")
        return None

# Function to save forecast data as RDF Turtle
def save_forecast_as_rdf(city_name, forecasts):
    try:
        # Create RDF graph
        g = Graph()
        g.bind("dbpedia", DBPEDIA)
        g.bind("dbo", DBPEDIA_ONT)

        # Define the city's URI
        city_uri = DBPEDIA[city_name.replace(" ", "_")]

        # Add forecast data to RDF graph
        for forecast in forecasts:
            forecast_uri = DBPEDIA[f"{city_name.replace(' ', '_')}_forecast_{forecast['datetime'].replace(':', '_')}"]
            g.add((forecast_uri, RDF.type, DBPEDIA_ONT.Forecast))
            g.add((forecast_uri, DBPEDIA_ONT.dateTime, Literal(forecast["datetime"], datatype=XSD.dateTime)))
            g.add((forecast_uri, DBPEDIA_ONT.temperature, Literal(forecast["temperature"], datatype=XSD.float)))
            g.add((forecast_uri, DBPEDIA_ONT.humidity, Literal(forecast["humidity"], datatype=XSD.float)))
            g.add((forecast_uri, DBPEDIA_ONT.weatherCondition, Literal(forecast["weather"], datatype=XSD.string)))
            g.add((forecast_uri, DBPEDIA_ONT.windSpeed, Literal(forecast["wind_speed"], datatype=XSD.float)))
            g.add((forecast_uri, DBPEDIA_ONT.belongsTo, city_uri))

        # Save to Turtle file
        folder_path = "./data"
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, f"{city_name.replace(' ', '_')}_forecast.ttl")
        g.serialize(destination=file_path, format="turtle")
        print(f"Forecast data saved as RDF Turtle at {file_path}")

        subprocess.run(["python3", script, city_name])
    except Exception as e:
        print(f"Error saving RDF data: {e}")

# Main function to fetch and save forecast data
def fetch_forecast_data(city_name):
    lat, lon, country_code = get_coordinates(city_name)
    if lat and lon:
        forecasts = get_forecast(lat, lon)
        if forecasts:
            save_forecast_as_rdf(city_name, forecasts)

# Schedule the script to run every 3 hours
def schedule_forecast_data(city_name):
    schedule.every(3).hours.do(fetch_forecast_data, city_name=city_name)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <city_name>")
        sys.exit(1)

    city_name = sys.argv[1].strip().title()
    print(f"Fetching forecast data for {city_name}...")
    fetch_forecast_data(city_name)  # Run once at startup
    schedule_forecast_data(city_name)
    while True:
        schedule.run_pending()
        time.sleep(1)  # Prevent high CPU usage

