"use client"

import { useQuery } from "@tanstack/react-query";
import { searchInstruments } from "../api/market-api";
import { useDebounce } from "@/hooks/use-debounce";

export function useInstrumentSearch(query: string) {
  const [debouncedQuery] = useDebounce(query, 300);

  return useQuery({
    queryKey: ["instruments", "search", debouncedQuery],
    queryFn: () => searchInstruments(debouncedQuery),
    enabled: debouncedQuery.length > 0,
    staleTime: 1000 * 60 * 5, // Cache for 5 minutes
  });
}
