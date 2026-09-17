# Design System: Dual-Tone Neomorphic Dashboard
Asset ID: assets/b7263f8aa4ea414aa05885bd0d637d80

---
name: Dual-Tone Neomorphic Dashboard
colors:
  surface: '#f7f9fc'
  surface-dim: '#d8dadd'
  surface-bright: '#f7f9fc'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f4f7'
  surface-container: '#eceef1'
  surface-container-high: '#e6e8eb'
  surface-container-highest: '#e0e3e6'
  on-surface: '#191c1e'
  on-surface-variant: '#44474a'
  inverse-surface: '#2d3133'
  inverse-on-surface: '#eff1f4'
  outline: '#75777b'
  outline-variant: '#c5c6ca'
  surface-tint: '#5b5f63'
  primary: '#0c1014'
  on-primary: '#ffffff'
  primary-container: '#212529'
  on-primary-container: '#888c91'
  inverse-primary: '#c3c7cc'
  secondary: '#00687a'
  on-secondary: '#ffffff'
  secondary-container: '#57dffe'
  on-secondary-container: '#006172'
  tertiary: '#1a0c00'
  on-tertiary: '#ffffff'
  tertiary-container: '#361f00'
  on-tertiary-container: '#c37c00'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#e0e3e8'
  primary-fixed-dim: '#c3c7cc'
  on-primary-fixed: '#181c20'
  on-primary-fixed-variant: '#43474c'
  secondary-fixed: '#acedff'
  secondary-fixed-dim: '#4cd7f6'
  on-secondary-fixed: '#001f26'
  on-secondary-fixed-variant: '#004e5c'
  tertiary-fixed: '#ffddb8'
  tertiary-fixed-dim: '#ffb95f'
  on-tertiary-fixed: '#2a1700'
  on-tertiary-fixed-variant: '#653e00'
  background: '#f7f9fc'
  on-background: '#191c1e'
  surface-variant: '#e0e3e6'
typography:
  headline-xl:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.015em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
  display-stat:
    fontFamily: Plus Jakarta Sans
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 34px
    letterSpacing: -0.02em
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  label-lg:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '600'
    lineHeight: 16px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
  label-sm:
    fontFamily: Inter
    fontSize: 10px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.04em
  stat-unit:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1.5rem
  margin: 2rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2rem
---

## Brand & Style

This design system embodies a split-canvas visual language combining clinical clarity with focused analytical power. It unifies two distinct atmospheric paradigms into a cohesive whole:

- **Left Canvas (The Light Sanctuary):** An airy, high-key porcelain and warm alabaster workspace. It communicates calm, transparency, and clinical precision through pure white elevated planes, delicate diffusion shadows, and pastel-cushioned metric tiles.
- **Right Canvas (The Obsidian Console):** A deep charcoal slate surface engineered for intense focus, deep metrics, and physiological telemetry. It provides rich contrast, reduced eye fatigue, and dramatic data presentation.

The interaction ethos balances soft tactile neomorphism—subtle extruded planes and soft embossed insets—with modern high-contrast digital typography. The result is warm, human-centric, and reassuring without sacrificing the analytical rigor demanded by health, wellness, and quantitative tracking platforms.

## Colors

The system uses a deliberate dual-zone palette alongside a family of chromatic semantic accents:

### Surface Ecosystem
- **Light Workspace Canvas:** `#FAF8F5` blending subtly into `#F4F6F9`.
- **Light Elevated Card Surface:** Pure `#FFFFFF` with ultra-soft ambient shadow falloffs.
- **Dark Inspector Console Canvas:** `#212529` with deep base `#1A1D24`.
- **Dark Elevated Container Surface:** `#2B303A` paired with soft internal borders (`rgba(255, 255, 255, 0.08)`).

