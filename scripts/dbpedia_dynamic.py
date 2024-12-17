import os
import sys
import requests
from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD
from requests.auth import HTTPBasicAuth

# Define namespaces
DBPEDIA = Namespace("http://dbpedia.org/resource/")
SCKB = Namespace("http://example.org/smartcity#")
GEO = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")

# SPARQL endpoint for DBpedia
sparql = SPARQLWrapper("http://dbpedia.org/sparql")

# Function to retrieve monthly weather conditions
def get_monthly_weather_conditions(city_name):
    query = f"""
    SELECT 
        ?month ?highC ?lowC ?meanC ?precipitationDays ?precipitationMm ?recordHighC ?recordLowC
    WHERE {{
        VALUES (?month ?highProp ?lowProp ?meanProp ?precipDaysProp ?precipMmProp) {{
            ("January" dbp:janHighC dbp:janLowC dbp:janMeanC dbp:janPrecipitationDays dbp:janPrecipitationMm)
            ("February" dbp:febHighC dbp:febLowC dbp:febMeanC dbp:febPrecipitationDays dbp:febPrecipitationMm)
            ("March" dbp:marHighC dbp:marLowC dbp:marMeanC dbp:marPrecipitationDays dbp:marPrecipitationMm)
            ("April" dbp:aprHighC dbp:aprLowC dbp:aprMeanC dbp:aprPrecipitationDays dbp:aprPrecipitationMm)
            ("May" dbp:mayHighC dbp:mayLowC dbp:mayMeanC dbp:mayPrecipitationDays dbp:mayPrecipitationMm)
            ("June" dbp:junHighC dbp:junLowC dbp:junMeanC dbp:junPrecipitationDays dbp:junPrecipitationMm)
            ("July" dbp:julHighC dbp:julLowC dbp:julMeanC dbp:julPrecipitationDays dbp:julPrecipitationMm)
            ("August" dbp:augHighC dbp:augLowC dbp:augMeanC dbp:augPrecipitationDays dbp:augPrecipitationMm)
            ("September" dbp:sepHighC dbp:sepLowC dbp:sepMeanC dbp:sepPrecipitationDays dbp:sepPrecipitationMm)
            ("October" dbp:octHighC dbp:octLowC dbp:octMeanC dbp:octPrecipitationDays dbp:octPrecipitationMm)
            ("November" dbp:novHighC dbp:novLowC dbp:novMeanC dbp:novPrecipitationDays dbp:novPrecipitationMm)
            ("December" dbp:decHighC dbp:decLowC dbp:decMeanC dbp:decPrecipitationDays dbp:decPrecipitationMm)
        }}
        OPTIONAL {{ dbr:{city_name} ?highProp ?highC . }}
        OPTIONAL {{ dbr:{city_name} ?lowProp ?lowC . }}
        OPTIONAL {{ dbr:{city_name} ?meanProp ?meanC . }}
        OPTIONAL {{ dbr:{city_name} ?precipDaysProp ?precipitationDays . }}
        OPTIONAL {{ dbr:{city_name} ?precipMmProp ?precipitationMm . }}
    }}
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    if results["results"]["bindings"]:
        return results["results"]["bindings"]
    else:
        return None

# Function to save data as RDF/Turtle
def save_to_rdf(city_name, weather_data):
    g = Graph()
    g.bind("sckb", SCKB)
    g.bind("rdfs", RDFS)

    # City and weather data URIs
    city_uri = URIRef(SCKB + city_name.replace(" ", "_"))
    climate_base_uri = URIRef(f"{SCKB}{city_name.replace(' ', '_')}/MonthlyWeatherSummary")

    # Add monthly weather data
    for entry in weather_data:
        month = entry["month"]["value"]
        month_uri = URIRef(f"{climate_base_uri}/{month}")

        g.add((month_uri, RDF.type, SCKB.MonthlyWeatherSummary))
        g.add((month_uri, RDFS.label, Literal(month, lang="en")))
        g.add((month_uri, SCKB.belongsTo, city_uri))

        if "highC" in entry:
            g.add((month_uri, SCKB.highC, Literal(float(entry["highC"]["value"]), datatype=XSD.float)))
        if "lowC" in entry:
            g.add((month_uri, SCKB.lowC, Literal(float(entry["lowC"]["value"]), datatype=XSD.float)))
        if "meanC" in entry:
            g.add((month_uri, SCKB.meanC, Literal(float(entry["meanC"]["value"]), datatype=XSD.float)))
        if "precipitationDays" in entry:
            g.add((month_uri, SCKB.precipitationDays, Literal(float(entry["precipitationDays"]["value"]), datatype=XSD.float)))
        if "precipitationMm" in entry:
            g.add((month_uri, SCKB.precipitationMm, Literal(float(entry["precipitationMm"]["value"]), datatype=XSD.float)))

    # Save to Turtle file
    folder_path = "./data"
    os.makedirs(folder_path, exist_ok=True)
    filename = f"{folder_path}/{city_name}_monthly_weather.ttl"
    g.serialize(destination=filename, format="turtle")
    print(f"Monthly weather data for {city_name} saved to {filename}")

# Function to insert data into Fuseki
def insert_monthly_weather_into_fuseki(city_name, weather_data):
    fuseki_endpoint = "http://localhost:3030/smartcity-kb/update"
    insert_statements = []

    # Base URI for the city's climate data
    climate_base_uri = f"http://example.org/smartcity#{city_name.replace(' ', '_')}/MonthlyWeatherSummary"
    city_uri = f"<http://example.org/smartcity#{city_name.replace(' ', '_')}>"

    # Construct INSERT statements for each month's data
    for entry in weather_data:
        month = entry["month"]["value"]
        month_uri = f"<{climate_base_uri}/{month}>"
        statements = [
            f"{month_uri} a sckb:MonthlyWeatherSummary ;",
            f"    rdfs:label \"{month}\"@en ;",
            f"    sckb:month \"{month}\"^^xsd:string ;",
            f"    sckb:belongsTo {city_uri} ;"
        ]

        if "highC" in entry:
            statements.append(f"    sckb:highC \"{entry['highC']['value']}\"^^xsd:float ;")
        if "lowC" in entry:
            statements.append(f"    sckb:lowC \"{entry['lowC']['value']}\"^^xsd:float ;")
        if "meanC" in entry:
            statements.append(f"    sckb:meanC \"{entry['meanC']['value']}\"^^xsd:float ;")
        if "precipitationDays" in entry:
            statements.append(f"    sckb:precipitationDays \"{entry['precipitationDays']['value']}\"^^xsd:float ;")
        if "precipitationMm" in entry:
            statements.append(f"    sckb:precipitationMm \"{entry['precipitationMm']['value']}\"^^xsd:float .")

        insert_statements.append("\n".join(statements))

    # Construct the full INSERT DATA query
    insert_query = f"""
    PREFIX sckb: <http://example.org/smartcity#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    INSERT DATA {{
        {' '.join(insert_statements)}
    }}
    """

    # Send the query to the Fuseki server
    try:
        headers = {"Content-Type": "application/sparql-update"}
        username = "admin"
        password = "smartcity-kb"

        response = requests.post(
            fuseki_endpoint,
            data=insert_query,
            headers=headers,
            auth=HTTPBasicAuth(username, password),
        )
        if response.status_code == 204:
            print(f"Monthly weather data for {city_name} inserted successfully into Fuseki.")
        else:
            print(f"Error inserting monthly weather data into Fuseki: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Error inserting monthly weather data into Fuseki: {e}")

# Main script
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <city_name>")
        sys.exit(1)
    
    city_name = sys.argv[1].strip().title()
    weather_data = get_monthly_weather_conditions(city_name)
    
    if weather_data:
        save_to_rdf(city_name, weather_data)
        insert_monthly_weather_into_fuseki(city_name, weather_data)
    else:
        print(f"No monthly weather data found for {city_name}.")

