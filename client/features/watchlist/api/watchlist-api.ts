/**
 * Watchlist API functions.
 *
 * Uses the existing `apiClient` from lib/api-client.ts — which already handles:
 *   - Bearer token attachment from Redux store
 *   - Automatic token refresh on 401
 *   - 403 account-banned redirect
 *   - Standardized ApiError shape
 *
 * All routes go through the API Gateway which maps /api/v1/watchlists → watchlist_service.
 */

import { apiClient } from "@/lib/api-client";
import type {
  Watchlist,
  WatchlistItem,
  CreateWatchlistPayload,
  AddItemPayload,
  ReorderPayload,
  WatchlistQueryParams,
} from "../types";

const BASE = "/api/v1/watchlists";

// ─── Watchlist CRUD ───────────────────────────────────────────────────────────

export async function fetchWatchlists(params: WatchlistQueryParams = {}): Promise<Watchlist[]> {
  const { skip = 0, limit = 20 } = params;
  const { data } = await apiClient.get<Watchlist[]>(BASE, {
    params: { skip, limit },
  });
  return data;
}

export async function fetchWatchlist(watchlistId: string): Promise<Watchlist> {
  const { data } = await apiClient.get<Watchlist>(`${BASE}/${watchlistId}`);
  return data;
}

export async function createWatchlist(payload: CreateWatchlistPayload): Promise<Watchlist> {
  const { data } = await apiClient.post<Watchlist>(BASE, payload);
  return data;
}

export async function deleteWatchlist(watchlistId: string): Promise<void> {
  await apiClient.delete(`${BASE}/${watchlistId}`);
}

// ─── Watchlist Items ───────────────────────────────────────────────────────────

export async function fetchWatchlistItems(
  watchlistId: string,
  params: WatchlistQueryParams = {}
): Promise<WatchlistItem[]> {
  const { skip = 0, limit = 50 } = params;
  const { data } = await apiClient.get<WatchlistItem[]>(`${BASE}/${watchlistId}/items`, {
    params: { skip, limit },
  });
  return data;
}

export async function addWatchlistItem(
  watchlistId: string,
  payload: AddItemPayload
): Promise<WatchlistItem> {
  const { data } = await apiClient.post<WatchlistItem>(`${BASE}/${watchlistId}/items`, payload);
  return data;
}

export async function removeWatchlistItem(
  watchlistId: string,
  instrumentId: string
): Promise<void> {
  await apiClient.delete(`${BASE}/${watchlistId}/items/${instrumentId}`);
}

export async function reorderWatchlistItems(
  watchlistId: string,
  updates: ReorderPayload[]
): Promise<void> {
  await apiClient.patch(`${BASE}/${watchlistId}/items/reorder`, { updates });
}
