"use client";

import React from "react";
import { TrendingUp, TrendingDown, Eye, Activity } from "lucide-react";

interface KPIProps {
  label: string;
  value: string | number;
  subValue: string;
  trend?: "up" | "down";
  sparkline?: React.ReactNode;
}

const KPI = ({ label, value, subValue, trend, sparkline }: KPIProps) => (
  <div className="glass-card p-4 relative overflow-hidden flex flex-col gap-1">
    <div className="ts-eyebrow uppercase text-[10.5px] tracking-[0.12em] font-semibold text-ink-3">
      {label}
    </div>
    <div className="ts-mono text-2xl font-bold text-ink tracking-[-0.01em] flex items-baseline gap-1">
      {value}
    </div>
    <div className={`ts-body text-[11.5px] ${trend === "up" ? "text-good" : trend === "down" ? "text-danger" : "text-ink-2"}`}>
      {subValue}
    </div>
    <div className="absolute right-3 top-4 opacity-10">
      {sparkline || <Activity size={48} />}
    </div>
  </div>
);

import { WatchlistItem } from "../types";

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
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
      <KPI 
        label="Tracked" 
        value={trackedCount} 
        subValue={`assets in list`} 
        sparkline={<Eye size={48} className="text-accent" />}
      />
      <KPI 
        label="Day's Avg Move" 
        value={`${avgMove >= 0 ? "+" : ""}${avgMove.toFixed(2)}%`} 
        subValue={`${advancingCount} advancing`} 
        trend={avgMove >= 0 ? "up" : "down"}
        sparkline={<Activity size={48} className={avgMove >= 0 ? "text-good" : "text-danger"} />}
      />
      {bestStock ? (
        <KPI 
          label="Best Today" 
          value={bestStock.symbol} 
          subValue={`${(bestStock.change_percent || 0) >= 0 ? "+" : ""}${(bestStock.change_percent || 0).toFixed(1)}% · ₹${(bestStock.last_price || 0).toLocaleString('en-IN')}`} 
          trend={(bestStock.change_percent || 0) >= 0 ? "up" : "down"}
          sparkline={<TrendingUp size={48} className="text-good" />}
        />
      ) : (
        <KPI label="Best Today" value="-" subValue="No data" />
      )}
      {worstStock ? (
        <KPI 
          label="Worst Today" 
          value={worstStock.symbol} 
          subValue={`${(worstStock.change_percent || 0) >= 0 ? "+" : ""}${(worstStock.change_percent || 0).toFixed(1)}% · ₹${(worstStock.last_price || 0).toLocaleString('en-IN')}`} 
          trend={(worstStock.change_percent || 0) >= 0 ? "up" : "down"}
          sparkline={<TrendingDown size={48} className="text-danger" />}
        />
      ) : (
        <KPI label="Worst Today" value="-" subValue="No data" />
      )}
    </div>
  );
};

