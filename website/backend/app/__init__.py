from flask import Flask, request, jsonify
import requests
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

SPARQL_ENDPOINT = "http://fuseki:3030/smartcity-kb/query"

@app.route("/")
def hello_world():
    return "Hello World!"

@app.route('/get-staticinfo')
def get_staticinfo():
    
    query = """
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX dbpedia: <http://dbpedia.org/resource/>

    SELECT ?abstract ?temperature ?humidity ?weather ?wind
    WHERE {
        dbpedia:Barcelona dbo:abstract ?abstract .
        dbpedia:Barcelona dbo:current_temperature ?temperature .
        dbpedia:Barcelona dbo:current_humidity ?humidity .
        dbpedia:Barcelona dbo:current_weatherCondition ?weatherCondition .
        dbpedia:Barcelona dbo:current_windSpeed ?windSpeed .
    }
    """
    try:
        params = {"query": query}
        response = requests.get(SPARQL_ENDPOINT, params=params)

        if response.status_code == 200:
            data = response.json()

            abstract = data['results']['bindings'][0]['abstract']['value']
            current_temp = data['results']['bindings'][0]['temperature']['value']
            current_humidity = data['results']['bindings'][0]['humidity']['value']
            # current_weatherCondition = data['results']['bindings'][0]['weather']['value']
            # current_windSpeed = data['results']['bindings'][0]['wind']['value']

            return jsonify({
                'abstract': abstract, 
                'current_temp': current_temp, 
                'current_humidity': current_humidity,
                # 'current_weather': current_weatherCondition,
                # 'current_windSpeend': current_windSpeed
                }), 200
        else:
            return f"Error: {response.status_code}, {response.text}"
    except Exception as e:
        return f"Error performing query: {e}"   




# def direct_sparql_query_get(endpoint):
#     query = """
#     PREFIX dbo: <http://dbpedia.org/ontology/>
#     PREFIX dbpedia: <http://dbpedia.org/resource/>

#     SELECT ?temperature ?humidity ?weatherCondition ?windSpeed
#     WHERE {
#         dbpedia:Barcelona dbo:current_temperature ?temperature .
#         dbpedia:Barcelona dbo:current_humidity ?humidity .
#         dbpedia:Barcelona dbo:current_weatherCondition ?weatherCondition .
#         dbpedia:Barcelona dbo:current_windSpeed ?windSpeed .
#     }
#     """
#     try:
#         params = {"query": query}
#         response = requests.get(endpoint, params=params)

#         if response.status_code == 200:
#             print("Response:", response.text)
#         else:
#             print(f"Error: {response.status_code}, {response.text}")
#     except Exception as e:
#         print(f"Error performing query: {e}")
