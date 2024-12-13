from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

SPARQL_ENDPOINT = "http://localhost:3030/dataset/smartcity-kb/query"

@app.route("/")
def hello_world():
    return "Hello World!"

@app.route('/search')
def search():

    query = 'barcelona'

    if not query:
        return jsonify({'error': 'Missing search query'}), 400
        
    sparql_query = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT * WHERE {{?sub ?pred ?obj .}} 
        LIMIT 2
        """
    
    response = requests.post(SPARQL_ENDPOINT, data={
        'query': sparql_query
    }, headers={
        'Accept': 'application/json'
    })

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch data from server"}), response.status_code

    results = response.json()
    return jsonify(results)


