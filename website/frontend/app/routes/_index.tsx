import { type MetaFunction } from "@remix-run/node";
import { Form } from "@remix-run/react";
import { Button } from "~/components/ui/button";
import { Input } from "~/components/ui/input";

// Page Metadata
export const meta: MetaFunction = () => [
  { title: "SmartCity KB" },
  {
    name: "description",
    content: "A knowledge base to enable better decision-making in smart cities. Search for cities!",
  },
];

// Index Page Component
export default function Index() {
  return (
    <div
      className="flex h-dvh flex-col items-center justify-center bg-gradient-to-br from-purple-500 via-blue-400 to-blue-600"
    >
      {/* Title and Description */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-extrabold text-gray-100">
          Welcome to SmartCity KB
        </h1>
        <p className="mt-4 text-lg text-gray-200">
          A knowledge base to enable better decision-making in smart cities. Search for cities!
        </p>
      </div>

      {/* Search Form */}
      <Form
        method="get"
        action="/search"
        className="flex flex-col gap-8 p-8 shadow-lg rounded-lg bg-white dark:bg-gray-800"
      >
        <div className="flex gap-4">
          <Input type="text" name="q" placeholder="Search..." className="w-full"/>
          <Button type="submit" className="px-6">
            Search
          </Button>
        </div>
      </Form>
    </div>
  );
}
