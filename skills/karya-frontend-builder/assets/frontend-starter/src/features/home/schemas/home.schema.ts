import { z } from "zod";

export const homeSummarySchema = z.object({
  title: z.string().min(1),
  description: z.string().min(1),
  nextStep: z.string().min(1)
});
