"use client";

import { Activity, Trash, ExternalLink, GripVertical } from "lucide-react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
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
import { WATCHLIST_COLUMNS } from "../config/column-definitions";
import { Numeric } from "@/components/ui/numeric";

interface WatchlistItemsTableProps {
  watchlistId: string;
  items: WatchlistItem[];
  isLoading: boolean;
}

const getSectorClass = (sector?: string) => {
  if (!sector) return "energy"; // default fallback
  const s = sector.toLowerCase();
  if (s.includes("bank") || s.includes("financial") || s.includes("nbfc")) return "fin";
  if (s.includes("it") || s.includes("software") || s.includes("tech")) return "it";
  if (s.includes("fmcg") || s.includes("consumer")) return "fmcg";
  if (s.includes("pharma") || s.includes("health")) return "pharma";
  return "energy";
};

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
    <div className="glass-card overflow-hidden">
      <div className="p-4 border-b border-rule flex items-center justify-between bg-white/40">
        <div className="flex items-center gap-2">
          <svg className="text-accent w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polygon points="12 2 15.1 8.6 22 9.6 17 14.5 18.2 21.5 12 18.1 5.8 21.5 7 14.5 2 9.6 8.9 8.6"/></svg>
          <span className="ts-h2 text-sm font-bold text-ink">{items.length > 0 ? "All tracked stocks" : "Watchlist"}</span>
          <span className="ts-eyebrow text-[10px] ml-2 tracking-widest">{items.length} items</span>
        </div>
      </div>
      <div className="overflow-x-auto">
        <Table className="w-full border-collapse">
          <TableHeader>
            <TableRow className="bg-white/30 hover:bg-white/30 border-b border-rule">
              <TableHead className="w-10 pl-4"></TableHead>
              {WATCHLIST_COLUMNS.map((col) => (
                <TableHead 
                  key={col.id} 
                  className={cn(
                    "ts-eyebrow text-[10.5px] py-4 font-bold tracking-widest",
                    col.align === "right" && "text-right",
                    col.align === "center" && "text-center",
                    col.id === "actions" && "pr-6"
                  )}
                  style={col.width ? { width: col.width } : {}}
                >
                  {col.label}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {items.map((item) => (
              <TableRow key={item.id} className="group hover:bg-white/60 border-b border-rule-2 transition-all duration-200">
                <TableCell className="text-center pl-4 cursor-grab active:cursor-grabbing">
                  <GripVertical className="w-4 h-4 text-ink-4 opacity-30 group-hover:opacity-100 group-hover:text-accent transition-all" />
                </TableCell>
                
                {WATCHLIST_COLUMNS.map((col) => {
                  switch (col.id) {
                    case "stock":
                      return (
                        <TableCell key={col.id}>
                          <div className="flex items-center gap-3 min-w-[220px]">
                            <div 
                              className="w-9 h-9 rounded-xl flex items-center justify-center font-bold text-xs text-white shadow-md shadow-ink/5"
                              style={{ background: getLogoGradient(item.symbol) }}
                            >
                              {item.symbol.slice(0, 2)}
                            </div>
                            <div>
                              <div className="ts-body font-bold text-ink leading-tight tracking-tight">{item.name || "Unknown Company"}</div>
                              <div className="ts-mono text-[10.5px] text-ink-3 font-semibold mt-0.5">{item.symbol} · NSE</div>
                            </div>
                          </div>
                        </TableCell>
                      );
                    case "price":
                      return (
                        <TableCell key={col.id} className="text-right">
                          <Numeric 
                            value={item.last_price || 0} 
                            type="currency" 
                            className="text-[13.5px] font-bold text-ink ts-mono" 
                          />
                        </TableCell>
                      );
                    case "change":
                      return (
                        <TableCell key={col.id} className="text-right">
                          <div className={cn(
                            "inline-flex items-center gap-1 px-2.5 py-1 rounded-full ts-mono text-[11px] font-bold",
                            (item.change_percent || 0) >= 0 ? "text-good bg-good-soft" : "text-danger-deep bg-danger-soft"
                          )}>
                            {(item.change_percent || 0) >= 0 ? (
                              <svg width="8" height="8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 14 12 8 18 14"/></svg>
                            ) : (
                              <svg width="8" height="8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 10 12 16 18 10"/></svg>
                            )}
                            <Numeric 
                              value={Math.abs(item.change_percent || 0)} 
                              type="number" 
                              precision={2} 
                            />%
                          </div>
                        </TableCell>
                      );
                    case "range":
                      return (
                        <TableCell key={col.id} className="text-center">
                          <PriceRangeBand 
                            current={item.last_price || 0} 
                            low={item.year_low || 0} 
                            high={item.year_high || 0} 
                          />
                        </TableCell>
                      );
                    case "sector":
                      return (
                        <TableCell key={col.id}>
                          <span className={cn("sec ts-mono text-[10px]", getSectorClass(item.sector))}>
                            {item.sector || "Other"}
                          </span>
                        </TableCell>
                      );
                    case "actions":
                      return (
                        <TableCell key={col.id} className="text-right pr-6">
                          <div className="flex justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
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
                      );
                    default:
                      return null;
                  }
                })}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}


