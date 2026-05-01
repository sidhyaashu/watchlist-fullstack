"use client";

import { use } from "react";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { DashboardLayout } from "@/components/layouts/dashboard-layout";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useWatchlist, useWatchlistItems, InstrumentSearch } from "@/features/watchlist";
import { WatchlistItemsTable } from "@/features/watchlist/components/watchlist-items-table";

export default function WatchlistDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const id = resolvedParams.id;
  
  const { data: watchlist, isLoading: isLoadingWatchlist } = useWatchlist(id);
  const { data: items = [], isLoading: isLoadingItems } = useWatchlistItems(id);

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center space-x-4">
          <Link href="/watchlists">
            <Button variant="outline" size="icon" className="h-8 w-8">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          {isLoadingWatchlist ? (
            <Skeleton className="h-8 w-48" />
          ) : (
            <div>
              <h1 className="text-2xl font-bold text-slate-900">{watchlist?.name}</h1>
              <p className="text-sm text-slate-500">Manage the instruments in this list</p>
            </div>
          )}
        </div>

        <div className="flex justify-between items-end">
          <h2 className="text-lg font-semibold mb-2">Instruments</h2>
          <InstrumentSearch watchlistId={id} />
        </div>

        <WatchlistItemsTable 
          watchlistId={id} 
          items={items} 
          isLoading={isLoadingItems} 
        />
      </div>
    </DashboardLayout>
  );
}
