import { ProgressSpinner } from "primereact/progressspinner";

interface RouteLoadingProps {
  label: string;
}

export function RouteLoading({ label }: RouteLoadingProps) {
  return (
    <main className="route-state" aria-live="polite" aria-busy="true">
      <ProgressSpinner aria-label={label} />
      <span>{label}</span>
    </main>
  );
}
