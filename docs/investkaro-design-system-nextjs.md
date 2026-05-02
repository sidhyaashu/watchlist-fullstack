# InvestKaro Design System — Next.js Handoff

Source extracted from `Design-System.html`.

## 1) Theme model

Use `data-theme="light"` or `data-theme="dark"` on `<html>`.

```html
<html lang="en" data-theme="light">
```

## 2) CSS tokens

### Light theme
```css
:root{
  --bg-1:#EAF2FF;
  --bg-2:#DCE9FF;

  --ink:#0B2545;
  --ink-2:#2B4570;
  --ink-3:#5B72A0;
  --ink-4:#9AAACB;

  --rule:rgba(91,114,160,0.18);
  --rule-2:rgba(91,114,160,0.10);

  --accent:#2B6BFF;
  --accent-2:#5C8DFF;
  --accent-deep:#1A4ED1;
  --accent-soft:rgba(43,107,255,0.10);
  --accent-soft-2:rgba(43,107,255,0.18);

  --good:#10A37F;
  --good-soft:rgba(16,163,127,0.12);

  --danger:#E2557A;
  --danger-deep:#C0365B;
  --danger-soft:rgba(226,85,122,0.12);

  --warn:#E29A2B;
  --warn-soft:rgba(226,154,43,0.14);

  --live:#E2557A;

  --glass-border:rgba(255,255,255,0.85);
  --glass-shadow:0 1px 0 rgba(255,255,255,0.7) inset, 0 8px 32px -10px rgba(43,69,112,0.18), 0 1px 2px rgba(43,69,112,0.06);

  --mono:'JetBrains Mono', ui-monospace, monospace;
  --sans:'Inter', system-ui, sans-serif;

  --r-sm:8px;
  --r-md:12px;
  --r-lg:16px;
  --r-xl:20px;
}
```

### Dark theme
```css
[data-theme="dark"]{
  --bg-1:#0A0A0B;
  --bg-2:#111114;

  --ink:#F2F2F3;
  --ink-2:#C8C8CC;
  --ink-3:#8A8A90;
  --ink-4:#5A5A60;

  --rule:rgba(255,255,255,0.10);
  --rule-2:rgba(255,255,255,0.06);

  --accent:#E5E5E7;
  --accent-2:#FFFFFF;
  --accent-deep:#FFFFFF;
  --accent-soft:rgba(255,255,255,0.08);
  --accent-soft-2:rgba(255,255,255,0.14);

  --good:#4ADE80;
  --good-soft:rgba(74,222,128,0.12);

  --danger:#F87171;
  --danger-deep:#FCA5A5;
  --danger-soft:rgba(248,113,113,0.14);

  --warn:#FBBF24;
  --warn-soft:rgba(251,191,36,0.14);

  --live:#F87171;

  --glass-border:rgba(255,255,255,0.08);
  --glass-shadow:0 1px 0 rgba(255,255,255,0.03) inset, 0 12px 36px -12px rgba(0,0,0,0.7), 0 1px 2px rgba(0,0,0,0.4);
}
```

## 3) Typography

- Font family: `Inter`
- Mono: `JetBrains Mono`
- Weight range: `400 / 500 / 600 / 700`

Scale:
```css
.ts-display{font-size:32px;font-weight:700;letter-spacing:-0.025em;line-height:1.1}
.ts-h1{font-size:24px;font-weight:700;letter-spacing:-0.02em;line-height:1.2}
.ts-h2{font-size:18px;font-weight:600;letter-spacing:-0.015em;line-height:1.3}
.ts-body{font-size:14px;font-weight:400;line-height:1.55}
.ts-small{font-size:12px;font-weight:500;line-height:1.4}
.ts-eyebrow{font-size:11px;text-transform:uppercase;letter-spacing:0.18em;font-weight:600;color:var(--ink-3)}
.ts-mono{font-family:var(--mono);font-size:13px;font-weight:500}
```

## 4) Radius, spacing, elevation

```css
/* Radius */
--r-sm:8px;
--r-md:12px;
--r-lg:16px;
--r-xl:20px;

/* Common usage */
Pills/chips: 999px
Buttons/inputs: 10px
Cards: 16px
App shell: 20px

/* Spacing scale */
4, 8, 12, 16, 24, 32, 48 px

/* Elevation */
.sh-sm{box-shadow:0 1px 2px rgba(43,69,112,.06), 0 0 0 1px rgba(255,255,255,.6) inset}
.sh-md{box-shadow:0 4px 12px -2px rgba(43,69,112,.12), 0 1px 0 rgba(255,255,255,.7) inset}
.sh-lg{box-shadow:0 8px 32px -10px rgba(43,69,112,.18), 0 1px 0 rgba(255,255,255,.7) inset}
.sh-xl{box-shadow:0 24px 60px -10px rgba(43,69,112,.25), 0 1px 0 rgba(255,255,255,.7) inset}
```

