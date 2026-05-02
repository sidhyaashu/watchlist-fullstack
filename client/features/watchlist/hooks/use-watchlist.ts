import { useQuery } from "@tanstack/react-query";
import { fetchWatchlist } from "../api/watchlist-api";
import { watchlistKeys } from "./use-watchlists";

/**
 * Single watchlist detail hook.
 * Disabled automatically when no id is provided (e.g. during navigation).
 */
export function useWatchlist(watchlistId: string | undefined) {
  return useQuery({
    queryKey: watchlistKeys.detail(watchlistId ?? ""),
    queryFn: () => fetchWatchlist(watchlistId!),
    enabled: !!watchlistId && !watchlistId.startsWith("temp-"),
    staleTime: 10 * 60 * 1000, // 10 min — matches backend DETAIL_TTL
  });
}
