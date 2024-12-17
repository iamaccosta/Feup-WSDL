import { LoaderFunctionArgs } from "@remix-run/node";
import { useLoaderData, Link } from "@remix-run/react";

export async function loader() {
    try {
        const response = await fetch('http://backend:5000/get-forecast', {
            method: 'GET',
            headers: {
                'Accept': 'image/png',
            },
        });

        if (!response.ok) {
            throw new Response("Failed fetching chart", { status: response.status });
        }

        const imageBlob = await response.blob();
        const imageUrl = URL.createObjectURL(imageBlob);

        console.log(imageUrl)

        return { imageUrl }; // Return the image URL for use in the component

    } catch (error) {
        console.error("Error fetching chart:", error);
        throw new Response('Error fetching chart', { status: 500 });
    }
}

export default function ForecastChart() {
    const { imageUrlTemp } = useLoaderData();

    return (
        <div className="h-dvh bg-gradient-to-br from-purple-500 via-blue-400 to-blue-600 text-gray-100 flex flex-col p-6">
          
          <header className="text-center mb-6">
            <h2 className="text-4xl font-extrabold">Forecast</h2>
          </header>
    
          
          <div className="flex flex-col md:flex-row gap-6">
            
            <div className="flex-1 text-center">
              <h3 className="text-lg font-semibold mb-4">Mean Monthly Temperature</h3>
              {imageUrlTemp ? (
                <img
                  src={imageUrlTemp}
                  alt="Mean Monthly Temperature Chart"
                  className="max-w-full h-auto rounded-lg shadow-lg"
                />
              ) : (
                <p className="text-center text-gray-300">Loading temperature chart...</p>
              )}
            </div>
    
            
            <div className="flex-1 text-center">
              <h3 className="text-lg font-semibold mb-4">Precipitation Monthly</h3>
              
            </div>
          </div>
        </div>
    );
}