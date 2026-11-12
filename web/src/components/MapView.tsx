// National map: MapLibre basemap (OpenFreeMap, keyless; plain background fallback) + deck.gl rail
// layers. Pattern adapted from TrafficTwin Jeddah web/src/engine.ts (Apache-2.0; see NOTICE).
import { useEffect, useRef, useState } from "react";
import maplibregl, { type StyleSpecification } from "maplibre-gl";
import { MapboxOverlay } from "@deck.gl/mapbox";
import { GeoJsonLayer, PathLayer, ScatterplotLayer } from "@deck.gl/layers";
import { PathStyleExtension } from "@deck.gl/extensions";
import type { Layer, PickingInfo } from "@deck.gl/core";
import type { FeatureCollection, Geometry, Position } from "geojson";
import {
  BASEMAP_STYLE_URL,
  INITIAL_VIEW,
  LAYER_STYLE,
  OSM_CREDIT,
  STAGE_STYLE,
} from "../config";
import type { LayerKey, LayersResponse, LineProps, RegisterRow, StationProps } from "../types";
import { readiness } from "../ready";

const BLANK_STYLE: StyleSpecification = {
  version: 8,
  sources: {},
  layers: [{ id: "background", type: "background", paint: { "background-color": "#eef0ee" } }],
};

interface PathDatum {
  path: Position[];
  props: LineProps;
}

function toPaths(fc: { features: { geometry: Geometry; properties: LineProps }[] }): PathDatum[] {
  const out: PathDatum[] = [];
  for (const f of fc.features) {
    const g = f.geometry;
    if (g.type === "LineString") out.push({ path: g.coordinates, props: f.properties });
    else if (g.type === "MultiLineString") for (const c of g.coordinates) out.push({ path: c, props: f.properties });
  }
  return out;
}

function toPoints(fc: { features: { geometry: Geometry; properties: LineProps }[] }): { pos: Position; props: LineProps }[] {
  const out: { pos: Position; props: LineProps }[] = [];
  for (const f of fc.features) if (f.geometry.type === "Point") out.push({ pos: f.geometry.coordinates, props: f.properties });
  return out;
}

export interface MapProps {
  layers: LayersResponse | null;
  stations: FeatureCollection<Geometry, StationProps> | null;
  regions: FeatureCollection | null;
  visible: Record<LayerKey, boolean>;
  hypotheticalIds: Set<string> | null; // null = all hypothetical corridors
  highlightIds?: Set<string>;
  register?: RegisterRow[] | null;
  caption: string;
}

export function MapView(props: MapProps) {
  const container = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const overlayRef = useRef<MapboxOverlay | null>(null);
  const [basemap, setBasemap] = useState<"loading" | "openfreemap" | "plain">("loading");

  useEffect(() => {
    if (!container.current) return;
    const map = new maplibregl.Map({
      container: container.current,
      style: BLANK_STYLE,
      center: [INITIAL_VIEW.longitude, INITIAL_VIEW.latitude],
      zoom: INITIAL_VIEW.zoom,
      attributionControl: false,
      canvasContextAttributes: { preserveDrawingBuffer: true },
    });
    // The OSM credit is always visible (rule 4): custom attribution, never compact.
    map.addControl(
      new maplibregl.AttributionControl({
        compact: false,
        customAttribution: `<a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer">${OSM_CREDIT}</a>`,
      }),
      "bottom-right",
    );
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");
    const overlay = new MapboxOverlay({
      interleaved: false,
      layers: [],
      getTooltip: (info: PickingInfo) => tooltip(info),
    } as ConstructorParameters<typeof MapboxOverlay>[0]);
    map.addControl(overlay);
    mapRef.current = map;
    overlayRef.current = overlay;
    readiness.mapIdle = false;
    map.on("idle", () => {
      readiness.mapIdle = true;
    });

    const plain = new URLSearchParams(window.location.search).get("basemap") === "none";
    if (plain) setBasemap("plain");
    else {
      fetch(BASEMAP_STYLE_URL)
        .then((r) => (r.ok ? (r.json() as Promise<StyleSpecification>) : Promise.reject(new Error(`${r.status}`))))
        .then((style) => {
          map.setStyle(style, { diff: false });
          setBasemap("openfreemap");
        })
        .catch((err: unknown) => {
          console.warn("basemap style failed; plain background", err);
          setBasemap("plain");
        });
    }
    return () => {
      map.remove();
      mapRef.current = null;
      overlayRef.current = null;
    };
  }, []);

  useEffect(() => {
    const overlay = overlayRef.current;
    if (!overlay) return;
    overlay.setProps({ layers: buildLayers(props) });
    readiness.mapIdle = false;
    mapRef.current?.triggerRepaint();
  }, [props.layers, props.stations, props.regions, props.visible, props.hypotheticalIds, props.highlightIds, props.register]);

  return (
    <div className="map-wrap">
      <div ref={container} className="map" />
      <Legend visible={props.visible} caption={props.caption} basemap={basemap} register={!!props.register} committed={props.layers?.layers.committed ?? null} />
    </div>
  );
}

