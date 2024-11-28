import { type MetaFunction } from "@remix-run/node";
import { Form } from "@remix-run/react";
import { Button } from "~/components/ui/button";
import { Input } from "~/components/ui/input";

export const meta: MetaFunction = () => {
  return [
    { title: "SmartCity KB" },
    { name: "description", content: "A knowledge base to enable better decision-making in smart cities." },
  ];
};

export default function Index() {
  return (
    <div className="flex h-dvh items-center justify-center">
      <Form method="get" action="/search" className="flex flex-col gap-6">
        <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-100">
          Welcome to SmartCity KB
        </h1>
        <div className="flex gap-4">
          <Input type="text" name="q" placeholder="Search..." />
          <Button type="submit">Search</Button>
        </div>
      </Form>
    </div>
  );
}
