import { apiClient } from "@/lib/api-client";

export interface Instrument {
  id: number;
  symbol: string;
  name: string;
  exchange: string;
  last_price: number | null;
  mcap: number | null;
  pe: number | null;
  updated_at?: string;
}

export async function searchInstruments(query: string): Promise<Instrument[]> {
  if (!query) return [];
  const response = await apiClient.get<Instrument[]>(`/api/v1/market/search?q=${encodeURIComponent(query)}`);
  return response.data;
}

export async function fetchPopularInstruments(limit = 8): Promise<Instrument[]> {
  const response = await apiClient.get<Instrument[]>(`/api/v1/market/popular?limit=${limit}`);
  return response.data;
}
