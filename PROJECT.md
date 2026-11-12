> **Document version:** PROJECT.md v1.0 (brief v5, 30 Oct 2026, Asia/Riyadh) | Author: Tariq Alturkestani (brief), coordinator (header) | Status: approved brief
> Source: `KSARailTwin/KSA_Rail_Twin_PROMPT.md` v5. This file is the brief for KSA Rail Twin; `CLAUDE.md` holds the working rules. Changes to the brief are made by Tariq only; builders never edit this file.

# KSA Rail Twin: a national, investment-grade feasibility study of a Saudi rail network

## 0. The real goal, who you are and how this works
**The real goal** is not a pretty simulation. It is a **national, investment-grade economic feasibility study**: should Saudi Arabia build a much larger rail network, which corridors, in what order, at what cost, with what long-term benefit, funded and owned by whom, and with what effect on people, culture and work? It must be benchmarked against what France, Japan, Spain, China and other countries actually did. **Simulation is the tool; the decision case is the product.** Building rail costs an astronomical amount, so every recommendation must survive honest cost research, reference-class realism and sensitivity testing.

You are the **supervisor/orchestrator** ("Fable 5"; Tariq's label, map it to an exact model id) of a new open-source project, **KSA Rail Twin**. It extends my TrafficTwin Jeddah project (https://github.com/alturkestani/TrafficTwin, Apache-2.0; local checkout `~/Documents/Projects/TrafficTwin`) from one city to the whole Kingdom.

This uses the same two layers as TrafficTwin. You, the coordinator, run on my Mac. You write the brief and the per-track prompts, create git worktrees, launch **Claude Code** builder runs (`claude -p`; coding on Opus, bulk or light tasks on "Hanko"), monitor their logs, merge, verify and report to me. The builders use the repo's own **subagents** (`.claude/agents/`) and **skills** (`.claude/skills/`). An independent **red-team verifier** must sign off every milestone before it counts as done.

Work in a NEW repo: `~/Documents/Projects/KSA-RailTwin`. Treat `~/Documents/Projects/TrafficTwin` and `~/Documents/Projects/TrafficTwin-publish` as **read-only**. Read them, copy files out of them, or symlink large data from them, but never edit, commit to, or run destructive commands in them.

## 1. Decision questions (national scope throughout)
1. **Network.** Across all 13 regions and every GASTAT governorate, which links, branches, commuter belts and station additions would create the most value? This is the full research: a systematic screening of every city, town and governorate centre, not a hand-picked list. Illustrative gaps include Jeddah–Riyadh, Makkah/Jeddah–Taif, the south (Asir, Jazan, Najran, Al-Baha), the north-west (Tabuk, NEOM, AlUla) and links within the Eastern Province. Illustrative small-town case: Al-Jumum, a planned Landbridge station.
2. **Cost.** What would each option really cost to build, run and renew over its life, including land, financing and a realistic overrun allowance?
3. **Benefit.** What are the long-term (30–60 year) economic, social and environmental benefits, and do they exceed the costs under honest assumptions?
4. **Who pays and who owns.** Public, private, or both? Which delivery and funding model suits each corridor, who carries which risk, and what is the fiscal exposure?
5. **Benchmarks.** What did France, Japan, Spain, Germany, China, South Korea, Italy, Morocco, Turkey, the UAE, Egypt and others do? What worked, what failed, and did intermediate small towns actually gain?
6. **People.** How would rail change commuting, work, women's mobility, family and religious travel, housing and the balance between Riyadh/Jeddah and the regions? Who gains and who loses, by region and income?
7. **Optimisation and phasing.** Which network, technology, service pattern, fares and build sequence give the best balance of NPV, coverage/equity, emissions and fiscal exposure under uncertainty to 2050/2060?

The 30-minute commute test stays as one lens. For towns 40–120 km from each major city, can a train deliver about 30 minutes in-vehicle (and what door to door)? How much car traffic would that remove? For Jeddah, measure it with TrafficTwin itself.

## 2. Non-negotiable rules (put these verbatim into CLAUDE.md and prompts/_common.md)
1. **No fabricated numbers.** Every figure is sourced (URL, publisher, date, access date) or flagged as an assumption in `docs/assumptions.md` (value, range, reason, status) through the `assumptions-register` skill. "Unknown/unverified" is acceptable. A guess presented as fact is a verifier FAIL. This applies equally to costs, benchmarks, survey findings and quotes.
2. **No silent omissions.** Every region and every GASTAT governorate appears in the coverage table, either as screened (with the result) or as excluded (with the reason). Every benchmark country the brief names appears in the benchmark dossier, with its findings or "no reliable data found". A gap is a verifier FAIL.
3. Label every modelled output **"synthetic demand, uncalibrated: scenario comparison, not a forecast"** until calibration says otherwise. Write "in the model, X reduced by", never "will reduce". Cost and benefit figures are always ranges (P10/P50/P90), never single points.
4. Use only public, licence-compatible data (open-source first, rule 12): OSM (ODbL, credited on every map), GASTAT (credited; derived tables marked as derived), SAR/HHR published facts, open population grids (GHSL/WorldPop, checking the licence), and published reports and peer-reviewed literature (cited). No Google, TomTom or HERE traffic, nothing scraped against a site's terms, and no imagery crops committed.
5. Planned lines are **"announced/planned"** with a source and date, never "existing". Keep three layers apart: `existing`, `committed/under procurement`, `hypothetical (ours)`.
6. Every scenario is compared against a matched baseline on the same zones, seed and parameters, with a sensitivity band. Appraisal follows a named standard (section 6d) and states any departures.
7. No real-world action. Builders and the coordinator never `git push`, publish, post, email, contact any agency, company or person, or field a survey. Surveys are **designed only**; humans field them. Do not sign up for, pay for, or send data to any external service (for example a cloud TTS provider) without my approval. Ask first, and use free tiers or trials only once I agree. I publish.
8. Commit nothing under `data/`, `runs/`, `movies/` or imagery, except small licence-compatible tables with a README. No secrets, no absolute home paths.
9. Keep this project personal. It has no content, branding, data or contacts from the author's company. It stays independent and non-partisan: present options and evidence, and do not advocate for any entity.
10. Determinism: every run takes `--seed` and records seed, config hash, data hash and code version.
11. The **verifier** signs off every milestone: tests pass, the README command runs, acceptance criteria are met, every number traces to a source or a `runs/` output, coverage is complete, the assumptions register is complete, and the licence & openness register is complete. An open FAIL means the milestone is not done.
12. **Open-source first, as much as possible: data, models, software and voices.**
   - **Data:** use open and public sources first (section 2a). Proprietary or paid data is allowed only when no open alternative exists. In that case, flag it, explain why, and get my approval before use.
   - **Software:** use open-source tools (section 2a).
   - **AI models inside the pipeline** (extraction, OCR, translation drafts, embeddings, classification, local LLM tasks): prefer open-weights models run locally.
   - **Voices and audio:** open-source TTS run locally comes first. Commercial TTS and a human narrator are fallbacks only.
   - **The orchestrators are the exception.** Claude itself ("Fable 5" supervisor; Opus and "Hanko" coders) stays as my chosen orchestrator and coder.
   - Every dataset, model, tool, voice, font, music track and image goes into the **licence & openness register** (`docs/licences.md` plus `docs/licences.csv`) with these columns: item, version, source URL, licence, open (Y/N), commercial use allowed (Y/N/unclear), attribution required (text), share-alike or other obligations, and where it is used. Before any public or commercial release, check licence compatibility (for example ODbL share-alike on derived databases, non-commercial model licences, CC-BY-NC music). Flag conflicts and do not resolve them silently.
   - **Compute:** prefer local compute on my Mac (Apple M3 Pro, 18 GB RAM, no CUDA; use Metal/MPS or CPU builds). Heavy jobs (large fine-tunes, 4K renders, big LLMs) may later move to sovereign or cloud GPU **only with my approval** (rule 7).

## 2a. Open-source-first toolkit (Claude must verify current availability, versions and licences before use; record each in the licence register)
- **Data:**
  - Maps and networks: OpenStreetMap via Geofabrik (ODbL), OpenRailwayMap, Overture Maps, Natural Earth.
  - Statistics: GASTAT open data, the Saudi Open Data portal (data.gov.sa), World Bank WDI, UN World Population Prospects, OECD/ITF transport statistics.
  - Terrain and population grids: Copernicus DEM / SRTM, GHSL and WorldPop.
  - Transit: GTFS feeds where available (Mobility Database, Transitland).
  - Images: Wikimedia Commons public-domain or CC archival images.
  - Published reports and peer-reviewed literature (cited).
- **Modelling and GIS:** Eclipse SUMO, MATSim (optional), OpenTripPlanner or R5 (`r5py`) for routing and accessibility, OSRM, NetworkX, igraph, OSMnx, GeoPandas, Shapely, PyProj, DuckDB, QGIS.
- **Optimisation and uncertainty:** OR-Tools, PuLP, HiGHS or CBC (siting, MILP); `pymoo` (NSGA-II multi-objective); NumPy/SciPy and PyMC (Monte Carlo and Bayesian calibration).
- **Dashboard:** React, deck.gl, MapLibre and FastAPI (already open, as in TrafficTwin), and kepler.gl.
- **Local AI models:** open-weights models through Ollama, llama.cpp, MLX or vLLM, for example Qwen, Llama, Mistral, and Arabic models such as Jais or ALLaM-family releases **where the licence permits**. Verify which exist, their size against 18 GB RAM, and their licence. Whisper or faster-whisper / whisper.cpp for transcription, alignment and subtitle QA.
- **Voice, audio and video:**
  - Text-to-speech candidates to verify and test on Saudi dialect: Coqui XTTS-v2 (note its CPML non-commercial licence caveat), F5-TTS, Chatterbox (used in TrafficTwin), Piper, Meta MMS-TTS, Fish-Speech, OpenVoice, Kokoro-82M (English, used in TrafficTwin), and any Arabic or Saudi-dialect open models or fine-tunes on Hugging Face.
  - Open speech datasets, only if the licence permits, for evaluation or fine-tuning: Common Voice Arabic, MGB/QASR, the SADA Saudi audio dataset. Fine-tuning an open model on properly licensed Saudi-dialect recordings is an option.
  - Video tools: ffmpeg, Blender, Manim, Remotion (check its licence terms), Kdenlive or Shotcut, and Aegisub for subtitles.
  - Fonts: Noto Sans/Naskh Arabic, IBM Plex Sans Arabic, Amiri.
  - Music: Creative Commons music (e.g. Free Music Archive) or royalty-free libraries, with each licence checked; avoid NC and ND licences if any commercial use is possible.

## 3. What to reuse from TrafficTwin (read these first, then summarise each in two lines for me)
- **Conventions:** `CLAUDE.md` (Python 3.12 via uv, ruff, pytest, a CLI for every module, YAML for every behavioural constant, background runs with logs under `logs/`), `PROJECT.md` (brief structure), `prompts/_common.md` and `prompts/_resume.md` (track contract: `<LABEL>: done` / `<LABEL>: blocked - <reason>`), `orchestrate.sh` and `run_track.sh` (worktrees, retries, 15-minute sleep on rate limits).
- **Agents and skills:** `.claude/agents/` (`data-scout`, `demand-modeler`, `sumo-engineer`, `viewer-engineer`, `strategist-engineer`, `verifier`) and `.claude/skills/` (`assumptions-register`, `milestone-handoff`, `policy-yaml`, `sumo-run`). Copy `assumptions-register`, `milestone-handoff` and `verifier` with minimal changes. Do not weaken them.
- **Methods:** `docs/loop-mode-choice.md` (binary logit with a coefficient sweep; generalise it to car/rail/air/bus), `docs/population.md` (synthetic population from GASTAT Census 2022), `docs/data-sources.md` (source-table format), `docs/policies.md` (matched-control reporting), `docs/movies.md` and `docs/movies-arabic.md` (offline English/Arabic narrated films).
- **Data:** `data/osm/gcc-states-latest.osm.pbf` (Geofabrik GCC extract, 243 MB). Symlink it, don't re-download. Also the Jeddah network `data/jeddah/jeddah.v2.net.xml` and its 10 % weekday baseline (for the Jeddah decongestion coupling).
- **Presentation:** `web/` (Vite + React + deck.gl + MapLibre, no API keys) and the FastAPI `api/` pattern.
- **Budget reference:** Jeddah took 27 Claude Code runs, about 41 agent-hours and about USD 420 (`Claude outputs/TrafficTwin-Riyadh-prompt.md`). This study has far more research, so estimate it before starting and log the actual cost per run in `docs/cost-log.md`.

National scale is not SUMO scale. Use a graph/skim model nationally, with open tools only (section 2a): road skims from the OSM GCC extract via OSRM, r5py/R5 or OpenTripPlanner, and NetworkX/igraph/OSMnx; rail from a line/timetable YAML. Use SUMO only where TrafficTwin has a city model (Jeddah), to measure decongestion. Optionally add SUMO rail for headway and capacity checks.

## 4. Grounding facts (starting points only; re-verify each and record the access date)
| Item | Starting fact | Source to re-verify |
|---|---|---|
| Haramain HSR | about 450 km (453 km), 300 km/h, stations Makkah (Rusaifah), Jeddah (Sulaymaniyah), KAIA, KAEC (Rabigh), Madinah. Distances 0/77/17/94/261 km. Makkah–Jeddah is 77 km in about 43 min. Cost, contract history (civil works packages; Spanish consortium for systems, operation and trains) and ridership against forecast are **to be researched** | sar.hhr.sa; grupo.renfe.com Haramain page; Wikipedia HHR (find primary sources) |
| North line (SAR) | Riyadh–Majmaah–Qassim–Hail–Jouf–Qurayyat–Al Haditha passenger line, about 1,250 km; north freight about 1,550 km. Cost to be researched | sar.com.sa/about-sar/railnetwork |
| East line (SAR) | Riyadh–Al-Kharj–Hofuf–Abqaiq–Dammam passenger line (SAR quotes 733 km double track) | same |
| Saudi Landbridge (planned) | new Riyadh–Jeddah line of about 950 km (MEED also says about 900 km), mixed freight/passenger up to about 220–250 km/h, more than 1,500 km of new track in total. Reported cost about SR100 bn (USD 26.6 bn, MEED quoting SAR's CEO); ENR also cites "USD 7 bn". **The two figures conflict: reconcile them or flag the conflict.** PPP talks with a Chinese consortium ended; SAR now delivers in phases, targeting 2034. Planned stations include "Jamuma", which is **Al-Jumum (الجموم), confirmed by me (Tariq)**; still cite meedprojects.com pid=114639 and locate the exact planned site | MEED (Jan and Jul 2026), ENR (Jun 2026), meedprojects.com, Wikipedia |
| GCC railway (planned) | Saudi section about 672 km, Al-Khafji–Dammam–Al-Batha, design tenders in 2026, 220 km/h passenger | MEED (Sep/Oct 2026), Railway Journal |
| Riyadh Metro | 6 lines, 176 km, 85 stations, phased opening Dec 2024 to Jan 2025. Cost to be researched (ENR headline "USD 25 B"; verify) | rcrc.gov.sa, spa.gov.sa, ENR |
| Rail ridership | GASTAT Railway Transport Statistics 2023: 30.3 M rail passengers; intercity passenger-km 2,618 M; HHR about 6.97 M (2023, per Wikipedia, which needs a primary source) | stats.gov.sa |
| Al-Jumum (illustrative) | Makkah region, population 89,575 (Census 2022); about 25 km from Makkah and 72 km from Jeddah by expressway; not on the Haramain alignment; a planned Landbridge station | makkah.gov.sa/aljmom; citypopulation.de; ar.wikipedia |
| City populations (Census 2022, city proper) | Riyadh 6.92 M, Jeddah 3.71 M, Makkah 2.39 M, Madinah 1.41 M, Dammam 1.39 M, Tabuk 0.59 M, Buraidah 0.57 M, Taif 0.56 M, Khamis Mushait 0.54 M, Abha 0.33 M (secondary aggregator; **replace with the GASTAT primary table**) | portal.saudicensus.sa; stats.gov.sa |

Reality check: Haramain averages about 107 km/h on Makkah–Jeddah. Test every 30-minute claim; do not assume it.

## 5. Workstreams (research and modelling run in parallel; each has an owner agent, outputs and acceptance criteria)

### W1. National data build and network (owners: `rail-data-scout`, `gis-network-engineer`)
- **Rail layers:** OSM rail relations plus SAR/HHR published lines, stations, timetables and fares (record the dates sampled), and planned lines digitised with source and uncertainty.
- **Settlement universe:** GASTAT's official list of regions and governorates, with Census 2022 population, plus GASTAT locality tables, OSM places and GHSL/WorldPop grids for towns that GASTAT does not tabulate.
- **Economic roles:** ports (Mawani), industrial cities (MODON, the Royal Commission for Jubail and Yanbu), mining (Ma'aden), tourism and heritage, Hajj/Umrah, airports (GACA), universities, and giga-projects (NEOM, Red Sea Global, AlUla, Qiddiya, Diriyah, ROSHN). Each needs a source.
- **Economy and demand data:** Labour Force Survey, regional GDP, VIIRS night lights (as a flagged proxy), real-estate price indicators (MoJ/REGA, `unverified` until checked), GASTAT/GACA air pairs, TGA/SAPTCO bus, Hajj/Umrah statistics, and any open road counts (say so if none exist).
- **Road skims:** OSRM or r5py on the GCC PBF; TrafficTwin peak times for Jeddah.

### W2. Kingdom-wide candidate screening (owners: 13 × `region-scout`, `screening-analyst`)
1. **Per-region sweep:** one `region-scout` per region (Riyadh, Makkah, Madinah, Eastern Province, Qassim, Asir, Tabuk, Hail, Northern Borders, Jazan, Najran, Al-Baha, Al-Jouf), run in parallel batches. Each lists every governorate, and every town at or above the population threshold.
2. **Candidate town register** (`cities/ksa/candidates.parquet` plus `docs/candidates.md`). Fields:
   - name in Arabic and English, region, governorate, OSM id, coordinates;
   - population with source, year and type (official/derived/grid), included at ≥10k with a ≥5k sensitivity tag;
   - distance and road time to the nearest existing line, the nearest committed line and its planned station, and the nearest metro;
   - economic roles, each sourced; terrain class.
3. **Screening funnel** (`docs/screening.md`): all settlements → long list (transparent filters) → short list (weighted multi-criteria score, weights explicit and swept ±25 %, rank stability reported). Thresholds and weights are registered assumptions that I approve.
4. **Corridor-family generation:** trunk gaps, branches/spurs to economic nodes, commuter belts per metro, and station additions on existing and committed lines. These are generated from the short list, never from a hard-coded town list.
5. **Coverage audit:** `docs/coverage.md` has one row per GASTAT governorate and must reconcile to GASTAT's governorate count.

### W3. Cost research (owner: `cost-estimator`)
- **Cost register** (`cities/ksa/costs/cost_register.yaml` plus `docs/costs.md`). Every item has a low/central/high value, unit, currency and price year, source, and status (sourced/derived/assumed). Inflation and currency conversion follow a documented index.
- **Bottom-up capex** per km and per item, by type and terrain:
  - Line type: HSR (≥250 km/h), conventional passenger, mixed freight/passenger, commuter, upgrade of an existing line.
  - Terrain: flat desert, sand dunes (sand mitigation and maintenance), sabkha, escarpment/mountain (the Sarawat/Asir and Hejaz ranges).
  - Structures: tunnels and viaducts as shares of alignment.
  - Systems: stations (by class), depots, rolling stock, signalling (ERTMS level), electrification versus diesel/hybrid/hydrogen, and power supply.
  - Land and utilities, plus design, project management and contingency.
- **Top-down capex:** cost per km from completed projects worldwide (from W5) and KSA data points: Haramain HSR, SAR North and East lines, the Riyadh Metro, and Landbridge estimates. Each must be clearly cited. Reconcile conflicts and flag unknowns, and never fill a gap with a guess.
- **Opex and lifecycle:** train operation, energy, maintenance of way (including sand), staffing (Saudisation share), and renewals over 30–60 years.
- **Financing cost:** sovereign borrowing, PIF, project finance and export-credit structures; interest during construction.
- **Reference-class forecasting:** apply Flyvbjerg-style optimism-bias uplifts. Use the UK Green Book supplementary guidance on optimism bias and the published reference-class literature for rail capex, schedule and ridership. Report P50 and P80 budgets and schedule-overrun distributions.
- **Acceptance:** every corridor family has a capex/opex range traceable to the register, and every KSA data point is cited or marked unknown.

### W4. Long-term benefits and CBA (owner: `economist`)
- **Standards:** UK HM Treasury Green Book and DfT TAG (including A2.4 wider economic impacts), the EU Guide to Cost-Benefit Analysis of Investment Projects (2014), World Bank transport appraisal guidance, and SAR/MEP or other Saudi guidance if any is published. State every departure from them.
- **Horizon and discounting:** 30, 40 and 60 years with residual value. Discount-rate sensitivity that includes a social rate and a commercial/financial rate, plus declining long-term rates (as in the Green Book).
- **Benefits:** travel-time savings (by purpose; KSA value-of-time as an assumption), reliability, safety (road crashes avoided), emissions and air quality, road decongestion (Jeddah via TrafficTwin; elsewhere VKT-based), freight shift road→rail, agglomeration and wider economic impacts (with no double counting), land value uplift and capture potential, tourism and Hajj/Umrah capacity, and regional development and Vision 2030 alignment (a qualitative scorecard, not monetised unless sourced).
- **Outputs:** NPV, BCR (with and without wider impacts), economic IRR and financial IRR, payback, fiscal cost to the state, Monte Carlo (P10/P50/P90; NumPy/PyMC), tornado charts, and switching values ("demand must be X % of forecast for BCR = 1").

### W5. Global benchmarks (owner: `benchmarks-researcher`)
- **Dossier per country/system** (`docs/benchmarks/<country>.md`):
  - France (TGV/LGV; SNCF, SNCF Réseau)
  - Japan (Shinkansen; JR companies)
  - Spain (AVE, ADIF)
  - Germany (ICE)
  - China (CR HSR)
  - South Korea (KTX)
  - Italy (Frecciarossa, Italo open access)
  - Morocco (Al Boraq)
  - Turkey (YHT)
  - UAE (Etihad Rail)
  - Egypt (HSR under construction)
  - Cautionary reference class: California HSR, UK HS2, and others found.
- **Metrics:** cost/km (price-year-adjusted), ridership against forecast, farebox recovery / operating ratio, population-density and city-size thresholds, the distance sweet spot (test the commonly cited roughly 200–800 km HSR competitiveness band against air and car, with sources), station spacing, timetable and stopping patterns, overruns, and the delivery model used.
- **Small-town evidence:** did intermediate stations gain? Cover Shinkansen intermediate stations, TGV stations outside towns (the "gare des betteraves" critique, e.g. some TGV stations in the fields) and AVE intermediate stops. Summarise the empirical studies, and say clearly where the evidence is mixed or negative.
- **Population-growth peers:** how countries with growing populations and good rail (and countries with shrinking ones) planned networks and housing around them.

### W6. Funding, ownership and delivery models (owner: `funding-ppp-analyst`)
- **Options:**
  - fully public (state budget, PIF, SAR);
  - public with private O&M;
  - PPP variants: DBFOM, DBFM, availability payment versus demand risk, and vertical separation (infrastructure versus operations) versus integrated;
  - private concession;
  - land value capture: station-area development, betterment levies, tax increment.
- **Case studies:** the Japan rail+real-estate model (JR East, private railways such as Tokyu), Hong Kong MTR rail+property, France SNCF Réseau and LGV concessions (SEA Tours–Bordeaux, LISEA), Spain ADIF/AVE, China CR and local-government financing, Morocco Al Boraq financing, and the Haramain contracts and consortium history.
- **Saudi frame:** the National Center for Privatization (NCP) PPP law and framework, PIF's role, SAR's mandate, and the Landbridge PPP history. Cite everything, and state where the law or practice is unclear.
- **Outputs:** a recommended model per corridor family, a risk-allocation matrix (construction, demand, revenue, operations, financing, land, regulatory/force majeure), the fiscal exposure (contingent liabilities, availability payments as a share of budget) and the value-for-money logic.

### W7. People, culture and work (owner: `socio-culture-analyst`)
- **Topics:**
  - commuting behaviour and willingness to travel in KSA;
  - heat and car culture, and first/last mile in summer;
  - women's mobility and labour-force participation since 2018 (sourced trends);
  - family/tribal ties and weekend visits, weekend, Eid and religious travel (Friday, Ramadan, Hajj/Umrah);
  - remote and hybrid work;
  - housing affordability and decentralisation away from Riyadh/Jeddah;
  - regional jobs and Saudisation;
  - displacement and land acquisition, heritage sites and route sensitivity.
- **Equity:** distributional analysis by region and income band. Who gains, who pays, and who is left out (towns with no station, freight-only corridors).
- **Survey design (design only, never fielded by Claude):** a stated-preference / discrete-choice survey (mode, time, fare, access, comfort, women-only or family carriages, prayer facilities), with the sample design by region, Arabic and English instruments, an ethics/consent note and an analysis plan. Mark all coefficients "literature-based until survey results exist".

### W8. Demand, population growth and simulation (owners: `demand-modeler`, `mode-choice-modeler`, `sim-engineer`)
- **Population scenarios to 2050/2060:** GASTAT projections if published, UN World Population Prospects (latest revision) low/medium/high, urbanisation trends, and Vision 2030 targets. Giga-projects (NEOM, Red Sea, Qiddiya, AlUla, Diriyah, etc.) are demand add-on scenarios with explicit uncertainty (announced versus delivered).
- **Demand:** zones at governorate level and finer around metros; doubly-constrained gravity by purpose (commute, business, leisure/VFR, pilgrimage, tourism); multinomial logit car/rail/air/bus extended from `docs/loop-mode-choice.md`; freight OD where data allows; calibration to observed rail, air and bus totals.
- **Network model:** a running-time model (acceleration–cruise–brake plus dwell, giving an explicit minute cost per stop), commute-shed isochrones (30/45/60 min) for every metro, and Jeddah decongestion through TrafficTwin matched-control runs (VHT, delay, teleport share, seed band).

### W9. Optimisation (owner: `optimizer`)
- **Multi-objective:** maximise NPV/BCR, coverage/equity (population and jobs reached, regional balance), emissions reduction; minimise fiscal exposure and risk.
- **Decision variables:**
  - which corridors to build, and their alignment options;
  - station siting (p-median / coverage with a through-passenger time penalty);
  - technology per corridor: HSR, conventional, upgrade or mixed freight/passenger;
  - service and stopping patterns (express, skip-stop, all-stop), frequencies, and fares.
- **Method:** a Pareto front (e.g. NSGA-II via `pymoo`, or epsilon-constraint with OR-Tools/HiGHS/CBC; justify the choice), with explicit trade-off charts.
- **Sequencing:** phasing over time as a **real-options** problem (stage-gates; build, expand or defer triggered by observed demand and population), evaluated under the W8 scenarios and W3/W4 uncertainty.
- **Outputs:** Pareto sets per budget envelope, a recommended phased programme with robustness (how often it stays near-optimal across Monte Carlo draws), and the dominated options explained.

### W10. Documentary film (owners: `documentary-director`, `motion-graphics`, `voice-audio`, `subtitles`, `film-editor`)
The study ends with a documentary-style film that tells the story honestly, built from the twin's real outputs.
- **Two cuts, each about 8–12 min, plus a 60–90 s social trailer for each:**
  - **Arabic cut:** narrated in an authentic **Saudi dialect**, with Arabic subtitles and optional English subtitles.
  - **English cut:** English narration and English subtitles, with optional Arabic subtitles.
- **Choosing the dialect:** research and recommend a register, for example a "white"/neutral educated Saudi register close to Najdi, a Hijazi register, or a mix (e.g. a Najdi narrator with Hijazi voices for western-region segments). Decide on these criteria:
  - intelligibility across all regions;
  - fit with the documentary tone;
  - what Saudi broadcast documentaries actually use (cite examples);
  - availability of a good voice.
  Present the choice with reasons. **A human native Saudi speaker must review the Arabic script and audio before any release.**
- **The Arabic script is written natively in Saudi dialect, not translated from the English.** The two cuts share facts and structure but may differ in phrasing.
- **Narrative arc** (all facts researched and cited; dates below are to verify, not given):
  1. History: the Hejaz Railway (opened 1908 to Madinah) and its fate; the Dammam–Riyadh line (1951); the SAR north line; the Haramain HSR (2018); the Riyadh Metro; the Landbridge plans.
  2. Today's gaps.
  3. Global lessons: France's TGV, Japan's Shinkansen, Spain's AVE, from the W5 dossiers.
  4. The simulated future network, as maps and animations from the twin's actual outputs.
  5. Economic benefits from the CBA (jobs, GDP, time savings), always as ranges, never point claims.
  6. Social benefits: small towns, commuting, women's mobility, family and Hajj/Umrah travel, emissions.
  7. Honest risks and costs, including overruns and fiscal exposure.
  8. A closing vision tied to Vision 2030, framed as possibility, not promise.
- **Fact rule:** every factual claim and number in the narration traces to the report, the cost register, the assumptions register or a cited historical source. The script carries citation footnotes per line. Uncertain figures are spoken as ranges. There are no fabricated or paraphrased-as-real quotes; quote only verifiable published statements, with the source. The `red-team-verifier` audits the script in both languages and checks the Arabic and English figures digit by digit.
- **Voice:**
  - **Open-source first (rule 12).** Test the open, locally run TTS candidates from section 2a on the same Saudi-dialect paragraph. Record the licence of each and whether commercial use is allowed, and score each on dialect authenticity, naturalness, pronunciation of place names and stability. Fine-tuning an open model on licensed Saudi-dialect recordings is an option.
  - **Fallbacks only:** commercial TTS (for example ElevenLabs, Azure Neural `ar-SA`, Google, AWS, regional Arabic providers) and a human Saudi voice-over artist (cost and timeline range, sourced). Present them side by side with the open options at CP8. Any use needs my approval (rule 7).
  - **Verify each option's current offering and licence yourself.** Do not assert a capability from memory.
  - Use Whisper (open) to transcribe each sample back for an intelligibility check and to align the subtitles.
  - Flag clearly that true dialect quality usually needs a human narrator, or at least native review.
  - The English cut uses an open voice first (for example TrafficTwin's offline Kokoro-82M), or the best open option you find.
- **Visuals:**
  - Prefer real data-driven animation built with open tools: deck.gl/kepler.gl captures of the twin, Manim or Remotion (check its licence) for charts and maps, Blender optional, and ffmpeg/Kdenlive/Shotcut for the edit. Use open Arabic fonts (Noto Naskh/Sans Arabic, IBM Plex Sans Arabic, Amiri).
  - Archival imagery only when public domain or licensed, verified, and logged (e.g. Hejaz Railway photos from archives with clear rights).
  - Any AI-generated footage is minimal and labelled on screen.
  - No logos of SAR, PIF or other entities that could imply endorsement.
- **Music:** open/CC or royalty-free only (e.g. Free Music Archive CC tracks, with licences checked; avoid NC/ND if any commercial use is possible), recorded in the rights log and the licence register.
- **Rights log:** `film/rights_log.csv` records every image, clip, track and voice with its source, licence, attribution and proof link.
- **Outputs:**
  - MP4 1080p for each cut and trailer, plus a 4K master if feasible on this Mac;
  - separate SRT and VTT files per language, with right-to-left Arabic rendered correctly and timing checked;
  - a script PDF with citations in each language;
  - the credits and rights log.

## 6. Scenarios (`scenarios/*.yaml`, TrafficTwin `policy-yaml` style)
- **S0, today:** existing lines including the Riyadh Metro.
- **S1, committed:** S0 plus the Landbridge (with its planned stations), the Riyadh Rail Link and the Saudi GCC section.
- **S2–S5, generated families** from W2: trunk gaps (illustration: Jeddah–Riyadh high speed versus the S1 mixed line), branches and spurs to economic nodes, commuter belts per metro, and station additions.
- **S6, optimised programmes** from W9, per budget envelope and delivery model.

Every scenario is run against the W8 population and giga-project scenarios, and costed with W3 and W4 ranges.

## 7. Agent topology (`.claude/agents/`; frontmatter `name`, `description`, `tools`, `model`)
| Agent | Model | Owns |
|---|---|---|
| **coordinator / supervisor** (you, in Cowork) | "Fable 5" (Tariq's label; map it to a model id) | plan, tracks, merges, cost log, checkpoints, reports to me |
| `rail-data-scout` | "Hanko" for bulk, Opus for judgement | W1 sources, grounding verification, planned station sites |
| `region-scout` × 13 (one per region, run in parallel batches) | "Hanko" for listing and fetching, Opus for ambiguous cases | W2 region registers |
| `screening-analyst` | Opus | W2 register merge, funnel, corridor families, coverage table |
| `gis-network-engineer` | Opus | W1 graphs, skims, distance fields, alignments |
| `cost-estimator` | Opus | W3 cost register, bottom-up and top-down estimates, reference-class uplifts |
| `economist` | Opus | W4 CBA, discounting, wider impacts, Monte Carlo, switching values |
| `benchmarks-researcher` | "Hanko" for collection, Opus for synthesis | W5 country dossiers, small-town evidence |
| `funding-ppp-analyst` | Opus | W6 delivery models, risk matrix, fiscal exposure |
| `socio-culture-analyst` | Opus | W7 social analysis, equity, survey design |
| `demand-modeler` and `mode-choice-modeler` | Opus | W8 population scenarios, gravity, logit, calibration |
| `sim-engineer` | Opus | W8 running times, isochrones, TrafficTwin Jeddah coupling, optional SUMO rail |
| `optimizer` | Opus | W9 Pareto, siting, real-options sequencing |
| `viz-engineer` | Opus, or "Hanko" for boilerplate | decision dashboard (`web/`, `api/`) |
| `report-writer` | Opus | feasibility report, policy brief, executive summaries in Arabic and English, deck-ready figures |
| `documentary-director` (scriptwriter) | Opus | W10 bilingual script; writes Arabic natively in Saudi dialect and English separately; narrative arc, citations per line, dialect recommendation |
| `motion-graphics` (storyboard) | Opus, or "Hanko" for batch renders | W10 storyboard and shot list; map animations and charts rendered from simulation outputs (deck.gl/kepler.gl captures, Manim/Remotion, Blender optional) |
| `voice-audio` | Opus | W10 TTS and voice research, test samples, shortlist versus a human artist, final narration, music bed, loudness |
| `subtitles` | "Hanko", with Opus review | W10 SRT/VTT per language, RTL correctness, line length and timing |
| `film-editor` (assembly) | Opus | W10 ffmpeg assembly pipeline, cuts, trailers, 1080p and 4K masters, credits, rights log |
| `red-team-verifier` | the strongest model, not the one that wrote the work | reads only. Audits: sources and number tracing (including every line of the film script in both languages, and the film rights log); the **licence & openness register** (every dataset, model, tool, voice, font, track and image listed; licence compatibility checked for public and commercial release; any proprietary item has my recorded approval); coverage (13/13 regions, every governorate, every named benchmark country); a 10 % random spot-check of register, cost and benchmark rows; double counting in the CBA; planned lines shown as existing; unflagged assumptions; and advocacy creeping into the text. Writes PASS/FAIL with evidence and does not fix |

Handoff contract: every handoff is a file (YAML/Parquet/GeoJSON/Markdown plus a `docs/status/<track>.md` entry). Nobody passes numbers in chat.

**Skills** (`.claude/skills/<name>/SKILL.md`):
- `region-sweep`, `screening-funnel`, `corridor-generator`
- `reference-class-forecasting` (uplift tables, P50/P80, sources)
- `cost-register` (schema, price-year and currency normalisation)
- `cba-appraisal` (standards, discounting, wider impacts without double counting, Monte Carlo, switching values)
- `ppp-structuring` (model options, risk matrix, fiscal exposure)
- `benchmark-dossier` (template, metrics, price-year adjustment, evidence grading)
- `survey-design` (SP/DCE design, Arabic/English instruments, ethics, design only)
- `pareto-optimizer` (objectives, NSGA-II/epsilon, real-options sequencing)
- `documentary-script` (narrative arc, a citation footnote per line, ranges not points, native Saudi-dialect writing rules, no fabricated quotes)
- `motion-maps` (rendering map animations and charts from run outputs, style guide, captions)
- `voiceover-tts` (provider verification, sample protocol, dialect review, loudness target)
- `subtitles-srt` (SRT/VTT, RTL Arabic, timing and reading speed)
- `osm-ksa-rail-network`, `line-yaml`, `gravity-calibration`, `isochrone-commute`, `scenario-yaml`, `source-citation`
- `licence-register` (how to record and check licences and commercial-use and attribution obligations; the open-source-first decision rule; the approval flag for proprietary items)
- `local-models` (running open-weights LLMs, Whisper and TTS locally on Apple silicon: Ollama/llama.cpp/MLX, memory limits, and when to ask for GPU)
- Copied from TrafficTwin: `assumptions-register`, `milestone-handoff`

## 8. Repository layout
```
KSA-RailTwin/
  CLAUDE.md  PROJECT.md  README.md  NOTICE  LICENSE (Apache-2.0)  pyproject.toml (uv, py3.12)
  .claude/agents/  .claude/skills/  prompts/ (_common.md, _resume.md, R0..R9.md, REGION_<name>.md)
  orchestrate.sh  run_track.sh  Makefile
  rail/ network/ screening/ costs/ demand/ modechoice/ access/ economics/ funding/ optimise/ coupling/ common/
  scenarios/  cities/ksa/ (regions/, candidates.parquet, costs/, zones, lines/*.yaml, population/, sources.yaml, assumptions/*.yaml)
  data/ (gitignored)  runs/ (gitignored)
  web/  api/  film/ (script/, storyboard/, subs/, rights_log.csv; renders/ and audio/ gitignored)
  docs/ (STATUS.md, assumptions.md, data-sources.md, licences.md, licences.csv, coverage.md, screening.md, costs.md, cba.md,
         funding.md, social.md, survey/, benchmarks/, regions/, cost-log.md, status/, report/)
  tests/ (tiny fixtures: 1 corridor, 6 zones, 1 mini-region register, 1 cost register, 1 CBA case; run in seconds)
```

## 9. Milestones (research runs early, in parallel with the data build; each ends with the verifier's PASS, `milestone-handoff`, and `R<n>: done`)
- **R0, skeleton and reuse audit:** repo, CI, rules, agents and skills; `docs/reuse-from-traffictwin.md`.
- **R1, parallel foundations** (four tracks in worktrees):
  - **R1a** national data build and network (W1).
  - **R1b** benchmark dossiers (W5).
  - **R1c** cost register v1 with KSA data points and reference-class uplifts (W3).
  - **R1d** funding/PPP landscape and the Saudi legal frame (W6), plus the social and culture literature review and survey draft (W7).
- **R2, national screening (W2):** 13 region-scouts, register, funnel, corridor families, coverage reconciled to GASTAT.
- **R3, demand and population scenarios (W8):** zones, gravity, logit, calibration, 2050/2060 scenarios, giga-project add-ons.
- **R4, network evaluation:** running times, isochrones and the 30-minute test for every metro, Jeddah decongestion coupling, corridor costs from the register.
- **R5, CBA (W4):** NPV/BCR/EIRR/FIRR, Monte Carlo and switching values for every corridor family.
- **R6, optimisation and phasing (W9):** Pareto fronts, real-options sequencing, robustness.
- **R7, delivery model per corridor (W6 final):** risk matrices, fiscal exposure, value for money.
- **R8, final deliverables:**
  - an **investment-grade feasibility report** (methods, results with ranges, benchmarks, risks, a per-region annex, a full source and assumption appendix);
  - a **decision dashboard** (national map, register and funnel filters, scenario/programme switcher, Pareto explorer, cost/benefit ranges, difference mode);
  - a **policy brief** (4–6 pages);
  - an **executive summary in Arabic and English**, with identical figures checked digit by digit;
  - deck-ready figures;
  - the **licence & openness register** (`docs/licences.md` and `.csv`), with a release-compatibility note;
  - the documentary film (R10).
- **R9, release prep:** README, credits, good-first issues. I publish, not you.
- **R10, documentary film (W10):**
  - research the dialect and voice options and produce test samples;
  - write the bilingual script with citations;
  - build the storyboard;
  - **stop at CP8**;
  - after approval, render the narration, motion graphics and subtitles, and assemble both cuts and both trailers;
  - the verifier audits the script, figures and rights log;
  - a human native Saudi review of the Arabic cut;
  - **stop at CP9**.
  Acceptance: every narrated number traces to a source or register entry, the rights log is complete, subtitles pass RTL and timing checks, and the native review is recorded.

Run at most three or four Claude Code builders at once on this 18 GB Mac (research tracks are light, compute tracks heavy). Before any run expected to take more than 90 minutes, record the estimate and give me a smaller-sample result first.

## 10. First session: what to do now, and where to stop and ask me
1. Read TrafficTwin as listed in section 3 (read-only) and give me the two-line summaries.
2. Create `~/Documents/Projects/KSA-RailTwin` with R0 done: skeleton, CLAUDE.md with the section 2 rules verbatim, all agents and skills, and the prompts. Map "Fable 5", Opus and "Hanko" to exact model ids and write them into the agent files. Start `docs/licences.md` with every tool and dataset chosen so far, and check which open-weights models and open TTS run on this Mac.
3. Have `rail-data-scout` run a **one-hour** verification pass: the section 4 table (including the Landbridge cost conflict), GASTAT's official region and governorate list with the count, and the best population tables. Write `docs/data-sources.md` v0.
4. Run a **national pilot**:
   - a coarse sweep of **all 13 regions**: every governorate centre plus the towns above a high cut-off (e.g. ≥50k);
   - plus a **stratified national sample** of smaller towns (several per region, mixed by distance to existing lines and by economic role), to test the `region-sweep` schema, the funnel filters and the weights;
   - a one-page **benchmark and cost scoping note**: which countries and KSA cost data points are reachable, and the gaps.
   Show me the pilot register, the draft coverage table and the funnel counts.
5. Write `docs/plan.md` with:
   - the proposed **screening criteria, thresholds and scoring weights** (10k plus the 5k sensitivity, the corridor distance, the commute band, the economic-role list, the weight sweep ranges);
   - the appraisal standard and discount-rate set;
   - the cost-register schema;
   - the benchmark country list;
   - the workstream and track plan for R1–R9, with how the region-scouts are batched;
   - estimated agent-hours and USD cost;
   - the open questions.
6. **CHECKPOINT 1, stop and ask me:** approve the screening criteria, thresholds and weights based on the national pilot (not a town list), the appraisal standard and discount rates, the benchmark list, the budget, and whether you may run unattended overnight.

Later checkpoints:
- **CP2** after R1 (data, benchmarks, cost register v1, funding landscape)
- **CP3** after R2 (funnel, short list, corridor families, coverage)
- **CP4** after R3 (calibration and population scenarios, before any economics)
- **CP5** after R6 (Pareto and phasing, before the delivery-model recommendations)
- **CP6** before the report or brief goes to anyone
- **CP7** before anything is published
- **CP8, film pre-render:** I approve the script in both languages, the storyboard, the dialect choice and the voice choice before any rendering. The tested open-source voices are shown first, side by side with the commercial and human-narrator fallbacks, with their licences
- **CP9, film final review:** I review both cuts, both trailers, the subtitles, the rights log and the native-speaker review before any public release

Between checkpoints, decide, record the decision in `docs/STATUS.md` and continue. Only wake me for a checkpoint or a blocker.

Report format to me: what was built; verified numbers, each with its run id, seed or source; what is assumed; what is blocked; the cost so far; and the decisions I need to make.
