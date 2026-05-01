"use client";

import { DashboardLayout } from "@/components/layouts/dashboard-layout";
import { useWatchlists } from "@/features/watchlist";
import { WatchlistCard } from "@/features/watchlist/components/watchlist-card";
import { CreateWatchlistDialog } from "@/features/watchlist/components/create-watchlist-dialog";
import { Skeleton } from "@/components/ui/skeleton";

export default function WatchlistsPage() {
  const { data: watchlists, isLoading } = useWatchlists();

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">Watchlists</h1>
            <p className="text-slate-500">Manage and track your custom lists of instruments.</p>
          </div>
          <CreateWatchlistDialog />
        </div>

        {isLoading ? (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {[...Array(3)].map((_, i) => (
              <Skeleton key={i} className="h-32 w-full rounded-xl" />
            ))}
          </div>
        ) : !watchlists || watchlists.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-24 text-center border-2 border-dashed rounded-xl bg-slate-50">
            <h3 className="mt-2 text-lg font-semibold text-slate-900">No watchlists</h3>
            <p className="mt-1 text-sm text-slate-500 mb-6">
              You haven't created any watchlists yet.
            </p>
            <CreateWatchlistDialog />
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {watchlists.map((watchlist) => (
              <WatchlistCard key={watchlist.id} watchlist={watchlist} />
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
