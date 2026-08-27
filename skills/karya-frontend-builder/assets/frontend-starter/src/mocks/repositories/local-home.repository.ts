import type { HomeRepository } from "@/features/home/repositories/home.repository";
import { homeSummarySchema } from "@/features/home/schemas/home.schema";
import type { HomeSummary } from "@/features/home/types/home.types";
import type { StorageAdapter } from "@/services/storage/storage.adapter";

const storageKey = "home-summary";

const defaultSummary: HomeSummary = {
  title: "Replace this starter with the product contract",
  description:
    "The factory foundation is ready: React, TypeScript, PrimeReact, Query, services, mocks, tests, and responsive tokens.",
  nextStep: "Implement the product's most important screen and primary journey first."
};

export class LocalHomeRepository implements HomeRepository {
  public constructor(private readonly storage: StorageAdapter) {}

  public async getSummary(): Promise<HomeSummary> {
    await new Promise((resolve) => window.setTimeout(resolve, 120));
    const stored = this.storage.get(storageKey, defaultSummary);
    return homeSummarySchema.parse(stored);
  }
}
