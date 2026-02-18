# SafeSquare: Design Specification & Creative Brief

## 1. Project Overview
**SafeSquare** is a high-end Italian real estate intelligence platform. It moves beyond simple property listings to provide institutional-grade data for every Italian municipality (7,900+ towns). The platform aggregates market prices, demographic trends, and environmental risks (seismic, flood, climate) into a single, proprietary **Investment Score**.

### The Value Proposition
"Invest in Italian Real Estate with Precision." The app is a decision-support tool for serious investors who need to see the 'hidden' risks and opportunities in any given area.

---

## 2. Brand Identity & Personality
The design should feel **Premium, Analytical, and Trustworthy**. It should look like a cross between a high-end fintech dashboard (like Bloomberg or Stripe) and a modern real estate portal.

*   **Keywords:** Precision, Safety, Intelligence, Authority, Modernity.
*   **Visual Tone:** High-contrast typography, plenty of whitespace, subtle glassmorphism, and a "data-first" aesthetic.
*   **Color Palette (Proposed):**
    *   **Primary:** Deep Cobalt Blue (#2563EB) - conveys trust and technology.
    *   **Background:** Off-white/Gray-50 (#F9FAFB) with pure white cards.
    *   **Accents:** Emerald Green (Success/Safe), Amber (Caution), Crimson (Risk).
    *   **Neutral:** Slate Grays (#1A202C) for text and depth.
*   **Typography:** Modern Sans-Serif (e.g., Inter, Outfit, or Roboto). Bold, heavy weights for headings; clean, readable weights for data points.

---

## 3. Core Page Architecture (Sitemap)

### 1. The Hero Home Page
The primary entry point. Its goal is to "WOW" the user and immediately establish authority.
*   **Hero Section:** High-impact heading, search bar with autocomplete, and "Quick Stats" (total towns covered, data points processed).
*   **Feature Grid:** Three main pillars: *Demographic Pulse*, *Safety & Risks*, *Yield Projections*.
*   **Interactive Discovery Map:** A muted, grayscale map of Italy with pulsing markers on major cities. Clicking a marker takes you to the details.
*   **Visual Goal:** Feel expansive and alive.

### 2. The Discovery/Search Page
A dual-pane layout (Map on one side, Results on the other).
*   **Sidebar:** List of municipalities with their scores and basic stats.
*   **Map:** Leaflet/Mapbox integration. Markers should change color based on the Investment Score (Red -> Yellow -> Green).
*   **Interactions:** Hovering on a list item highlights the map marker and vice-versa.

### 3. The Property Details Page (The "Alpha" Dashboard)
This is the most important page. It aggregates everything for a specific town.
*   **Identity Header:** Bold town name, region badge (e.g., "LOMBARDIA"), and "Save/Download" actions.
*   **Score Card:** A prominent visual representation of the Investment Score (0-10).
*   **Stats Summary Grid:** 4 key metrics (Avg Price per sqm, Population, Rental Yield, Population Growth).
*   **The Visualization Suite:**
    *   **Price Trend:** Line chart showing historical price movement.
    *   **Investment Radar:** A radar/spider chart showing balanced scores (Market vs. Safety vs. Services).
    *   **Spatial Risk Map:** A map with toggles for Seismic, Flood, Landslide, and Air Quality layers.
    *   **Climate Trends:** Chart showing 2050 warming/rainfall projections.
*   **AI Verdict:** A highlight box with written "Market Verdict" and "Analysis Confidence" percentage.

---

## 4. Key UI Components & Design Tokens
*   **Card System:** Rounded corners (2xl/3xl), subtle borders (no harsh shadows), white background.
*   **Badges:** Small, uppercase, high-contrast badges for risk levels (EXCELLENT, MODERATE, HIGH RISK).
*   **Data Density:** Information should be dense but organized. Use grids and defined vertical spacing.
*   **Micro-animations:** Hover states on cards, pulsing map markers, and smooth transitions between dashboard tabs.

---

## 5. Technical Design Constraints
*   **Responsive Grid:** Desktop-first (analytical use), but must degrade gracefully to a clean mobile list view.
*   **Map Theming:** Maps should use a "Positron" (light grayscale) or "Dark Matter" theme to ensure markers and data layers pop.
*   **Iconography:** Thin-stroke, modern SVG icons (e.g., Lucide or Heroicons). Avoid "cartoonish" or filled icons unless for specific emphasis.

---

## 6. Project Vision for the Designer
Imagine you are building a tool for a professional fund manager who is looking to buy 50 apartments across Italy. They need to see, at a glance, why Milan is "Greener" than Naples, or why a specific town in the mountains has a low score due to "Access Connectivity" despite low prices.

**The final design should not look like a "website," but like a "platform."**
