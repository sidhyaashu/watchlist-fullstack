"use client";

import { use, useState, useMemo } from "react";
import Link from "next/link";
import { DashboardLayout } from "@/components/layouts/dashboard-layout";
import {
  useWatchlist,
  useWatchlistItems,
  InstrumentSearch,
  WatchlistKPIs,
  WatchlistItemsTable,
} from "@/features/watchlist";
import { WatchlistTabs } from "@/features/watchlist/components/watchlist-tabs";

export default function WatchlistDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const id = resolvedParams.id;

  const { data: watchlist, isLoading: isLoadingWatchlist } = useWatchlist(id);

  // ── Pagination state ──────────────────────────────────────────────────────
  const [page, setPage] = useState(1);
  const limit = 10;

  // We fetch a larger batch (100) to ensure KPIs, Tabs, and Filters work 
  // across the whole watchlist, as tags are currently client-side.
  const { data: paginatedData, isLoading: isLoadingItems } = useWatchlistItems(id, { skip: 0, limit: 100 });
  const allItems = paginatedData?.items ?? [];
  const totalItemsCount = paginatedData?.total ?? 0;

  // ── Hero search: filters already-added stocks ─────────────────────────────
  const [heroQuery, setHeroQuery] = useState("");

  // ── Tabs: active tag (null = All) ─────────────────────────────────────────
  const [activeTagId, setActiveTagId] = useState<string | null>(null);

  // ── Derive filtered + tagged view ─────────────────────────────────────────
  const filteredItems = useMemo(() => {
    let list = allItems;

    // Filter by hero search
    if (heroQuery.trim()) {
      const q = heroQuery.toLowerCase();
      list = list.filter(
        item =>
          item.symbol.toLowerCase().includes(q) ||
          (item.name ?? "").toLowerCase().includes(q) ||
          (item.sector ?? "").toLowerCase().includes(q)
      );
    }

    // Filter by active tag
    if (activeTagId !== null) {
      try {
        const stored = JSON.parse(
          localStorage.getItem(`wl_tags_${id}`) || "[]"
        ) as Array<{ id: string; symbol_ids: string[] }>;
        const tag = stored.find(t => t.id === activeTagId);
        if (tag) {
          list = list.filter(item => tag.symbol_ids.includes(item.id));
        }
      } catch { /* ignore */ }
    }

    return list;
  }, [allItems, heroQuery, activeTagId, id]);

  // ── Slice for pagination ──────────────────────────────────────────────────
  const displayItems = useMemo(() => {
    const start = (page - 1) * limit;
    return filteredItems.slice(start, start + limit);
  }, [filteredItems, page, limit]);

  return (
    <DashboardLayout>
      <div className="flex flex-col gap-0 animate-in fade-in duration-500 max-w-7xl mx-auto w-full pb-8">

        {/* ── HERO SECTION ── */}
        <div className="hero mb-8">
          <div>
            <div className="ts-eyebrow mb-2">
              <Link href="/dashboard" className="hover:text-accent transition-colors">Home</Link>&nbsp;/&nbsp;Watchlist
            </div>
            {isLoadingWatchlist ? (
              <div className="h-10 w-64 bg-ink-4/10 animate-pulse rounded-xl mb-2" />
            ) : (
              <h1 className="ts-display mb-2">{watchlist?.name || "My Watchlist"}</h1>
            )}
            <div className="ts-body text-ink-3 max-w-2xl">
              Stocks you&apos;re tracking, organised your way. Click any name to dive into the full
              brief — price action, fundamentals, AI verdict.
            </div>
          </div>
        </div>

        {/* ── KPI STRIP ── */}
        <WatchlistKPIs items={allItems} />

        {/* ── HERO SEARCH  +  ADD STOCK BUTTON ── */}
        {/*
          The search input here filters the list the user already has.
          The "Add stock" button inside InstrumentSearch opens the DB-backed modal.
        */}
        <div className="hero-search mb-6">
          {/* Search icon */}
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
            strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4 flex-shrink-0"
            style={{ color: "var(--ink-3)" }}>
            <circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>
          </svg>
<truncated 10 lines>
          <input
            value={heroQuery}
            onChange={e => setHeroQuery(e.target.value)}
            placeholder="Filter your watchlist — symbol, name or sector…"
            className="bg-transparent"
          />

          {/* Keyboard hint */}
          <div className="kbd">⌘K</div>

          {/* Add stock — this opens the DB search modal via InstrumentSearch */}
          <InstrumentSearch watchlistId={id} heroOnly />
        </div>

        {/* ── LIST TABS ── */}
        <WatchlistTabs
          watchlistId={id}
          items={allItems}
          activeTagId={activeTagId}
          onTagChange={(newId) => {
            setActiveTagId(newId);
            setPage(1); // Reset to page 1 when changing tabs
          }}
        />

        {/* ── TABLE CARD ── */}
        <WatchlistItemsTable
          watchlistId={id}
          items={displayItems}
          isLoading={isLoadingItems}
          allItems={allItems}
          activeTagId={activeTagId}
          page={page}
          onPageChange={setPage}
          totalItems={filteredItems.length}
        />
      </div>
    </DashboardLayout>
  );
}
