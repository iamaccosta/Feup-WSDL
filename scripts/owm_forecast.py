import requests
import sys
import os
import schedule
import time
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD
from requests.auth import HTTPBasicAuth
import subprocess

# Your OpenWeatherMap API Key
API_KEY = "3b89c692d961ddb0d96c893a41852dfc"

# OpenWeatherMap API URLs
GEO_API_URL = "http://api.openweathermap.org/geo/1.0/direct"
FORECAST_API_URL = "https://api.openweathermap.org/data/2.5/forecast"

# RDF Namespaces
DBPEDIA = Namespace("http://dbpedia.org/resource/")
DBP = Namespace("http://dbpedia.org/property/")
GEO = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")

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
        forecasts = []
        for entry in data.get("list", []):
            forecast = {
                "datetime": entry.get("dt_txt", "").replace(" ", "T"),  # Ensure ISO 8601 compliance
                "temperature": entry["main"].get("temp"),
                "humidity": entry["main"].get("humidity"),
                "weather": entry["weather"][0].get("description"),
                "wind_speed": entry["wind"].get("speed"),
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
        g.bind("dbp", DBP)
        g.bind("rdfs", RDFS)

        # Define the base URI for forecasts
        base_uri = f"http://dbpedia.org/resource/{city_name.replace(' ', '_')}/Forecast/"

        # Add forecast data to RDF graph
        for forecast in forecasts:
            forecast_uri = URIRef(base_uri + forecast["datetime"].replace(":", "_"))
            g.add((forecast_uri, RDF.type, DBP.Forecast))
            g.add((forecast_uri, RDFS.label, Literal(forecast["datetime"])))
            g.add((forecast_uri, DBP.temperature, Literal(forecast["temperature"], datatype=XSD.float)))
            g.add((forecast_uri, DBP.humidity, Literal(forecast["humidity"], datatype=XSD.float)))
            g.add((forecast_uri, DBP.weatherCondition, Literal(forecast["weather"], datatype=XSD.string)))
            g.add((forecast_uri, DBP.windSpeed, Literal(forecast["wind_speed"], datatype=XSD.float)))

        # Save to Turtle file
        folder_path = "./data"
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, f"{city_name.replace(' ', '_')}_forecast.ttl")
        g.serialize(destination=file_path, format="turtle")
        print(f"Forecast data saved as RDF Turtle at {file_path}")

        # if os.path.exists(script):
        #    subprocess.run(["python3", script, city_name])
    except Exception as e:
        print(f"Error saving RDF data: {e}")

#Updates Jena Forecasts
def update_forecasts(city_name, endpoint, forecasts):
    headers = {"Content-Type": "application/sparql-update"}  
    username = "admin"
    password = "smartcity-kb"

    delete_query= f"""
    PREFIX dbp: <http://dbpedia.org/property/>
    PREFIX dbpedia: <http://dbpedia.org/resource/>

    DELETE WHERE {{
        ?forecast a dbp:Forecast ;
            dbp:humidity ?humidity ;
            dbp:temperature ?temperature ;
            dbp:weatherCondition ?condition ;
            dbp:windSpeed ?windSpeed .
    }}
    """
    try:
        delete_response = requests.post(endpoint, data=delete_query, headers=headers, auth=HTTPBasicAuth(username, password))

        if delete_response.status_code == 200:
            print("Response:", response.text)
        elif delete_response.status_code == 204:
            print("Old forecasts deleted successfully!")
        else:
            print(f"Error: {delete_response.status_code}, {delete_response.text}")
    except Exception as e:
        print(f"Error performing update: {e}")

    # insert forecasts
    insert_statements = []
    for forecast in forecasts:
        forecast_uri = f"<http://dbpedia.org/resource/{city_name.replace(' ', '_')}/Forecast/{forecast['datetime'].replace(':', '_')}>"
        insert_statements.append(f"""
            {forecast_uri} a dbp:Forecast ;
                            rdfs:label "{forecast['datetime']}" ;
                            dbp:humidity "{forecast['humidity']}"^^xsd:float ;
                            dbp:temperature "{forecast['temperature']}"^^xsd:float ;
                            dbp:weatherCondition "{forecast['weather']}"^^xsd:string ;
                            dbp:windSpeed "{forecast['wind_speed']}"^^xsd:float ;
                            dbp:belongsTo dbpedia:{city_name.replace(" ", "_")} .
        """)

    insert_query = f"""
    PREFIX dbp: <http://dbpedia.org/property/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX dbpedia: <http://dbpedia.org/resource/>

    INSERT DATA {{
        {' '.join(insert_statements)}
    }}
    """
    try:
        insert_response  = requests.post(endpoint, data=insert_query, headers=headers, auth=HTTPBasicAuth(username, password))

        if insert_response .status_code == 200:
            print("Response:", response.text)
        elif insert_response .status_code == 204:
            print("New forecasts inserted successfully!")
        else:
            print(f"Error: {insert_response .status_code}, {insert_response .text}")
    except Exception as e:
        print(f"Error performing update: {e}")


# Main function to fetch and save forecast data
def fetch_forecast_data(city_name):
    lat, lon, country_code = get_coordinates(city_name)
    if lat and lon:
        forecasts = get_forecast(lat, lon)
        if forecasts:
            save_forecast_as_rdf(city_name, forecasts)
            update_forecasts(city_name, "http://localhost:3030/smartcity-kb/update", forecasts)

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
