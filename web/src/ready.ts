// Readiness flags for the headless capture script (scripts/screenshot.mjs polls window.__rt).
export const readiness = { dataLoaded: false, mapIdle: true, needsMap: false, error: "" };

declare global {
  interface Window {
    __rt?: { ready: () => boolean; state: () => typeof readiness };
  }
}

window.__rt = {
  ready: () => readiness.dataLoaded && (!readiness.needsMap || readiness.mapIdle),
  state: () => ({ ...readiness }),
};
