from flask import Flask, request, jsonify, Response, abort, make_response
import requests
import matplotlib.pyplot as plt
import multiprocessing
import functools
from flask_cors import CORS
import json

from . import plots

app = Flask(__name__)
CORS(app)

SPARQL_ENDPOINT = "http://fuseki:3030/smartcity-kb/query"
JENA_SUPPORTED_CONTENT_TYPES = [
    "application/sparql-results+json",
    "application/json",
    "text/turtle",
    "text/plain",
    "application/rdf+xml",
    "application/xml",
    "text/csv",
    "text/tsv"
]

render_pool = multiprocessing.Pool(processes=2)

def on_render_pool(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return render_pool.apply(func, args, kwargs)
    return wrapper

generate_forecast = on_render_pool(plots.generate_forecast)
generate_precipitation = on_render_pool(plots.generate_precipitation)

def get_sparql_results(query: str, accept: str):
    params = {"query": query}
    headers = {"Accept": accept}
    
    try:
        response = requests.get(SPARQL_ENDPOINT, params=params, headers=headers, timeout=10)
    
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"Error performing query: {e}")
        
    return None

def content_negotiation(handled_content_type: str, query: str):
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            accept = request.headers.get('Accept')
            accept = None if accept == handled_content_type or accept not in JENA_SUPPORTED_CONTENT_TYPES else accept
            
            formatted_query = query.format(*args, **kwargs)
            
            if accept is None:
                results = get_sparql_results(formatted_query, "application/sparql-results+json")
                if results is None:
                    return abort(500)
                
                data = json.loads(results)
                return func(*args, **kwargs, data=data,)
            
            else:
                results = get_sparql_results(formatted_query, accept)
                if results is None:
                    return abort(500)
                
                response = make_response(results)
                response.headers["Content-Type"] = accept
                return response, 200
        return wrapper
    return decorator
        

@app.get('/<city>')
@content_negotiation(
    "application/json",
    """
    PREFIX sckb: <http://example.org/smartcity#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX geo1: <http://www.w3.org/2003/01/geo/wgs84_pos#>

    SELECT ?description ?currentTemperature ?currentWeatherCondition ?latitude ?longitude
    WHERE {{
        sckb:{city} sckb:description ?description .
        sckb:{city} sckb:currentTemperature ?currentTemperature .
        sckb:{city} sckb:currentWeatherCondition ?currentWeatherCondition .
        sckb:{city} geo1:lat ?latitude .
        sckb:{city} geo1:long ?longitude .
    }}
    """
)
def get_static_info(city, data):
    result = data['results']['bindings']
    if len(result) == 0:
        return abort(404)
    
    result = result[0]
    description = result['description']['value']
    current_temperature = result['currentTemperature']['value']
    current_weather_condition = result['currentWeatherCondition']['value']
    latitude = result['latitude']['value']
    longitude = result['longitude']['value']
    
    return jsonify({
        'label': city,
        'description': description,
        'currentTemperature' : current_temperature,
        'currentWeatherCondition': current_weather_condition,   
        'latitude': latitude,
        'longitude': longitude
    })  


@app.route('/<city>/forecast')
@content_negotiation(
    "application/json",
    """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX sckb: <http://example.org/smartcity#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT 
        ?date
        (AVG(xsd:float(?temperature)) AS ?avgTemperature)
        (AVG(xsd:float(?humidity)) AS ?avgHumidity)
        (AVG(xsd:float(?windSpeed)) AS ?avgWindSpeed)
        (GROUP_CONCAT(DISTINCT ?weatherCondition; SEPARATOR=", ") AS ?conditions)
    WHERE {{
        ?forecast a sckb:Forecast ;
                sckb:belongsTo sckb:{city} ;
                sckb:temperature ?temperature ;
                sckb:humidity ?humidity ;
                sckb:windSpeed ?windSpeed ;
                sckb:weatherCondition ?weatherCondition .
        BIND(SUBSTR(STR(?forecast), 1, STRLEN(STR(?forecast)) - STRLEN(STRAFTER(STR(?forecast), "T"))) AS ?date)
    }}
    GROUP BY ?date
    ORDER BY ?date
    """
)
def get_forec(city, data):
    
    days_in_report = []
    for entry in data['results']['bindings']:
        date = entry['date']['value'].split("/")[-1].replace("T", "")
        days_in_report.append({
            'date': date,
            'meanT': entry['avgTemperature']['value'],
            'meanWind': entry['avgWindSpeed']['value'],
            'condition': entry['conditions']['value']
        })
        
    return days_in_report


