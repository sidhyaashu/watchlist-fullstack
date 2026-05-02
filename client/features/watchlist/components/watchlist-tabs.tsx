"use client";

import { useState, useEffect, useRef } from "react";
import { X, Plus, Check } from "lucide-react";
import { WatchlistItem } from "@/features/watchlist";
import { getLogoGradient } from "@/lib/utils/logo-utils";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface WatchlistTag {
  id: string;
  name: string;
  color: string;
  symbol_ids: string[]; // watchlist item IDs belonging to this tag
}

const PRESET_TAGS: Array<{ name: string; color: string; description: string }> = [
  { name: "Core Holdings",  color: "#2B6BFF", description: "Your long-term foundation stocks" },
  { name: "IT Services",    color: "#10A37F", description: "Technology & software companies" },
  { name: "Banks & NBFC",   color: "#E29A2B", description: "Banking and financial services" },
  { name: "Speculative",    color: "#E2557A", description: "High-risk, high-reward bets" },
  { name: "Growth",         color: "#7A3EB5", description: "Mid-cap growth opportunities" },
];

function uid() {
  return Math.random().toString(36).slice(2, 9);
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function loadTags(watchlistId: string): WatchlistTag[] {
  if (typeof window === "undefined") return [];
  try {
    return JSON.parse(localStorage.getItem(`wl_tags_${watchlistId}`) || "[]");
  } catch { return []; }
}

function saveTags(watchlistId: string, tags: WatchlistTag[]) {
  localStorage.setItem(`wl_tags_${watchlistId}`, JSON.stringify(tags));
}

// ─── New List Modal ────────────────────────────────────────────────────────────

interface NewListModalProps {
  watchlistId: string;
  items: WatchlistItem[];
  onClose: () => void;
  onSave: (tag: WatchlistTag) => void;
  existingTags: WatchlistTag[];
}

function NewListModal({ watchlistId, items, onClose, onSave, existingTags }: NewListModalProps) {
  const [step, setStep] = useState<"name" | "assign">("name");
  const [selectedPreset, setSelectedPreset] = useState<typeof PRESET_TAGS[0] | null>(null);
  const [customName, setCustomName] = useState("");
  const [customColor, setCustomColor] = useState("#2B6BFF");
  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set());
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setTimeout(() => inputRef.current?.focus(), 80);
  }, []);

  const finalName = selectedPreset ? selectedPreset.name : customName.trim();
  const finalColor = selectedPreset ? selectedPreset.color : customColor;
  const alreadyExists = existingTags.some(t => t.name.toLowerCase() === finalName.toLowerCase());

  const handleNext = () => {
    if (!finalName || alreadyExists) return;
    setStep("assign");
  };

  const handleSave = () => {
    if (!finalName) return;
    const tag: WatchlistTag = {
      id: uid(),
      name: finalName,
      color: finalColor,
      symbol_ids: [...selectedItems],
    };
    onSave(tag);
    onClose();
  };

  const toggleItem = (id: string) => {
    setSelectedItems(prev => {
      const n = new Set(prev);
      n.has(id) ? n.delete(id) : n.add(id);
      return n;
    });
  };

  const selectPreset = (p: typeof PRESET_TAGS[0]) => {
    setSelectedPreset(prev => prev?.name === p.name ? null : p);
    setCustomName("");
  };

  return (
    <div
      className="fixed inset-0 z-[110] flex items-start justify-center pt-16 px-4"
      style={{ background: "rgba(11,37,69,.36)", backdropFilter: "blur(8px)" }}
      onClick={e => e.target === e.currentTarget && onClose()}
    >
      <div
        className="w-full max-w-[520px] rounded-[18px] overflow-hidden glass-card"
        style={{
          animation: "modalIn .25s cubic-bezier(.2,.7,.3,1) both",
        }}
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4" style={{ borderBottom: "1px solid var(--rule)" }}>
          <div className="flex items-center gap-2 font-semibold text-[15px] text-ink">
            {step === "name" ? (
              <>
                <Plus className="w-4 h-4 text-accent" strokeWidth={2.5} />
                Create new list
              </>
            ) : (
              <>
                <span className="inline-block w-3 h-3 rounded-[3px]" style={{ background: finalColor }} />
                Assign stocks to "{finalName}"
              </>
            )}
          </div>
          <button onClick={onClose} className="act"><X className="w-4 h-4" /></button>
        </div>

        {step === "name" ? (
          <>
            {/* Preset pills */}
            <div className="px-5 pt-5 pb-3">
              <div className="ts-eyebrow mb-3">COMMON CATEGORIES</div>
              <div className="flex flex-col gap-2">
                {PRESET_TAGS.map(p => {
                  const taken = existingTags.some(t => t.name === p.name);
                  const isSelected = selectedPreset?.name === p.name;
                  return (
                    <button
                      key={p.name}
                      disabled={taken}
                      onClick={() => selectPreset(p)}
                      className="flex items-center gap-3 rounded-xl px-4 py-3 text-left transition-all w-full"
                      style={{
                        border: isSelected ? `1.5px solid ${p.color}` : "1.5px solid var(--rule)",
                        background: isSelected ? `${p.color}14` : "rgba(255,255,255,var(--tab-bg-op, .6))",
                        opacity: taken ? 0.45 : 1,
                        cursor: taken ? "not-allowed" : "pointer",
                      }}
                    >
                      <span className="w-3 h-3 rounded-[3px] flex-shrink-0" style={{ background: p.color }} />
                      <div className="flex-1">
                        <div className="text-[13px] font-semibold text-ink">{p.name}</div>
                        <div className="text-[11px] text-ink-3 mt-0.5">{p.description}</div>
                      </div>
                      {taken && <span className="text-[10px] text-ink-4 font-mono">Already created</span>}
                      {isSelected && <Check className="w-4 h-4 flex-shrink-0" style={{ color: p.color }} />}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Divider */}
            <div className="flex items-center gap-3 px-5 py-2">
              <div className="flex-1 h-px" style={{ background: "var(--rule)" }} />
              <span className="text-[11px] text-ink-4 font-mono">or custom</span>
              <div className="flex-1 h-px" style={{ background: "var(--rule)" }} />
            </div>

            {/* Custom name input */}
            <div className="px-5 pb-5">
              <div className="flex items-center gap-2">
                {/* Color picker */}
                <div className="relative flex-shrink-0">
                  <input
                    type="color"
                    value={customColor}
                    onChange={e => { setCustomColor(e.target.value); setSelectedPreset(null); }}
                    className="w-10 h-10 rounded-lg cursor-pointer border"
                    style={{ border: "1px solid var(--rule)", padding: 2 }}
                    title="Pick colour"
                  />
                </div>
                <input
                  ref={inputRef}
                  value={customName}
                  onChange={e => { setCustomName(e.target.value); setSelectedPreset(null); }}
                  onKeyDown={e => e.key === "Enter" && handleNext()}
                  placeholder="e.g. Dividend picks, Smallcaps…"
                  className="flex-1 rounded-xl px-4 py-3 text-[14px] text-ink outline-none transition-all"
                  style={{
                    border: "1px solid var(--rule)",
                    background: "var(--rule-2)",
                  }}
                  onFocus={e => { e.currentTarget.style.borderColor = "var(--accent-2)"; e.currentTarget.style.background = "var(--bg-1)"; e.currentTarget.style.boxShadow = "0 0 0 3px var(--accent-soft)"; }}
                  onBlur={e => { e.currentTarget.style.borderColor = "var(--rule)"; e.currentTarget.style.background = "var(--rule-2)"; e.currentTarget.style.boxShadow = "none"; }}
                />
              </div>
              {alreadyExists && (
                <div className="text-[11.5px] mt-2 px-1" style={{ color: "var(--danger-deep)" }}>
                  A list named "{finalName}" already exists.
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="flex justify-end gap-2 px-5 py-4" style={{ borderTop: "1px solid var(--rule-2)" }}>
              <button onClick={onClose} className="tool">Cancel</button>
              <button
                onClick={handleNext}
                disabled={!finalName || alreadyExists}
                className="tool primary"
                style={{ opacity: (!finalName || alreadyExists) ? 0.5 : 1 }}
              >
                Next — assign stocks
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round">
                  <path d="M5 12h14M13 5l7 7-7 7"/>
                </svg>
              </button>
            </div>
          </>
        ) : (
          <>
            {/* Assign step */}
            <div className="px-5 pt-4 pb-2">
              <div className="ts-eyebrow mb-2">SELECT STOCKS TO ADD TO THIS LIST</div>
              <div className="text-[12px] text-ink-3 mb-3">
                You can always reassign stocks later from the Actions menu.
              </div>
            </div>

            <div style={{ maxHeight: 320, overflowY: "auto" }} className="px-5 pb-2">
              {items.length === 0 ? (
                <div className="text-center py-8 text-ink-3 text-[13px]">No stocks in this watchlist yet.</div>
              ) : (
                <div className="flex flex-col gap-1.5">
                  {items.map(item => {
                    const isSelected = selectedItems.has(item.id);
                    return (
                      <button
                        key={item.id}
                        onClick={() => toggleItem(item.id)}
                        className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-left transition-all w-full"
                        style={{
                          border: isSelected ? `1.5px solid ${finalColor}` : "1.5px solid var(--rule)",
                          background: isSelected ? `${finalColor}0f` : "rgba(255,255,255,.5)",
                        }}
                      >
                        <div
                          className="logo flex-shrink-0"
                          style={{ width: 30, height: 30, fontSize: 10, borderRadius: 8, background: getLogoGradient(item.symbol) }}
                        >
                          {item.symbol.slice(0, 2)}
                        </div>
                        <div className="flex-1">
                          <div className="text-[13px] font-semibold text-ink leading-tight">{item.name || item.symbol}</div>
                          <div className="text-[10.5px] text-ink-3 font-mono mt-0.5">{item.symbol} · {item.sector || "—"}</div>
                        </div>
                        <div
                          className="w-5 h-5 rounded-md flex items-center justify-center flex-shrink-0 transition-all"
                          style={{
                            background: isSelected ? finalColor : "var(--rule-2)",
                            border: isSelected ? `1px solid ${finalColor}` : "1px solid var(--rule)",
                          }}
                        >
                          {isSelected && <Check className="w-3 h-3 text-white" strokeWidth={3} />}
                        </div>
                      </button>
                    );
                  })}
                </div>
              )}
            </div>

            <div className="flex items-center justify-between px-5 py-4" style={{ borderTop: "1px solid var(--rule-2)" }}>
              <button onClick={() => setStep("name")} className="tool">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round">
                  <path d="M19 12H5M12 19l-7-7 7-7"/>
                </svg>
                Back
              </button>
              <button onClick={handleSave} className="tool primary">
                <Check className="w-3.5 h-3.5" />
                Create list
                {selectedItems.size > 0 && ` (${selectedItems.size} stock${selectedItems.size !== 1 ? "s" : ""})`}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

// ─── Main WatchlistTabs Component ─────────────────────────────────────────────

interface WatchlistTabsProps {
  watchlistId: string;
  items: WatchlistItem[];
  activeTagId: string | null;
  onTagChange: (id: string | null) => void;
}

export function WatchlistTabs({ watchlistId, items, activeTagId, onTagChange }: WatchlistTabsProps) {
  const [tags, setTags] = useState<WatchlistTag[]>([]);
  const [showNewList, setShowNewList] = useState(false);

  useEffect(() => {
    setTags(loadTags(watchlistId));
  }, [watchlistId]);

  const handleSave = (tag: WatchlistTag) => {
    const updated = [...tags, tag];
    setTags(updated);
    saveTags(watchlistId, updated);
    onTagChange(tag.id); // auto-select the newly created tag
  };

  const activeTag = tags.find(t => t.id === activeTagId) ?? null;

  return (
    <>
      <div className="wl-tabs-row">
        <div className="wl-tabs">
          {/* All tab */}
          <div
            className={`wl-tab bg-white/40 dark:bg-white/5 ${activeTagId === null ? "active" : ""}`}
            onClick={() => onTagChange(null)}
          >
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polygon points="12 2 15.1 8.6 22 9.6 17 14.5 18.2 21.5 12 18.1 5.8 21.5 7 14.5 2 9.6 8.9 8.6"/>
            </svg>
            All <span className="ct bg-white/60 dark:bg-white/10">{items.length}</span>
          </div>

          {/* User-created tag tabs */}
          {tags.map(tag => {
            const count = tag.symbol_ids.filter(sid => items.some(i => i.id === sid)).length;
            return (
              <div
                key={tag.id}
                className={`wl-tab bg-white/40 dark:bg-white/5 ${activeTagId === tag.id ? "active" : ""}`}
                onClick={() => onTagChange(tag.id)}
              >
                <span style={{ width: 8, height: 8, borderRadius: 2, background: tag.color, display: "inline-block", flexShrink: 0 }} />
                {tag.name}
                <span className="ct bg-white/60 dark:bg-white/10">{count}</span>
              </div>
            );
          })}
        </div>

        <div className="wl-tab add bg-white/40 dark:bg-white/5 hover:bg-white/70 dark:hover:bg-white/10" onClick={() => setShowNewList(true)} style={{ cursor: "pointer" }}>
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round">
            <path d="M12 5v14M5 12h14"/>
          </svg>
          New list
        </div>
      </div>

      {showNewList && (
        <NewListModal
          watchlistId={watchlistId}
          items={items}
          onClose={() => setShowNewList(false)}
          onSave={handleSave}
          existingTags={tags}
        />
      )}
    </>
  );
}
