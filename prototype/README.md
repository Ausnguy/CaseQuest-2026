# Gate Console (standalone 3D prototype)

`lone-mesa-gate-console.html` is a single self-contained file. Open it in any browser; no server or internet needed.

- 3D map of the six sites: HSE HOLD cages, spare-shelf cubes, avoided-hours towers
- Role picker (Planner / Site HSE supervisor / Manager) with the gate rules from `docs/phase-5-product-design.md`
- Replay of 2025 using only readings received by the chosen date
- Rollout and business-case sliders (reproduces 666 h year 1, 968 h steady state at month 3 / base)
- Guardrail self-test on the HSE tab

Data is embedded from `data/processed/*.csv` at build time (readings, events, HSE, sites, assets). If the processed data changes, the embedded numbers will not update automatically.

Standalone demo aid, independent of the Streamlit app.

## VIGIL voice agent

Orb at bottom-right. Answers are computed from the embedded data and Solutions rules (no LLM, no API key), tailored to Plant manager / Parts planner / HSE supervisor / Executive, and it moves the 3D camera and rollout sliders. It never lifts a hold, verifies a closure or approves work.

- Speech in: Whisper (`whisper-tiny.en`) via transformers.js from jsDelivr, about 40 MB on first use. Click "Prepare Whisper" before the demo while online. Falls back to browser speech recognition, then typing.
- Speech out: browser text-to-speech.
- Microphone needs a secure origin: serve it (`python3 -m http.server`) or use GitHub Pages; a plain file:// may block the mic.