@app.route('/<city>/monthlyweathersummary')
@content_negotiation(
    "image/png",
    """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX sckb: <http://example.org/smartcity#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?monthLabel (MAX(?highCValue) AS ?highTemp) 
    (MIN(?lowCValue) AS ?lowTemp) (SAMPLE(?meanCValue) AS ?meanTemp)
    WHERE {{
        ?month a sckb:MonthlyWeatherSummary ;
            rdfs:label ?monthLabel ;
            sckb:highC ?highC ;
            sckb:lowC ?lowC ;
            sckb:meanC ?meanC ;
            sckb:belongsTo sckb:{city} ;

    BIND(xsd:float(?highC) AS ?highCValue)
    BIND(xsd:float(?lowC) AS ?lowCValue)
    BIND(xsd:float(?meanC) AS ?meanCValue)
    }}
    GROUP BY ?monthLabel
    ORDER BY ?monthLabel
    """
)
def get_forecast(city, data):
    print(data, flush=True)
    result = data['results']['bindings']

    months = [entry['monthLabel']['value'] for entry in result]
    meanC = [float(entry['meanTemp']['value']) for entry in result]
    highC = [float(entry['highTemp']['value']) for entry in result]
    lowC = [float(entry['lowTemp']['value']) for entry in result]

    month_order = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    sorted_data = sorted(zip(months, meanC, highC, lowC), key=lambda x: month_order.index(x[0]))

    temperature_chart = generate_forecast(sorted_data) 
    return Response(temperature_chart.getvalue(), mimetype='image/png')
         

@app.route('/<city>/get-precipitation')
@content_negotiation(
    "image/png",
    """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX sckb: <http://example.org/smartcity#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?monthLabel (SAMPLE(?precipDays) AS ?sPrecipDays) (SAMPLE(?precipMm) AS ?sPrecipMm)
    WHERE {{
        ?month a sckb:MonthlyWeatherSummary ;
            rdfs:label ?monthLabel ;
            sckb:precipitationDays ?precipDays ;
            sckb:precipitationMm ?precipMm ;
            sckb:belongsTo sckb:{city} ;
    }}
    GROUP BY ?monthLabel 
    ORDER BY ?monthLabel
    """
)
def get_precipitation(city, data):
    
    result = data['results']['bindings']

    months = [entry['monthLabel']['value'] for entry in result]
    precipDays = [float(entry['sPrecipDays']['value']) for entry in result]
    precipMm = [float(entry['sPrecipMm']['value']) for entry in result]

    month_order = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    sorted_data = sorted(zip(months, precipDays, precipMm), key=lambda x: month_order.index(x[0]))

    precipitation_chart = generate_precipitation(sorted_data) 
    return Response(precipitation_chart.getvalue(), mimetype='image/png')

       
@app.route('/<city>/BusStop')
@content_negotiation(
    "application/json",
    """
    PREFIX geo1: <http://www.w3.org/2003/01/geo/wgs84_pos#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX sckb: <http://example.org/smartcity#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT DISTINCT ?busStopId ?label ?latitude ?longitude
    WHERE {{
    ?busStop a sckb:BusStop ;
        sckb:busStopId ?busStopId ;
        rdfs:label ?label ;
        sckb:isLocatedIn sckb:{city} ;
        geo1:lat ?latitude ;
        geo1:long ?longitude .
    }}
    """
)
def get_busstations(city, data):

    def func(result):
        busStopName = result['label']['value']
        latitude = result['latitude']['value']
        longitude = result['longitude']['value']
        busStopId = result['busStopId']['value']
        
        return {
            'busStopName': busStopName,
            'latitude': latitude,
            'longitude': longitude,
            'busStopId': busStopId,
            'city': city
        }
        
    results = list(map(func, data['results']['bindings']))
    

    return results

@app.get("/<city>/BusStop/stop_<busStopId>")
@content_negotiation(
    "application/json",
    """
    PREFIX geo1: <http://www.w3.org/2003/01/geo/wgs84_pos#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX sckb: <http://example.org/smartcity#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?nextBusLabel ?destination ?line ?timeInMinutes
    WHERE {{
        ?busStop a sckb:BusStop ;
            sckb:busStopId "{busStopId}"^^xsd:string ;
            sckb:hasNextBus ?nextBus ;
            sckb:isLocatedIn sckb:{city} .

        ?nextBus a sckb:BusInfo ;
            rdfs:label ?nextBusLabel ;
            sckb:destination ?destination ;
            sckb:line ?line ;
            sckb:timeInMinutes ?timeInMinutes .
    }}
    """
)
def get_businfo(city, busStopId, data):
    result = data['results']['bindings']
    if len(result) == 0:
        return abort(404)

    result = result[0]

    next_bus_label = result['nextBusLabel']['value']
    destination = result['destination']['value']
    line = result['line']['value']
    time_in_minutes = result['timeInMinutes']['value']

    return jsonify({
        'nextBusLabel': next_bus_label,
        'destination': destination,
        'line': line,
        'timeInMinutes': time_in_minutes
    })

    return result


       