## 5) Component primitives

### Button
```css
.btn{
  display:inline-flex;
  align-items:center;
  gap:7px;
  height:34px;
  padding:0 14px;
  border-radius:10px;
  font-size:13px;
  font-weight:600;
  cursor:pointer;
  border:1px solid var(--rule);
  background:rgba(255,255,255,0.6);
  color:var(--ink-2);
  transition:.18s;
  font-family:inherit;
}
.btn.primary{
  background:linear-gradient(135deg, var(--accent) 0%, var(--accent-2) 100%);
  color:#fff;
  border-color:transparent;
}
.btn.ghost{background:transparent}
.btn.danger{color:var(--danger-deep);border-color:rgba(226,85,122,.3);background:var(--danger-soft)}
```

### Input
```css
.input{
  height:36px;
  padding:0 12px;
  border-radius:10px;
  border:1px solid var(--rule);
  background:rgba(255,255,255,0.6);
  color:var(--ink);
  font:inherit;
  font-size:13px;
  width:100%;
}
```

### Pill / chip
```css
.pill{
  font-size:11px;
  padding:5px 10px;
  border:1px solid var(--rule);
  border-radius:999px;
  color:var(--ink-2);
  background:rgba(255,255,255,0.5);
  font-weight:500;
  display:inline-flex;
  align-items:center;
  gap:5px;
}
.pill.acc{color:var(--accent-deep);background:var(--accent-soft)}
.pill.up{color:var(--good);background:var(--good-soft)}
.pill.dn{color:var(--danger-deep);background:var(--danger-soft)}
.pill.warn{color:var(--warn);background:var(--warn-soft)}
```

### Glass card
```css
.card{
  background:linear-gradient(180deg, rgba(255,255,255,0.7), rgba(255,255,255,0.45));
  border:1px solid var(--glass-border);
  border-radius:var(--r-lg);
  box-shadow:var(--glass-shadow);
  overflow:hidden;
}
```

## 6) Motion

- Standard UI transitions: `.15s` to `.18s ease`
- Reveal animations: `.25s` to `.35s ease`
- Pane slide: `.35s cubic-bezier(.4,0,.2,1)`
- Live dot blink: `1.6s infinite`
- Background drift: `18s` and `22s`

## 7) Recommended Next.js setup

### `app/layout.tsx`
```tsx
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" data-theme="light">
      <body>{children}</body>
    </html>
  );
}
```

### `app/globals.css`
Paste the token blocks above, then add:
```css
html, body{
  margin:0;
  padding:0;
  color:var(--ink);
  font-family:var(--sans);
  -webkit-font-smoothing:antialiased;
}

body{
  min-height:100vh;
  background:
    radial-gradient(900px 600px at 12% -10%, rgba(92,141,255,0.35), transparent 60%),
    radial-gradient(700px 600px at 100% 10%, rgba(155,193,255,0.45), transparent 65%),
    radial-gradient(800px 700px at 80% 100%, rgba(116,162,255,0.32), transparent 60%),
    linear-gradient(180deg, #EAF2FF 0%, #DCE9FF 100%);
}
[data-theme="dark"] body{
  background:
    radial-gradient(900px 600px at 12% -10%, rgba(60,60,65,0.4), transparent 60%),
    radial-gradient(700px 600px at 100% 10%, rgba(40,40,45,0.5), transparent 65%),
    radial-gradient(800px 700px at 80% 100%, rgba(50,50,55,0.4), transparent 60%),
    linear-gradient(180deg, #08080A 0%, #0E0E11 100%);
}
```

## 8) Tailwind mapping idea

If you use Tailwind, map these to CSS variables in `tailwind.config.ts`:

```ts
theme: {
  extend: {
    colors: {
      bg: "var(--bg-1)",
      bg2: "var(--bg-2)",
      ink: "var(--ink)",
      ink2: "var(--ink-2)",
      accent: "var(--accent)",
      good: "var(--good)",
      danger: "var(--danger)",
      warn: "var(--warn)",
    },
    borderRadius: {
      sm: "8px",
      md: "12px",
      lg: "16px",
      xl: "20px",
    },
    boxShadow: {
      sm: "0 1px 2px rgba(43,69,112,.06), 0 0 0 1px rgba(255,255,255,.6) inset",
      md: "0 4px 12px -2px rgba(43,69,112,.12), 0 1px 0 rgba(255,255,255,.7) inset",
      lg: "0 8px 32px -10px rgba(43,69,112,.18), 0 1px 0 rgba(255,255,255,.7) inset",
      xl: "0 24px 60px -10px rgba(43,69,112,.25), 0 1px 0 rgba(255,255,255,.7) inset",
    }
  }
}
```
