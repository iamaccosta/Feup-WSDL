import os
import sys
import requests
from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD
from requests.auth import HTTPBasicAuth

# Define namespaces
DBPEDIA = Namespace("http://dbpedia.org/resource/")
DBP = Namespace("http://dbpedia.org/property/")

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
    
    # Bind namespaces
    g.bind("dbpedia", DBPEDIA)
    g.bind("dbp", DBP)
    g.bind("rdfs", RDFS)
    
    # Base URI for the city's climate data
    climate_base_uri = URIRef(f"{DBPEDIA}{city_name}/climate")
    
    # Add monthly weather data
    for entry in weather_data:
        month = entry["month"]["value"]
        month_uri = URIRef(f"{climate_base_uri}/{month}")
        
        g.add((month_uri, RDF.type, DBP.Climate))
        g.add((month_uri, RDFS.label, Literal(month, lang="en")))
        g.add((month_uri, DBP.month, Literal(month, datatype=XSD.string)))
        
        # Select only the first value if multiple values are present
        if "highC" in entry:
            highC = entry["highC"]["value"]
            if isinstance(highC, list):
                highC = highC[0]  # Take the first value
            g.add((month_uri, DBP.highC, Literal(float(highC), datatype=XSD.float)))
        
        if "lowC" in entry:
            lowC = entry["lowC"]["value"]
            if isinstance(lowC, list):
                lowC = lowC[0]  # Take the first value
            g.add((month_uri, DBP.lowC, Literal(float(lowC), datatype=XSD.float)))
        
        if "meanC" in entry:
            meanC = entry["meanC"]["value"]
            if isinstance(meanC, list):
                meanC = meanC[0]  # Take the first value
            g.add((month_uri, DBP.meanC, Literal(float(meanC), datatype=XSD.float)))
        
        if "precipitationDays" in entry:
            precipitationDays = entry["precipitationDays"]["value"]
            if isinstance(precipitationDays, list):
                precipitationDays = precipitationDays[0]  # Take the first value
            g.add((month_uri, DBP.precipitationDays, Literal(float(precipitationDays), datatype=XSD.float)))
        
        if "precipitationMm" in entry:
            precipitationMm = entry["precipitationMm"]["value"]
            if isinstance(precipitationMm, list):
                precipitationMm = precipitationMm[0]  # Take the first value
            g.add((month_uri, DBP.precipitationMm, Literal(float(precipitationMm), datatype=XSD.float)))
    
    # Save graph to a TTL file
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
    climate_base_uri = f"http://dbpedia.org/resource/{city_name}/climate"

    # Construct INSERT statements for each month's data
    for entry in weather_data:
        month = entry["month"]["value"]
        month_uri = f"<{climate_base_uri}/{month}>"
        statements = [
            f"{month_uri} a dbp:Climate ;",
            f"    rdfs:label \"{month}\"@en ;",
            f"    dbp:month \"{month}\"^^xsd:string ;"
        ]

        if "highC" in entry:
            statements.append(f"    dbp:highC \"{entry['highC']['value']}\"^^xsd:float ;")
        if "lowC" in entry:
            statements.append(f"    dbp:lowC \"{entry['lowC']['value']}\"^^xsd:float ;")
        if "meanC" in entry:
            statements.append(f"    dbp:meanC \"{entry['meanC']['value']}\"^^xsd:float ;")
        if "precipitationDays" in entry:
            statements.append(f"    dbp:precipitationDays \"{entry['precipitationDays']['value']}\"^^xsd:float ;")
        if "precipitationMm" in entry:
            statements.append(f"    dbp:precipitationMm \"{entry['precipitationMm']['value']}\"^^xsd:float .")
        
        insert_statements.append("\n".join(statements))

    # Construct the full INSERT DATA query
    insert_query = f"""
    PREFIX dbp: <http://dbpedia.org/property/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    INSERT DATA {{
        {" ".join(insert_statements)}
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

