import { createContext, useState, useEffect, useContext } from "react";
import { useMounted } from "~/hooks/use-mounted";

function getCurrentPosition() {
  return new Promise<GeolocationPosition>((resolve, reject) => {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve(position);
      },
      (error) => {
        reject(error);
      }
    );
  });
}

function useInitialGeolocation() {
  const [geolocation, setGeolocation] = useState<Position | null>(
    null
  );
  const mounted = useMounted();

  useEffect(() => {
    if (!("navigator" in window && "geolocation" in navigator) || !mounted) {
      return;
    }

    async function updateGeolocation() {
      const geolocation = await getCurrentPosition();
      if (!mounted) return;

      setGeolocation(geolocation.coords);
    }

    updateGeolocation();
  }, [mounted]);

  return geolocation;
}

type Position = { latitude: number, longitude: number };
const GeolocationContext = createContext<{ currentLocation: Position | null, setCurrentLocation: (location: Position) => void }>({ currentLocation: null, setCurrentLocation: () => {} });

export function useGeolocation() {
    return useContext(GeolocationContext);
}

export function GeolocationProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  if ("navigator" in window && "geolocation" in navigator) {
    return <InnerGeolocationProvider>{children}</InnerGeolocationProvider>;
  }

  return <>{children}</>;
}

function InnerGeolocationProvider({ children }: { children: React.ReactNode }) {
  const initialGeolocation = useInitialGeolocation();
  const [currentLocation, setCurrentLocation] = useState<Position | null>(null);

  useEffect(() => {
    if (initialGeolocation && currentLocation === null) {
      setCurrentLocation(initialGeolocation);
    }
  }, [initialGeolocation, currentLocation]);

  return (
    <GeolocationContext.Provider value={{ currentLocation, setCurrentLocation }}>
      {children}
    </GeolocationContext.Provider>
  );
}
