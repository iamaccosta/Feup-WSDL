import sys
import requests
from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS
from requests.auth import HTTPBasicAuth

# Define namespaces
DBPEDIA = Namespace("http://dbpedia.org/resource/")
DBPEDIA_ONT = Namespace("http://dbpedia.org/ontology/")
GEO = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")
SCKB = Namespace("http://example.org/smartcity#")

# SPARQL endpoint for DBpedia
sparql = SPARQLWrapper("http://dbpedia.org/sparql")

# Function to retrieve static city data
def get_static_city_data(city_name):
    query = f"""
    SELECT ?name ?description ?latitude ?longitude
    WHERE {{
        dbr:{city_name} rdfs:label ?name .
        dbr:{city_name} dbo:abstract ?description .
        dbr:{city_name} geo:lat ?latitude .
        dbr:{city_name} geo:long ?longitude .
        FILTER (lang(?name) = 'en' && lang(?description) = 'en')
    }}
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    if results["results"]["bindings"]:
        return results["results"]["bindings"][0]
    else:
        return None

# Function to save data as RDF/Turtle
def save_to_rdf(city_name, data):
    g = Graph()
    
    # Bind namespaces
    g.bind("dbpedia", DBPEDIA)
    g.bind("dbo", DBPEDIA_ONT)
    g.bind("geo", GEO)
    g.bind("sckb", SCKB)
    
    # Custom and external URIs
    city_uri = URIRef(SCKB + city_name.replace(" ", "_"))  # Custom URI for the city
    dbpedia_uri = URIRef(DBPEDIA + city_name.replace(" ", "_"))  # External DBpedia link

    # Add data to graph
    g.add((city_uri, RDF.type, SCKB.City))
    g.add((city_uri, RDFS.label, Literal(data["name"]["value"], lang="en")))
    g.add((city_uri, SCKB.description, Literal(data["description"]["value"], lang="en")))
    g.add((city_uri, GEO.lat, Literal(data["latitude"]["value"], datatype=XSD.float)))
    g.add((city_uri, GEO.long, Literal(data["longitude"]["value"], datatype=XSD.float)))
    g.add((city_uri, SCKB.linkedTo, dbpedia_uri))  # Linking to external DBpedia entity
    
    # Save graph to a TTL file
    filename = f"./data/{city_name}_static_data.ttl"
    g.serialize(destination=filename, format="turtle")
    print(f"Data for {city_name} saved to {filename}")

# Function to insert data into Fuseki
def insert_data_into_fuseki(city_name, data):
    fuseki_endpoint = "http://localhost:3030/smartcity-kb/update"
    insert_query = f"""
    PREFIX sckb: <http://example.org/smartcity#>
    PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX dbpedia: <http://dbpedia.org/resource/>

    INSERT DATA {{
        sckb:{city_name.replace(" ", "_")} a sckb:City ;
            rdfs:label "{data['name']['value']}"@en ;
            sckb:description "{data['description']['value']}"@en ;
            geo:lat "{data['latitude']['value']}"^^xsd:float ;
            geo:long "{data['longitude']['value']}"^^xsd:float ;
            sckb:linkedTo dbpedia:{city_name.replace(" ", "_")} .
    }}
    """
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
            print(f"Data for {city_name} inserted successfully into Fuseki.")
        else:
            print(f"Error inserting data into Fuseki: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Error inserting data into Fuseki: {e}")

# Main script
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <city_name>")
        sys.exit(1)

    city_name = sys.argv[1].strip().title()
    city_data = get_static_city_data(city_name)
    
    if city_data:
        save_to_rdf(city_name, city_data)
        insert_data_into_fuseki(city_name, city_data)
    else:
        print(f"No data found for {city_name}.")
