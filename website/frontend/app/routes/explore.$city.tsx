import { useLoaderData } from "@remix-run/react";
import { useEffect, useMemo } from "react";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "~/components/ui/carousel";
import { useBusStops } from "~/context/bus-stops";
import { useGeolocation } from "~/context/geolocation";
import { getBusStops, getDiaryReport, getStaticInfo } from "~/lib/requests";

export async function clientLoader({ params }: { params: { city: string } }) {
  const info = await getStaticInfo(params.city);
  if (info === null) {
    return new Response("Could not find city", { status: 404 });
  }

  const [busStops, diaryReport] = await Promise.all([
    getBusStops(params.city),
    getDiaryReport(params.city),
  ]);

  return { info, busStops, city: params.city, diaryReport };
}

function CitySection({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col gap-2 p-4 border-b">
      <p className="text-lg font-bold">{title}</p>
      <div className="text-xs relative">{children}</div>
    </div>
  );
}

export default function City() {
  const data = useLoaderData<typeof clientLoader>();

  const location = useGeolocation();
  const setLocation = useMemo(
    () => location.setCurrentLocation,
    [location.setCurrentLocation]
  );

  const busStops = useBusStops();
  const setBusStops = useMemo(
    () => busStops.setBusStops,
    [busStops.setBusStops]
  );

  useEffect(() => {
    const { latitude, longitude } = data.info;

    setLocation({
      latitude: parseFloat(latitude),
      longitude: parseFloat(longitude),
    });
  }, []);

  useEffect(() => {
    setBusStops(data.busStops);
  }, []);

  return (
    <div>
      <CitySection title="Weather Forecast">
        <img
          src={`http://localhost:5000/${data.city}/monthlyweathersummary`}
          alt="Weather Forecast"
          className="w-full h-auto"
        />
      </CitySection>
      <CitySection title="Precipitation History">
        <img
          src={`http://localhost:5000/${data.city}/get-precipitation`}
          alt="Weather Forecast"
          className="w-full h-auto"
        />
      </CitySection>
      <CitySection title="Forecast">
        <Carousel className="relative w-3/4 mx-auto">
          <CarouselContent className="flex">
            {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
            {data.diaryReport.map((entry: any, index: any) => {
              return (
                <CarouselItem key={index} className="flex gap-8 p-4 w-3/4">
                  <div className="flex-1">
                    <h4 className="text-xl font-bold mb-2">{entry.date}</h4>
                    <p className="text-md">
                      <strong>Condition:</strong> {entry.condition}
                    </p>
                    <p className="text-md">
                      <strong>Mean Temperature:</strong>{" "}
                      {parseFloat(entry.meanT).toFixed(1)} ºC
                    </p>
                    <p className="text-md">
                      <strong>Mean Wind:</strong>{" "}
                      {parseFloat(entry.meanWind).toFixed(1)} m/s
                    </p>
                  </div>
                </CarouselItem>
              );
            })}
          </CarouselContent>
          <CarouselPrevious />
          <CarouselNext />
        </Carousel>
      </CitySection>
      <CitySection title="Description">
        <p>{data.info.description}</p>
      </CitySection>
    </div>
  );
}
