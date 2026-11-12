// Display constants (no modelling constants live here). Neutral styling, no logos (rule 9).
import type { LayerKey, Population, Stage } from "./types";

// Open, keyless vector basemap (OpenFreeMap, OSM data). `?basemap=none` uses a plain background.
export const BASEMAP_STYLE_URL = "https://tiles.openfreemap.org/styles/positron";
export const OSM_CREDIT = "© OpenStreetMap contributors";

export const INITIAL_VIEW = { longitude: 44.2, latitude: 24.2, zoom: 4.75 };

type RGBA = [number, number, number, number];

export interface LayerStyle {
  name: string;
  color: RGBA;
  width: number;
  dash: [number, number] | null; // null = solid; only `existing` is solid (rule 5)
  legend: string;
}

// Rule 5: the three rail layers (plus historical) are visually distinct; planned lines never
// share the solid "existing" style.
export const LAYER_STYLE: Record<LayerKey, LayerStyle> = {
  existing: { name: "existing", color: [31, 78, 121, 255], width: 3.2, dash: null, legend: "solid" },
  committed: {
    name: "committed/under procurement (announced/planned)",
    color: [217, 119, 6, 255],
    width: 3.2,
    dash: [5, 3],
    legend: "long dash",
  },
  hypothetical: {
    name: "hypothetical (ours)",
    color: [124, 58, 237, 255],
    width: 3.6,
    dash: [1.5, 1.5],
    legend: "dotted; stations as rings",
  },
  historical: {
    name: "historical",
    color: [120, 120, 120, 200],
    width: 1.6,
    dash: [1, 3],
    legend: "sparse dots",
  },
};
export const LAYER_ORDER: LayerKey[] = ["existing", "committed", "hypothetical", "historical"];

export const STAGE_STYLE: Record<Stage, { name: string; color: RGBA }> = {
  short_list: { name: "short list", color: [190, 24, 93, 230] },
  long_list: { name: "long list", color: [234, 88, 12, 200] },
  served: { name: "served (station-addition bucket)", color: [22, 163, 74, 220] },
  not_long_listed: { name: "not long-listed", color: [148, 163, 184, 140] },
};
export const STAGE_ORDER: Stage[] = ["short_list", "long_list", "served", "not_long_listed"];

export const POP_LABEL: Record<Population, string> = {
  un_wpp_low: "UN WPP low",
  un_wpp_medium: "UN WPP medium",
  un_wpp_high: "UN WPP high",
};

// Switcher order. S6-L4, S6-L5 (trade-off illustrations) and S6-L6 (comparison layout, not the
// recommended programme) are deliberately absent: Pareto view only.
export const SWITCHER = ["S0", "S1", "S2", "S3", "S4", "S5", "S6-L2", "S6-L1", "S6-L3"] as const;
export const SHORT_ROLE: Record<string, string> = {
  "S6-L2": "central case",
  "S6-L1": "upside case",
  "S6-L3": "reach alternative",
};

export const FAMILY_OF: Record<string, string> = {
  S2: "trunk_gap",
  S3: "branch_spur",
  S4: "commuter_belt",
  S5: "station_addition",
};
