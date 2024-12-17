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
SCKB = Namespace("http://example.org/smartcity#")
DBPEDIA = Namespace("http://dbpedia.org/resource/")
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")

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

# Save forecasts to RDF
def save_forecast_as_rdf(city_name, forecasts):
    g = Graph()
    g.bind("sckb", SCKB)
    g.bind("rdfs", RDFS)

    city_uri = URIRef(SCKB[city_name.replace(" ", "_")])
    forecast_base = f"http://example.org/smartcity#{city_name.replace(' ', '_')}/Forecast/"

    for forecast in forecasts:
        forecast_uri = URIRef(f"{forecast_base}{forecast['datetime'].replace(':', '_')}")
        g.add((forecast_uri, RDF.type, SCKB.Forecast))
        g.add((forecast_uri, RDFS.label, Literal(f"Forecast on {forecast['datetime'].replace('T', ' ')}", lang="en")))
        g.add((forecast_uri, SCKB.temperature, Literal(forecast["temperature"], datatype=XSD.float)))
        g.add((forecast_uri, SCKB.humidity, Literal(forecast["humidity"], datatype=XSD.float)))
        g.add((forecast_uri, SCKB.weatherCondition, Literal(forecast["weather"], datatype=XSD.string)))
        g.add((forecast_uri, SCKB.windSpeed, Literal(forecast["wind_speed"], datatype=XSD.float)))
        g.add((forecast_uri, SCKB.belongsTo, city_uri))  # Link to City

    folder = "./data"
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"{city_name.replace(' ', '_')}_forecast.ttl")
    g.serialize(destination=path, format="turtle")
    print(f"Forecast RDF saved at: {path}")

# Update forecasts in Fuseki
def update_forecasts(city_name, endpoint, forecasts):
    headers = {"Content-Type": "application/sparql-update"}
    auth = HTTPBasicAuth("admin", "smartcity-kb")
    forecast_base = f"http://example.org/smartcity#{city_name.replace(' ', '_')}/Forecast/"

    # DELETE existing forecasts
    delete_query = f"""
    PREFIX sckb: <http://example.org/smartcity#>
    DELETE WHERE {{
        ?forecast a sckb:Forecast ;
            ?p ?o .
    }}
    """
    requests.post(endpoint, data=delete_query, headers=headers, auth=auth)

    # INSERT new forecasts
    insert_statements = [
        f"""
        <{forecast_base}{forecast['datetime'].replace(':', '_')}> a sckb:Forecast ;
            rdfs:label "Forecast on {forecast['datetime'].replace('T', ' ')}"@en ;
            sckb:temperature "{forecast['temperature']}"^^xsd:float ;
            sckb:humidity "{forecast['humidity']}"^^xsd:float ;
            sckb:weatherCondition "{forecast['weather']}"^^xsd:string ;
            sckb:windSpeed "{forecast['wind_speed']}"^^xsd:float ;
            sckb:belongsTo <http://example.org/smartcity#{city_name.replace(' ', '_')}> .
        """
        for forecast in forecasts
    ]

    insert_query = f"""
    PREFIX sckb: <http://example.org/smartcity#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    INSERT DATA {{
        {" ".join(insert_statements)}
    }}
    """
    response = requests.post(endpoint, data=insert_query, headers=headers, auth=auth)
    if response.status_code == 204:
        print("Forecast data updated successfully in Fuseki.")

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
