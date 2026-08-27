import type { AxiosInstance } from "axios";

import type { HomeRepository } from "@/features/home/repositories/home.repository";
import { homeSummarySchema } from "@/features/home/schemas/home.schema";
import type { HomeSummary } from "@/features/home/types/home.types";

export class ApiHomeRepository implements HomeRepository {
  public constructor(private readonly client: AxiosInstance) {}

  public async getSummary(): Promise<HomeSummary> {
    const response = await this.client.get<unknown>("/home/summary");
    return homeSummarySchema.parse(response.data);
  }
}