### Metric & Status Accents
- **Warm Amber:** `#F59E0B` (Badge tint: `#FEF3C7` at 20% opacity) for metabolic indices, glucose, and meditation activity.
- **Rose / Coral:** `#EF4444` (Badge tint: `#FEE2E2` at 20% opacity) for cardiovascular metrics and aerobic peaks.
- **Soft Teal / Cyan:** `#06B6D4` (Badge tint: `#CFFAFE` at 20% opacity) for blood pressure, fluid metrics, and yoga milestones.
- **Vibrant Mint:** `#10B981` (Badge tint: `#D1FAE5`) for optimal diagnostic statuses, badges, and positive shifts.

### Text & Contrast Rules
- **Light Zone:** Primary typography `#1E293B` (slate-900), secondary `#64748B` (slate-500), subtle `#94A3B8` (slate-400).
- **Dark Zone:** Primary typography `#F8FAFC` (slate-50), secondary `#94A3B8` (slate-400), muted `#64748B` (slate-500).

## Typography

The type system blends the friendly geometric curves of **Plus Jakarta Sans** with the structural clarity of **Inter**:

- **Plus Jakarta Sans** governs all titles, section headlines, interactive metric triggers, and primary value readouts. Its subtle ink-traps and warm curves soften clinical data, transforming dense biological or numerical feedback into accessible insights.
- **Inter** handles high-density microcopy, data-table labels, chart tick values, sparkline captions, and measurement units (e.g., `mg/dL`, `bpm`, `mmHg`). Its neutral stance ensures absolute legibility even at 10px and 12px scales.
- Numeric figures in statistics and charts must use tabular figures (`font-variant-numeric: tabular-nums`) to prevent layout jitter during dynamic data streaming.

## Layout & Spacing

The layout is built upon an asymmetric split master canvas:

### Structural Grid & Proportion
- **Navigation Dock:** A dedicated 80px-wide floating vertical rail fixed to the far left.
- **Primary Workspace (Light Zone):** Occupies 60%–65% of viewport width on desktop displays. Operates on an 8-column nested sub-grid with `1.5rem` gutters.
- **Analytical Console (Dark Zone):** Occupies 35%–40% of the viewport width. Designed as a self-contained monolith panel utilizing a 4-column nested sub-grid.
- **Breakpoint Behavior:**
  - **Desktop (>= 1280px):** Simultaneous side-by-side dual canvas layout.
  - **Tablet (768px - 1279px):** Dark Analytical Console moves below the light workspace as a docked bottom sheet or stacked section. Left navigation rail collapses to an adaptive icon bar.
  - **Mobile (< 768px):** Full vertical stacking. Navigation moves to a compact bottom navigation bar. Cards take full container width minus `1rem` outer margins.

## Elevation & Depth

Visual hierarchy uses two distinct approaches tailored to each zone:

### Light Canvas: Soft Neomorphic Diffusion
The light zone avoids harsh borders and heavy shadows in favor of smooth, luminous depth:
- **Default Card Float:** `box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.04), 0 4px 6px -2px rgba(0, 0, 0, 0.02);`
- **Icon Pod Insets & Soft Badges:** `box-shadow: inset 0 1px 2px rgba(255, 255, 255, 0.8), 0 2px 4px rgba(0, 0, 0, 0.03);`
- **Interactive Control Hover:** Translates -2px along the Y-axis, transitioning to `0 16px 36px -4px rgba(0, 0, 0, 0.06)`.

### Dark Canvas: Tonal Stacking & Specular Rim Light
The dark zone relies on tone-on-tone value shifts combined with ultra-fine light catchers:
- **Base Console:** Solid `#212529` with no outer cast shadow.
- **Elevated Sub-Cards:** Background `#2B303A` bordered by `1px solid rgba(255, 255, 255, 0.06)`, with ambient drop shadow `0 8px 24px -4px rgba(0, 0, 0, 0.40)`.
- **Glow Accents:** Status dots and anatomical callout rings use localized color blurs: `box-shadow: 0 0 12px currentColor`.

## Shapes

The design system maintains a welcoming, tactile contour standard (`roundedness: 2`):

