// Decision dashboard shell: view tabs, scenario/programme switcher, map, panels, footer.
import { useEffect, useMemo, useState } from "react";
import type { FeatureCollection, Geometry } from "geojson";
import { api } from "./api";
import { POP_LABEL, SHORT_ROLE, SWITCHER } from "./config";
import type { LayerKey, LayersResponse, Meta, Population, RegisterRow, Scenario, StationProps, View } from "./types";
import { MapView } from "./components/MapView";
import { Footer } from "./components/Footer";
import { ScenarioPanel } from "./views/ScenarioPanel";
import { RegisterView } from "./views/RegisterView";
import { RangesView } from "./views/RangesView";
import { ParetoView } from "./views/ParetoView";
import { DifferenceView } from "./views/DifferenceView";
import { readiness } from "./ready";

const VIEWS: { id: View; name: string }[] = [
  { id: "map", name: "National map" },
  { id: "register", name: "Register & funnel" },
  { id: "ranges", name: "Cost/benefit ranges" },
  { id: "pareto", name: "Pareto explorer" },
  { id: "difference", name: "Difference vs S1" },
];

function param(name: string): string | null {
  return new URLSearchParams(window.location.search).get(name);
}

function visibleFor(id: string): Record<LayerKey, boolean> {
  return {
    existing: true,
    historical: true,
    committed: id !== "S0",
    hypothetical: id !== "S0" && id !== "S1",
  };
}

export function App() {
  const [view, setView] = useState<View>((param("view") as View | null) ?? "map");
  const [scenario, setScenario] = useState<string>(param("scenario") ?? "S6-L2");
  const [pop, setPop] = useState<Population>((param("pop") as Population | null) ?? "un_wpp_medium");
  const [meta, setMeta] = useState<Meta | null>(null);
  const [layers, setLayers] = useState<LayersResponse | null>(null);
  const [stations, setStations] = useState<FeatureCollection<Geometry, StationProps> | null>(null);
  const [regions, setRegions] = useState<FeatureCollection | null>(null);
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [error, setError] = useState<string>("");
  const [viewReady, setViewReady] = useState(false);
  const [registerRows, setRegisterRows] = useState<RegisterRow[] | null>(null);
  const [diffIds, setDiffIds] = useState<string[] | null>(null);

  useEffect(() => {
    Promise.all([api.meta(), api.layers(), api.stations(), api.regions(), api.scenarios()])
      .then(([m, l, s, r, sc]) => {
        setMeta(m);
        setLayers(l);
        setStations(s);
        setRegions(r);
        setScenarios(sc.scenarios);
      })
      .catch((e: unknown) => setError(String(e)));
  }, []);

  useEffect(() => {
    const q = new URLSearchParams(window.location.search);
    q.set("view", view);
    q.set("scenario", scenario);
    q.set("pop", pop);
    window.history.replaceState(null, "", `?${q.toString()}`);
  }, [view, scenario, pop]);

  const needsMap = view === "map" || view === "register" || view === "difference";
  useEffect(() => {
    readiness.needsMap = needsMap;
    readiness.dataLoaded = !!(meta && layers && viewReady);
    readiness.error = error;
  }, [meta, layers, viewReady, needsMap, error]);
  useEffect(() => setViewReady(view === "map"), [view]);

  const sc = scenarios.find((s) => s.id === scenario) ?? null;
  const hypIds = useMemo(() => new Set(sc ? sc.candidates : []), [sc]);
  const diffSet = useMemo(() => new Set(diffIds ?? (sc ? sc.candidates : [])), [diffIds, sc]);
  const visible = useMemo(() => visibleFor(scenario), [scenario]);
  const tradeOffOnly = sc?.trade_off_only ?? false;

  const caption = meta ? `${meta.label}. ${scenarioCaption(scenario, sc)}` : "";

  return (
    <div className="app">
      <header className="header">
        <div className="title">
          <h1>KSA Rail Twin: decision dashboard</h1>
          <div className="subtitle">{meta ? meta.label : ""}</div>
        </div>
        <nav className="tabs" aria-label="views">
          {VIEWS.map((v) => (
            <button key={v.id} className={v.id === view ? "tab active" : "tab"} onClick={() => setView(v.id)}>
              {v.name}
            </button>
          ))}
        </nav>
        <div className="switcher" aria-label="scenario and programme switcher">
          {SWITCHER.map((id) => (
            <button key={id} className={id === scenario ? "chip active" : "chip"} onClick={() => setScenario(id)} title={scenarios.find((s) => s.id === id)?.title ?? id}>
              {id}
              {SHORT_ROLE[id] ? <small> {SHORT_ROLE[id]}</small> : null}
            </button>
          ))}
          <select value={pop} onChange={(e) => setPop(e.target.value as Population)} aria-label="population scenario">
            {(Object.keys(POP_LABEL) as Population[]).map((p) => (
              <option key={p} value={p}>
                {POP_LABEL[p]}
              </option>
            ))}
          </select>
        </div>
        <div className="switcher-note">
          S6-L4 and S6-L5 ({meta?.trade_off_caption ?? "trade-off illustration only"}) and S6-L6 ({meta?.comparison_caption ?? "comparison layout, not the recommended programme"}) appear only in the
          Pareto explorer.
        </div>
      </header>
      {error ? <div className="error">API error: {error}</div> : null}
      <main className={needsMap ? "main with-map" : "main"}>
        {needsMap ? (
          <MapView
            layers={layers}
            stations={stations}
            regions={regions}
            visible={visible}
            hypotheticalIds={view === "difference" ? diffSet : hypIds}
            highlightIds={view === "difference" ? diffSet : undefined}
            register={view === "register" ? registerRows : null}
            caption={caption}
          />
        ) : null}
        <section className="panel">
          {tradeOffOnly ? <div className="caption-warn">{meta?.trade_off_caption}</div> : null}
          {view === "map" ? <ScenarioPanel scenario={sc} meta={meta} pop={pop} /> : null}
          {view === "register" ? <RegisterView onRows={setRegisterRows} onReady={() => setViewReady(true)} /> : null}
          {view === "ranges" ? <RangesView scenario={sc} scenarios={scenarios} pop={pop} meta={meta} onReady={() => setViewReady(true)} /> : null}
          {view === "pareto" ? <ParetoView meta={meta} onReady={() => setViewReady(true)} /> : null}
          {view === "difference" ? <DifferenceView scenario={sc} scenarios={scenarios} pop={pop} meta={meta} onCorridors={setDiffIds} onReady={() => setViewReady(true)} /> : null}
        </section>
      </main>
      <Footer meta={meta} />
    </div>
  );
}

function scenarioCaption(id: string, sc: Scenario | null): string {
  if (id === "S0") return "S0: existing lines only.";
  if (id === "S1") return "S1: existing + committed/under procurement (the baseline).";
  if (sc?.role && id.startsWith("S6")) return `${id} (${sc.role}) over S1.`;
  return `${id}: generated hypothetical corridors of this family over S1.`;
}
