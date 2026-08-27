import { z } from "zod";

const environmentSchema = z.object({
  VITE_APP_ENV: z.enum(["development", "test", "production"]).default("development"),
  VITE_API_BASE_URL: z.url().default("http://localhost:8000/api"),
  VITE_USE_MOCKS: z
    .enum(["true", "false"])
    .default("true")
    .transform((value) => value === "true")
});

export const env = environmentSchema.parse(import.meta.env);
