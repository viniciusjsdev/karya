import { env } from "@/app/config/env";
import { ApiHomeRepository } from "@/features/home/repositories/api-home.repository";
import type { HomeRepository } from "@/features/home/repositories/home.repository";
import { LocalHomeRepository } from "@/mocks/repositories/local-home.repository";
import { apiClient } from "@/services/api-client";
import { browserStorage } from "@/services/storage/storage.adapter";

const homeRepository: HomeRepository = env.VITE_USE_MOCKS
  ? new LocalHomeRepository(browserStorage)
  : new ApiHomeRepository(apiClient);

export const homeService = {
  getSummary: () => homeRepository.getSummary()
};
