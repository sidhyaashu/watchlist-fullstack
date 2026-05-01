"use client";

import { Trash, ExternalLink, GripVertical } from "lucide-react";
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
import { PriceRangeBand } from "./price-range-band";
import { getLogoGradient } from "@/lib/utils/logo-utils";

interface WatchlistItemsTableProps {
  watchlistId: string;
  items: WatchlistItem[];
  isLoading: boolean;
}

export function WatchlistItemsTable({ watchlistId, items, isLoading }: WatchlistItemsTableProps) {
  const removeItem = useRemoveWatchlistItem();

  const handleRemove = (instrumentId: number) => {
    removeItem.mutate(
      { watchlistId, instrumentId: instrumentId.toString() },
      {
        onSuccess: () => toast.success("Item removed"),
        onError: () => toast.error("Failed to remove item"),
      }
    );
  };

  if (isLoading) {
    return <div className="p-8 text-center text-ink-3 ts-body">Loading items...</div>;
  }

  if (items.length === 0) {
    return (
      <div className="glass-card p-12 text-center mt-6">
        <h3 className="ts-h2 text-ink">Your watchlist is empty</h3>
        <p className="ts-body text-ink-3 mt-1">Add instruments to start tracking them here.</p>
      </div>
    );
  }

  return (
    <div className="glass-card mt-6 overflow-hidden">
      <div className="p-4 border-b border-rule flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity className="text-accent w-4 h-4" />
          <span className="ts-h2 text-sm font-semibold">Tracked Assets</span>
          <span className="ts-eyebrow ml-2">{items.length} items</span>
        </div>
      </div>
      <div className="overflow-x-auto">
        <Table className="w-full border-collapse">
          <TableHeader>
            <TableRow className="bg-white/40 hover:bg-white/40">
              <TableHead className="w-10"></TableHead>
              <TableHead className="ts-eyebrow py-3">Stock</TableHead>
              <TableHead className="ts-eyebrow text-right">Price</TableHead>
              <TableHead className="ts-eyebrow text-right">Day</TableHead>
              <TableHead className="ts-eyebrow text-center">52W Range</TableHead>
              <TableHead className="ts-eyebrow">Sector</TableHead>
              <TableHead className="w-20 text-right pr-6">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {items.map((item) => (
              <TableRow key={item.id} className="group hover:bg-white/55 border-b border-rule-2 transition-colors">
                <TableCell className="text-center cursor-grab active:cursor-grabbing">
                  <GripVertical className="w-4 h-4 text-ink-4 opacity-50 group-hover:opacity-100 group-hover:text-accent transition-opacity" />
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-3 min-w-[200px]">
                    <div 
                      className="w-9 h-9 rounded-lg flex items-center justify-center font-bold text-xs text-white shadow-sm"
                      style={{ background: getLogoGradient(item.symbol) }}
                    >
                      {item.symbol.slice(0, 2)}
                    </div>
                    <div>
                      <div className="ts-body font-semibold text-ink leading-tight">{item.name || "Unknown Company"}</div>
                      <div className="ts-mono text-[10.5px] text-ink-3 font-medium mt-0.5">{item.symbol} · NSE</div>
                    </div>
                  </div>
                </TableCell>
                <TableCell className="text-right">
                  <span className="ts-mono text-[13.5px] font-bold text-ink">
                    ₹{item.last_price?.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </span>
                </TableCell>
                <TableCell className="text-right">
                  <div className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full ts-mono text-[11.5px] font-semibold ${item.change_percent && item.change_percent >= 0 ? "text-good bg-good-soft" : "text-danger-deep bg-danger-soft"}`}>
                    {item.change_percent !== null ? (
                      <>
                        {item.change_percent >= 0 ? "↑" : "↓"}
                        {Math.abs(item.change_percent).toFixed(2)}%
                      </>
                    ) : "—"}
                  </div>
                </TableCell>
                <TableCell className="text-center">
                  <PriceRangeBand current={item.last_price || 0} low={item.last_price ? item.last_price * 0.8 : 0} high={item.last_price ? item.last_price * 1.2 : 0} />
                </TableCell>
                <TableCell>
                  <span className="inline-block ts-small px-2 py-0.5 rounded-full bg-accent-soft text-accent-deep border border-accent/20">
                    Financials
                  </span>
                </TableCell>
                <TableCell className="text-right pr-6">
                  <div className="flex justify-end gap-1">
                    <Button variant="ghost" size="icon" className="w-8 h-8 rounded-lg text-ink-3 hover:bg-accent-soft hover:text-accent-deep transition-all">
                      <ExternalLink className="w-3.5 h-3.5" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="w-8 h-8 rounded-lg text-ink-3 hover:bg-danger-soft hover:text-danger-deep transition-all"
                      onClick={() => handleRemove(item.instrument_id)}
                      disabled={removeItem.isPending}
                    >
                      <Trash className="w-3.5 h-3.5" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}

import { Activity } from "lucide-react";

