import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createWatchlist } from "../api/watchlist-api";
import { watchlistKeys } from "./use-watchlists";
import type { Watchlist, CreateWatchlistPayload } from "../types";

/**
 * Optimistic create mutation.
 *
 * Optimistic UI flow:
 *   1. onMutate  → immediately insert a temp entry into the list cache
 *   2. onError   → roll back to the snapshot if the server rejects
 *   3. onSettled → always invalidate so React Query refetches the real data
 *
 * Why `cancelQueries` first:
 *   Prevents an in-flight background refetch from overwriting our optimistic update
 *   before the mutation response arrives.
 */
export function useCreateWatchlist() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CreateWatchlistPayload) => createWatchlist(payload),

    onMutate: async (payload) => {
      // Cancel any outgoing refetches so they don't overwrite our optimistic update
      await queryClient.cancelQueries({ queryKey: watchlistKeys.lists() });

      // Snapshot all list cache entries before mutation (for rollback)
      const snapshot = queryClient.getQueriesData<Watchlist[]>({
        queryKey: watchlistKeys.lists(),
      });

      // Optimistically insert a placeholder entry into every cached page
      queryClient.setQueriesData<Watchlist[]>(
        { queryKey: watchlistKeys.lists() },
        (old) => [
          ...(old ?? []),
          {
            id: `temp-${Date.now()}`,
            name: payload.name,
            is_default: false,
            created_at: new Date().toISOString(),
          },
        ]
      );

      return { snapshot };
    },

    onError: (_err, _payload, context) => {
      // Roll back all list cache entries to their pre-mutation snapshots
      if (context?.snapshot) {
        for (const [queryKey, data] of context.snapshot) {
          queryClient.setQueryData(queryKey, data);
        }
      }
    },

    onSettled: () => {
      // Always sync with server after mutation (success or failure)
      queryClient.invalidateQueries({ queryKey: watchlistKeys.lists() });
    },
  });
}
