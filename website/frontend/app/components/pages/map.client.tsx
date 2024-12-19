import { useLoaderData } from "@remix-run/react";
import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";

export default function Page() {
  const data = useLoaderData();

  return (
    <MapContainer center={[45.505, -0.09]} zoom={13} scrollWheelZoom={true} className="w-full h-dvh">
        <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {data.busStops.map((busStop) => {
            return (
                <Marker key={busStop.busStopName} position={[busStop.latitude, busStop.longitude]}>
                    <Popup>
                        {busStop.busStopName}
                    </Popup>
                </Marker>
            )
        })}
    </MapContainer>
  );
}
