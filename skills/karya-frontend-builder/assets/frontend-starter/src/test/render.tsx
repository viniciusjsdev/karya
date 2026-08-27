import type { ReactElement } from "react";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, type RenderOptions } from "@testing-library/react";
import { PrimeReactProvider } from "primereact/api";
import { MemoryRouter } from "react-router-dom";

interface AppRenderOptions extends Omit<RenderOptions, "wrapper"> {
  route?: string;
}

export function renderWithAppProviders(
  ui: ReactElement,
  { route = "/", ...options }: AppRenderOptions = {}
) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } }
  });

  return render(
    <PrimeReactProvider>
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={[route]}>{ui}</MemoryRouter>
      </QueryClientProvider>
    </PrimeReactProvider>,
    options
  );
}
