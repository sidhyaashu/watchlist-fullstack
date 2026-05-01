import { cn } from "@/lib/utils";

interface NumericProps extends React.HTMLAttributes<HTMLSpanElement> {
  value: number | string;
  type?: "currency" | "percent" | "number";
  precision?: number;
  showPlus?: boolean;
}

/**
 * Numeric component for InvestKaro Design System.
 * Ensures all financial figures use JetBrains Mono (ts-mono) for consistent alignment.
 */
export function Numeric({ 
  value, 
  type = "number", 
  precision = 2, 
  showPlus = false, 
  className, 
  ...props 
}: NumericProps) {
  const num = typeof value === "string" ? parseFloat(value) : value;
  
  if (isNaN(num)) return <span className={cn("ts-mono", className)} {...props}>—</span>;

  let formatted = "";
  if (type === "currency") {
    formatted = num.toLocaleString("en-IN", {
      minimumFractionDigits: precision,
      maximumFractionDigits: precision,
    });
    formatted = `₹${formatted}`;
  } else if (type === "percent") {
    formatted = num.toFixed(precision);
    if (showPlus && num > 0) formatted = `+${formatted}`;
    formatted = `${formatted}%`;
  } else {
    formatted = num.toLocaleString("en-IN", {
      minimumFractionDigits: precision,
      maximumFractionDigits: precision,
    });
  }

  return (
    <span className={cn("ts-mono font-medium", className)} {...props}>
      {formatted}
    </span>
  );
}