function tooltip(info: PickingInfo): { html: string } | null {
  const o = info.object as { props?: LineProps; row?: RegisterRow; station?: StationProps } | undefined;
  if (!o) return null;
  if (o.row) {
    const r = o.row;
    return {
      html: `<b>${r.name_en ?? ""}</b> <span dir="rtl">${r.name_ar ?? ""}</span><br/>${r.region} · ${STAGE_STYLE[r.stage].name}<br/>population ${r.population?.toLocaleString("en-US") ?? "n/a"} (${r.pop_source_status ?? "status n/a"})`,
    };
  }
  if (o.station) {
    const s = o.station;
    return { html: `<b>${s.name_en ?? ""}</b> <span dir="rtl">${s.name_ar ?? ""}</span><br/>station · ${LAYER_STYLE[s.layer].name}` };
  }
  const p = o.props;
  if (!p) return null;
  const name = p.station_name_en ? `${p.name_en ?? p.id}` : (p.name_en ?? p.id ?? p.line_id ?? "");
  return {
    html: `<b>${name}</b><br/>layer: ${LAYER_STYLE[p.layer].name}${p.status ? ` · ${p.status}` : ""}${p.source ? `<br/>source: ${p.source}${p.source_date ? `, ${p.source_date}` : ""}` : ""}`,
  };
}

function buildLayers(p: MapProps): Layer[] {
  const out: Layer[] = [];
  if (p.regions) {
    out.push(
      new GeoJsonLayer({
        id: "regions",
        data: p.regions,
        stroked: true,
        filled: false,
        getLineColor: [90, 90, 90, 90],
        lineWidthMinPixels: 0.7,
        pickable: false,
      }),
    );
  }
  if (p.register) {
    out.push(
      new ScatterplotLayer<{ pos: [number, number]; row: RegisterRow }>({
        id: "register",
        data: p.register.filter((r) => r.lat !== null && r.lon !== null).map((r) => ({ pos: [r.lon as number, r.lat as number], row: r })),
        getPosition: (d) => d.pos,
        getFillColor: (d) => STAGE_STYLE[d.row.stage].color,
        getRadius: (d) => (d.row.stage === "not_long_listed" ? 2.2 : 4),
        radiusUnits: "pixels",
        pickable: true,
      }),
    );
  }
  if (!p.layers) return out;
  const L = p.layers.layers;
  const order: LayerKey[] = ["historical", "existing", "committed", "hypothetical"];
  for (const key of order) {
    if (!p.visible[key]) continue;
    const st = LAYER_STYLE[key];
    let paths = toPaths(L[key]);
    if (key === "hypothetical" && p.hypotheticalIds) {
      const ids = p.hypotheticalIds;
      paths = paths.filter((d) => ids.has(d.props.id ?? ""));
    }
    const hi = p.highlightIds;
    out.push(
      new PathLayer<PathDatum>({
        id: `lines-${key}`,
        data: paths,
        getPath: (d) => d.path as [number, number][],
        getColor: st.color,
        getWidth: (d) => (hi && hi.has(d.props.id ?? "") ? st.width * 1.8 : st.width),
        widthUnits: "pixels",
        capRounded: true,
        jointRounded: true,
        pickable: true,
        updateTriggers: { getWidth: [hi ? [...hi].join(",") : ""] },
        ...(st.dash
          ? { getDashArray: st.dash, dashJustified: true, dashGapPickable: true, extensions: [new PathStyleExtension({ dash: true })] }
          : {}),
      } as ConstructorParameters<typeof PathLayer<PathDatum>>[0]),
    );
    if (key === "hypothetical") {
      let pts = toPoints(L.hypothetical);
      if (p.hypotheticalIds) {
        const ids = p.hypotheticalIds;
        pts = pts.filter((d) => ids.has(d.props.id ?? ""));
      }
      out.push(
        new ScatterplotLayer<{ pos: Position; props: LineProps }>({
          id: "hypothetical-stations",
          data: pts,
          getPosition: (d) => d.pos as [number, number],
          getRadius: 6,
          radiusUnits: "pixels",
          stroked: true,
          filled: true,
          getFillColor: [255, 255, 255, 255],
          getLineColor: st.color,
          lineWidthUnits: "pixels",
          getLineWidth: 3,
          pickable: true,
        }),
      );
    }
  }
  if (p.stations) {
    const data = p.stations.features
      .filter((f) => f.geometry.type === "Point" && p.visible[f.properties.layer])
      .map((f) => ({ pos: (f.geometry as { coordinates: Position }).coordinates, station: f.properties }));
    out.push(
      new ScatterplotLayer<{ pos: Position; station: StationProps }>({
        id: "stations",
        data,
        getPosition: (d) => d.pos as [number, number],
        getRadius: 2.6,
        radiusUnits: "pixels",
        stroked: true,
        getFillColor: [255, 255, 255, 255],
        getLineColor: (d) => LAYER_STYLE[d.station.layer].color,
        lineWidthUnits: "pixels",
        getLineWidth: 1.4,
        pickable: true,
      }),
    );
  }
  return out;
}

