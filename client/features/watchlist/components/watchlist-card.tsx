"use client";

import Link from "next/link";
import { format } from "date-fns";
import { MoreHorizontal, Trash, ListEnd } from "lucide-react";
import { toast } from "sonner";
import { Watchlist, useDeleteWatchlist } from "@/features/watchlist";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";

interface WatchlistCardProps {
  watchlist: Watchlist;
}

export function WatchlistCard({ watchlist }: WatchlistCardProps) {
  const deleteWatchlist = useDeleteWatchlist();

  const handleDelete = (e: React.MouseEvent) => {
    e.preventDefault(); // Prevent navigating to the link
    if (confirm("Are you sure you want to delete this watchlist?")) {
      deleteWatchlist.mutate(watchlist.id, {
        onSuccess: () => toast.success("Watchlist deleted"),
        onError: () => toast.error("Failed to delete watchlist"),
      });
    }
  };

  return (
    <Link href={`/watchlists/${watchlist.id}`}>
      <div className="glass-card hover:bg-white/60 hover:-translate-y-1 hover:shadow-lg transition-all duration-300 cursor-pointer h-full flex flex-col group p-5">
        <div className="flex flex-row items-center justify-between pb-2">
          <h2 className="ts-h2 text-ink group-hover:text-accent transition-colors">
            {watchlist.name}
          </h2>
          <div onClick={(e) => e.preventDefault()}>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="h-8 w-8 text-ink-3 hover:text-ink hover:bg-white/40">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="glass-card">
                <DropdownMenuItem
                  className="text-danger-deep focus:text-danger focus:bg-danger-soft cursor-pointer ts-body"
                  onClick={handleDelete}
                >
                  <Trash className="mr-2 h-4 w-4" />
                  Delete
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
        <div className="flex-1">
          <div className="flex items-center ts-body text-ink-3 mt-4">
            <ListEnd className="mr-2 h-4 w-4 opacity-50" />
            <span className="ts-small">Created {format(new Date(watchlist.created_at), "MMM d, yyyy")}</span>
          </div>
        </div>
      </div>
    </Link>
  );
}

