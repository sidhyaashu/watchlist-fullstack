"use client";

import { use } from "react";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { DashboardLayout } from "@/components/layouts/dashboard-layout";
import { 
  useWatchlist, 
  useWatchlistItems, 
  InstrumentSearch, 
  WatchlistKPIs, 
  WatchlistItemsTable 
} from "@/features/watchlist";


export default function WatchlistDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const id = resolvedParams.id;
  
  const { data: watchlist, isLoading: isLoadingWatchlist } = useWatchlist(id);
  const { data: items = [], isLoading: isLoadingItems } = useWatchlistItems(id);

  return (
    <DashboardLayout>
      <div className="flex flex-col gap-6 animate-in fade-in duration-500">
        {/* ── HERO SECTION ── */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
          <div className="space-y-1.5">
            <div className="ts-eyebrow text-[10px] flex items-center gap-2">
              <Link href="/dashboard" className="hover:text-accent transition-colors">Home</Link>
              <span className="opacity-30">/</span>
              <span>Watchlist</span>
            </div>
            {isLoadingWatchlist ? (
              <div className="h-10 w-64 bg-ink-4/10 animate-pulse rounded-lg" />
            ) : (
              <h1 className="text-4xl font-bold text-ink tracking-tight">{watchlist?.name || "My Watchlist"}</h1>
            )}
            <p className="ts-body text-ink-3 max-w-[540px]">
              Stocks you're tracking, organised your way. Click any name to dive into the full brief — price action, fundamentals, AI verdict.
            </p>
          </div>
        </div>

        {/* ── KPI STRIP ── */}
        <WatchlistKPIs items={items} />

        {/* ── HERO SEARCH ── */}
        <div className="glass-card p-1.5 flex items-center gap-3 group focus-within:ring-4 focus-within:ring-accent-soft transition-all duration-300">
          <div className="pl-3.5 text-ink-3 group-focus-within:text-accent transition-colors">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
          </div>
          <input 
            placeholder="Search your watchlist or add a stock — e.g. TCS, Reliance, Bajaj Finance…" 
            className="flex-1 bg-transparent border-0 outline-none ts-body py-2.5 text-ink placeholder:text-ink-4"
          />
          <div className="hidden sm:flex items-center gap-1.5 px-2 py-1 rounded-md bg-white/60 border border-rule ts-mono text-[10px] text-ink-3 font-semibold uppercase">
            ⌘K
          </div>
          <InstrumentSearch watchlistId={id} />
        </div>

        {/* ── LIST TABS ── */}
        <div className="glass-card p-2 flex items-center gap-2 overflow-x-auto no-scrollbar">
          <div className="flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-accent-soft border border-accent/20 text-accent-deep font-bold ts-small shadow-sm">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polygon points="12 2 15.1 8.6 22 9.6 17 14.5 18.2 21.5 12 18.1 5.8 21.5 7 14.5 2 9.6 8.9 8.6"/></svg>
            All <span className="bg-accent text-white px-1.5 rounded-full text-[9px] ml-1">{items.length}</span>
          </div>
          <div className="flex items-center gap-1.5 px-3.5 py-2 rounded-lg hover:bg-white/60 text-ink-2 font-medium ts-small transition-all cursor-pointer">
            <span className="w-2 h-2 rounded-sm bg-good opacity-80" />
            Core holdings <span className="text-ink-4 text-[10px] ml-1">5</span>
          </div>
          <div className="flex items-center gap-1.5 px-3.5 py-2 rounded-lg hover:bg-white/60 text-ink-2 font-medium ts-small transition-all cursor-pointer">
            <span className="w-2 h-2 rounded-sm bg-accent opacity-80" />
            IT services <span className="text-ink-4 text-[10px] ml-1">3</span>
          </div>
          <div className="ml-auto flex items-center gap-1.5 px-3.5 py-2 rounded-lg border border-dashed border-rule text-ink-3 font-medium ts-small hover:border-accent hover:text-accent transition-all cursor-pointer">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><path d="M12 5v14M5 12h14"/></svg>
            New list
          </div>
        </div>

        {/* ── TABLE CARD ── */}
        <WatchlistItemsTable 
          watchlistId={id} 
          items={items} 
          isLoading={isLoadingItems} 
        />
      </div>
    </DashboardLayout>
  );
}

