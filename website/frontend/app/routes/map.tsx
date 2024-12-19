import { lazy, Suspense } from "react";
import 'leaflet/dist/leaflet.css';

const MapPage = lazy(() => import("~/components/pages/map.client"));

export async function clientLoader({ request }: { request: Request }) {
    const url = new URL(request.url);
    const city = url.searchParams.get("city");

    const response = await fetch(`http://localhost:5000/${city}/BusStop`, {
      method: 'GET',
      headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
      },
    })

    const busStops = await response.json()
    return { busStops }
}

export default function Page() {
  return (
    <div className="overflow-hidden">
        <Suspense fallback={<p>Loading...</p>}>
            <MapPage />
        </Suspense>
    </div>
  );
}
