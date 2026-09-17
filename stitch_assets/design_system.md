---
name: AI Resume & Career Intelligence Engine
colors:
  surface: '#0f131c'
  surface-dim: '#0f131c'
  surface-bright: '#353942'
  surface-container-lowest: '#0a0e16'
  surface-container-low: '#181c24'
  surface-container: '#1c2028'
  surface-container-high: '#262a33'
  surface-container-highest: '#31353e'
  on-surface: '#dfe2ee'
  on-surface-variant: '#c7c4d7'
  inverse-surface: '#dfe2ee'
  inverse-on-surface: '#2c3039'
  outline: '#908fa0'
  outline-variant: '#464554'
  surface-tint: '#c0c1ff'
  primary: '#c0c1ff'
  on-primary: '#1000a9'
  primary-container: '#8083ff'
  on-primary-container: '#0d0096'
  inverse-primary: '#494bd6'
  secondary: '#4edea3'
  on-secondary: '#003824'
  secondary-container: '#00a572'
  on-secondary-container: '#00311f'
  tertiary: '#ffb95f'
  on-tertiary: '#472a00'
  tertiary-container: '#ca8100'
  on-tertiary-container: '#3e2400'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#e1e0ff'
  primary-fixed-dim: '#c0c1ff'
  on-primary-fixed: '#07006c'
  on-primary-fixed-variant: '#2f2ebe'
  secondary-fixed: '#6ffbbe'
  secondary-fixed-dim: '#4edea3'
  on-secondary-fixed: '#002113'
  on-secondary-fixed-variant: '#005236'
  tertiary-fixed: '#ffddb8'
  tertiary-fixed-dim: '#ffb95f'
  on-tertiary-fixed: '#2a1700'
  on-tertiary-fixed-variant: '#653e00'
  background: '#0f131c'
  on-background: '#dfe2ee'
  surface-variant: '#31353e'
typography:
  headline-xl:
    fontFamily: Plus Jakarta Sans
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-xl-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 30px
    fontWeight: '700'
    lineHeight: 38px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.015em
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.015em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 30px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 26px
    letterSpacing: -0.005em
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 26px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 22px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 18px
  label-code:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
    letterSpacing: 0.02em
  label-badge:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.05em
  label-caption:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.01em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1.25rem
  gutter-lg: 2rem
  margin: 1rem
  margin-md: 2rem
  margin-lg: 3rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
---

## Brand & Style

The design system establishes a high-precision, technical, and executive-grade visual language tailored for an automated AI resume intelligence and recruitment platform. It caters to candidates, talent acquisition specialists, and executive recruiters who expect rigorous data parsing, instant feedback, and trustworthy algorithmic matching.

The visual style blends **Dark-mode Modernism** with subtle **Glassmorphism** and **Technical Precision**. It achieves depth through layered slate-to-obsidian surfaces, fine hair-line borders (1px structural accents), and targeted micro-glows behind critical scores. The emotional tone is decisive, intelligent, highly organized, and calm under data density. The interface avoids frivolous ornamentation; every visual cue directly reinforces match quality, skill verification, or diagnostic status.

## Colors

The palette is engineered specifically for deep OLED contrast and extended cognitive focus during heavy data review:

- **Primary (`#6366F1` - Electric Indigo):** Anchors primary actions, interactive controls, AI model generation indicators, and navigational active states.
- **Secondary (`#10B981` - Emerald Green):** Signals high semantic match confidence, verified skill alignment, positive diagnostic validation, and ATS compatibility milestones.
- **Tertiary (`#F59E0B` - Amber Gold):** Dedicated to critical skill gaps, missing keyword alerts, required certifications, and conditional recommendations.
- **Neutral Core (`#0B0F17` - Deep Obsidian Canvas):** Provides a clean, noise-free foundation.

### Additional Functional Surfaces & Borders
- **Surface Elevation 1 (`#121B2B` with 70–85% alpha blur):** Frosted container background for content cards, data tables, and modal shells.
- **Surface Elevation 2 (`#1A253A`):** Hover states, nested breakdown chips, and dropdown flyouts.
- **Border Trim (`#1E293B`):** 1px structural separator across all cards, dividers, and input borders to guarantee razor-sharp compartmentalization without visually cluttering the viewport.
- **Text & Metadata Hierarchy:** High-contrast text uses `#F8FAFC` for headlines and primary metrics, `#94A3B8` for secondary labels, and `#64748B` for tertiary captions and metadata.

## Typography

The type system is divided across three complementary roles:
1. **Display & Section Headers (Plus Jakarta Sans):** Introduces geometric authority with soft contemporary warmth, balancing high-tech intelligence with human career navigation.
2. **Body & Prose (Inter):** Highly legible, neutral workhorse optimized for parsing dense resumes, job descriptions, ATS breakdowns, and comparative evaluations.
3. **Data, Tokens & Metrics (JetBrains Mono):** Reserved for technical metrics (e.g., match score percentages, keyword frequencies, ATS parsing syntax, latency values, and skill gap counts). This creates clear visual demarcation between human narrative and machine analytics.

