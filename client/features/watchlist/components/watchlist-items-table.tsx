"use client";

import { Trash, ArrowUpDown } from "lucide-react";
import { toast } from "sonner";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { WatchlistItem, useRemoveWatchlistItem } from "@/features/watchlist";

interface WatchlistItemsTableProps {
  watchlistId: string;
  items: WatchlistItem[];
  isLoading: boolean;
}

export function WatchlistItemsTable({ watchlistId, items, isLoading }: WatchlistItemsTableProps) {
  const removeItem = useRemoveWatchlistItem();

  const handleRemove = (instrumentId: string) => {
    removeItem.mutate(
      { watchlistId, instrumentId },
      {
        onSuccess: () => toast.success("Item removed"),
        onError: () => toast.error("Failed to remove item"),
      }
    );
  };

  if (isLoading) {
    return <div className="p-8 text-center text-slate-500">Loading items...</div>;
  }

  if (items.length === 0) {
    return (
      <div className="p-12 text-center border rounded-lg bg-slate-50 mt-4">
        <h3 className="text-lg font-medium text-slate-900">Your watchlist is empty</h3>
        <p className="text-slate-500 mt-1">Add instruments to start tracking them here.</p>
      </div>
    );
  }

  return (
    <div className="rounded-md border mt-4">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[100px]">Symbol</TableHead>
            <TableHead>Name</TableHead>
            <TableHead>Exchange</TableHead>
            <TableHead className="text-right">Last Price</TableHead>
            <TableHead className="text-right">Change</TableHead>
            <TableHead className="w-[80px]"></TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {items.map((item) => (
            <TableRow key={item.id}>
              <TableCell className="font-medium">{item.symbol}</TableCell>
              <TableCell>{item.name || "—"}</TableCell>
              <TableCell>{item.exchange}</TableCell>
              <TableCell className="text-right">
                {item.last_price !== null ? `$${item.last_price.toFixed(2)}` : "—"}
              </TableCell>
              <TableCell className={`text-right ${item.change_percent && item.change_percent >= 0 ? "text-green-600" : "text-red-600"}`}>
                {item.change_percent !== null ? `${item.change_percent > 0 ? "+" : ""}${item.change_percent.toFixed(2)}%` : "—"}
              </TableCell>
              <TableCell>
                <Button
                  variant="ghost"
                  size="icon"
                  className="text-slate-400 hover:text-red-600"
                  onClick={() => handleRemove(item.instrument_id)}
                  disabled={removeItem.isPending}
                >
                  <Trash className="h-4 w-4" />
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
