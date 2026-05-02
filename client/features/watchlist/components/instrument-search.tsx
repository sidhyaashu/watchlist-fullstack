"use client";

import { useState, useRef, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { searchInstruments, fetchPopularInstruments } from "../api/market-api";
import { useAddWatchlistItem } from "../hooks/use-add-watchlist-item";
import { useWatchlistItems } from "../hooks/use-watchlist-items";
import { useDebounce } from "@/hooks/use-debounce";
import { Loader2 } from "lucide-react";
import type { Instrument } from "../api/market-api";
import { getLogoGradient } from "@/lib/utils/logo-utils";
import { Numeric } from "@/components/ui/numeric";
import { toast } from "sonner";

interface InstrumentSearchProps {
  watchlistId: string;
  /** When true, renders only the "Add stock" button (hero search bar is handled by parent) */
  heroOnly?: boolean;
}

function fmtPrice(n: number | null) {
  if (!n) return "—";
  return n.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

export function InstrumentSearch({ watchlistId, heroOnly = false }: InstrumentSearchProps) {
  const [query, setQuery] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [localTracked, setLocalTracked] = useState<Set<string>>(new Set());
  const modalInputRef = useRef<HTMLInputElement>(null);
  const [debouncedQuery] = useDebounce(query, 300);

  // Live search results (only fires when user types)
  const { data: searchResults, isLoading: isSearching } = useQuery({
    queryKey: ["instruments", "search", debouncedQuery],
    queryFn: () => searchInstruments(debouncedQuery),
    enabled: debouncedQuery.length > 0,
    staleTime: 1000 * 60 * 5,
  });

  // Popular instruments — shown on open with no query
  const { data: popularResults, isLoading: isLoadingPopular } = useQuery({
    queryKey: ["instruments", "popular"],
    queryFn: () => fetchPopularInstruments(8),
    staleTime: 1000 * 60 * 10,
    enabled: isModalOpen, // only fetch when modal is actually open
  });

  // Current watchlist items — for "Already Added" detection
  const { data: paginatedItems } = useWatchlistItems(watchlistId, { limit: 100 }); // Fetch enough to detect tracked
  const trackedSymbols = new Set([
    ...(paginatedItems?.items?.map(i => i.symbol) ?? []),
    ...localTracked,
  ]);

  const addMutation = useAddWatchlistItem();

  // Which list to show
  const displayList = debouncedQuery.length > 0 ? (searchResults ?? []) : (popularResults ?? []);
  const sectionLabel = debouncedQuery.length > 0
    ? `${displayList.length} match${displayList.length !== 1 ? "es" : ""}`
    : "Popular on InvestKaro";
  const isLoading = debouncedQuery.length > 0 ? isSearching : isLoadingPopular;

  // CMD+K shortcut
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") { e.preventDefault(); setIsModalOpen(true); }
      if (e.key === "Escape" && isModalOpen) { setIsModalOpen(false); }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isModalOpen]);

  // External open event (table header button)
  useEffect(() => {
    const handleOpenModal = () => setIsModalOpen(true);
    document.addEventListener("open-add-stock-modal", handleOpenModal);
    return () => document.removeEventListener("open-add-stock-modal", handleOpenModal);
  }, []);

  // Auto-focus input when modal opens
  useEffect(() => {
    if (isModalOpen) {
      setTimeout(() => modalInputRef.current?.focus(), 50);
    } else {
      setQuery(""); // reset search when closing
    }
  }, [isModalOpen]);

  // Enter key — add first match
  const handleModalKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      const first = displayList.find(i => !trackedSymbols.has(i.symbol));
      if (first) handleSelect(first);
    }
  };

  const handleSelect = (instrument: Instrument) => {
    if (trackedSymbols.has(instrument.symbol)) {
      toast.error(`${instrument.symbol} is already in your watchlist`);
      return;
    }

    // Optimistic local tracking so the green "Added" shows instantly
    setLocalTracked(prev => new Set([...prev, instrument.symbol]));

    addMutation.mutate(
      {
        watchlistId,
        payload: {
          instrument_id: instrument.id,
          symbol: instrument.symbol,
          exchange: instrument.exchange,
        },
      },
      {
        onSuccess: () => toast.success(`${instrument.symbol} added to watchlist`),
        onError: () => {
          toast.error(`Failed to add ${instrument.symbol}`);
          setLocalTracked(prev => { const n = new Set(prev); n.delete(instrument.symbol); return n; });
        },
      }
    );
  };

  return (
    <>
      {/* Hero search bar — only rendered when not in heroOnly mode */}
      {!heroOnly && (
        <div className="hero-search bg-white/40 dark:bg-black/20" onClick={() => setIsModalOpen(true)}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4 text-ink-3 flex-shrink-0">
            <circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>
          </svg>
          <input
            readOnly
            placeholder="Search your watchlist or add a stock — e.g. TCS, Reliance, Bajaj Finance…"
            className="cursor-pointer bg-transparent"
          />
          <div className="kbd">⌘K</div>
          <button className="add-btn bg-accent text-white dark:text-bg-1" onClick={e => { e.stopPropagation(); setIsModalOpen(true); }}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round">
              <path d="M12 5v14M5 12h14"/>
            </svg>
            Add stock
          </button>
        </div>
      )}

      {/* heroOnly mode: just render the Add stock button */}
      {heroOnly && (
        <button className="add-btn" onClick={() => setIsModalOpen(true)}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round">
            <path d="M12 5v14M5 12h14"/>
          </svg>
          Add stock
        </button>
      )}

      {/* Modal */}
      {isModalOpen && (
        <div
          className="fixed inset-0 z-[100] flex items-start justify-center pt-20 px-4"
          style={{ background: "rgba(11,37,69,.32)", backdropFilter: "blur(6px)" }}
          onClick={e => { if (e.target === e.currentTarget) setIsModalOpen(false); }}
        >
          <div
            className="w-full max-w-[580px] rounded-[18px] overflow-hidden glass-card"
            style={{
              animation: "modalIn .25s cubic-bezier(.2,.7,.3,1) both",
            }}
            onClick={e => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="flex items-center justify-between px-[18px] py-4" style={{ borderBottom: "1px solid var(--rule)" }}>
              <div className="flex items-center gap-2 text-[15px] font-semibold text-ink">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ color: "var(--accent)" }}>
                  <circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>
                </svg>
                Add stock to watchlist
              </div>
              <button
                onClick={() => setIsModalOpen(false)}
                className="w-7 h-7 rounded-lg grid place-items-center text-ink-3 hover:text-ink transition-colors"
                style={{ border: 0, background: "transparent" }}
                onMouseEnter={e => (e.currentTarget.style.background = "var(--rule-2)")}
                onMouseLeave={e => (e.currentTarget.style.background = "transparent")}
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
                  <path d="M18 6L6 18M6 6l12 12"/>
                </svg>
              </button>
            </div>

            {/* Search Field */}
            <div className="px-[18px] py-[14px]" style={{ borderBottom: "1px solid var(--rule-2)" }}>
              <div
                className="flex items-center gap-[10px] rounded-[10px] px-[14px] py-[10px] transition-all"
                style={{
                  background: "var(--rule-2)",
                  border: "1px solid var(--rule)",
                }}
                onFocusCapture={e => {
                  e.currentTarget.style.borderColor = "var(--accent-2)";
                  e.currentTarget.style.background = "var(--bg-1)";
                  e.currentTarget.style.boxShadow = "0 0 0 3px var(--accent-soft)";
                }}
                onBlurCapture={e => {
                  e.currentTarget.style.borderColor = "var(--rule)";
                  e.currentTarget.style.background = "var(--rule-2)";
                  e.currentTarget.style.boxShadow = "none";
                }}
              >
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ color: "var(--ink-3)", flexShrink: 0 }}>
                  <circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>
                </svg>
                <input
                  ref={modalInputRef}
                  value={query}
                  onChange={e => setQuery(e.target.value)}
                  onKeyDown={handleModalKeyDown}
                  placeholder="Search NSE / BSE — type a name or ticker"
                  autoComplete="off"
                  style={{
                    border: 0, outline: 0, background: "transparent",
                    fontSize: 14, flex: 1, color: "var(--ink)", fontFamily: "inherit",
                  }}
                />
                {isLoading && <Loader2 className="w-4 h-4 animate-spin text-ink-3" />}
              </div>
              <div className="mt-2" style={{ fontSize: 11, color: "var(--ink-3)", fontFamily: "var(--mono)", letterSpacing: ".06em" }}>
                Press <b>Enter</b> to add the top match · <b>Esc</b> to close
              </div>
            </div>

            {/* Results List */}
            <div style={{ maxHeight: 340, overflowY: "auto", padding: 6 }}
              className="[&::-webkit-scrollbar]:w-[6px] [&::-webkit-scrollbar-thumb]:bg-rule [&::-webkit-scrollbar-thumb]:rounded-md"
            >
              {isLoading && debouncedQuery.length > 0 ? (
                <div className="flex justify-center items-center py-10 text-ink-3 text-[13px] gap-2">
                  <Loader2 className="w-4 h-4 animate-spin" /> Searching…
                </div>
              ) : displayList.length === 0 && debouncedQuery.length > 0 ? (
                <div style={{ padding: "36px 18px", textAlign: "center", color: "var(--ink-3)", fontSize: 13 }}>
                  No matches for "<b>{debouncedQuery}</b>". Try a ticker like <b>RELIANCE</b> or <b>TCS</b>.
                </div>
              ) : (
                <>
                  {/* Section Label */}
                  <div style={{
                    fontFamily: "var(--mono)", fontSize: "9.5px", color: "var(--ink-3)",
                    textTransform: "uppercase", letterSpacing: ".12em",
                    padding: "10px 12px 4px", fontWeight: 600,
                  }}>
                    {sectionLabel}
                  </div>

                  {/* Rows */}
                  {displayList.map(instrument => {
                    const isTracked = trackedSymbols.has(instrument.symbol);
                    const changeIsPositive = (instrument.pe ?? 0) >= 0;

                    return (
                      <div
                        key={instrument.id}
                        onClick={() => handleSelect(instrument)}
                        style={{
                          display: "grid",
                          gridTemplateColumns: "auto 1fr auto auto",
                          gap: 11,
                          alignItems: "center",
                          padding: "9px 12px",
                          borderRadius: 9,
                          cursor: isTracked ? "default" : "pointer",
                          transition: ".12s",
                        }}
                        onMouseEnter={e => { if (!isTracked) e.currentTarget.style.background = "var(--accent-soft)"; }}
                        onMouseLeave={e => { e.currentTarget.style.background = "transparent"; }}
                      >
                        {/* Logo */}
                        <div
                          className="logo"
                          style={{
                            width: 30, height: 30, fontSize: "10.5px", borderRadius: 8,
                            background: getLogoGradient(instrument.symbol),
                          }}
                        >
                          {instrument.symbol.slice(0, 2)}
                        </div>

                        {/* Info */}
                        <div>
                          <div style={{ fontSize: 13, fontWeight: 600, color: "var(--ink)" }}>{instrument.name}</div>
                          <div style={{ fontSize: 11, color: "var(--ink-3)", fontFamily: "var(--mono)", marginTop: 1 }}>
                            {instrument.symbol} · {instrument.exchange || "NSE"}
                          </div>
                        </div>

                        {/* Price + Change */}
                        <div style={{ fontSize: 12, textAlign: "right" }}>
                          <div style={{ fontFamily: "var(--mono)", fontWeight: 600, color: "var(--ink)" }}>
                            ₹{fmtPrice(instrument.last_price)}
                          </div>
                          {instrument.pe != null && (
                            <div
                              className="ch"
                              style={{
                                fontSize: "10.5px",
                                padding: "1px 6px",
                                marginTop: 2,
                                display: "inline-flex",
                              }}
                            >
                              <span className={changeIsPositive ? "ch up" : "ch dn"}>
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" style={{ width: 9, height: 9 }}>
                                  {changeIsPositive
                                    ? <polyline points="6 14 12 8 18 14"/>
                                    : <polyline points="6 10 12 16 18 10"/>
                                  }
                                </svg>
                                {changeIsPositive ? "+" : ""}<Numeric value={instrument.pe} precision={2} />%
                              </span>
                            </div>
                          )}
                        </div>

                        {/* Added indicator OR Add button */}
                        {isTracked ? (
                          <div style={{
                            color: "var(--good)", fontSize: 11, fontWeight: 600,
                            display: "flex", alignItems: "center", gap: 4, minWidth: 60,
                          }}>
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" style={{ width: 12, height: 12 }}>
                              <polyline points="20 6 9 17 4 12"/>
                            </svg>
                            Added
                          </div>
                        ) : (
                          <div
                            className="add-ic"
                            style={{ width: 30, height: 30, borderRadius: 8 }}
                            onClick={e => { e.stopPropagation(); handleSelect(instrument); }}
                          >
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round">
                              <path d="M12 5v14M5 12h14"/>
                            </svg>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
