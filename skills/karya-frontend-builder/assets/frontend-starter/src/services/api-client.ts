import axios from "axios";

import { env } from "@/app/config/env";

export const apiClient = axios.create({
  baseURL: env.VITE_API_BASE_URL,
  timeout: 15_000,
  headers: {
    "Content-Type": "application/json"
  }
});
