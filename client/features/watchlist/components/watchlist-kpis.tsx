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

export const WatchlistKPIs = () => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
      <KPI 
        label="Tracked" 
        value="12" 
        subValue="across 4 lists" 
        sparkline={<Eye size={48} className="text-accent" />}
      />
      <KPI 
        label="Day's Avg Move" 
        value="+0.78%" 
        subValue="↑ 8 of 12 advancing" 
        trend="up"
        sparkline={<TrendingUp size={48} className="text-good" />}
      />
      <KPI 
        label="Best Today" 
        value="BAJFINANCE" 
        subValue="+3.1% · ₹7,420" 
        trend="up"
      />
      <KPI 
        label="Worst Today" 
        value="WIPRO" 
        subValue="−1.8% · ₹284" 
        trend="down"
      />
    </div>
  );
};
