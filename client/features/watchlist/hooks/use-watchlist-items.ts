import { useQuery } from "@tanstack/react-query";
import { fetchWatchlistItems } from "../api/watchlist-api";
import { watchlistKeys } from "./use-watchlists";
import type { WatchlistQueryParams } from "../types";

interface UseWatchlistItemsOptions extends WatchlistQueryParams {
  enabled?: boolean;
}

export function useWatchlistItems(
  watchlistId: string | undefined,
  { skip = 0, limit = 50, enabled = true }: UseWatchlistItemsOptions = {}
) {
  return useQuery({
    queryKey: watchlistKeys.items(watchlistId ?? "", { skip, limit }),
    queryFn: () => fetchWatchlistItems(watchlistId!, { skip, limit }),
    enabled: !!watchlistId && enabled,
    staleTime: 60 * 1000, // 1 minute
  });
}
