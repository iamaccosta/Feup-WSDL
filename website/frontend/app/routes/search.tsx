import { LoaderFunctionArgs } from "@remix-run/node";
import { useLoaderData } from "@remix-run/react";

export function loader({ request }: LoaderFunctionArgs) {
    const url = new URL(request.url);
    
    const query = url.searchParams.get("q");
    if (!query) {
        throw new Response("A search query must be provided", { status: 400 });
    }

    // Make a request to the Python backend here
    // const response = await fetch(..., {
    // 
    // }
    
    return { query };
}

export default function Search() {
    const data = useLoaderData<typeof loader>();

    return (
        <p>You searched for {data.query}</p>
    )
}