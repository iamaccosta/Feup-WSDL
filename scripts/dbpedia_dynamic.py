from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD

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
        VALUES (?month ?highProp ?lowProp ?meanProp ?precipDaysProp ?precipMmProp ?recordHighProp ?recordLowProp) {{
            ("January" dbp:janHighC dbp:janLowC dbp:janMeanC dbp:janPrecipitationDays dbp:janPrecipitationMm dbp:janRecordHighC dbp:janRecordLowC)
            ("February" dbp:febHighC dbp:febLowC dbp:febMeanC dbp:febPrecipitationDays dbp:febPrecipitationMm dbp:febRecordHighC dbp:febRecordLowC)
            ("March" dbp:marHighC dbp:marLowC dbp:marMeanC dbp:marPrecipitationDays dbp:marPrecipitationMm dbp:marRecordHighC dbp:marRecordLowC)
            ("April" dbp:aprHighC dbp:aprLowC dbp:aprMeanC dbp:aprPrecipitationDays dbp:aprPrecipitationMm dbp:aprRecordHighC dbp:aprRecordLowC)
            ("May" dbp:mayHighC dbp:mayLowC dbp:mayMeanC dbp:mayPrecipitationDays dbp:mayPrecipitationMm dbp:mayRecordHighC dbp:mayRecordLowC)
            ("June" dbp:junHighC dbp:junLowC dbp:junMeanC dbp:junPrecipitationDays dbp:junPrecipitationMm dbp:junRecordHighC dbp:junRecordLowC)
            ("July" dbp:julHighC dbp:julLowC dbp:julMeanC dbp:julPrecipitationDays dbp:julPrecipitationMm dbp:julRecordHighC dbp:julRecordLowC)
            ("August" dbp:augHighC dbp:augLowC dbp:augMeanC dbp:augPrecipitationDays dbp:augPrecipitationMm dbp:augRecordHighC dbp:augRecordLowC)
            ("September" dbp:sepHighC dbp:sepLowC dbp:sepMeanC dbp:sepPrecipitationDays dbp:sepPrecipitationMm dbp:sepRecordHighC dbp:sepRecordLowC)
            ("October" dbp:octHighC dbp:octLowC dbp:octMeanC dbp:octPrecipitationDays dbp:octPrecipitationMm dbp:octRecordHighC dbp:octRecordLowC)
            ("November" dbp:novHighC dbp:novLowC dbp:novMeanC dbp:novPrecipitationDays dbp:novPrecipitationMm dbp:novRecordHighC dbp:novRecordLowC)
            ("December" dbp:decHighC dbp:decLowC dbp:decMeanC dbp:decPrecipitationDays dbp:decPrecipitationMm dbp:decRecordHighC dbp:decRecordLowC)
        }}
        OPTIONAL {{ dbr:{city_name} ?highProp ?highC . }}
        OPTIONAL {{ dbr:{city_name} ?lowProp ?lowC . }}
        OPTIONAL {{ dbr:{city_name} ?meanProp ?meanC . }}
        OPTIONAL {{ dbr:{city_name} ?precipDaysProp ?precipitationDays . }}
        OPTIONAL {{ dbr:{city_name} ?precipMmProp ?precipitationMm . }}
        OPTIONAL {{ dbr:{city_name} ?recordHighProp ?recordHighC . }}
        OPTIONAL {{ dbr:{city_name} ?recordLowProp ?recordLowC . }}
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
    g.bind("dbp", DBP)
    
    # Create city URI
    city_uri = URIRef(DBPEDIA + city_name)
    climate_uri = URIRef(city_uri + "/climate")
    
    # Add monthly weather data
    for entry in weather_data:
        month = entry["month"]["value"]
        month_uri = URIRef(climate_uri + f"/{month}")
        
        g.add((month_uri, RDF.type, DBP.Climate))
        g.add((month_uri, RDFS.label, Literal(month)))
        
        if "highC" in entry:
            g.add((month_uri, DBP[month.lower() + "HighC"], Literal(float(entry["highC"]["value"]), datatype=XSD.float)))
        if "lowC" in entry:
            g.add((month_uri, DBP[month.lower() + "LowC"], Literal(float(entry["lowC"]["value"]), datatype=XSD.float)))
        if "meanC" in entry:
            g.add((month_uri, DBP[month.lower() + "MeanC"], Literal(float(entry["meanC"]["value"]), datatype=XSD.float)))
        if "precipitationDays" in entry:
            g.add((month_uri, DBP[month.lower() + "PrecipitationDays"], Literal(float(entry["precipitationDays"]["value"]), datatype=XSD.float)))
        if "precipitationMm" in entry:
            g.add((month_uri, DBP[month.lower() + "PrecipitationMm"], Literal(float(entry["precipitationMm"]["value"]), datatype=XSD.float)))
        if "recordHighC" in entry:
            g.add((month_uri, DBP[month.lower() + "RecordHighC"], Literal(float(entry["recordHighC"]["value"]), datatype=XSD.float)))
        if "recordLowC" in entry:
            g.add((month_uri, DBP[month.lower() + "RecordLowC"], Literal(float(entry["recordLowC"]["value"]), datatype=XSD.float)))
    
    # Save graph to a TTL file
    filename = f"./data/{city_name}_monthly_weather.ttl"
    g.serialize(destination=filename, format="turtle")
    print(f"Monthly weather data for {city_name} saved to {filename}")

# Main script
if __name__ == "__main__":
    city_name = "Barcelona"  # Replace with the desired city name
    weather_data = get_monthly_weather_conditions(city_name)
    
    if weather_data:
        save_to_rdf(city_name, weather_data)
    else:
        print(f"No monthly weather data found for {city_name}.")
