import type { HomeSummary } from "@/features/home/types/home.types";

export interface HomeRepository {
  getSummary(): Promise<HomeSummary>;
}
