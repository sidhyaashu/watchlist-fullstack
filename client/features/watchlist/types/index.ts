/**
 * Watchlist feature types — mirrors the backend Pydantic schemas exactly.
 *
 * WatchlistResponse  → app/watchlist/schemas/watchlist.py :: WatchlistResponse
 * WatchlistItem      → app/watchlist/schemas/watchlist_item.py :: WatchlistItemResponse
 */

export interface Watchlist {
  id: string;
  name: string;
  is_default: boolean;
  created_at: string; // ISO 8601
}

export interface WatchlistItem {
  id: string;
  watchlist_id: string;
  instrument_id: string;
  symbol: string;
  exchange: string;
  position: number;
  // Enriched fields from MarketService (may be null if data unavailable)
  name: string | null;
  last_price: number | null;
  change_percent: number | null;
}

// ─── Request payloads ─────────────────────────────────────────────────────────

export interface CreateWatchlistPayload {
  name: string;
}

export interface AddItemPayload {
  instrument_id: string;
  symbol: string;
  exchange: string;
}

export interface ReorderPayload {
  instrument_id: string;
  position: number;
}

// ─── Paginated query params ───────────────────────────────────────────────────

export interface WatchlistQueryParams {
  skip?: number;
  limit?: number;
}
