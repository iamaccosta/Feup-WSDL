from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
import os


app = Flask(__name__)
CORS(app)

APACHE_URL = 'http://localhost:3030'

@app.route("/")
def hello_world():
    return "Hello World!"

@app.route('/api/search', methods=['POST'])
def search():
    data = request.get_json()
    query = data.get('query')

    if not query:
        return jsonify({'error': 'Missing search query'}), 400

    #TODO: Build the query to APACHE JENA
        
    print("QUERYYYYYY " + query)
    return  
