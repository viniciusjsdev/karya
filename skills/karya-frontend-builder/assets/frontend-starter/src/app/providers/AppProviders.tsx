import type { PropsWithChildren } from "react";
import { useState } from "react";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { PrimeReactProvider } from "primereact/api";

export function AppProviders({ children }: PropsWithChildren) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            retry: 1,
            staleTime: 30_000
          }
        }
      })
  );

  return (
    <PrimeReactProvider value={{ ripple: true }}>
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    </PrimeReactProvider>
  );
}
