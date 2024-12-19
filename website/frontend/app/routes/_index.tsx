import { MetaFunction } from "@remix-run/react";

export const meta: MetaFunction = () => [
  { title: "SmartCity KB" },
  {
    name: "description",
    content: "A knowledge base to enable better decision-making in smart cities. Search for cities!",
  },
];

export function clientLoader() {
    return Response.redirect("/explore")
}

export default function Index() {
    return <></>
}