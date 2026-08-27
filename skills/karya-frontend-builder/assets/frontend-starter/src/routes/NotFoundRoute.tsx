import { Button } from "primereact/button";
import { useNavigate } from "react-router-dom";

import { AppShell } from "@/shared/components/AppShell/AppShell";

export function NotFoundRoute() {
  const navigate = useNavigate();

  return (
    <AppShell>
      <main className="route-state">
        <i className="pi pi-compass" aria-hidden="true" />
        <h1>Page not found</h1>
        <p>The address may be incorrect or the page may have moved.</p>
        <Button label="Return home" icon="pi pi-arrow-left" onClick={() => navigate("/")} />
      </main>
    </AppShell>
  );
}
