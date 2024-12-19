import { ClientActionFunctionArgs, Form, Outlet } from "@remix-run/react";
import { MapController } from "~/components/pages/map/controller";
import { Button } from "~/components/ui/button";
import { Input } from "~/components/ui/input";
import { Label } from "~/components/ui/label";
import { BusStopsProvider } from "~/context/bus-stops";
import { GeolocationProvider } from "~/context/geolocation";
import { normalizeCityName } from "~/lib/city";

export async function clientAction({ request }: ClientActionFunctionArgs) {
  const formData = await request.formData()
  const city = formData.get("city")

  if (!city || typeof city !== "string") {
    return null; 
  }

  const normalizedCityName = normalizeCityName(city);

  const response = await fetch(`http://localhost:5000/${normalizedCityName}`, {
    method: 'HEAD',
  })

  if (response.status !== 200) {
    alert("City not found.")
    return null
  }

  return Response.redirect(`/explore/${normalizedCityName}`)
}

export default function Index() {
  return (
    <GeolocationProvider>
      <BusStopsProvider>
        <div className="grid grid-cols-[1fr,auto] h-dvh">
          <MapController />
          <div className="w-96 bg-white shadow-xl max-h-dvh overflow-y-auto">
            <Form method="post">
              <div className="grid grid-cols-[1fr,auto] border-b">
                <div className="flex flex-col px-4 py-2">
                  <Label htmlFor="city" className="text-xs text-neutral-600">
                    City
                  </Label>
                  <Input
                    id="city"
                    name="city"
                    type="text"
                    placeholder="A city..."
                    className="text-2xl border-none shadow-none focus-visible:ring-0 p-0 ml-0"
                    required
                  />
                </div>
                <div>
                  <Button
                    type="submit"
                    className="w-full bg-purple-600 text-white ring-0 shadow-none hover:bg-purple-500 focus-visible:bg-purple-500 rounded-none h-full"
                  >
                    Search
                  </Button>
                </div>
              </div>   
            </Form>
            <div>
              <Outlet />
            </div>
          </div>
        </div>
      </BusStopsProvider>
    </GeolocationProvider>
  );
}
