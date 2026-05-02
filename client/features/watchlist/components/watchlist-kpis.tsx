"use client";

import { TrendingUp, TrendingDown, Eye, Activity } from "lucide-react";
import { WatchlistItem } from "../types";
import { Numeric } from "@/components/ui/numeric";

interface KPIProps {
  label: string;
  value: string | number;
  subValue: React.ReactNode;
  trend?: "up" | "down";
  sparkline?: React.ReactNode;
}

const KPI = ({ label, value, subValue, trend }: KPIProps) => (
  <div className="glass-card p-5 relative overflow-hidden flex flex-col gap-1.5 transition-all hover:translate-y-[-2px] hover:shadow-xl group">
    <div className="ts-eyebrow text-ink-3">
      {label}
    </div>
    <div className="ts-mono text-2xl font-bold text-ink tracking-tight flex items-baseline gap-1">
      {typeof value === 'number' ? <Numeric value={value} precision={0} /> : value}
    </div>
    <div className={`ts-body text-[11.5px] font-medium ${trend === "up" ? "text-good" : trend === "down" ? "text-danger" : "text-ink-2"}`}>
      {subValue}
    </div>
    
    {/* ── SPARKLINE OVERLAY ── */}
    <div className="absolute right-[-10px] bottom-[-5px] w-32 h-16 pointer-events-none opacity-[0.12] group-hover:opacity-20 transition-opacity">
      <svg width="100%" height="100%" viewBox="0 0 100 40" preserveAspectRatio="none" className={trend === "up" ? "text-good" : trend === "down" ? "text-danger" : "text-accent"}>
        <path 
          d={trend === "up" ? "M0 35 L20 28 L40 32 L60 15 L80 18 L100 5" : trend === "down" ? "M0 5 L20 15 L40 12 L60 28 L80 25 L100 35" : "M0 20 L20 22 L40 18 L60 21 L80 19 L100 20"} 
          fill="none" 
          stroke="currentColor" 
          strokeWidth="3.5" 
          strokeLinecap="round" 
          strokeLinejoin="round"
        />
      </svg>
    </div>
  </div>
);

export const WatchlistKPIs = ({ items }: { items: WatchlistItem[] }) => {
  const trackedCount = items.length;
  
  const bestStock = items.length > 0 
    ? [...items].sort((a, b) => (b.change_percent || 0) - (a.change_percent || 0))[0]
    : null;
    
  const worstStock = items.length > 0 
    ? [...items].sort((a, b) => (a.change_percent || 0) - (b.change_percent || 0))[0]
    : null;
 
  const avgMove = items.length > 0
    ? items.reduce((acc, curr) => acc + (curr.change_percent || 0), 0) / items.length
    : 0;
 
  const advancingCount = items.filter(i => (i.change_percent || 0) > 0).length;
 
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <KPI 
        label="Tracked Assets" 
        value={trackedCount} 
        subValue={<span>instruments in list</span>} 
      />
      <KPI 
        label="Day's Avg Move" 
        value={<Numeric value={avgMove} type="percent" showPlus />} 
        subValue={<span className="ts-mono">{advancingCount} advancing today</span>} 
        trend={avgMove >= 0 ? "up" : "down"}
      />
      {bestStock ? (
        <KPI 
          label="Top Performer" 
          value={bestStock.symbol} 
          subValue={
            <div className="flex items-center gap-1.5">
              <span className="text-good font-bold">
                <Numeric value={bestStock.change_percent || 0} type="percent" showPlus />
              </span>
              <span className="opacity-40">·</span>
              <Numeric value={bestStock.last_price || 0} type="currency" />
            </div>
          } 
          trend={(bestStock.change_percent || 0) >= 0 ? "up" : "down"}
        />
      ) : (
        <KPI label="Top Performer" value="—" subValue="No assets found" />
      )}
      {worstStock ? (
        <KPI 
          label="Bottom Performer" 
          value={worstStock.symbol} 
          subValue={
            <div className="flex items-center gap-1.5">
              <span className="text-danger font-bold">
                <Numeric value={worstStock.change_percent || 0} type="percent" showPlus />
              </span>
              <span className="opacity-40">·</span>
              <Numeric value={worstStock.last_price || 0} type="currency" />
            </div>
          } 
          trend={(worstStock.change_percent || 0) >= 0 ? "up" : "down"}
        />
      ) : (
        <KPI label="Bottom Performer" value="—" subValue="No assets found" />
      )}
    </div>
  );
};