function Swatch({ k }: { k: LayerKey }) {
  const st = LAYER_STYLE[k];
  const [r, g, b] = st.color;
  const dash = st.dash ? `${st.dash[0] * 3} ${st.dash[1] * 3}` : undefined;
  return (
    <svg width="38" height="10" aria-hidden="true">
      <line x1="2" y1="5" x2="36" y2="5" stroke={`rgb(${r},${g},${b})`} strokeWidth={st.width} strokeDasharray={dash} strokeLinecap="round" />
      {k === "hypothetical" ? <circle cx="30" cy="5" r="3.5" fill="#fff" stroke={`rgb(${r},${g},${b})`} strokeWidth="2" /> : null}
    </svg>
  );
}

function Legend({
  visible,
  caption,
  basemap,
  register,
  committed,
}: {
  visible: Record<LayerKey, boolean>;
  caption: string;
  basemap: string;
  register: boolean;
  committed: LayersResponse["layers"]["committed"] | null;
}) {
  const keys: LayerKey[] = ["existing", "committed", "hypothetical", "historical"];
  return (
    <div className="legend" data-testid="legend">
      <div className="legend-title">Rail layers</div>
      {keys.map((k) => (
        <div key={k} className={`legend-row${visible[k] ? "" : " off"}`}>
          <Swatch k={k} />
          <span>{LAYER_STYLE[k].name}</span>
          {visible[k] ? null : <span className="muted"> (not in this scenario)</span>}
        </div>
      ))}
      {register ? (
        <div className="legend-register">
          {(Object.keys(STAGE_STYLE) as (keyof typeof STAGE_STYLE)[]).map((s) => {
            const [r, g, b] = STAGE_STYLE[s].color;
            return (
              <div key={s} className="legend-row">
                <svg width="38" height="10" aria-hidden="true">
                  <circle cx="19" cy="5" r="4" fill={`rgb(${r},${g},${b})`} />
                </svg>
                <span>{STAGE_STYLE[s].name}</span>
              </div>
            );
          })}
        </div>
      ) : null}
      {committed && committed.features.length ? (
        <div className="legend-committed">
          Committed lines are announced/planned, not existing (source, date):{" "}
          {committed.features
            .map((f) => `${f.properties.line_id ?? f.properties.id ?? ""} (${f.properties.source ?? "source n/a"}, ${f.properties.source_date || "date not stated in the source"})`)
            .join("; ")}
        </div>
      ) : null}
      <div className="legend-caption">{caption}</div>
      <div className="legend-credit">
        Map data {OSM_CREDIT} (ODbL){basemap === "openfreemap" ? "; basemap OpenFreeMap / OpenMapTiles" : "; plain background"}
      </div>
    </div>
  );
}
