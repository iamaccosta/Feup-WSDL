import { useLoaderData, Link } from "@remix-run/react";


export async function clientLoader({ request }: { request: Request }) {
    const url = new URL(request.url); 
    const city = url.searchParams.get("city");

    const response = await fetch(`http://localhost:5000/${city}`, {
      method: 'GET',
      headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
      },
    })

    const currentCondition = await response.json()
    return {
      forecastUrl: `http://localhost:5000/${city}/monthlyweathersummary`,
      precipitationUrl: `http://localhost:5000/${city}/get-precipitation`,
      currentWeather: currentCondition
    }
}

export default function ForecastChart() {
    const { forecastUrl, precipitationUrl, currentWeather } = useLoaderData<typeof clientLoader>();

    return (
        <div className="h-dvh bg-gradient-to-br from-purple-500 via-blue-400 to-blue-600 text-gray-100 flex flex-col p-6">
          
          <header className="text-center mb-6">
            <h2 className="text-4xl font-extrabold">Forecast</h2>
            <h4>Current Temperature: {currentWeather.currentTemperature} ºC</h4>
            <h5>Current Condition: {currentWeather.currentWeatherCondition} </h5>
          </header>
    
          
          <div className="flex flex-col md:flex-row gap-6">
            
            <div className="flex-1 text-center">
              <h3 className="text-lg font-semibold mb-4">Mean Monthly Temperature</h3>
              {forecastUrl ? (
                <img
                  src={forecastUrl}
                  alt="Mean Monthly Temperature Chart"
                  className="max-w-full h-auto rounded-lg shadow-lg"
                  content="image/png"
                />
              ) : (
                <p className="text-center text-gray-300">Loading temperature chart...</p>
              )}
            </div>
            
            <div className="flex-1 text-center">
              <h3 className="text-lg font-semibold mb-4">Precipitation Monthly</h3>
              {precipitationUrl ? (
                <img
                  src={precipitationUrl}
                  alt="Mean Monthly Precipitation and Density Chart"
                  className="max-w-full h-auto rounded-lg shadow-lg"
                />
              ) : (
                <p className="text-center text-gray-300">Loading temperature chart...</p>
              )}
            </div>
          </div>
        </div>
    );
}