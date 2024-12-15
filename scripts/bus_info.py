import os
import csv
import requests
import sys
import pandas as pd
import numpy as np
import threading
import concurrent.futures
import time
import schedule
from datetime import datetime
from time import sleep
from sklearn.cluster import DBSCAN
from geopy.distance import great_circle
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, XSD
from requests.auth import HTTPBasicAuth

# Define API Key and endpoint
TMB_API_KEY = 'eb439a2ff7c70b6daf9f7e5becebecec'
TMB_APP_ID = '48f061ed'

EX = Namespace("http://example.org/busstop#")
GEO = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")

# Define Fuseki endpoint and credentials
FUSEKI_ENDPOINT = "http://localhost:3030/smartcity-kb/update"
FUSEKI_USER = "admin"
FUSEKI_PASSWORD = "smartcity-kb"

# Retrieves the important information from "parades.csv" into "paragens_bus_barcelona.csv"
def extract_bus_stop_info(input_file, output_file):
    """
    Extracts bus stop information (stop ID, stop name, coordinates) 
    from the input CSV file and saves it to a new CSV file.

    Args:
        input_file (str): Path to the input CSV file.
        output_file (str): Path to the output CSV file.
    """
    # Define the headers for the output CSV
    output_headers = ["stop_id", "stop_name", "coordinates"]

    try:
        with open(input_file, mode="r", encoding="utf-8") as infile, \
             open(output_file, mode="w", encoding="utf-8", newline="") as outfile:

            # Create CSV reader and writer
            reader = csv.DictReader(infile)
            writer = csv.writer(outfile)

            # Write the headers to the output file
            writer.writerow(output_headers)

            # Extract required information
            for row in reader:
                stop_code = row["CODI_PARADA"]  # Stop Code
                stop_name = row["NOM_PARADA"]  # Stop name
                coordinates = row["GEOMETRY"]  # Coordinates

                # Write the extracted row to the output file
                writer.writerow([stop_code, stop_name, coordinates])

        print(f"Extracted bus stop information saved to {output_file}.")

    except Exception as e:
        print(f"An error occurred: {e}")

# Creates clusters of bus_stops with same of really close coordinates
# NOT BEING USED FOR NOW
def cluster_stops():
    # Load bus stops data
    file_path = "paragens_bus_barcelona.csv"  # Adjust as needed
    bus_stops = pd.read_csv(file_path)

    # Parse coordinates into latitude and longitude
    def parse_coordinates(coord):
        lat, lon = coord.replace("POINT (", "").replace(")", "").split()
        return float(lon), float(lat)  # Note: (lon, lat) format for great_circle

    bus_stops[['longitude', 'latitude']] = bus_stops['coordinates'].apply(lambda x: pd.Series(parse_coordinates(x)))

    # Prepare data for clustering
    coords = bus_stops[['latitude', 'longitude']].values

    # Use DBSCAN for clustering stops by proximity
    # eps is the radius in kilometers (e.g., 0.05 for ~50 meters)
    db = DBSCAN(eps=0.05, min_samples=1, metric=lambda x, y: great_circle(x, y).m).fit(coords)
    bus_stops['cluster_id'] = db.labels_

    # Save the clustered data to a file
    output_path = "clustered_bus_stops.csv"
    bus_stops.to_csv(output_path, index=False)
    print(f"Clustered stops saved to {output_path}")

# Function to fetch next bus data for a given stop_id
def fetch_next_buses(stop_id):
    url = f"https://api.tmb.cat/v1/ibus/stops/{stop_id}?app_id={TMB_APP_ID}&app_key={TMB_API_KEY}&numberOfPredictions=1"
    retries = 3
    delay = 0.5 
    
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=3)  # Set a timeout for the request
            response.raise_for_status()
            return response.json()["data"]["ibus"]
        except requests.RequestException as e:
            #print(f"Error fetching data for stop_id {stop_id}: {e}")
            if attempt < retries - 1:
                sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                print(f"Failed to fetch data for stop_id {stop_id} after {retries} attempts.")
                return []

# Function to process a single stop
def process_stop(stop, stop_data):
    try:
        stop_id = stop["stop_id"]
        next_buses = fetch_next_buses(stop_id)
        stop["next_buses"] = next_buses
        stop_data.append(stop)
    except Exception as e:
        print(f"Error processing stop_id {stop['stop_id']}: {e}")

# Function to create RDF data
def create_rdf(stop_data, output_folder, city_name):
    g = Graph()
    g.bind("ex", EX)
    g.bind("geo", GEO)

    # Create a city URI
    city_uri = URIRef(f"{EX}{city_name.replace(' ', '_')}")

    # Add stops to RDF
    for stop in stop_data:
        stop_uri = URIRef(f"{EX}stop_{stop['stop_id']}")
        g.add((stop_uri, RDF.type, EX.BusStop))
        g.add((stop_uri, EX.stopId, Literal(stop['stop_id'], datatype=XSD.string)))
        g.add((stop_uri, EX.stopName, Literal(stop['stop_name'], datatype=XSD.string)))
        g.add((stop_uri, GEO.lat, Literal(stop['latitude'], datatype=XSD.float)))
        g.add((stop_uri, GEO.long, Literal(stop['longitude'], datatype=XSD.float)))

        # Link to city
        g.add((stop_uri, EX.isLocatedIn, city_uri))

        # Add bus information
        for bus in stop.get("next_buses", []):
            if isinstance(bus, dict) and "line" in bus and "destination" in bus:
                bus_uri = URIRef(f"{stop_uri}/bus_{bus['line']}_{bus['destination'].replace(' ', '_')}")
                g.add((bus_uri, RDF.type, EX.BusInfo))
                g.add((bus_uri, EX.line, Literal(bus['line'], datatype=XSD.string)))
                g.add((bus_uri, EX.destination, Literal(bus['destination'], datatype=XSD.string)))
                g.add((bus_uri, EX.timeInMinutes, Literal(bus.get("t-in-min", 0), datatype=XSD.int)))
                g.add((stop_uri, EX.hasNextBus, bus_uri))

    # Save RDF file
    output_file_name = f"{city_name.replace(' ', '_')}_bus_stops.ttl"
    output_path = os.path.join(output_folder, output_file_name)
    g.serialize(destination=output_path, format="turtle")
    print(f"RDF data saved to {output_path}")

