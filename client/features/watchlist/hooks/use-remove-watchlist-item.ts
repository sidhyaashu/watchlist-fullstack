import { useMutation, useQueryClient } from "@tanstack/react-query";
import { removeWatchlistItem } from "../api/watchlist-api";
import { watchlistKeys } from "./use-watchlists";

export function useRemoveWatchlistItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ watchlistId, instrumentId }: { watchlistId: string; instrumentId: string }) =>
      removeWatchlistItem(watchlistId, instrumentId),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: watchlistKeys.items(variables.watchlistId, {}),
      });
      queryClient.invalidateQueries({
        queryKey: watchlistKeys.detail(variables.watchlistId),
      });
    },
  });
}
