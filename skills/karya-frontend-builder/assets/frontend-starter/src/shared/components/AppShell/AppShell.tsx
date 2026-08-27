import type { PropsWithChildren } from "react";

import styles from "./AppShell.module.scss";

export function AppShell({ children }: PropsWithChildren) {
  return (
    <div className={styles.shell}>
      <header className={styles.header}>
        <a className={styles.brand} href="/" aria-label="Product home">
          <span className={styles.mark} aria-hidden="true">
            A
          </span>
          <span>Product name</span>
        </a>
      </header>
      {children}
    </div>
  );
}
