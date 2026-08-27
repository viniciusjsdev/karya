import { Component, type ErrorInfo, type PropsWithChildren, type ReactNode } from "react";

import { Button } from "primereact/button";

interface AppErrorBoundaryState {
  hasError: boolean;
}

export class AppErrorBoundary extends Component<PropsWithChildren, AppErrorBoundaryState> {
  public state: AppErrorBoundaryState = { hasError: false };

  public static getDerivedStateFromError(): AppErrorBoundaryState {
    return { hasError: true };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error("Uncaught application error", error, errorInfo);
  }

  public render(): ReactNode {
    if (!this.state.hasError) return this.props.children;

    return (
      <main className="route-state" role="alert">
        <i className="pi pi-exclamation-triangle" aria-hidden="true" />
        <h1>Something went wrong</h1>
        <p>Reload the application. If the problem continues, contact support.</p>
        <Button label="Reload" icon="pi pi-refresh" onClick={() => window.location.reload()} />
      </main>
    );
  }
}
