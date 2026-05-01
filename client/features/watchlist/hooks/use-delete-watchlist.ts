import { useMutation, useQueryClient } from "@tanstack/react-query";
import { deleteWatchlist } from "../api/watchlist-api";
import { watchlistKeys } from "./use-watchlists";
import type { Watchlist } from "../types";

/**
 * Optimistic delete mutation.
 *
 * Removes the item from the list cache immediately on click.
 * If the server returns an error, the item is restored.
 */
export function useDeleteWatchlist() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (watchlistId: string) => deleteWatchlist(watchlistId),

    onMutate: async (watchlistId) => {
      await queryClient.cancelQueries({ queryKey: watchlistKeys.lists() });

      // Snapshot all list pages for rollback
      const snapshot = queryClient.getQueriesData<Watchlist[]>({
        queryKey: watchlistKeys.lists(),
      });

      // Optimistically remove the entry from all cached list pages
      queryClient.setQueriesData<Watchlist[]>(
        { queryKey: watchlistKeys.lists() },
        (old) => (old ?? []).filter((w) => w.id !== watchlistId)
      );

      // Also remove the detail cache entry immediately
      queryClient.removeQueries({ queryKey: watchlistKeys.detail(watchlistId) });

      return { snapshot };
    },

    onError: (_err, _watchlistId, context) => {
      if (context?.snapshot) {
        for (const [queryKey, data] of context.snapshot) {
          queryClient.setQueryData(queryKey, data);
        }
      }
    },

    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: watchlistKeys.lists() });
    },
  });
}
