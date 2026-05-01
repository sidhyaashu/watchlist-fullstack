"use client";

import React from "react";

interface PriceRangeBandProps {
  current: number;
  low: number;
  high: number;
}

export const PriceRangeBand = ({ current, low, high }: PriceRangeBandProps) => {
  const percentage = Math.min(Math.max(((current - low) / (high - low)) * 100, 0), 100);

  return (
    <div className="w-[120px] inline-flex flex-col gap-1">
      <div className="h-[6px] w-full rounded-full bg-gradient-to-r from-danger/20 via-warn/20 to-good/20 relative border border-ink-4/10">
        <div 
          className="absolute top-[-3px] w-[3px] h-[12px] bg-ink rounded-[2px] shadow-[0_0_0_2px_rgba(255,255,255,0.9),0_0_0_3px_rgba(11,37,69,0.15)] transition-all duration-300"
          style={{ left: `${percentage}%`, transform: 'translateX(-50%)' }}
        />
      </div>
      <div className="flex justify-between ts-mono text-[9.5px] text-ink-3 tracking-[-0.005em]">
        <span>₹{low.toLocaleString('en-IN')}</span>
        <span className="text-accent-deep font-semibold">{percentage.toFixed(0)}%</span>
        <span>₹{high.toLocaleString('en-IN')}</span>
      </div>
    </div>
  );
};
