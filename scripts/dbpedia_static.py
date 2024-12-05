from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, FOAF

# Define namespaces
DBPEDIA = Namespace("http://dbpedia.org/resource/")
DBPEDIA_ONT = Namespace("http://dbpedia.org/ontology/")
GEO = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")

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
    g.bind("dbo", DBPEDIA_ONT)
    g.bind("geo", GEO)
    g.bind("foaf", FOAF)
    
    # Create city URI
    city_uri = URIRef(DBPEDIA + city_name)
    
    # Add data to graph
    g.add((city_uri, RDFS.label, Literal(data["name"]["value"], lang="en")))
    g.add((city_uri, DBPEDIA_ONT.abstract, Literal(data["description"]["value"], lang="en")))
    g.add((city_uri, GEO.lat, Literal(data["latitude"]["value"], datatype="http://www.w3.org/2001/XMLSchema#float")))
    g.add((city_uri, GEO.long, Literal(data["longitude"]["value"], datatype="http://www.w3.org/2001/XMLSchema#float")))
    
    # Save graph to a TTL file
    filename = f"./data/{city_name}_static_data.ttl"
    g.serialize(destination=filename, format="turtle")
    print(f"Data for {city_name} saved to {filename}")

# Main script
if __name__ == "__main__":
    city_name = "Barcelona"  # Replace with the desired city name
    city_data = get_static_city_data(city_name)
    
    if city_data:
        save_to_rdf(city_name, city_data)
    else:
        print(f"No data found for {city_name}.")
