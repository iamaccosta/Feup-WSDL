from flask import Flask, request, jsonify, Response
import requests
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
        headers = {"Accept": "application/json"}
        
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

    query ="""
    PREFIX sckb: <http://example.org/smartcity#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?currentTemp ?cond 
    WHERE {
        sckb:Barcelona sckb:currentTemperature ?currentTemp .
  		sckb:Barcelona sckb:currentWeatherCondition ?cond .
    }
    """
    try:
        params = {"query": query}
        headers = {"Accept": "application/json"}

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

    # ADD CITY TO TH QUERY
    city = request.args.get('q')

    query = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX sckb: <http://example.org/smartcity#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?monthLabel (MAX(?highCValue) AS ?highTemp) (MIN(?lowCValue) AS ?lowTemp) (SAMPLE(?meanCValue) AS ?meanTemp)
    WHERE {
    ?month a sckb:MonthlyWeatherSummary ;
            rdfs:label ?monthLabel ;
            sckb:highC ?highC ;
            sckb:lowC ?lowC ;
            sckb:meanC ?meanC ;
            sckb:belongsTo sckb:Barcelona ;

    BIND(xsd:float(?highC) AS ?highCValue)
    BIND(xsd:float(?lowC) AS ?lowCValue)
    BIND(xsd:float(?meanC) AS ?meanCValue)
    }
    GROUP BY ?monthLabel
    ORDER BY ?monthLabel
    """

    try:
        params = {"query": query}
        headers = {"Accept": "application/json"}

        response = requests.get(SPARQL_ENDPOINT, params=params, headers=headers)

        if response.status_code == 200:
            data = response.json()['results']['bindings']

            months = [entry['monthLabel']['value'] for entry in data]
            meanC = [float(entry['meanTemp']['value']) for entry in data]
            highC = [float(entry['highTemp']['value']) for entry in data]
            lowC = [float(entry['lowTemp']['value']) for entry in data]

            month_order = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
            sorted_data = sorted(zip(months, meanC, highC, lowC), key=lambda x: month_order.index(x[0]))

            months_sorted, meanC_sorted, highC_sorted, lowC_sorted = zip(*sorted_data)

            plt.figure(figsize=(10, 6))
            plt.plot(months_sorted, meanC_sorted, marker='o', linestyle='-', label='Mean Temperature', color='skyblue', linewidth=2)
            plt.plot(months_sorted, highC_sorted, marker='o', linestyle='--', label='High Temperature', color='orange', linewidth=2)
            plt.plot(months_sorted, lowC_sorted, marker='o', linestyle=':', label='Low Temperature', color='purple', linewidth=2)
            plt.xlabel('Month')
            plt.ylabel('Temperature (Celsius)')
            plt.title('Monthly Temperatures')
            plt.grid(True)
            plt.xticks(rotation=45)
            plt.legend()
            plt.tight_layout()
            
            temperature_chart = io.BytesIO()
            plt.savefig(temperature_chart, format='png')
            temperature_chart.seek(0)
            plt.close()

            return Response(temperature_chart.getvalue(), mimetype='image/png')
         
        else:
            return f"Error: {response.status_code}, {response.text}"
    except Exception as e:
        return f"Error performing query: {e}"


@app.route('/get-precipitation')
def get_precipitation():

    # ADD CITY TO TH QUERY
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
        response = requests.get(SPARQL_ENDPOINT, params=params)
        
        if response.status_code == 200:
            data = response.json()['results']['bindings']

            months = [entry['monthLabel']['value'] for entry in data]
            precipDays = [float(entry['sPrecipDays']['value']) for entry in data]
            precipMm = [float(entry['sPrecipMm']['value']) for entry in data]

            month_order = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
            sorted_data = sorted(zip(months, precipDays, precipMm), 
                                 key=lambda x: month_order.index(x[0]))

            months_sorted, precipDays_sorted, precipMm_sorted = zip(*sorted_data)

            fig, ax1 = plt.subplots(figsize=(10, 6))

            ax1.bar(months_sorted, precipDays_sorted, color='skyblue', alpha=0.7, label='Precipitation Days')
            ax1.set_xlabel('Month')
            ax1.set_ylabel('Precipitation Days', color='skyblue')
            ax1.tick_params(axis='y', labelcolor='skyblue')

            ax2 = ax1.twinx()
            ax2.plot(months_sorted, precipMm_sorted, color='purple', marker='o', label='Precipitation (mm)')
            ax2.set_ylabel('Precipitation (mm)', color='purple')
            ax2.tick_params(axis='y', labelcolor='purple')

            plt.title('Monthly Precipitation')
            fig.tight_layout()

            precipitation_chart = io.BytesIO()
            plt.savefig(precipitation_chart, format='png')
            precipitation_chart.seek(0)
            plt.close()

            return Response(precipitation_chart.getvalue(), mimetype='image/png')

        else:
            return f"Error: {response.status_code}, {response.text}"
    except Exception as e:
        return f"Error performing query: {e}"
