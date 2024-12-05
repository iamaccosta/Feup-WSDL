import matplotlib.pyplot as plt
from rdflib import Graph
from datetime import datetime, timedelta
import os
import sys

# Load RDF file
def load_rdf(file_path):
    g = Graph()
    g.parse(file_path, format="turtle")
    return g

# Query RDF file for forecast data
def query_forecast_data(g):
    query = """
    PREFIX dbpedia: <http://dbpedia.org/resource/>
    PREFIX dbo: <http://dbpedia.org/ontology/>

    SELECT ?datetime ?temperature ?humidity ?wind_speed ?weather_condition
    WHERE {
      ?forecast a dbo:Forecast ;
                dbo:dateTime ?datetime ;
                dbo:temperature ?temperature ;
                dbo:humidity ?humidity ;
                dbo:windSpeed ?wind_speed ;
                dbo:weatherCondition ?weather_condition .
    }
    ORDER BY ?datetime
    """
    return g.query(query)

# Filter data into separate days
def filter_data_by_day(results):
    daily_data = {}
    for row in results:
        dt = datetime.fromisoformat(str(row.datetime))
        date_key = dt.date()
        if date_key not in daily_data:
            daily_data[date_key] = []
        daily_data[date_key].append({
            "datetime": dt,
            "temperature": float(row.temperature),
            "humidity": float(row.humidity),
            "wind_speed": float(row.wind_speed),
            "weather_condition": str(row.weather_condition),
        })
    return daily_data

# Plot data for a single day
def plot_day_forecast(day_data, city_name, date_key, output_folder):
    # Prepare data for plotting
    times = [d["datetime"].strftime("%H:%M") for d in day_data]
    temperatures = [d["temperature"] for d in day_data]
    humidities = [d["humidity"] for d in day_data]
    wind_speeds = [d["wind_speed"] for d in day_data]
    weather_conditions = [d["weather_condition"] for d in day_data]

    # Create the plot
    fig, ax1 = plt.subplots(figsize=(10, 5))

    # Plot temperature on the left vertical axis
    ax1.set_xlabel("Time")
    ax1.set_ylabel("Temperature (°C) / Humidity (%) / Wind Speed (m/s)", color="red")
    ax1.set_ylim(-20, 100)  # Temperature axis range
    ax1.plot(times, temperatures, marker="o", color="red", label="Temperature (°C)")
    ax1.plot(times, humidities, marker="o", color="blue", linestyle="--", label="Humidity (%)")
    ax1.plot(times, wind_speeds, marker="o", color="green", linestyle="-.", label="Wind Speed (m/s)")
    ax1.tick_params(axis="y", labelcolor="red")

    # Create a secondary vertical axis for humidity and wind speed
    ax2 = ax1.twinx()
    ax2.set_ylabel("", color="blue")
    ax2.set_ylim(0, 100)  # Humidity and wind speed axis range
    
    ax2.tick_params(axis="y", labelcolor="blue")

    # Add labels for each point
    for i, time in enumerate(times):
        ax1.text(
            time, temperatures[i], f"{temperatures[i]:.1f}°C",
            color="red", ha="center", fontsize=8, bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="red")
        )
        ax1.text(
            time, humidities[i], f"{humidities[i]:.0f}%",
            color="blue", ha="center", fontsize=8, bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="blue")
        )
        ax1.text(
            time, wind_speeds[i], f"{wind_speeds[i]:.1f}m/s",
            color="green", ha="center", fontsize=8, bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="green")
        )

    # Add weather condition labels/icons at the top
    for i, time in enumerate(times):
        ax1.text(
            time, 45, weather_conditions[i],  # Adjust icon position above the temperature axis
            color="black", ha="center", fontsize=10, bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", edgecolor="black")
        )

    # Configure plot appearance
    ax1.set_title(f"Weather Forecast for {city_name} - {date_key}", fontsize=16)
    fig.tight_layout()

    # Save the plot to a file
    os.makedirs(output_folder, exist_ok=True)
    file_path = os.path.join(output_folder, f"{city_name.replace(' ', '_')}_{date_key}.png")
    plt.savefig(file_path, format="png")
    print(f"Forecast graphic saved to {file_path}")
    plt.close(fig)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <city_name>")
        sys.exit(1)

    city_name = sys.argv[1].strip().title()
    file_path = f"./data/{city_name.replace(' ', '_')}_forecast.ttl"
    output_folder = "./images"

    # Load RDF data and query
    g = load_rdf(file_path)
    results = query_forecast_data(g)

    # Filter and plot data for each day
    daily_forecasts = filter_data_by_day(results)
    for date_key, day_data in daily_forecasts.items():
        plot_day_forecast(day_data, city_name, date_key, output_folder)
