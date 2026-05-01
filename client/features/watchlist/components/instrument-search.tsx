"use client";

import { useState, useRef, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { useInstrumentSearch } from "../hooks/use-instrument-search";
import { useAddWatchlistItem } from "../hooks/use-add-watchlist-item";
import { Loader2, Search } from "lucide-react";
import type { Instrument } from "../api/market-api";

interface InstrumentSearchProps {
  watchlistId: string;
}

export function InstrumentSearch({ watchlistId }: InstrumentSearchProps) {
  const [query, setQuery] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  
  const { data: instruments, isLoading, isFetching } = useInstrumentSearch(query);
  const addMutation = useAddWatchlistItem(watchlistId);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSelect = (instrument: Instrument) => {
    addMutation.mutate({ instrument_id: instrument.id });
    setQuery("");
    setIsOpen(false);
  };

  return (
    <div className="relative w-full max-w-sm" ref={containerRef}>
      <div className="relative">
        <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-500" />
        <Input
          placeholder="Search ticker (e.g., AAPL)..."
          className="pl-9"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setIsOpen(true);
          }}
          onFocus={() => setIsOpen(true)}
          disabled={addMutation.isLoading}
        />
        {((isLoading || isFetching) && query.length > 0) || addMutation.isLoading ? (
          <Loader2 className="absolute right-2.5 top-2.5 h-4 w-4 animate-spin text-slate-500" />
        ) : null}
      </div>

      {isOpen && query.length > 0 && instruments && (
        <div className="absolute z-10 mt-1 w-full rounded-md border bg-white shadow-lg py-1 max-h-60 overflow-y-auto">
          {instruments.length === 0 ? (
            <div className="px-4 py-2 text-sm text-slate-500 text-center">No matching tickers found.</div>
          ) : (
            instruments.map((instrument) => (
              <div
                key={instrument.id}
                className="flex cursor-pointer items-center justify-between px-4 py-2 hover:bg-slate-100 border-b last:border-b-0 border-slate-50"
                onClick={() => handleSelect(instrument)}
              >
                <div>
                  <div className="font-semibold text-slate-800">{instrument.symbol}</div>
                  <div className="text-xs text-slate-500 line-clamp-1">{instrument.name}</div>
                </div>
                <div className="flex flex-col items-end">
                  <div className="text-xs font-medium text-slate-700 bg-slate-100 px-1.5 py-0.5 rounded border">
                    {instrument.exchange}
                  </div>
                  <div className="text-xs text-slate-500 mt-1">${instrument.last_price?.toFixed(2)}</div>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