# Function to generate SPARQL DELETE query
def generate_delete_query():
    return """
    PREFIX ex: <http://example.org/busstop#>
    DELETE WHERE {
        ?s a ex:BusStop .
        ?s ex:hasNextBus ?b .
        ?b a ex:BusInfo .
    }
    """

# Function to generate SPARQL INSERT query
def generate_insert_query(stop_data, city_name):
    triples = []
    city_uri = f"ex:{city_name.replace(' ', '_')}"

    for stop in stop_data:
        stop_uri = f"ex:stop_{stop['stop_id']}"
        triples.append(f"{stop_uri} a ex:BusStop ;")
        triples.append(f"    ex:stopId \"{stop['stop_id']}\"^^xsd:string ;")
        triples.append(f"    ex:stopName \"{stop['stop_name']}\"^^xsd:string ;")
        triples.append(f"    geo:lat \"{stop['latitude']}\"^^xsd:float ;")
        triples.append(f"    geo:long \"{stop['longitude']}\"^^xsd:float ;")
        triples.append(f"    ex:isLocatedIn {city_uri} .")

        for bus in stop.get("next_buses", []):
            if isinstance(bus, dict) and "line" in bus and "destination" in bus:
                bus_uri = f"<{stop_uri}/bus_{bus['line']}_{bus['destination'].replace(' ', '_')}>"
                triples.append(f"{bus_uri} a ex:BusInfo ;")
                triples.append(f"    ex:destination \"{bus['destination']}\"^^xsd:string ;")
                triples.append(f"    ex:line \"{bus['line']}\"^^xsd:string ;")
                triples.append(f"    ex:timeInMinutes \"{bus.get('t-in-min', 0)}\"^^xsd:int .")
                triples.append(f"{stop_uri} ex:hasNextBus {bus_uri} .")

    return f"""
    PREFIX ex: <http://example.org/busstop#>
    PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    INSERT DATA {{
        {" ".join(triples)}
    }}
    """

# Function to update data in Fuseki
def update_fuseki(city_name, stop_data):
    print("Updating RDF data in Fuseki...")

    try:
        delete_query = generate_delete_query()
        insert_query = generate_insert_query(stop_data, city_name)

        headers = {"Content-Type": "application/sparql-update"}

        # Execute DELETE query
        delete_response = requests.post(FUSEKI_ENDPOINT, data=delete_query, headers=headers, auth=HTTPBasicAuth(FUSEKI_USER, FUSEKI_PASSWORD))
        if delete_response.status_code != 204:
            print(f"Failed to delete data: {delete_response.status_code}, {delete_response.text}")
            return
        
        print("Deleted existing Bus Stops RDF data in Fuseki.")

        # Execute INSERT query
        insert_response = requests.post(FUSEKI_ENDPOINT, data=insert_query, headers=headers, auth=HTTPBasicAuth(FUSEKI_USER, FUSEKI_PASSWORD))
        if insert_response.status_code == 204:
            print("RDF data updated successfully in Fuseki.")
        else:
            print(f"Failed to insert data: {insert_response.status_code}, {insert_response.text}")
    except Exception as e:
        print(f"Error updating Fuseki: {e}")

# Main function to fetch bus stop data
def fetch_bus_stop_data(csv_file, output_folder, city_name):
    print(f"Fetching bus stop data for {city_name}...")
    stop_data = []

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Read CSV
    with open(csv_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        stops = []
        for row in reader:
            try:
                point = row['coordinates']
                coordinates = point.replace("POINT (", "").replace(")", "").split()
                longitude = float(coordinates[0])
                latitude = float(coordinates[1])
                stops.append({
                    "stop_id": row["stop_id"],
                    "stop_name": row["stop_name"],
                    "latitude": latitude,
                    "longitude": longitude,
                    "next_buses": []
                })
            except ValueError as e:
                print(f"Skipping invalid stop data: {e}")

    # Process stops concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_stop, stop, stop_data) for stop in stops]
        concurrent.futures.wait(futures)

    # Create RDF
    create_rdf(stop_data, output_folder, city_name)
    update_fuseki(city_name, stop_data)

# Schedule the script to run every 10 minutes
def schedule_bus_stops(city_name, output_folder, input_file):
    schedule.every(10).seconds.do(fetch_bus_stop_data, city_name=city_name, output_folder=output_folder, csv_file=input_file)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <city_name>")
        sys.exit(1)

    city_name = sys.argv[1].strip().title()

    # input_file = "./data/parades.csv"
    # output_file = "./data/paragens_bus_barcelona.csv"
    # extract_bus_stop_info(input_file, output_file)

    input_file = f"./data/paragens_bus_{city_name.lower()}.csv"
    output_folder = "./data/"

    fetch_bus_stop_data(input_file, output_folder, city_name)
    
    schedule_bus_stops(city_name, output_folder, input_file)
    while True:
        schedule.run_pending()
        time.sleep(1) 
