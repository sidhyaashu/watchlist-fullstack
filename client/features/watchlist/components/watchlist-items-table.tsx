"use client";

import { useState, useRef, useEffect } from "react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { WatchlistItem, useRemoveWatchlistItem, useReorderWatchlistItems } from "@/features/watchlist";
import { PriceRangeBand } from "./price-range-band";
import { getLogoGradient } from "@/lib/utils/logo-utils";
import { Numeric } from "@/components/ui/numeric";

interface WatchlistItemsTableProps {
  watchlistId: string;
  items: WatchlistItem[];        // filtered / visible items
  allItems?: WatchlistItem[];   // all items (unfiltered) — for display counts
  isLoading: boolean;
  activeTagId?: string | null;  // currently selected tag
  page?: number;
  onPageChange?: (page: number) => void;
  totalItems?: number;
}

const getSectorClass = (sector?: string) => {
  if (!sector) return "energy";
  const s = sector.toLowerCase();
  if (s.includes("bank") || s.includes("financial") || s.includes("nbfc")) return "fin";
  if (s.includes("it") || s.includes("software") || s.includes("tech")) return "it";
  if (s.includes("fmcg") || s.includes("consumer")) return "fmcg";
  if (s.includes("pharma") || s.includes("health")) return "pharma";
  if (s.includes("auto")) return "auto";
  if (s.includes("eng")) return "eng";
  return "energy";
};

