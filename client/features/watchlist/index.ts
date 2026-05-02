/**
 * Watchlist feature barrel export.
 * Import everything from here — never import from deep paths inside the feature.
 *
 * Usage:
 *   import { useWatchlists, useCreateWatchlist, type Watchlist } from "@/features/watchlist"
 */

// Types
export type { Watchlist, WatchlistItem, CreateWatchlistPayload, WatchlistQueryParams } from "./types";

// API functions (rarely needed directly — prefer hooks)
export { fetchWatchlists, fetchWatchlist, createWatchlist, deleteWatchlist } from "./api/watchlist-api";
export { fetchWatchlistItems, addWatchlistItem, removeWatchlistItem, reorderWatchlistItems } from "./api/watchlist-api";

// Query key factory (useful when you need to invalidate from outside the feature)
export { watchlistKeys } from "./hooks/use-watchlists";

// Hooks
export { useWatchlists } from "./hooks/use-watchlists";
export { useWatchlist } from "./hooks/use-watchlist";
export { useCreateWatchlist } from "./hooks/use-create-watchlist";
export { useDeleteWatchlist } from "./hooks/use-delete-watchlist";
export { useWatchlistItems } from "./hooks/use-watchlist-items";
export { useAddWatchlistItem } from "./hooks/use-add-watchlist-item";
export { useRemoveWatchlistItem } from "./hooks/use-remove-watchlist-item";
export { useReorderWatchlistItems } from "./hooks/use-reorder-watchlist-items";

// Components
export { InstrumentSearch } from "./components/instrument-search";
export { WatchlistKPIs } from "./components/watchlist-kpis";
export { WatchlistItemsTable } from "./components/watchlist-items-table";
export { PriceRangeBand } from "./components/price-range-band";
export { WatchlistTabs } from "./components/watchlist-tabs";
export type { WatchlistTag } from "./components/watchlist-tabs";

