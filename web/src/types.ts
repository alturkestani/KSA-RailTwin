// Types for the dashboard API contract v1.0 (api/README.md). Hand-written from api/data.py.
import type { Feature, FeatureCollection, Geometry } from "geojson";

export type LayerKey = "existing" | "committed" | "hypothetical" | "historical";

export interface Range {
  p10: number | null;
  p50: number | null;
  p90: number | null;
}

export interface Labelled {
  label: string;
  alignment_limitation: string;
}

export interface Framing {
  role: string;
  trade_off_only: boolean;
}

export interface Meta extends Labelled {
  contract_version: string;
  judge: { version: string; sha256: string; source: string };
  seed: number;
  osm_credit: string;
  layers: Record<LayerKey, string>;
  baseline: string;
  baseline_run: string;
  central_row: { population: string; horizon: number; rate_case: string };
  framing: Record<string, Framing>;
  trade_off_caption: string;
  comparison_caption: string;
  comparison_layouts: string[];
}

export interface LineProps {
  layer: LayerKey;
  layer_name: string;
  line_id?: string;
  id?: string;
  name_en?: string | null;
  name_ar?: string | null;
  status?: string | null;
  source?: string | null;
  source_date?: string | null;
  accessed?: string | null;
  family?: string | null;
  scenario?: string | null;
  kind?: string;
  length_km?: number | null;
  alignment_km?: number | null;
  station_name_en?: string | null;
}

export type LineFC = FeatureCollection<Geometry, LineProps> & { source: string };
export type LineFeature = Feature<Geometry, LineProps>;

export interface LayersResponse extends Labelled {
  osm_credit: string;
  layer_names: Record<LayerKey, string>;
  layers: Record<LayerKey, LineFC>;
}

export interface StationProps {
  line_id: string | null;
  name_en: string | null;
  name_ar: string | null;
  class: string | null;
  layer: LayerKey;
}

export type Stage = "not_long_listed" | "served" | "long_list" | "short_list";

export interface RegisterRow {
  row_key: string;
  name_en: string | null;
  name_ar: string | null;
  region: string;
  governorate: string | null;
  lat: number | null;
  lon: number | null;
  population: number | null;
  pop_source_status: string | null;
  economic_roles: string[];
  terrain_class: string | null;
  screened: boolean;
  exclusion_reason: string | null;
  stage: Stage;
  score: number | null;
  rank: number | null;
}

export interface RegisterResponse {
  label: string;
  stages: Stage[];
  count: number;
  rows: RegisterRow[];
}

export interface FunnelResponse {
  label: string;
  stages: { stage: string; count: number; source: string }[];
  per_region: { region: string; settlements: number; long_list: number; served: number; short_list: number }[];
  corridors_by_family: Record<string, number>;
  appraised_by_family: Record<string, number>;
}

export interface Scenario {
  id: string;
  kind: string | null;
  title: string | null;
  baseline: string | null;
  layers: string[];
  lines: string[];
  candidates: string[];
  role: string | null;
  trade_off_only: boolean;
  caption: string | null;
  source: string;
}

export interface CbaCase {
  case: string;
  family: string | null;
  scenario: string | null;
  baseline: string | null;
  candidate: string | null;
  units: string | null;
  metrics: Record<"npv" | "bcr" | "pvb" | "pvc" | "npv_wei" | "bcr_wei" | "fiscal_cost" | "pv_capex", Range | null>;
  source: string;
}

export interface Programme {
  id: string;
  role: string;
  trade_off_only: boolean;
  caption: string | null;
  baseline: string;
  corridors: string[];
  phases: Record<string, string[]>;
  flags: string | null;
  metrics: { npv: Range | null; bcr: Range | null; pvc: Range | null; capex: Range };
  npv_at_p50_cost: Record<"low" | "medium" | "high", number | null>;
  npv_at_p90_cost: Record<"low" | "medium" | "high", number | null>;
  robust_npv: number | null;
  access_gain_120: number | null;
  new_route_km: number | null;
  units: string | null;
  p90_cost_note?: string;
  source: string[];
}

export interface Band {
  low: number | null;
  medium: number | null;
  high: number | null;
}

export interface ParetoPoint {
  engine: string;
  layout_hash: string;
  robust_npv: number | null;
  npv_band: Band;
  capex_p50: number | null;
  access_gain_60: number | null;
  access_gain_120: number | null;
  n_corridors: number | null;
  on_full_front: boolean;
}

export interface ParetoLayout {
  id: string;
  role: string;
  trade_off_only: boolean;
  comparison_only: boolean; // S6-L6: connectivity comparison, not a search result
  kind: "search" | "comparison";
  caption: string | null;
  robust_npv: number | null;
  npv_band: Band;
  npv_draws_medium: Range;
  capex: Range;
  access_gain_120: number | null;
  national_reach_gain_120: number | null;
  n_corridors: number | null;
}

export interface ParetoResponse extends Labelled {
  front: ParetoPoint[];
  layouts: ParetoLayout[];
  caption_trade_off: string;
  caption_comparison: string;
  objectives: Record<string, string>;
}

export interface FiscalModel {
  model: string;
  kind: string | null;
  net_fiscal_cost_60y: Range | null;
  net_fiscal_cost_30y: Range | null;
  upfront_public_capex: Range | null;
}

export interface FiscalEntity {
  entity: string;
  role: string | null;
  capex: Range | null;
  judge_sha256: string | null;
  models: FiscalModel[];
}

export interface FiscalResponse extends Labelled {
  units: string;
  population_case: string;
  programmes: FiscalEntity[];
  corridors: FiscalEntity[];
  baseline_s1: { case: string; run: string; fiscal_cost_60y: Range | null; pv_capex: Range | null };
}

export interface VfmEntity {
  entity: string;
  role: string | null;
  psc: number | null;
  ppp: number | null;
  vfm: { low: number | null; central: number | null; high: number | null };
  sign_central: string | null;
  not_sourced_for_ksa: string[] | null;
}

export interface VfmResponse extends Labelled {
  units: string;
  definition: string;
  population_case: string;
  range_note: string;
  programmes: VfmEntity[];
  corridors: VfmEntity[];
}

export interface DiffRow {
  metric: string;
  unit: string;
  scenario: number | null;
  S1: number | null;
  delta: number | null;
}

export interface DifferenceResponse extends Labelled {
  scenario: string;
  baseline: string;
  role: string | null;
  population: string;
  rows: DiffRow[];
  lines_2050: { line_id: string; scenario: number | null; S1: number | null; delta: number | null; note: string | null }[];
  lines_2050_coverage?: { s1_lines_covered: string[]; s1_lines_not_covered: string[]; why: string };
  increments: { basis: string; [k: string]: Range | string | null };
  p90_cost_note?: string | null;
  added_corridors: string[];
  source: string | string[];
}

export type Population = "un_wpp_low" | "un_wpp_medium" | "un_wpp_high";
export type View = "map" | "register" | "ranges" | "pareto" | "difference";
