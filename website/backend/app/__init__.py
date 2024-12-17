from flask import Flask, request, jsonify, Response
import requests
from requests.auth import HTTPBasicAuth
import matplotlib.pyplot as plt
import io

app = Flask(__name__)

SPARQL_ENDPOINT = "http://fuseki:3030/smartcity-kb/query"

@app.route("/")
def hello_world():
    return "Hello World!"


@app.route('/get-staticinfo')
def get_staticinfo():

    city = request.args.get('q')

    query = f"""
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX dbpedia: <http://dbpedia.org/resource/>

    SELECT ?abstract ?temperature ?humidity ?weather ?wind
    WHERE {{
        dbpedia:{city} dbo:abstract ?abstract .
        dbpedia:{city} dbo:current_temperature ?temperature .
        dbpedia:{city} dbo:current_humidity ?humidity .
        dbpedia:{city} dbo:current_weatherCondition ?weatherCondition .
        dbpedia:{city} dbo:current_windSpeed ?windSpeed .
    }}
    """
    try:
        params = {"query": query}
        response = requests.get(SPARQL_ENDPOINT, params=params)

        if response.status_code == 200:
            data = response.json()

            abstract = data['results']['bindings'][0]['abstract']['value']
            current_temp = data['results']['bindings'][0]['temperature']['value']
            current_humidity = data['results']['bindings'][0]['humidity']['value']

            accept_header = request.headers.get("Accept", "application/json")

            if "application/ld+json" in accept_header:
                return jsonify({
                    '@context': 'http://schema.org',
                    'city': city,
                    'abstract': abstract,
                    'current_temp': current_temp,
                    'current_humidity': current_humidity,
                }), 200
            elif 'application/rdf+xml' in accept_header:
                return Response(response.content, content_type='application/rdf+xml')
            elif 'text/turtle' in accept_header:
                return Response(response.content, content_type='text/turtle')
            elif 'application/json' in accept_header:
                return jsonify({
                    'city': city,
                    'abstract': abstract,
                    'current_temp': current_temp,
                    'current_humidity': current_humidity,
                }), 200
            else:
                return jsonify({
                    'city': city,
                    'abstract': abstract,
                    'current_temp': current_temp,
                    'current_humidity': current_humidity,
                }), 200
                
        else:
            return f"Error: {response.status_code}, {response.text}"
    except Exception as e:
        return f"Error performing query: {e}"   


@app.route('/get-forecast')
def get_forecast():

    query = """
    PREFIX dbp: <http://dbpedia.org/property/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?month ?highC ?lowC ?meanC ?precipitationDays ?precipitationMm
    WHERE {
        ?climate a dbp:Climate ;
                rdfs:label ?month ;
                dbp:highC ?highC ;
                dbp:lowC ?lowC ;
                dbp:meanC ?meanC ;
                dbp:precipitationDays ?precipitationDays ;
                dbp:precipitationMm ?precipitationMm .
    }
    ORDER BY ?month
    """

    try:
        params = {"query": query}
        response = requests.get(SPARQL_ENDPOINT, params=params)

        if response.status_code == 200:
            data = response.json()['results']['bindings']

            months = [entry['month']['value'] for entry in data]
            meanC = [float(entry['meanC']['value']) for entry in data]

            month_order = ["January", "February", "March", "April", "May", "June", "July",
                        "August", "September", "October", "November", "December"]
            sorted_data = sorted(zip(months, meanC), key=lambda x: month_order.index(x[0]))

            months_sorted, meanC_sorted = zip(*sorted_data)

            plt.figure(figsize=(10, 6))
            plt.plot(months_sorted, meanC_sorted, marker='o', linestyle='-', color='skyblue', linewidth=2)
            plt.xlabel('Month')
            plt.ylabel('Mean Temperature (Celsius)')
            plt.title('Mean Monthly Temperature')
            plt.grid(True)
            plt.xticks(rotation=45) 
            plt.tight_layout()
            
            img = io.BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)
            plt.close()

            return Response(img.getvalue(), mimetype='image/png')
         
        else:
            return f"Error: {response.status_code}, {response.text}"
    except Exception as e:
        return f"Error performing query: {e}"

