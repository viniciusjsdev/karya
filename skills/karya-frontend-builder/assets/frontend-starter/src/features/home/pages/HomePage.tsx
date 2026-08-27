import { Button } from "primereact/button";
import { ProgressSpinner } from "primereact/progressspinner";

import { useHomeViewModel } from "@/features/home/hooks/useHomeViewModel";
import { AppShell } from "@/shared/components/AppShell/AppShell";

import styles from "./HomePage.module.scss";

export function HomePage() {
  const viewModel = useHomeViewModel();

  return (
    <AppShell>
      <main className={styles.page}>
        {viewModel.isLoading ? (
          <ProgressSpinner aria-label="Loading product" />
        ) : viewModel.errorMessage ? (
          <section className={styles.state} role="alert">
            <p>{viewModel.errorMessage}</p>
            <Button label="Try again" icon="pi pi-refresh" onClick={() => void viewModel.retry()} />
          </section>
        ) : (
          <section className={styles.hero}>
            <span className={styles.eyebrow}>Karya frontend</span>
            <h1>{viewModel.summary?.title}</h1>
            <p>{viewModel.summary?.description}</p>
            <div className={styles.nextStep}>
              <i className="pi pi-sparkles" aria-hidden="true" />
              <span>{viewModel.summary?.nextStep}</span>
            </div>
          </section>
        )}
      </main>
    </AppShell>
  );
}
