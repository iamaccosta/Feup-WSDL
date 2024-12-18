import { lazy, Suspense } from "react";
import 'leaflet/dist/leaflet.css';

const MapPage = lazy(() => import("~/components/pages/map.client"));

export default function Page() {
  return (
    <div className="overflow-hidden">
        <Suspense fallback={<p>Loading...</p>}>
            <MapPage />
        </Suspense>
    </div>
  );
}
