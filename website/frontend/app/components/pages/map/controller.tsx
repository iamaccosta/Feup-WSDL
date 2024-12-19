import { useEffect, useState } from "react";
import MarkerClusterGroup from "~/client-imports/react-leaflet-cluser.client";
import {
  MapContainer,
  Marker,
  Popup,
  TileLayer,
  useMap,
} from "~/client-imports/react-leaflet.client";
import { BusStop, useBusStops } from "~/context/bus-stops";
import { useGeolocation } from "~/context/geolocation";
import { useMounted } from "~/hooks/use-mounted";
import { getBusInfo } from "~/lib/requests";

function InnerMapUpdater() {
  const geolocation = useGeolocation();
  const map = useMap();

  useEffect(() => {
    const currentLocation = geolocation.currentLocation;
    if (!currentLocation) return;

    const { latitude, longitude } = currentLocation;
    map.flyTo([latitude, longitude], 15, {
      animate: false,
    });
  }, [geolocation.currentLocation, map]);

  return <></>;
}

export function MapController() {
  const { busStops } = useBusStops();
 
  return (
    <MapContainer
      center={[0, 0]}
      zoom={1}
      scrollWheelZoom={true}
      className="w-full h-dvh"
    >
      <InnerMapUpdater />
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <MarkerClusterGroup chunkedLoading>
        {busStops.map((busStop) => {
          return (
            <Marker
              key={busStop.busStopId}
              position={[busStop.latitude, busStop.longitude]}
            >
              <Popup>
                <BusStopPopupContent busStop={busStop} />
              </Popup> 
            </Marker>
          );
        })}
      </MarkerClusterGroup>
    </MapContainer>
  );
}


function BusStopPopupContent({ busStop }: { busStop: BusStop }) {
    const mounted = useMounted();
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const [busInfo, setBusInfo] = useState<any>(undefined);

    const city = busStop.city;
    const busStopId = busStop.busStopId;

    useEffect(() => {
        if (!mounted) return;

        async function updateBusInfo() {
            const busInfo = await getBusInfo(city, busStopId);
            if (!mounted) return;

            setBusInfo(busInfo);
        }

        updateBusInfo();
    }, [city, busStopId, mounted]);

  return (
    busInfo === undefined
        ? <p>Loading...</p>
        : busInfo === null
            ? <p>No buses found.</p>
            : <div className="w-24 text-xs space-y-1">
                <p className="font-bold text-sm mb-2">Next Bus</p>
                <p><span className="font-semibold">Destination:</span> {busInfo.destination}</p>
                <p><span className="font-semibold">Line:</span> {busInfo.line}</p>
                <p><span className="font-semibold">ETA (min):</span> {busInfo.timeInMinutes}</p>
            </div>
  );
}