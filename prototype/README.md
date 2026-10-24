# Parvius (standalone prototype)

`parvius.html` is a single self-contained file. Open it in any browser; no server or internet needed.

Parvius is Lone Mesa's operations console for the gate-first spare-parts program. It has three pages, chosen from the left sidebar:

- **Overview** (opens first): what's going on, in plain English, for whichever 2025 day you're replaying.
  - a headline (sites on hold, machines down, machines waiting for parts)
  - what's broken right now
  - what might break next, with the backtest caveat
  - what should happen next, ordered by payoff
  - where the 2025 hours went
  - a "what happened" feed of the last 14 days
- **Work**: who needs to do what.
  - **Do now**: safety checks to verify, and readiness flags at cleared sites.
  - **Blocked by a safety hold**: flags that wait on a site's checks, with a link to those checks.
  - **Done**: verified checks and planner decisions.
  - You verify checks and decide on flags right on the cards. "Who's on it" and "Progress" sit alongside.
- **Map**: the 3D command center.
  - **Story mode**: six beats (Problem → Why parts → The gate → Unlock it → Payoff → Plan) that fly the camera. In "Unlock it" you verify Arroyo's checks yourself and watch the cage drop and the prize meter count up.
  - **Explore mode**: click any site or asset to open the inspector.
  - **Site trends** (`#/site/S04`): double-click a site, or use the button in its inspector, to open a full-page dashboard for that site. It shows vibration, downtime by stage and parts-wait by day, week or month; this month against last; any two periods side by side; causes; per-asset stats; and a sortable list of stops. It uses observed 2025 data only. There is one year of data, so there is no year-on-year view. Spare-parts stock has no history, so parts are measured by time spent waiting for them.
  - **Briefings**: Why, Business case (rollout sliders reproduce 666 h year 1 and 968 h steady state at month 3 / base), Safety & guardrails (self-test), Plan & KPIs.

Everywhere:
- **Acting as** in the sidebar (HSE supervisor / Planner / Manager) enforces the gate rules from `docs/phase-5-product-design.md`. There is no override on HOLD; a locked action offers a one-click role switch instead.
- The **date chip** in the top bar steps through 2025 or replays it. Every page is "as of" that day, using only readings received by then.
- The **prize meter** fills as sites are cleared.
- The **decision log** is under the bell: append-only, with JSON export and demo reset.

Keyboard: `Ctrl/⌘ K` or `/` opens the command bar, `1`–`4` open the briefings, and `Esc` closes things. On the Map page, `→`/`Space` goes to the next story beat, `←` goes back, `P` turns on presenter mode and `N` turns on Parvis narration.

Data is embedded from `data/processed/*.csv` at build time (readings, events, HSE, sites, assets). If the processed data changes, the embedded numbers will not update automatically.

Standalone demo aid, independent of the Streamlit app.

## Parvis voice agent

Parvis lives in the `Ctrl/⌘ K` command bar at the top. Type or speak a question, or jump straight to a page, site, asset, briefing or action.

Answers are computed from the embedded data and Solutions rules (no LLM, no API key). They're tailored to a plant manager, parts planner, HSE supervisor or executive, and they move the 3D camera and rollout sliders. Parvis never lifts a hold, verifies a closure or approves work.

- **Speech in:** Whisper (`whisper-tiny.en`, about 40 MB) via transformers.js. While it loads, Chrome/Edge/Safari built-in recognition is used. Recording stops automatically when you pause; failures are explained in the chat.
- **Speech out:** Kokoro HD British male voices (George, Lewis, Daniel, Fable), about 330 MB. Needs WebGPU (Chrome/Edge). Falls back to the best British browser voice.
- Click "Prepare voices (~370 MB)" while online before the demo; the browser then caches the models.
- To use the mic, serve it: run `python3 -m http.server 8000` in this folder and open `http://localhost:8000/parvius.html`, or use GitHub Pages. Opening it as a local file can block the microphone and model cache.
