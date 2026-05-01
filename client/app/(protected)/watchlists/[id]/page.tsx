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
      <div className="max-w-[1200px] mx-auto space-y-8 py-4">
        {/* Header Section */}
        <div className="flex flex-col gap-1">
          <div className="flex items-center gap-3">
            <Link href="/watchlists" className="p-2 -ml-2 rounded-full hover:bg-white/40 transition-colors">
              <ArrowLeft className="h-5 w-5 text-ink-3" />
            </Link>
            {isLoadingWatchlist ? (
              <div className="h-8 w-48 bg-ink-4/10 animate-pulse rounded" />
            ) : (
              <h1 className="ts-h1 text-ink">{watchlist?.name}</h1>
            )}
          </div>
          <p className="ts-body text-ink-3 ml-8">
            Manage your tracked assets and monitor performance in real-time.
          </p>
        </div>

        {/* KPIs Strip */}
        <WatchlistKPIs items={items} />


        {/* Main Content Area */}
        <div className="space-y-4">
          <div className="flex justify-between items-end">
            <div className="flex flex-col gap-1">
              <h2 className="ts-h2 text-ink">Instruments</h2>
              <div className="ts-eyebrow">Showing {items.length} stocks</div>
            </div>
            <div className="flex items-center gap-3">
              <InstrumentSearch watchlistId={id} />
            </div>
          </div>

          <WatchlistItemsTable 
            watchlistId={id} 
            items={items} 
            isLoading={isLoadingItems} 
          />
        </div>
      </div>
    </DashboardLayout>
  );
}

