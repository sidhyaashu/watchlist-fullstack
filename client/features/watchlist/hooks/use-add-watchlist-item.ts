import { useMutation, useQueryClient } from "@tanstack/react-query";
import { addWatchlistItem } from "../api/watchlist-api";
import { watchlistKeys } from "./use-watchlists";
import type { AddItemPayload } from "../types";

export function useAddWatchlistItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ watchlistId, payload }: { watchlistId: string; payload: AddItemPayload }) =>
      addWatchlistItem(watchlistId, payload),
    onSuccess: (data, variables) => {
      // Invalidate the specific watchlist items cache to refetch
      queryClient.invalidateQueries({
        queryKey: watchlistKeys.items(variables.watchlistId, {}),
      });
      // Also invalidate the detail since item count/summary might change
      queryClient.invalidateQueries({
        queryKey: watchlistKeys.detail(variables.watchlistId),
      });
    },
  });
}
