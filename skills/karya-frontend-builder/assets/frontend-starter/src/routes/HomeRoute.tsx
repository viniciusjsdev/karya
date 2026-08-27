import { lazy, Suspense } from "react";

import { RouteLoading } from "@/shared/components/RouteLoading/RouteLoading";

const HomePage = lazy(() =>
  import("@/features/home").then((module) => ({ default: module.HomePage }))
);

export function HomeRoute() {
  return (
    <Suspense fallback={<RouteLoading label="Loading product" />}>
      <HomePage />
    </Suspense>
  );
}
