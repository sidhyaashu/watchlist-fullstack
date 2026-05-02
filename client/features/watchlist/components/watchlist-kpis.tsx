"use client";

import { WatchlistItem } from "../types";
import { Numeric } from "@/components/ui/numeric";

interface KPIProps {
  label: string;
  value: React.ReactNode;
  subValue: React.ReactNode;
  trend?: "up" | "down";
  sparkPath?: string;
  sparkColor?: string;
}

const KPI = ({ label, value, subValue, trend, sparkPath, sparkColor }: KPIProps) => (
  <div className="kpi">
    <div className="lab">{label}</div>
    <div className="v">{value}</div>
    <div className={`d ${trend === "up" ? "up" : trend === "down" ? "dn" : ""}`}>
      {subValue}
    </div>
    
    {sparkPath && (
      <svg className="spark" viewBox="0 0 64 24" fill="none" stroke={sparkColor || "currentColor"} strokeWidth="1.5" strokeLinecap="round">
        <polyline points={sparkPath} />
      </svg>
    )}
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
    <div className="kpis">
      <KPI 
        label="Tracked" 
        value={<>{trackedCount}</>} 
        subValue={<>across <span>1 list</span></>}
        sparkPath="0,18 10,14 18,16 26,10 34,12 42,6 50,9 58,4 64,7"
        sparkColor="#2B6BFF"
      />
      <KPI 
        label="Day's avg move" 
        value={<><span style={{ color: avgMove >= 0 ? "var(--good)" : "var(--danger-deep)" }}>{avgMove >= 0 ? "+" : ""}<Numeric value={avgMove} precision={2} /></span><small>%</small></>} 
        subValue={<>{avgMove >= 0 ? "↑" : "↓"} {advancingCount} of {trackedCount} advancing</>} 
        trend={avgMove >= 0 ? "up" : "down"}
        sparkPath={avgMove >= 0 
          ? "0,16 10,15 18,12 26,13 34,9 42,11 50,8 58,6 64,4"
          : "0,4 10,5 18,8 26,7 34,11 42,9 50,12 58,14 64,16"
        }
        sparkColor={avgMove >= 0 ? "#10A37F" : "#E2557A"}
      />
      {bestStock ? (
        <KPI 
          label="Best today" 
          value={<>{bestStock.name?.split(' ')[0] || bestStock.symbol} <small style={{ fontFamily: "var(--mono)", fontSize: "11px", color: "var(--ink-3)", fontWeight: 500, marginLeft: "4px" }}>{bestStock.symbol}</small></>} 
          subValue={<>+{<Numeric value={bestStock.change_percent || 0} precision={2} />}% · ₹<Numeric value={bestStock.last_price || 0} precision={2} /></>} 
          trend="up"
        />
      ) : (
        <KPI label="Best today" value="—" subValue="No data" />
      )}
      {worstStock ? (
        <KPI 
          label="Worst today" 
          value={<>{worstStock.name?.split(' ')[0] || worstStock.symbol} <small style={{ fontFamily: "var(--mono)", fontSize: "11px", color: "var(--ink-3)", fontWeight: 500, marginLeft: "4px" }}>{worstStock.symbol}</small></>} 
          subValue={<>−{<Numeric value={Math.abs(worstStock.change_percent || 0)} precision={2} />}% · ₹<Numeric value={worstStock.last_price || 0} precision={2} /></>} 
          trend="down"
        />
      ) : (
        <KPI label="Worst today" value="—" subValue="No data" />
      )}
    </div>
  );
};
