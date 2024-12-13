from flask import Flask, request, jsonify
import requests
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

SPARQL_ENDPOINT = "http://fuseki:3030/smartcity-kb/query"

@app.route("/")
def hello_world():
    return "Hello World!"

@app.route('/search')
def search():
    
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
        response = requests.get(SPARQL_ENDPOINT, params=params)

        if response.status_code == 200:
            return f"Response: {response.text}"
        else:
            return f"Error: {response.status_code}, {response.text}"
    except Exception as e:
        return f"Error performing query: {e}"

    
    # query = """
    # PREFIX dbo: <http://dbpedia.org/ontology/>
    # PREFIX dbpedia: <http://dbpedia.org/resource/>

    # SELECT ?temperature
    # WHERE {
    # dbpedia:Barcelona dbo:current_temperature ?temperature .
    # }
    # """

    # try:
    #     username = "admin"
    #     password = "smartcity-kb"
    #     params = {"query": query}
    #     headers = {"Content-Type": "application/sparql-query"}
    #     response = requests.post(SPARQL_ENDPOINT, params=params, auth=HTTPBasicAuth(username, password))

    #     if response.status_code == 200:
    #         return "Response:", response.text
    #     else:
    #         return f"Error: {response.status_code}, {response.text}"
    # except Exception as e:
    #     return f"Error performing query: {e}"   
    

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
