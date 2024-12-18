from flask import Flask, request, jsonify, Response
import requests
import matplotlib.pyplot as plt
import multiprocessing
import functools

from . import plots

app = Flask(__name__)

SPARQL_ENDPOINT = "http://fuseki:3030/smartcity-kb/query"

render_pool = multiprocessing.Pool(processes=2)

def on_render_pool(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return render_pool.apply(func, args, kwargs)
    return wrapper

generate_forecast = on_render_pool(plots.generate_forecast)
generate_precipitation = on_render_pool(plots.generate_precipitation)

@app.route("/")
def hello_world():
    return "Hello World!"


@app.route('/get-staticinfo')
def get_staticinfo():

    city = request.args.get('q')

    query = f"""
    PREFIX sckb: <http://example.org/smartcity#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?label ?description 
    WHERE {{
        sckb:{city} rdfs:label ?label .
        sckb:{city} sckb:description ?description .
    }}
    """
    try:
        params = {"query": query}
        headers = {"Accept": "application/sparql-results+json"}
        
        response = requests.get(SPARQL_ENDPOINT, params=params, headers=headers)

        if response.status_code == 200:
            data = response.json()

            label = data['results']['bindings'][0]['label']['value']
            description = data['results']['bindings'][0]['description']['value']
           
            return jsonify({
                'city': city,
                'label': label,
                'description': description
            }), 200
                
        else:
            return f"Error: {response.status_code}, {response.text}"
    except Exception as e:
        return f"Error performing query: {e}"   

@app.route('/get-currentWeather')
def get_currentWeather():
    city = request.args.get('q')

    query =f"""
    PREFIX sckb: <http://example.org/smartcity#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?currentTemp ?cond 
    WHERE {{
        sckb:{city} sckb:currentTemperature ?currentTemp .
  		sckb:{city} sckb:currentWeatherCondition ?cond .
    }}
    """
    try:
        params = {"query": query}
        headers = {"Accept": "application/sparql-results+json"}

        response = requests.get(SPARQL_ENDPOINT, params=params, headers=headers)
        
        if response.status_code == 200:
            data = response.json()

            currentTemp = data['results']['bindings'][0]['currentTemp']['value']
            currentCondition = data['results']['bindings'][0]['cond']['value']
           
            return ({
                'currentTemp': currentTemp,
                'currentCondition': currentCondition,
            })
                
        else:
            return f"Error: {response.status_code}, {response.text}"
    except Exception as e:
        return f"Error performing query: {e}"   


@app.route('/get-forecast')
def get_forecast():

    # Need to change this, after check if chart appears in the backend
    city = request.args.get('q')

    query = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX sckb: <http://example.org/smartcity#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?monthLabel (MAX(?highCValue) AS ?highTemp) (MIN(?lowCValue) AS ?lowTemp) (SAMPLE(?meanCValue) AS ?meanTemp)
    WHERE {{
        ?month a sckb:MonthlyWeatherSummary ;
            rdfs:label ?monthLabel ;
            sckb:highC ?highC ;
            sckb:lowC ?lowC ;
            sckb:meanC ?meanC ;
            sckb:belongsTo sckb:Barcelona ;

    BIND(xsd:float(?highC) AS ?highCValue)
    BIND(xsd:float(?lowC) AS ?lowCValue)
    BIND(xsd:float(?meanC) AS ?meanCValue)
    }}
    GROUP BY ?monthLabel
    ORDER BY ?monthLabel
    """

    try:
        params = {"query": query}
        headers = {"Accept": "application/sparql-results+json"}

        response = requests.get(SPARQL_ENDPOINT, params=params, headers=headers)

        if response.status_code == 200:
            data = response.json()['results']['bindings']

            months = [entry['monthLabel']['value'] for entry in data]
            meanC = [float(entry['meanTemp']['value']) for entry in data]
            highC = [float(entry['highTemp']['value']) for entry in data]
            lowC = [float(entry['lowTemp']['value']) for entry in data]

            month_order = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
            sorted_data = sorted(zip(months, meanC, highC, lowC), key=lambda x: month_order.index(x[0]))

            temperature_chart = generate_forecast(sorted_data) 
            return Response(temperature_chart.getvalue(), mimetype='image/png')
         
        else:
            return f"Error: {response.status_code}, {response.text}"
    except Exception as e:
        return f"Error performing query: {e}"
    


@app.route('/get-precipitation')
def get_precipitation():

     # Need to change this, after check if chart appears in the backend
    city = request.args.get('q')

    query = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX sckb: <http://example.org/smartcity#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?monthLabel (SAMPLE(?precipDays) AS ?sPrecipDays) (SAMPLE(?precipMm) AS ?sPrecipMm)
    WHERE {
            ?month a sckb:MonthlyWeatherSummary ;
            rdfs:label ?monthLabel ;
            sckb:precipitationDays ?precipDays ;
            sckb:precipitationMm ?precipMm ;
            sckb:belongsTo sckb:Barcelona ;
    }
    GROUP BY ?monthLabel 
    ORDER BY ?monthLabel
    """

    try:
        params = {"query": query}
        headers = {"Accept": "application/sparql-results+json"}

        response = requests.get(SPARQL_ENDPOINT, params=params, headers=headers)
        
        if response.status_code == 200:
            data = response.json()['results']['bindings']

            months = [entry['monthLabel']['value'] for entry in data]
            precipDays = [float(entry['sPrecipDays']['value']) for entry in data]
            precipMm = [float(entry['sPrecipMm']['value']) for entry in data]

            month_order = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
            sorted_data = sorted(zip(months, precipDays, precipMm), key=lambda x: month_order.index(x[0]))

            precipitation_chart = generate_precipitation(sorted_data) 
            return Response(precipitation_chart.getvalue(), mimetype='image/png')

        else:
            return f"Error: {response.status_code}, {response.text}"
    except Exception as e:
        return f"Error performing query: {e}"
