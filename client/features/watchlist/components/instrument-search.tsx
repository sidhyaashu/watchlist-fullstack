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
    // instrument.id is the FINCODE (Integer)
    addMutation.mutate({ 
      instrument_id: parseInt(instrument.id.toString()), 
      symbol: instrument.symbol,
      exchange: instrument.exchange
    });
    setQuery("");
    setIsOpen(false);
  };

  return (
    <div className="relative w-full max-w-sm" ref={containerRef}>
      <div className="relative group">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-ink-3 group-focus-within:text-accent transition-colors" />
        <Input
          placeholder="Search tickers (e.g. RELIANCE)..."
          className="pl-10 bg-white/50 border-ink-4/20 focus:bg-white focus:border-accent transition-all rounded-xl ts-body"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setIsOpen(true);
          }}
          onFocus={() => setIsOpen(true)}
          disabled={addMutation.isPending}
        />
        {((isLoading || isFetching) && query.length > 0) || addMutation.isPending ? (
          <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 animate-spin text-accent" />
        ) : null}
      </div>

      {isOpen && query.length > 0 && instruments && (
        <div className="glass-card absolute z-50 mt-2 w-full py-1 max-h-[400px] overflow-y-auto border-rule shadow-xl">
          {instruments.length === 0 ? (
            <div className="px-4 py-8 text-center">
              <div className="ts-body text-ink-3">No matching tickers found</div>
              <div className="ts-small text-ink-4 mt-1">Try a different search term</div>
            </div>
          ) : (
            instruments.map((instrument) => (
              <div
                key={instrument.id}
                className="flex cursor-pointer items-center justify-between px-4 py-3 hover:bg-white/60 transition-colors border-b border-rule-2 last:border-b-0"
                onClick={() => handleSelect(instrument)}
              >
                <div className="flex flex-col gap-0.5">
                  <div className="ts-mono text-[13px] font-bold text-ink">{instrument.symbol}</div>
                  <div className="ts-small text-ink-3 line-clamp-1">{instrument.name}</div>
                </div>
                <div className="flex flex-col items-end gap-1">
                  <span className="ts-mono text-[11px] px-1.5 py-0.5 rounded bg-bg-2 text-ink-2 border border-ink-4/10">
                    {instrument.exchange}
                  </span>
                  <span className="ts-mono text-[12px] text-ink-2 font-medium">
                    ₹{instrument.last_price?.toLocaleString('en-IN')}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

