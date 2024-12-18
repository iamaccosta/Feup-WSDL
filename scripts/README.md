# Information about the Scripts

To test every feature you must use 'Barcelona' or 'barcelona' as `<city-name>`.

---

### DBPedia Static Data
The script `dbpedia_static.py` collects the static data required for a city.
- description
- lat
- long

**Run** `python/python3 dbpedia_static.py <city-name>`

#
### DBPedia Monthly Weather Summary
The script `dbpedia_dynamic.py` collects the monthly weather summary of a city. Assuming that these values are oftenly updated, for the future relevance the script should run every 24 hours.<br>
Monthly Weather Summary: (a sckb:MonthlyWeatherSummary)
- HighC 
- LowC
- MeanC
- PrecipitationDays
- PrecipitationMm

> The parameters presented exists for every month.

**Run** `python/python3 dbpedia_dynamic.py <city-name>`

#
### OpenWeatherMap API - Current Weather Conditions
The script `owm_current_weather.py` collects the current weather conditions for a city from the OpenWeatherMap API.
- current_temperature
- current_humidity
- current_weatherCondition -> `Sky Info`
- current_windSpeed

**Run** `python/python3 owm_current_weather.py <city-name>`

#
### OpenWeatherMap API - Forecasts
The scrpit `owm_forecast.py` collects the forecasts for the next 5 days for a city, presenting a set of values for each 3 hours.<br>
Forecast: (a sckb:Forecast)
- temperature
- humidity
- weatherCondition -> `Sky Info`
- windSpeed

**Run** `python/python3 owm_forecasts.py <city-name>`

#
### Bus Stops Information
The script `bus_info.py` collects the bus stops of a city. Each bus stop contains the next bus information. for performance purposes the script uses **multithreading** for the operation of data collection.<br>
Bus Stop: (a sckb:BusStop)
- stopId
- stopName -> `Stop Name and Destination`
- lat
- long
- hasNextBus -> `Array with Next Bus`

Next Bus Information: (a sckb:BusInfo)
- destination
- line
- timeInMinutes -> `Time left in Minutes for its Arrival`

**Run** `python/python3 bus_info.py <city-name>`

#
## Examples of Queries
> **host-name** may be the name of Docker container if running queries from other container.

### Apache Jena Fuseki SELECT Query

#### GET
- endpoint: <http://host-name:port/DB-name/query>
- params: `{"query": query}`

```
endpoint = "http://localhost:3030/smartcity/query"
query = """
PREFIX sckb: <http://example.org/smartcity#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?temperature
WHERE {
    sckb:Barcelona sckb:currentTemperature ?temperature .
}
"""

params = {"query": query}
response = requests.get(endpoint, params=params)
```

#### POST
- endpoint: <http://host-name:port/DB-name/query>
- data: query
- headers: `{"Content-Type": "application/sparql-query"}`

```
endpoint = "http://localhost:3030/smartcity/query"
query = """
PREFIX sckb: <http://example.org/smartcity#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?temperature
WHERE {
    sckb:Barcelona sckb:currentTemperature ?temperature .
}
"""

headers = {"Content-Type": "application/sparql-query"}
response = requests.post(endpoint, data=query, headers=headers)
```

#
### Apache Jena Fuseki Update Query

#### POST
- endpoint: <http://host-name:port/DB-name/update>
- data: query
- headers: `{"Content-Type": "application/sparql-update"}`
- auth: HTTPBasicAuth(username, password)

```
endpoint = "http://localhost:3030/smartcity-kb/update"
query = f"""
PREFIX sckb: <http://example.org/smartcity#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

DELETE {{
    {city_uri} sckb:currentTemperature ?oldTemperature ;
                sckb:currentHumidity ?oldHumidity ;
                sckb:currentWeatherCondition ?oldCondition ;
                sckb:currentWindSpeed ?oldWindSpeed .
}}
INSERT {{
    {city_uri} a sckb:City ;
                sckb:currentTemperature "{weather_info['current_temperature']}"^^xsd:float ;
                sckb:currentHumidity "{weather_info['current_humidity']}"^^xsd:float ;
                sckb:currentWeatherCondition "{weather_info['current_weather']}"^^xsd:string ;
                sckb:currentWindSpeed "{weather_info['current_wind_speed']}"^^xsd:float ;
                sckb:linkedTo {dbpedia_link} .
}}
WHERE {{
    OPTIONAL {{
        {city_uri} sckb:currentTemperature ?oldTemperature ;
                    sckb:currentHumidity ?oldHumidity ;
                    sckb:currentWeatherCondition ?oldCondition ;
                    sckb:currentWindSpeed ?oldWindSpeed .
    }}
}}
"""

headers = {"Content-Type": "application/sparql-update"}
        
username = "admin"
password = "smartcity-kb"

response = requests.post(endpoint, data=query, headers=headers, auth=HTTPBasicAuth(username, password))
```