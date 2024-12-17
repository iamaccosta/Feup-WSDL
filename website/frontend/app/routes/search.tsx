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
    const {results} = useLoaderData<typeof loader>();

    return (
        <div className="h-dvh bg-gradient-to-br from-purple-500 via-blue-400 to-blue-600 text-gray-100 flex flex-col">
    
            <header className="p-6 text-center">
                <h1 className="text-5xl font-extrabold">Barcelona</h1>
            </header>

            <div className="flex-1 flex flex-col items-center justify-start p-6 overflow-y-auto">
                <div className="flex flex-col gap-6 text-lg max-w-4xl">
            
                <p className="text-sm text-justify text-gray-200">
                  <strong>Abstract:</strong>{" "}
                    {"Barcelona (/\u02ccb\u0251\u02d0rs\u0259\u02c8lo\u028an\u0259/ BAR-s\u0259-LOH-n\u0259, Catalan: [b\u0259\u027es\u0259\u02c8lon\u0259], Spanish: [ba\u027e\u03b8e\u02c8lona]) is a city on the coast of northeastern Spain. It is the capital and largest city of the autonomous community of Catalonia, as well as the second most populous municipality of Spain. With a population of 1.6 million within city limits, its urban area extends to numerous neighbouring municipalities within the Province of Barcelona and is home to around 4.8 million people, making it the fifth most populous urban area in the European Union after Paris, the Ruhr area, Madrid, and Milan. It is one of the largest metropolises on the Mediterranean Sea, located on the coast between the mouths of the rivers Llobregat and Bes\u00f2s, and bounded to the west by the Serra de Collserola mountain range, the tallest peak of which is 512 metres (1,680 feet) high. Founded as a Roman city, in the Middle Ages Barcelona became the capital of the County of Barcelona. After joining with the Kingdom of Aragon to form the confederation of the Crown of Aragon, Barcelona, which continued to be the capital of the Principality of Catalonia, became the most important city in the Crown of Aragon and the main economic and administrative centre of the Crown, only to be overtaken by Valencia, wrested from Arab domination by the Catalans, shortly before the dynastic union between the Crown of Castile and the Crown of Aragon in 1492. Barcelona has a rich cultural heritage and is today an important cultural centre and a major tourist destination. Particularly renowned are the architectural works of Antoni Gaud\u00ed and Llu\u00eds Dom\u00e8nech i Montaner, which have been designated UNESCO World Heritage Sites. The city is home to two of the most prestigious universities in Spain: the University of Barcelona and Pompeu Fabra University. The headquarters of the Union for the Mediterranean are located in Barcelona. The city is known for hosting the 1992 Summer Olympics as well as world-class and also many international sport tournaments. Barcelona is a major cultural, economic, and financial centre in southwestern Europe, as well as the main biotech hub in Spain. As a leading world city, Barcelona's influence in global socio-economic affairs qualifies it for global city status (Beta +). Barcelona is a transport hub, with the Port of Barcelona being one of Europe's principal seaports and busiest European passenger port, an international airport, Barcelona\u2013El Prat Airport, which handles over 50 million passengers per year, an , and a high-speed rail line with a link to France and the rest of Europe."}
                  
                </p>
                <p className="text-gray-200">
                  <strong>Current Temperature:</strong>{" "}
                    { `12°C` }
                </p>
                <p className="text-gray-200">
                  <strong>Current Humidity:</strong>{" "}
                    {`15.3%`}
                </p>
              </div>
            
          </div>
        </div>
    )
}