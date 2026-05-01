export type ColumnId = 'stock' | 'price' | 'change' | 'range' | 'sector' | 'actions';

export interface WatchlistColumn {
  id: ColumnId;
  label: string;
  align?: 'left' | 'right' | 'center';
  width?: string;
}

/**
 * Static configuration for Watchlist Table columns.
 * Supports the PM request for dynamic columns and consistent UI alignment.
 */
export const WATCHLIST_COLUMNS: WatchlistColumn[] = [
  { id: 'stock', label: 'Stock', align: 'left', width: '300px' },
  { id: 'price', label: 'Price', align: 'right' },
  { id: 'change', label: 'Day', align: 'right' },
  { id: 'range', label: '52W Range', align: 'center' },
  { id: 'sector', label: 'Sector', align: 'left' },
  { id: 'actions', label: 'Actions', align: 'right', width: '100px' },
];
