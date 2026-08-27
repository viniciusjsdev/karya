import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import "primeicons/primeicons.css";
import "primereact/resources/themes/lara-light-cyan/theme.css";

import { App } from "@/app/App";
import "@/app/styles/globals.scss";

const root = document.getElementById("root");

if (!root) {
  throw new Error("Root element was not found.");
}

createRoot(root).render(
  <StrictMode>
    <App />
  </StrictMode>
);
