import { useQuery } from "@tanstack/react-query";

import { homeService } from "@/features/home/services/home.service";

export function useHomeViewModel() {
  const summaryQuery = useQuery({
    queryKey: ["home", "summary"],
    queryFn: homeService.getSummary
  });

  return {
    summary: summaryQuery.data,
    isLoading: summaryQuery.isLoading,
    errorMessage: summaryQuery.isError ? "We could not load this experience." : null,
    retry: summaryQuery.refetch
  };
}
