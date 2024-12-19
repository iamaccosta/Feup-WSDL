import { createContext, useContext, useState } from "react";

export type BusStop = {
    busStopId: string;
    busStopName: string;
    latitude: number;
    longitude: number;
    city: string;
}

type BusStops = {
    busStops: BusStop[];
    setBusStops: (busStops: BusStop[]) => void;
}

const BusStopsContext = createContext<BusStops | null>(null);

export function BusStopsProvider({ children }: { children: React.ReactNode }) {
    const [busStops, setBusStops] = useState<BusStop[]>([]);

    return (
        <BusStopsContext.Provider value={{ busStops, setBusStops }}>
            {children}
        </BusStopsContext.Provider>
    );
}

export function useBusStops() {
    const context = useContext(BusStopsContext);
    if (context === null) {
        throw new Error("useBusStops must be used within a BusStopsProvider");
    }
    return context;
}