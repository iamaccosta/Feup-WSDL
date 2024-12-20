import requests
import sys
import os
import time
import schedule
from rdflib import Graph, Namespace, Literal, URIRef, RDF, XSD
from requests.auth import HTTPBasicAuth


# Your OpenWeatherMap API Key
API_KEY = "3b89c692d961ddb0d96c893a41852dfc"

# OpenWeatherMap API URLs
GEO_API_URL = "http://api.openweathermap.org/geo/1.0/direct"
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"

# RDF Namespaces
DBPEDIA = Namespace("http://dbpedia.org/resource/")
GEO = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
SCKB = Namespace("http://example.org/smartcity#")
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")

FUSEKI_UPDATE_URL = "http://localhost:3030/#/dataset/smartcity/query"

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

# Function to get current weather using latitude and longitude
def get_current_weather(lat, lon):
    try:
        params = {"lat": lat, "lon": lon, "appid": API_KEY, "units": "metric"}
        response = requests.get(WEATHER_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        weather_info = {
            "current_temperature": data.get("main", {}).get("temp"),
            "current_humidity": data.get("main", {}).get("humidity"),
            "current_weather": data.get("weather", [{}])[0].get("description"),
            "current_wind_speed": data.get("wind", {}).get("speed"),
        }
        if None in weather_info.values():
            print(f"Some weather data is missing: {weather_info}")
        print(f"Current Weather Data: {weather_info}")
        return weather_info
    except requests.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None

# Function to save weather data as RDF Turtle
def save_weather_as_rdf(city_name, weather_info):
    try:
        g = Graph()

        # Bind namespaces
        g.bind("sckb", SCKB)
        g.bind("geo", GEO)
        g.bind("xsd", XSD)

        # Define the city's URI (in our local namespace)
        city_uri = URIRef(SCKB[city_name.replace(" ", "_")])
        dbpedia_uri = URIRef(DBPEDIA[city_name.replace(" ", "_")])

        # Add weather data to RDF graph
        g.add((city_uri, RDF.type, SCKB.City))
        g.add((city_uri, SCKB.currentTemperature, Literal(weather_info["current_temperature"], datatype=XSD.float)))
        g.add((city_uri, SCKB.currentHumidity, Literal(weather_info["current_humidity"], datatype=XSD.float)))
        g.add((city_uri, SCKB.currentWeatherCondition, Literal(weather_info["current_weather"], datatype=XSD.string)))
        g.add((city_uri, SCKB.currentWindSpeed, Literal(weather_info["current_wind_speed"], datatype=XSD.float)))
        g.add((city_uri, SCKB.linkedTo, dbpedia_uri))  # Link to DBpedia

        # Save to Turtle file
        folder_path = "./data"
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, f"{city_name.replace(' ', '_')}_current_weather.ttl")
        g.serialize(destination=file_path, format="turtle")
        print(f"Weather data saved as RDF Turtle at {file_path}")
    except Exception as e:
        print(f"Error saving RDF data: {e}")

# Selects the temperature of Barcelona through a POST HTTP request
def direct_sparql_query_post(endpoint):
    query = """
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX dbpedia: <http://dbpedia.org/resource/>

    SELECT ?temperature
    WHERE {
        dbpedia:Barcelona dbo:current_temperature ?temperature .
    }
    """
    try:
        headers = {"Content-Type": "application/sparql-query"}
        response = requests.post(endpoint, data=query, headers=headers)

        if response.status_code == 200:
            print("Response:", response.text)
        else:
            print(f"Error: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Error performing query: {e}")

# Selects the temperature of Barcelona through a GET HTTP request
def direct_sparql_query_get(endpoint):
    query = """
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX dbpedia: <http://dbpedia.org/resource/>

    SELECT ?temperature ?humidity ?weatherCondition ?windSpeed
    WHERE {
        dbpedia:Barcelona dbo:current_temperature ?temperature .
        dbpedia:Barcelona dbo:current_humidity ?humidity .
        dbpedia:Barcelona dbo:current_weatherCondition ?weatherCondition .
        dbpedia:Barcelona dbo:current_windSpeed ?windSpeed .
    }
    """
    try:
        params = {"query": query}
        response = requests.get(endpoint, params=params)

        if response.status_code == 200:
            print("Response:", response.text)
        else:
            print(f"Error: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Error performing query: {e}")

# Updates the temperature of Barcelona through a POST HTTP request
def direct_sparql_update(endpoint, weather_info):
    city_uri = f"<http://example.org/smartcity#{city_name.replace(' ', '_')}>"
    dbpedia_link = f"<http://dbpedia.org/resource/{city_name.replace(' ', '_')}>"

    query = f"""
    PREFIX sckb: <http://example.org/smartcity#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    DELETE {{
        {city_uri} sckb:currentTemperature ?oldTemperature ;
                   sckb:currentHumidity ?oldHumidity ;
                   sckb:currentWeatherCondition ?oldCondition ;
                   sckb:currentWindSpeed ?oldWindSpeed .
    }}
    INSERT {{
        {city_uri} a sckb:City ;
                   sckb:currentTemperature "{weather_info['current_temperature']}"^^xsd:float ;
                   sckb:currentHumidity "{weather_info['current_humidity']}"^^xsd:float ;
                   sckb:currentWeatherCondition "{weather_info['current_weather']}"^^xsd:string ;
                   sckb:currentWindSpeed "{weather_info['current_wind_speed']}"^^xsd:float ;
                   sckb:linkedTo {dbpedia_link} .
    }}
    WHERE {{
        OPTIONAL {{
            {city_uri} sckb:currentTemperature ?oldTemperature ;
                       sckb:currentHumidity ?oldHumidity ;
                       sckb:currentWeatherCondition ?oldCondition ;
                       sckb:currentWindSpeed ?oldWindSpeed .
        }}
    }}
    """
    try:
        headers = {"Content-Type": "application/sparql-update"}
        
        username = "admin"
        password = "smartcity-kb"

        response = requests.post(endpoint, data=query, headers=headers, auth=HTTPBasicAuth(username, password))

        if response.status_code == 200:
            print("Response:", response.text)
        elif response.status_code == 204:
            print("Update Successful!")
        else:
            print(f"Error: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Error performing update: {e}")

# Main function to fetch, save, and update weather data
def fetch_weather_data(city_name):
    lat, lon, country_code = get_coordinates(city_name)
    if lat and lon:
        weather_info = get_current_weather(lat, lon)
        if weather_info:
            save_weather_as_rdf(city_name, weather_info)
            direct_sparql_update("http://localhost:3030/smartcity-kb/update", weather_info)
            #direct_sparql_query_post("http://localhost:3030/smartcity-kb/query")

# Schedule the script to run every 10 minutes
def schedule_weather_data(city_name):
    schedule.every(10).minutes.do(fetch_weather_data, city_name=city_name)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <city_name>")
        sys.exit(1)

    city_name = sys.argv[1].strip().title()
    print(f"Fetching weather data for {city_name}...")
    fetch_weather_data(city_name)
    schedule_weather_data(city_name)
    while True:
        schedule.run_pending()
        time.sleep(1)  # Prevent high CPU usage
