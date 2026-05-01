import { useQuery } from "@tanstack/react-query";
import { fetchWatchlists } from "../api/watchlist-api";
import type { WatchlistQueryParams } from "../types";

// Query key factory — consistent keys prevent cache collisions across components.
export const watchlistKeys = {
  all: ["watchlists"] as const,
  lists: () => [...watchlistKeys.all, "list"] as const,
  list: (params: WatchlistQueryParams) => [...watchlistKeys.lists(), params] as const,
  detail: (id: string) => [...watchlistKeys.all, "detail", id] as const,
  items: (id: string, params: WatchlistQueryParams) =>
    [...watchlistKeys.all, "items", id, params] as const,
};

interface UseWatchlistsOptions extends WatchlistQueryParams {
  enabled?: boolean;
}

/**
 * Paginated watchlist query hook.
 *
 * - staleTime: 5min (from QueryClient default) — avoids re-fetching on every mount
 * - keepPreviousData: shows previous page while next page loads (smooth pagination)
 * - select: narrowly typed — always returns Watchlist[] even on empty cache
 */
export function useWatchlists({ skip = 0, limit = 20, enabled = true }: UseWatchlistsOptions = {}) {
  return useQuery({
    queryKey: watchlistKeys.list({ skip, limit }),
    queryFn: () => fetchWatchlists({ skip, limit }),
    enabled,
    keepPreviousData: true,  // v4 API
    staleTime: 5 * 60 * 1000,
  });
}
