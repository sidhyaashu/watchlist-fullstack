import { apiClient } from "@/lib/api-client";

export interface Instrument {
  id: number;
  symbol: string;
  name: string;
  exchange: string;
  last_price: number;
  updated_at: string;
}

export async function searchInstruments(query: string): Promise<Instrument[]> {
  if (!query) return [];
  const response = await apiClient.get<Instrument[]>(`/market/search?q=${encodeURIComponent(query)}`);
  return response.data;
}