export function WatchlistItemsTable(props: WatchlistItemsTableProps) {
  const {
    watchlistId, items, allItems, isLoading, activeTagId,
    page = 1, onPageChange, totalItems = items.length
  } = props;

  // Resolve tag name from localStorage for header display
  const tagName = (() => {
    if (!activeTagId) return null;
    try {
      const stored = JSON.parse(localStorage.getItem(`wl_tags_${watchlistId}`) || "[]") as Array<{ id: string; name: string }>;
      return stored.find(t => t.id === activeTagId)?.name ?? null;
    } catch { return null; }
  })();
  const removeItem = useRemoveWatchlistItem();
  const reorderMutation = useReorderWatchlistItems();
  const [sortConfig, setSortConfig] = useState<{ key: string; dir: 'asc' | 'desc' } | null>(null);
  const [openMenuId, setOpenMenuId] = useState<string | null>(null);
  const menuRef = useRef<HTMLDivElement>(null);

  // Drag state
  const [localItems, setLocalItems] = useState<WatchlistItem[]>(items);
  const [draggedId, setDraggedId] = useState<string | null>(null);
  const [dragOverId, setDragOverId] = useState<string | null>(null);
  const [dragOverPosition, setDragOverPosition] = useState<'top' | 'bottom' | null>(null);

  useEffect(() => {
    if (!draggedId) {
      setLocalItems(items);
    }
  }, [items, draggedId]);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setOpenMenuId(null);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const handleRemove = (instrumentId: number, e?: React.MouseEvent) => {
    if (e) {
      e.stopPropagation();
      e.preventDefault();
    }
    removeItem.mutate(
      { watchlistId, instrumentId: instrumentId.toString() },
      {
        onSuccess: () => {
          toast.success("Removed stock from watchlist");
          setOpenMenuId(null);
        },
        onError: () => toast.error("Failed to remove item"),
      }
    );
  };

  const handleSort = (key: string) => {
    setSortConfig((prev) => {
      if (prev?.key === key) {
        return { key, dir: prev.dir === 'asc' ? 'desc' : 'asc' };
      }
      return { key, dir: 'asc' };
    });
  };

  const isReorderable = !activeTagId && !sortConfig && totalItems <= 10;

  // Drag Handlers
  const handleDragStart = (e: React.DragEvent, id: string) => {
    if (!isReorderable) return;
    setDraggedId(id);
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', id);
  };

  const handleDragOver = (e: React.DragEvent, id: string) => {
    if (!isReorderable) return;
    e.preventDefault();
    if (id === draggedId) return;

    const row = e.currentTarget as HTMLTableRowElement;
    const rect = row.getBoundingClientRect();
    const after = (e.clientY - rect.top) > rect.height / 2;
    
    setDragOverId(id);
    setDragOverPosition(after ? 'bottom' : 'top');
  };

  const handleDragLeave = () => {
    setDragOverId(null);
    setDragOverPosition(null);
  };

  const handleDrop = (e: React.DragEvent, targetId: string) => {
    e.preventDefault();
    if (!draggedId || draggedId === targetId) {
      setDraggedId(null);
      setDragOverId(null);
      return;
    }

    const fromIndex = localItems.findIndex(item => item.id === draggedId);
    if (fromIndex < 0) return;

    const newItems = [...localItems];
    const [moved] = newItems.splice(fromIndex, 1);
    
    const currentTargetIndex = newItems.findIndex(item => item.id === targetId);
    if (currentTargetIndex < 0) return;
    
    newItems.splice(dragOverPosition === 'bottom' ? currentTargetIndex + 1 : currentTargetIndex, 0, moved);
    
    setLocalItems(newItems);
    setDraggedId(null);
    setDragOverId(null);
    setSortConfig(null);
    
    const updates = newItems.map((item, index) => ({
      instrument_id: item.instrument_id.toString(),
      position: index
    }));
    
    reorderMutation.mutate({ watchlistId, updates }, {
      onError: () => {
        toast.error("Failed to reorder items");
        setLocalItems(items);
      }
    });
  };

  const handleDragEnd = () => {
    setDraggedId(null);
    setDragOverId(null);
  };

  const sortedItems = [...localItems].sort((a, b) => {
    if (!sortConfig) return 0;
    const { key, dir } = sortConfig;
    
    let valA: any = a[key as keyof WatchlistItem];
    let valB: any = b[key as keyof WatchlistItem];

    // Handle nested fields or specific columns
    if (key === 'stock') { valA = a.name; valB = b.name; }
    if (key === 'change') { valA = a.change_percent; valB = b.change_percent; }
    if (key === 'band') { valA = a.last_price; valB = b.last_price; } // Rough approximation
    
    if (valA < valB) return dir === 'asc' ? -1 : 1;
    if (valA > valB) return dir === 'asc' ? 1 : -1;
    return 0;
  });

  if (isLoading) {
    return <div className="p-8 text-center text-ink-3 ts-body">Loading items...</div>;
  }

  if (items.length === 0) {
    return (
      <div className="glass-card p-12 text-center mt-6">
        <svg className="w-12 h-12 text-ink-4 mx-auto mb-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><polygon points="12 2 15.1 8.6 22 9.6 17 14.5 18.2 21.5 12 18.1 5.8 21.5 7 14.5 2 9.6 8.9 8.6"/></svg>
        <h3 className="ts-h2 text-ink">This list is empty</h3>
        <p className="ts-body text-ink-3 mt-1">Add stocks to your watchlist from the search above.</p>
      </div>
    );
  }

  return (
    <div className="tbl-card">
      <div className="tbl-head">
        <div className="ttl">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="12 2 15.1 8.6 22 9.6 17 14.5 18.2 21.5 12 18.1 5.8 21.5 7 14.5 2 9.6 8.9 8.6"/></svg>
          <span>{tagName ?? "All stocks"}</span>
          <span className="meta">{totalItems} item{totalItems !== 1 ? "s" : ""}</span>
        </div>
        <div className="tbl-tools">
          {!isReorderable && (
            <span className="text-[11.5px] text-ink-4 mr-2" title="Drag to reorder is only available on 'All stocks' without active sorting or pagination.">
              Ordering disabled
            </span>
          )}
          <button className="tool" onClick={() => setSortConfig(null)}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 12a9 9 0 1 0 3-6.7"/><path d="M3 4v5h5"/></svg>
            Reset
          </button>
          <button className="tool">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            Export
          </button>
          <button className="tool primary" onClick={() => document.dispatchEvent(new CustomEvent('open-add-stock-modal'))}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round"><path d="M12 5v14M5 12h14"/></svg>
            Add stock
          </button>
        </div>
      </div>
      
      <div className="max-h-[560px] overflow-auto">
        <table className="wl">
          <thead>
            <tr>
              <th className="handle"></th>
              <th onClick={() => handleSort('stock')} className={cn(sortConfig?.key === 'stock' && "sorted")}>
                Stock <span className="sortix">{sortConfig?.key === 'stock' ? (sortConfig.dir === 'asc' ? '↑' : '↓') : '↕'}</span>
              </th>
              <th className="r" onClick={() => handleSort('last_price')} className={cn(sortConfig?.key === 'last_price' && "sorted")}>
                Price <span className="sortix">{sortConfig?.key === 'last_price' ? (sortConfig.dir === 'asc' ? '↑' : '↓') : '↕'}</span>
              </th>
              <th className="r" onClick={() => handleSort('change')} className={cn(sortConfig?.key === 'change' && "sorted")}>
                Day <span className="sortix">{sortConfig?.key === 'change' ? (sortConfig.dir === 'asc' ? '↑' : '↓') : '↕'}</span>
              </th>
              <th className="c" onClick={() => handleSort('band')} className={cn(sortConfig?.key === 'band' && "sorted")}>
                52W range <span className="sortix">{sortConfig?.key === 'band' ? (sortConfig.dir === 'asc' ? '↑' : '↓') : '↕'}</span>
              </th>
              <th className="r col-mc" onClick={() => handleSort('mcap')} className={cn(sortConfig?.key === 'mcap' && "sorted")}>
                Mkt cap <span className="sortix">{sortConfig?.key === 'mcap' ? (sortConfig.dir === 'asc' ? '↑' : '↓') : '↕'}</span>
              </th>
              <th className="r col-pe" onClick={() => handleSort('pe')} className={cn(sortConfig?.key === 'pe' && "sorted")}>
                P / E <span className="sortix">{sortConfig?.key === 'pe' ? (sortConfig.dir === 'asc' ? '↑' : '↓') : '↕'}</span>
              </th>
              <th onClick={() => handleSort('sector')} className={cn(sortConfig?.key === 'sector' && "sorted")}>
                Sector <span className="sortix">{sortConfig?.key === 'sector' ? (sortConfig.dir === 'asc' ? '↑' : '↓') : '↕'}</span>
              </th>
              <th className="actions" style={{ textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {sortedItems.map((item) => (
              <tr 
                key={item.id} 
                data-id={item.id} 
                draggable="true"
                onDragStart={(e) => handleDragStart(e, item.id)}
                onDragOver={(e) => handleDragOver(e, item.id)}
                onDragLeave={handleDragLeave}
                onDrop={(e) => handleDrop(e, item.id)}
                onDragEnd={handleDragEnd}
                className={cn(
                  draggedId === item.id && "opacity-40 bg-accent-soft",
                  dragOverId === item.id && dragOverPosition === 'top' && "shadow-[inset_0_2px_0_var(--accent)]",
                  dragOverId === item.id && dragOverPosition === 'bottom' && "shadow-[inset_0_-2px_0_var(--accent)]"
                )}
              >
                <td className="handle" title="Drag to reorder">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><circle cx="9" cy="6" r="1"/><circle cx="9" cy="12" r="1"/><circle cx="9" cy="18" r="1"/><circle cx="15" cy="6" r="1"/><circle cx="15" cy="12" r="1"/><circle cx="15" cy="18" r="1"/></svg>
                </td>
                <td>
                  <a href="#" className="sym-cell" style={{ textDecoration: 'none', color: 'inherit' }}>
                    <div 
                      className="logo"
                      style={{ background: getLogoGradient(item.symbol) }}
                    >
                      {item.symbol.slice(0, 2)}
                    </div>
                    <div>
                      <div className="nm">{item.name || "Unknown Company"}</div>
                      <div className="tk">{item.symbol} · NSE</div>
                    </div>
                  </a>
                </td>
                <td className="r">
                  <span className="px">₹<Numeric value={item.last_price || 0} precision={2} /></span>
                </td>
                <td className="r">
                  <div className={cn("ch", (item.change_percent || 0) >= 0 ? "up" : "dn")}>
                    {(item.change_percent || 0) >= 0 ? (
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 14 12 8 18 14"/></svg>
                    ) : (
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 10 12 16 18 10"/></svg>
                    )}
                    {(item.change_percent || 0) > 0 ? "+" : ""}<Numeric value={item.change_percent || 0} precision={2} />%
                  </div>
                </td>
                <td className="c">
                  <PriceRangeBand 
                    current={item.last_price || 0} 
                    low={item.year_low || 0} 
                    high={item.year_high || 0} 
                  />
                </td>
                <td className="r col-mc">
                  <span className="px" style={{ fontSize: '12.5px' }}>
                    {item.mcap ? `₹${(item.mcap / 10).toFixed(1)} Cr` : "—"}
                  </span>
                </td>
                <td className="r col-pe">
                  <span className="px" style={{ fontSize: '12.5px' }}>
                    {item.pe ? item.pe.toFixed(1) : "—"}
                  </span>
                </td>
                <td>
                  <span className={cn("sec", getSectorClass(item.sector))}>
                    {item.sector || "Other"}
                  </span>
                </td>
                <td className="actions">
                  <div className="act-cell" ref={menuRef}>
                    <a className="act" href="#" title="Open detail">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
                    </a>
                    <div className="menu-anchor">
                      <button 
                        className="act js-menu" 
                        title="Move to list"
                        onClick={(e) => {
                          e.stopPropagation();
                          setOpenMenuId(openMenuId === item.id ? null : item.id);
                        }}
                      >
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="5" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="12" cy="19" r="1"/></svg>
                      </button>
                      
                      <div className={cn("menu", openMenuId === item.id && "open")}>
                        <div className="lbl">Move to list</div>
                        <div className="item js-move curr" onClick={(e) => e.stopPropagation()}>
                          <span className="dot-list" style={{ background: '#2B6BFF' }}></span>
                          All stocks
                          <svg className="check" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                        </div>
                        <div className="item js-move" onClick={(e) => e.stopPropagation()}>
                          <span className="dot-list" style={{ background: '#10A37F' }}></span>
                          IT services
                          <svg className="check" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                        </div>
                        <hr />
                        <a className="item" href="#">
                          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
                          Open detail
                        </a>
                        <div 
                          className="item danger js-remove" 
                          onClick={(e) => handleRemove(item.instrument_id, e)}
                        >
                          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/><path d="M10 11v6M14 11v6"/></svg>
                          Remove from watchlist
                        </div>
                      </div>
                    </div>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {totalItems > 10 && (
        <div className="flex items-center justify-between px-5 py-3 border-t" style={{ borderColor: 'var(--rule)' }}>
          <div className="text-[12px] text-ink-3">
            Showing {(page - 1) * 10 + 1} to {Math.min(page * 10, totalItems)} of {totalItems} entries
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => onPageChange?.(page - 1)}
              disabled={page === 1}
              className="px-3 py-1.5 rounded-lg text-[13px] font-medium transition-all"
              style={{
                background: page === 1 ? 'rgba(0,0,0,0.02)' : 'rgba(255,255,255,0.6)',
                color: page === 1 ? 'var(--ink-4)' : 'var(--ink-2)',
                border: '1px solid var(--rule-2)',
                cursor: page === 1 ? 'not-allowed' : 'pointer'
              }}
            >
              Previous
            </button>
            <div className="px-3 py-1.5 rounded-lg text-[13px] font-medium bg-white text-ink shadow-sm border" style={{ borderColor: 'var(--rule)' }}>
              Page {page} of {Math.ceil(totalItems / 10)}
            </div>
            <button
              onClick={() => onPageChange?.(page + 1)}
              disabled={page >= Math.ceil(totalItems / 10)}
              className="px-3 py-1.5 rounded-lg text-[13px] font-medium transition-all"
              style={{
                background: page >= Math.ceil(totalItems / 10) ? 'rgba(0,0,0,0.02)' : 'rgba(255,255,255,0.6)',
                color: page >= Math.ceil(totalItems / 10) ? 'var(--ink-4)' : 'var(--ink-2)',
                border: '1px solid var(--rule-2)',
                cursor: page >= Math.ceil(totalItems / 10) ? 'not-allowed' : 'pointer'
              }}
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