- **Master Split Containers:** Outer boundaries use extra-large radii (24px to 32px) to frame the dual workspaces smoothly.
- **Metric Cards & Data Displays:** Use 16px (`rounded-lg` / `1rem`) corner radii, balancing soft approachability with strict data alignment.
- **Badges, Action Chips & Pills:** Full pill contour (`rounded-full` / 9999px) for status indicators ("Normal", "Healthy", date markers) and circular icon backing plates.
- **Form Inputs & Nested Selectors:** 10px to 12px curvature, offering a clear visual contrast against the more rounded parent cards.

## Components

### 1. Metric Tile (Light Canvas)
- **Structure:** Pure white card surface, `1.5rem` internal padding, featuring a top row with an icon badge and metric label, a middle readout row, and a bottom sparkline or status badge.
- **Icon Badge:** 40x40px rounded squircle (12px radius) tinted with 12% opacity of the metric's accent color (Amber, Rose, Cyan) with the primary icon centered at 20px.
- **Sparkline Area:** Sub-chart using soft gradient fills transitioning from 20% accent color opacity to transparent at the baseline.

### 2. Dual-Mode Buttons & Controls
- **Light Canvas Primary:** Clean white surface, subtle 1px border (`#E2E8F0`), drop shadow `0 2px 4px rgba(0,0,0,0.04)`, dark text (`#1E293B`).
- **Dark Canvas Primary:** Charcoal slate `#2B303A`, subtle rim border (`rgba(255, 255, 255, 0.12)`), white text (`#FFFFFF`).
- **Pill Filter / Dropdown:** Pill shape (9999px), internal padding `0.375rem 0.875rem`, accompanied by a trailing micro chevron icon.

### 3. Anatomical & Telemetry Visualizer (Dark Canvas)
- **Container:** Dark substrate `#2B303A` embedded within `#212529`.
- **Measurement Callout Pointers:** 1px glowing line (`rgba(239, 68, 68, 0.6)`) anchored to the visual vector, terminating in a white stat card displaying the label, value, and directional trend arrow.

### 4. Status Chips & Badges
- **Size:** Compact vertical height (22px to 26px), horizontal padding `0.625rem`.
- **Style:** Filled with 15% opacity of the semantic status color; typography set in `label-sm` with matched colored glyphs and text.

### 5. Multi-Color Segmented Activity Chart
- **Bars:** Vertically segmented pill stacks with 4px corner radii, spaced with `0.5rem` gaps.
- **Color Coding:** Tri-color distribution per column matching Aerobics (Coral `#EF4444`), Yoga (Cyan `#06B6D4`), and Meditation (Amber `#F59E0B`).

## Brand & Style

This design system embodies a split-canvas visual language combining clinical clarity with focused analytical power. It unifies two distinct atmospheric paradigms into a cohesive whole:

- **Left Canvas (The Light Sanctuary):** An airy, high-key porcelain and warm alabaster workspace. It communicates calm, transparency, and clinical precision through pure white elevated planes, delicate diffusion shadows, and pastel-cushioned metric tiles.
- **Right Canvas (The Obsidian Console):** A deep charcoal slate surface engineered for intense focus, deep metrics, and physiological telemetry. It provides rich contrast, reduced eye fatigue, and dramatic data presentation.

The interaction ethos balances soft tactile neomorphism—subtle extruded planes and soft embossed insets—with modern high-contrast digital typography. The result is warm, human-centric, and reassuring without sacrificing the analytical rigor demanded by health, wellness, and quantitative tracking platforms.

## Layout & Spacing

The layout is built upon an asymmetric split master canvas:

