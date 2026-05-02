import { useMutation, useQueryClient } from "@tanstack/react-query";
import { reorderWatchlistItems } from "../api/watchlist-api";
import { watchlistKeys } from "./use-watchlists";
import type { ReorderPayload } from "../types";

export function useReorderWatchlistItems() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ watchlistId, updates }: { watchlistId: string; updates: ReorderPayload[] }) =>
      reorderWatchlistItems(watchlistId, updates),
    onSuccess: (_, { watchlistId }) => {
      queryClient.invalidateQueries(watchlistKeys.items(watchlistId));
    },
  });
}
