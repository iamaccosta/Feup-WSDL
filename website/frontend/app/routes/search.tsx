import { LoaderFunctionArgs } from "@remix-run/node";
import { useLoaderData, Link } from "@remix-run/react";

export async function loader({ request }: LoaderFunctionArgs) {
    
    const url = new URL(request.url);
    
    const query = url.searchParams.get("q");
    
    if (!query) {
        throw new Response("A search query must be provided", { status: 400 });
    }

    try {
        const response = await fetch(`http://backend:5000/get-staticinfo?q=${query}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/ld+json',
            },
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

    return (
        <div className="h-dvh bg-gradient-to-br from-purple-500 via-blue-400 to-blue-600 text-gray-100 flex flex-col">
    
            <header className="p-6 text-center">
                <h1 className="text-4xl font-extrabold">{results.city}</h1>
            </header>

            <div className="flex justify-center gap-6 mb-6">
                
                <Link
                to={`/forecast?city=${results.city}`}
                className="bg-purple-600 hover:bg-purple-700 text-white font-semibold py-3 px-6 rounded-lg shadow-lg transition-all"
                >
                Forecast
                </Link>

                <Link
                to="/bus-station"
                className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-3 px-6 rounded-lg shadow-lg transition-all"
                >
                Bus Station
                </Link>
            </div>

            {
                results ? (
                <div className="flex-1 flex flex-col items-center justify-start p-6 overflow-y-auto">
                    <div className="flex flex-col gap-6 text-lg max-w-4xl">
                        <p className="text-sm text-justify text-gray-200">
                            {results.description || "No abstract provided"}
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