### Structural Grid & Proportion
- **Navigation Dock:** A dedicated 80px-wide floating vertical rail fixed to the far left.
- **Primary Workspace (Light Zone):** Occupies 60%–65% of viewport width on desktop displays. Operates on an 8-column nested sub-grid with `1.5rem` gutters.
- **Analytical Console (Dark Zone):** Occupies 35%–40% of the viewport width. Designed as a self-contained monolith panel utilizing a 4-column nested sub-grid.
- **Breakpoint Behavior:**
  - **Desktop (>= 1280px):** Simultaneous side-by-side dual canvas layout.
  - **Tablet (768px - 1279px):** Dark Analytical Console moves below the light workspace as a docked bottom sheet or stacked section. Left navigation rail collapses to an adaptive icon bar.
  - **Mobile (< 768px):** Full vertical stacking. Navigation moves to a compact bottom navigation bar. Cards take full container width minus `1rem` outer margins.

## Elevation & Depth

Visual hierarchy uses two distinct approaches tailored to each zone:

### Light Canvas: Soft Neomorphic Diffusion
The light zone avoids harsh borders and heavy shadows in favor of smooth, luminous depth:
- **Default Card Float:** `box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.04), 0 4px 6px -2px rgba(0, 0, 0, 0.02);`
- **Icon Pod Insets & Soft Badges:** `box-shadow: inset 0 1px 2px rgba(255, 255, 255, 0.8), 0 2px 4px rgba(0, 0, 0, 0.03);`
- **Interactive Control Hover:** Translates -2px along the Y-axis, transitioning to `0 16px 36px -4px rgba(0, 0, 0, 0.06)`.

### Dark Canvas: Tonal Stacking & Specular Rim Light
The dark zone relies on tone-on-tone value shifts combined with ultra-fine light catchers:
- **Base Console:** Solid `#212529` with no outer cast shadow.
- **Elevated Sub-Cards:** Background `#2B303A` bordered by `1px solid rgba(255, 255, 255, 0.06)`, with ambient drop shadow `0 8px 24px -4px rgba(0, 0, 0, 0.40)`.
- **Glow Accents:** Status dots and anatomical callout rings use localized color blurs: `box-shadow: 0 0 12px currentColor`.

## Components

### 1. Metric Tile (Light Canvas)
- **Structure:** Pure white card surface, `1.5rem` internal padding, featuring a top row with an icon badge and metric label, a middle readout row, and a bottom sparkline or status badge.
- **Icon Badge:** 40x40px rounded squircle (12px radius) tinted with 12% opacity of the metric's accent color (Amber, Rose, Cyan) with the primary icon centered at 20px.
- **Sparkline Area:** Sub-chart using soft gradient fills transitioning from 20% accent color opacity to transparent at the baseline.

### 2. Dual-Mode Buttons & Controls
- **Light Canvas Primary:** Clean white surface, subtle 1px border (`#E2E8F0`), drop shadow `0 2px 4px rgba(0,0,0,0.04)`, dark text (`#1E293B`).
- **Dark Canvas Primary:** Charcoal slate `#2B303A`, subtle rim border (`rgba(255, 255, 255, 0.12)`), white text (`#FFFFFF`).
- **Pill Filter / Dropdown:** Pill shape (9999px), internal padding `0.375rem 0.875rem`, accompanied by a trailing micro chevron icon.

### 3. Anatomical & Telemetry Visualizer (Dark Canvas)
- **Container:** Dark substrate `#2B303A` embedded within `#212529`.
- **Measurement Callout Pointers:** 1px glowing line (`rgba(239, 68, 68, 0.6)`) anchored to the visual vector, terminating in a white stat card displaying the label, value, and directional trend arrow.

### 4. Status Chips & Badges
- **Size:** Compact vertical height (22px to 26px), horizontal padding `0.625rem`.
- **Style:** Filled with 15% opacity of the semantic status color; typography set in `label-sm` with matched colored glyphs and text.

### 5. Multi-Color Segmented Activity Chart
- **Bars:** Vertically segmented pill stacks with 4px corner radii, spaced with `0.5rem` gaps.
- **Color Coding:** Tri-color distribution per column matching Aerobics (Coral `#EF4444`), Yoga (Cyan `#06B6D4`), and Meditation (Amber `#F59E0B`).
