import { useLoaderData } from "@remix-run/react";
import { getStaticInfo } from "~/lib/requests";

export async function clientLoader({ params }: { params: { city: string } }) {
    const info = await getStaticInfo(params.city);
    if (info === null) {
        return new Response("Could not find city", { status: 404 });
    }
    return { info }
}

export default function City() {
    return <>{JSON.stringify(useLoaderData<typeof clientLoader>())}</>
}