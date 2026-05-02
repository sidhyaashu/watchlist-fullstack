"use client";

import React from "react";
import { Numeric } from "@/components/ui/numeric";

interface PriceRangeBandProps {
  current: number;
  low: number;
  high: number;
}

export const PriceRangeBand = ({ current, low, high }: PriceRangeBandProps) => {
  const percentage = Math.min(Math.max(((current - low) / (high - low)) * 100, 0), 100);

  return (
    <div className="band">
      <div className="track">
        <div 
          className="mark"
          style={{ left: `${percentage}%` }}
        />
      </div>
      <div className="scale">
        <span>₹<Numeric value={low} precision={0} /></span>
        <span className="pct">{percentage.toFixed(0)}%</span>
        <span>₹<Numeric value={high} precision={0} /></span>
      </div>
    </div>
  );
};
