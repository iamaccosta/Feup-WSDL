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

            # Extract months and meanC values
            months = [entry['month']['value'] for entry in data]
            meanC = [float(entry['meanC']['value']) for entry in data]

            # Sort data based on month order for better visualization
            month_order = ["January", "February", "March", "April", "May", "June", "July",
                        "August", "September", "October", "November", "December"]
            sorted_data = sorted(zip(months, meanC), key=lambda x: month_order.index(x[0]))

            # Unpack the sorted data
            months_sorted, meanC_sorted = zip(*sorted_data)

             # Generate the chart
            plt.figure(figsize=(10, 6))
            plt.plot(months_sorted, meanC_sorted, marker='o', linestyle='-', color='skyblue', linewidth=2)
            plt.xlabel('Month')
            plt.ylabel('Mean Temperature (Celsius)')
            plt.title('Mean Monthly Temperature')
            plt.grid(True)  # Add grid for better readability
            plt.xticks(rotation=45)  # Rotate x-axis labels for better visibility
            plt.tight_layout()

            # Save the chart to a BytesIO object
            img = io.BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)
            plt.close()

            # Return the image
            return Response(img.getvalue(), mimetype='image/png')

            # return data
            # abstract = data['results']['bindings'][0]['abstract']['value']
            # current_temp = data['results']['bindings'][0]['temperature']['value']
            # current_humidity = data['results']['bindings'][0]['humidity']['value']
            # # current_weatherCondition = data['results']['bindings'][0]['weather']['value']
            # # current_windSpeed = data['results']['bindings'][0]['wind']['value']

            # return jsonify({
            #     'abstract': abstract, 
            #     'current_temp': current_temp, 
            #     'current_humidity': current_humidity,
            #     # 'current_weather': current_weatherCondition,
            #     # 'current_windSpeend': current_windSpeed
            #     }), 200
         
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
