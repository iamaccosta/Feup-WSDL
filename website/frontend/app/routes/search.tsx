import { LoaderFunctionArgs } from "@remix-run/node";
import { useLoaderData } from "@remix-run/react";

export async function loader({ request }: LoaderFunctionArgs) {
    
    const url = new URL(request.url);
    
    const query = url.searchParams.get("q");
    if (!query) {
        throw new Response("A search query must be provided", { status: 400 });
    }

    try {
        const response = await fetch('http://backend:5000/get-staticinfo', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/ld+json',
            },
            //body: JSON.stringify({query})
        })

        if (!response.ok) {
            throw new Response("Failed fetching search results", { status: response.status });
        }

        const results = await response.json()

        return results 


    } catch (error) {
        throw new Response('Error fetching search results', { status: 500 });
    }
    
}

export default function Search() {
    const results = useLoaderData<typeof loader>();


    console.log("HBCJHEFBVCHRBF", results)
    return (
        <div className="h-dvh bg-gradient-to-br from-purple-500 via-blue-400 to-blue-600 text-gray-100 flex flex-col">
    
            <header className="p-6 text-center">
                <h1 className="text-5xl font-extrabold">Barcelona</h1>
            </header>

            {
                results ? (
                <div className="flex-1 flex flex-col items-center justify-start p-6 overflow-y-auto">
                    <div className="flex flex-col gap-6 text-lg max-w-4xl">
                        <p className="text-sm text-justify text-gray-200">
                            {results.abstract || "No abstract provided"}
                        </p>
                        <p className="text-gray-200">
                        <strong>Current Temperature:</strong>{" "}
                            {results.current_temp ? `${results.current_temp}°C` : "N/A"}
                        </p>
                        <p className="text-gray-200">
                        <strong>Current Humidity:</strong>{" "}
                            {results.current_humidity ? `${results.current_humidity}%` : "N/A"}
                        </p>
                    </div>
                </div>
                ) : (
                    <p className="text-center text-gray-300 text-lg">There are no information about this city.</p>
                )
            }
        </div>
    )
}