## Layout & Spacing

The dashboard relies on an asymmetric 12-column fluid grid system designed for multi-pane productivity.

### Breakpoints & Layout Adapters
- **Desktop (>= 1280px):** 12-column setup with `gutter-lg` (32px) and `margin-lg` (48px). Configured for a three-pane layout: Left Navigation (Collapsible/Iconic: 72px–260px), Central Workspace/Resume Viewer (7–8 columns), and Right Diagnostic Intelligence Pane (4–5 columns).
- **Tablet (768px – 1279px):** 8-column layout with `gutter` (20px) and `margin-md` (32px). Secondary analysis drawers fold into slide-over panels or tabbed views beneath the core resume viewer.
- **Mobile (< 768px):** Single-column stacked flow with `margin` (16px). Key performance indicators (Match % pill, critical gaps) pin to sticky headers, while deep analysis sections stack into expandable accordion panels.

Component spacing uses strict multiples of 4px, where `space-md` (16px) governs internal card padding and `space-lg` (24px) establishes section boundaries within analytic widgets.

## Elevation & Depth

Visual depth is achieved through translucent planar layering, hairline boundaries, and subtle luminescence rather than heavy opaque drop shadows:

- **Surface Ground (Base Canvas):** Solid `#0B0F17`. Non-interactive backdrop.
- **Level 1 (Card & Module Shells):** `#121B2B` rendered at 80% opacity with an active backdrop blur of `16px`. Outlined with a strict 1px border of `#1E293B`.
- **Level 2 (Active States, Drawers, Flyouts):** `#1A253A` (90% opacity, 24px blur) accompanied by an ambient, diffused shadow: `0 12px 32px -4px rgba(2, 6, 23, 0.7)`.
- **Level 3 (Modal Overlays & Popovers):** `#1F2E47` elevated with `0 20px 48px -8px rgba(0, 0, 0, 0.85)` and border highlights of `#334155`.
- **Accent Glow Highlights:** High match cards (e.g., Match > 85%) project a localized, 15% opacity radial emerald gradient (`rgba(16, 185, 129, 0.12)`) along their top edge, while alert gaps carry a gentle 15% amber perimeter luminescence.

## Shapes

The design system standardizes on **Rounded (Level 2)** geometries:
- Interactive elements (standard buttons, search bars, text inputs, table headers) use `rounded` (0.5rem / 8px).
- Structural containers (cards, analysis modules, resume parsing frames) utilize `rounded-lg` (1rem / 16px).
- Full pill profiles (`rounded-full` / 9999px) are strictly allocated to status badges, score metrics, filter tags, and category chips to distinguish discrete analytical metadata from structural blocks.

## Components

### Buttons
- **Primary:** Background in `#6366F1` with white text, font `Inter` semibold. On hover, background shifts to `#4F46E5` with a subtle box shadow `0 0 16px rgba(99, 102, 241, 0.35)`.
- **Secondary / Ghost:** Transparent background with a 1px border of `#1E293B`, filled with text `#94A3B8`. Hover transitions to `#1E293B` background and `#F8FAFC` text.
- **Destructive / Warning:** Transparent with `#F59E0B` text and border `#F59E0B33`; transitions to `rgba(245, 158, 11, 0.1)` on hover.

### Chips & Pill Badges
- **Match Score Badge:** Pill shape with `JetBrains Mono` bold. High match (>85%) uses `bg-[#10B981]/15 text-[#10B981] border border-[#10B981]/30`.
- **Skill Gap Badge:** Pill shape with `JetBrains Mono` medium. Missing skills render with `bg-[#F59E0B]/15 text-[#F59E0B] border border-[#F59E0B]/30`.
- **ATS Keyword Tag:** Compact pill with neutral background `bg-[#1E293B]` and `#94A3B8` text; interactive dismissal triggers cross icon.

### Form Inputs & Upload Targets
- **Input Fields:** `#0E1420` background with a 1px border in `#1E293B`. Focused state transitions border to `#6366F1` and adds a subtle 2px glow ring `rgba(99, 102, 241, 0.2)`. Placeholder text in `#64748B`.
- **Resume Upload Dropzone:** Elevated card featuring dashed `1.5px` border in `#334155`, active hover states shift to dashed `#6366F1` with an inner radiant indigo gradient.

### Cards & Analytical Modules
- Built on `#121B2B` with frosted glass backdrop blur and 1px `#1E293B` outline. Headers feature an uppercase title in `label-caption` with `letterSpacing: 0.05em` accompanied by an inline status badge or telemetry icon.

### Selection Controls (Checkboxes & Radios)
- Custom squares and circles with 1.5px border `#334155`. Checked state fills `#6366F1` with crisp white check/dot icon.

### Specialized AI Agent Widgets
- **Skill Matrix Diff:** Dual-column split comparison with green checkmark ribbons for matches and amber indicators for missing requirements.
- **Semantic Score Meter:** Circular or linear progress track in `#1E293B`, animated bar with `#10B981` (high confidence) or `#6366F1` (baseline).