// Typed client for the dashboard API (contract v1.0, api/README.md). Same-origin: the dev server
// proxies /api to uvicorn; `make dashboard` serves web/dist from the API itself.
import type {
  CbaCase,
  DifferenceResponse,
  FiscalResponse,
  FunnelResponse,
  LayersResponse,
  Labelled,
  Meta,
  ParetoResponse,
  Population,
  Programme,
  RegisterResponse,
  Scenario,
  StationProps,
  VfmResponse,
} from "./types";
import type { FeatureCollection, Geometry } from "geojson";

export async function getJSON<T>(path: string): Promise<T> {
  const res = await fetch(path);
  if (!res.ok) {
    let detail = `${res.status}`;
    try {
      const body = (await res.json()) as { detail?: string };
      if (body.detail) detail += `: ${body.detail}`;
    } catch {
      /* not JSON */
    }
    throw new Error(`${path} -> ${detail}`);
  }
  return (await res.json()) as T;
}

export const api = {
  meta: () => getJSON<Meta>("/api/meta"),
  layers: () => getJSON<LayersResponse>("/api/layers"),
  stations: () => getJSON<FeatureCollection<Geometry, StationProps>>("/api/stations"),
  regions: () => getJSON<FeatureCollection>("/api/regions"),
  register: () => getJSON<RegisterResponse>("/api/register"),
  funnel: () => getJSON<FunnelResponse>("/api/funnel"),
  scenarios: () => getJSON<Labelled & { baseline: string; scenarios: Scenario[] }>("/api/scenarios"),
  cba: (pop: Population) => getJSON<Labelled & { cases: CbaCase[] }>(`/api/cba?population=${pop}`),
  programmes: (pop: Population) =>
    getJSON<Labelled & { programmes: Programme[] }>(`/api/programmes?population=${pop}`),
  pareto: () => getJSON<ParetoResponse>("/api/pareto"),
  fiscal: () => getJSON<FiscalResponse>("/api/fiscal"),
  vfm: () => getJSON<VfmResponse>("/api/vfm"),
  difference: (scenario: string, pop: Population) =>
    getJSON<DifferenceResponse>(`/api/difference?scenario=${encodeURIComponent(scenario)}&population=${pop}`),
};
