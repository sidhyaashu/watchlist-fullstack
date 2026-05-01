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
      <Card className="hover:border-indigo-500 hover:shadow-md transition-all cursor-pointer h-full flex flex-col group">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-lg font-semibold group-hover:text-indigo-600 transition-colors">
            {watchlist.name}
          </CardTitle>
          <div onClick={(e) => e.preventDefault()}>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="h-8 w-8">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem
                  className="text-red-600 focus:text-red-600 cursor-pointer"
                  onClick={handleDelete}
                >
                  <Trash className="mr-2 h-4 w-4" />
                  Delete
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </CardHeader>
        <CardContent className="flex-1">
          <div className="flex items-center text-sm text-slate-500 mt-2">
            <ListEnd className="mr-2 h-4 w-4" />
            <span>Created {format(new Date(watchlist.created_at), "MMM d, yyyy")}</span>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
