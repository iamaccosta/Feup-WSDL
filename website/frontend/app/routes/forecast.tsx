import { useLoaderData, Link } from "@remix-run/react";
import { Carousel, CarouselContent, CarouselItem, CarouselNext, CarouselPrevious } from "~/components/ui/carousel";



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

    const response2 = await fetch(`http://localhost:5000/${city}/forecast`, {
      method: 'GET',
      headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
      },
    })

    const diaryReport = await response2.json()

    return {
      forecastUrl: `http://localhost:5000/${city}/monthlyweathersummary`,
      precipitationUrl: `http://localhost:5000/${city}/get-precipitation`,
      currentWeather: currentCondition,
      diaryReport: diaryReport,
    }
}

export default function ForecastChart() {
    const { forecastUrl, precipitationUrl, currentWeather, diaryReport } = useLoaderData<typeof clientLoader>();

    return (
      <div className="min-h-dvh flex flex-col items-center bg-gradient-to-br from-purple-500 via-blue-400 to-blue-600 text-gray-100">
        <header className="text-center my-6">
          <h2 className="text-4xl font-extrabold">Forecast</h2>
          <h4>Current Temperature: {currentWeather.currentTemperature} ºC</h4>
          <h5>Current Condition: {currentWeather.currentWeatherCondition}</h5>
        </header>
  
        <div className="flex flex-col md:flex-row gap-6 px-4">
          <div className="flex-1 text-center">
            <h3 className="text-lg font-semibold mb-4">Mean Monthly Temperature</h3>
            {forecastUrl ? (
              <img
                src={forecastUrl}
                alt="Mean Monthly Temperature Chart"
                className="max-w-full h-auto rounded-lg shadow-lg"
                content="image/png"/>
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
                className="max-w-full h-auto rounded-lg shadow-lg"/>
            ) : (
              <p className="text-center text-gray-300">Loading precipitation chart...</p>
            )}
          </div>
        </div>
  
        <section className="mt-8 text-gray-100" role="region" aria-labelledby="diary-report-heading">
          <h3 id="diary-report-heading" className="text-2xl font-semibold text-center mb-6">
            Diary Report
          </h3>
          <Carousel className="relative max-w-4xl mx-auto">
            <CarouselContent className="flex">
              {diaryReport.map((entry, index) => {
                const nextEntry = diaryReport[index + 1];
                return (
                  index % 2 === 0 && (
                    <CarouselItem key={index} className="flex gap-8 p-4">
                      <div className="flex-1">
                        <h4 className="text-xl font-bold mb-2">{entry.date}</h4>
                        <p className="text-md">
                          <strong>Condition:</strong> {entry.condition}
                        </p>
                        <p className="text-md">
                          <strong>Mean Temperature:</strong>{" "}
                          {parseFloat(entry.meanT).toFixed(1)} ºC
                        </p>
                        <p className="text-md">
                          <strong>Mean Wind:</strong> {parseFloat(entry.meanWind).toFixed(1)}{" "}
                          m/s
                        </p>
                      </div>
  
                      {nextEntry && (
                        <div className="flex-1">
                          <h4 className="text-xl font-bold mb-2">{nextEntry.date}</h4>
                          <p className="text-md">
                            <strong>Condition:</strong> {nextEntry.condition}
                          </p>
                          <p className="text-md">
                            <strong>Mean Temperature:</strong>{" "}
                            {parseFloat(nextEntry.meanT).toFixed(1)} ºC
                          </p>
                          <p className="text-md">
                            <strong>Mean Wind:</strong>{" "}
                            {parseFloat(nextEntry.meanWind).toFixed(1)} m/s
                          </p>
                        </div>
                      )}
                    </CarouselItem>
                  )
                );
              })}
            </CarouselContent>
            <CarouselPrevious />
            <CarouselNext />
          </Carousel>
        </section>
      </div>
  );
}