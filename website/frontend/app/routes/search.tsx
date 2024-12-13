import { LoaderFunctionArgs } from "@remix-run/node";
import { useLoaderData } from "@remix-run/react";

export async function loader({ request }: LoaderFunctionArgs) {
    const url = new URL(request.url);
    
    const query = url.searchParams.get("q");
    if (!query) {
        throw new Response("A search query must be provided", { status: 400 });
    }

    try {
        const response = await fetch('http://localhost:5000/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/ld+json',
            },
            body: JSON.stringify({query})
        })

        if (!response.ok) {
            throw new Response("Failed fetching search results", { status: response.status });
        }

        //TODO: Parse the RDF and show the information

    } catch (error) {
        throw new Response('Error fetching search results', { status: 500 });
    }
    
}

export default function Search() {
    const data = useLoaderData<typeof loader>();

    return (
        <p>You searched for {data.query}</p>
    )
}