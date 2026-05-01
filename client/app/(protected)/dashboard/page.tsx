"use client";

import { DashboardLayout } from "@/components/layouts/dashboard-layout";
import { useAuth } from "@/hooks/use-auth";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useWatchlists } from "@/features/watchlist";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";

export default function DashboardPage() {
  const { user } = useAuth();

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Overview</h1>
          <p className="text-slate-500">Welcome to your investment dashboard.</p>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Account Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">Active</div>
              <p className="text-xs text-slate-500">Verified as {user?.email}</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Last Login</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">Just now</div>
              <p className="text-xs text-slate-500">Secure session established</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Assets Under Management</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">$0.00</div>
              <p className="text-xs text-slate-500">Connect a wallet to get started</p>
            </CardContent>
          </Card>
        </div>

        {/* Watchlists Widget added below the top metrics */}
        <div className="grid gap-6 md:grid-cols-2">
          <WatchlistWidget />
          
          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
              <CardDescription>
                Your latest authentication and account events.
              </CardDescription>
            </CardHeader>
            <CardContent>
            <div className="space-y-4">
              <div className="flex items-center">
                <div className="ml-4 space-y-1">
                  <p className="text-sm font-medium leading-none">Login Successful</p>
                  <p className="text-sm text-slate-500">You logged in from a new device.</p>
                </div>
                <div className="ml-auto font-medium text-xs text-slate-400">2 minutes ago</div>
              </div>
              <div className="flex items-center">
                <div className="ml-4 space-y-1">
                  <p className="text-sm font-medium leading-none">Email Verified</p>
                  <p className="text-sm text-slate-500">Your account is now fully active.</p>
                </div>
                <div className="ml-auto font-medium text-xs text-slate-400">10 minutes ago</div>
              </div>
            </div>
          </CardContent>
        </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}

function WatchlistWidget() {
  const { data: watchlists, isLoading } = useWatchlists({ limit: 3 });

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div>
          <CardTitle>Your Watchlists</CardTitle>
          <CardDescription>Recently active lists</CardDescription>
        </div>
        <Link href="/watchlists">
          <Button variant="ghost" size="sm" className="text-indigo-600">
            View All <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </Link>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-3">
            {[1, 2].map(i => (
              <div key={i} className="h-12 bg-slate-100 rounded-md animate-pulse" />
            ))}
          </div>
        ) : !watchlists || watchlists.length === 0 ? (
          <div className="text-center p-4 border border-dashed rounded-md text-slate-500 text-sm">
            No watchlists created yet.
          </div>
        ) : (
          <div className="space-y-3">
            {watchlists.map(list => (
              <Link key={list.id} href={`/watchlists/${list.id}`}>
                <div className="flex justify-between items-center p-3 rounded-md border hover:border-indigo-300 hover:bg-slate-50 transition-colors cursor-pointer">
                  <span className="font-medium text-slate-800">{list.name}</span>
                  <span className="text-xs text-slate-400">View</span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
