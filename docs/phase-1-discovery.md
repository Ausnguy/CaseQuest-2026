# Phase 1 — Repository and Project Discovery

**Date:** 2026-10-23 (Friday, case day 1)
**Submission deadline:** 2026-10-24, 4:45 PM CT. That is about one working day away.
**Status:** Complete. No application code was written in this phase.

> **Like I'm 5:** Before building a LEGO castle, you dump out the box to see which pieces you have and read the instructions. That's this phase. We built nothing yet. We only looked.

---

## 1. Objective

Take stock of what the team already has (repo, files, tools, rules) so the next phases build on real facts instead of guesses.

## 2. What was inspected

| Item | Location | How |
|---|---|---|
| Team repo | `github.com/Ausnguy/CaseQuest-2026` (public), cloned to this folder | git log, branches, GitHub API |
| Participant packet (PDF, 7 pages) | `~/Downloads/CaseQuest2026_ParticipantPacket (2).pdf` | Read every page |
| Packet transcription | `Dataset-Rules/CaseQuest2026_ParticipantPacket.md` | Compared line by line with the PDF |
| Workbook | `Dataset-Rules/CaseQuest2026Dataset.xlsx` | Profiled all 8 tabs (see section 5) |
| Local tooling | This Mac | Version checks |

## 3. Findings: repository

| Fact | Evidence | So what? |
|---|---|---|
| The repo is a skeleton: 4 commits, all by Austin Nguyen, one branch (`main`), no PRs or issues | `git log`, `git branch -a` | Nothing to reuse. We choose the structure. |
| It contains only `README.md` (placeholder), the packet `.md`, the `.xlsx`, and `.vscode/.gitignore` (ignores a personal `github-accounts.json`) | `git ls-files` | No code, no dependency files, no tests yet. |
| The repo `.xlsx` is byte-identical to the downloaded workbook | `cmp`, SHA-256 below | One source of truth. |
| The packet `.md` faithfully matches the PDF | Manual comparison | Safe to cite either one. |
| `AayanUH` has no push access, but **`Sp00keee` has push access** to `Ausnguy/CaseQuest-2026` | GitHub API `permissions.push: true` for Sp00keee | Resolved: `gh` is switched to Sp00keee, and this repo's local git config commits as Sp00keee (noreply email) and pushes through `gh`. A push dry-run succeeds. |
| This folder sits inside a git repo rooted at your **home directory** (`/Users/aayan`, remote `Sp00keee/tp33711`) | `git rev-parse --show-toplevel` | Always run git commands **inside** `CaseQuest2026/`. Never run `git add .` from your home folder. |

> **Like I'm 5:** The team's toy box is almost empty. It holds only the instruction sheet and the puzzle pieces (the data). Also, your name isn't on the "allowed to put toys in the box" list yet, so Austin needs to add you.

### Raw-data fingerprints (proof we never altered the originals)

| File | SHA-256 |
|---|---|
| `Dataset-Rules/CaseQuest2026Dataset.xlsx` | `b4d32ee1935619eec5a7729428e525eb74c44f2d5cd04a0f7e13fe4cd84533b8` |
| `CaseQuest2026_ParticipantPacket (2).pdf` | `792738b0c7e66a26acd4188f32e7fe529c5ffeef75f37bf667f7bf490a2a4ee8` |

**Rule from now on:** the `.xlsx` is read-only. All cleaning writes to new files, and every change is logged.

## 4. Findings: tools available on this machine

| Tool | Version | Note |
|---|---|---|
| Python (system) | 3.9.6 | Old. No pandas installed. |
| Python via `uv` | 3.12.13 | **Use this.** `uv` gives a clean, reproducible environment. |
| Node / npm | 26.9 / 11.19 | Available if we build a web app. |
| git / gh | 2.54 / 2.100 | Two GitHub accounts are logged in; `AayanUH` is active. |
| VS Code | installed | — |
| Excel / Power BI / Tableau | **not found** | Rules out an Excel- or BI-only prototype on this machine. |

## 5. Findings: the rules of the game (packet plus workbook ReadMe)

> **Like I'm 5:** There are two rule books. The packet is the short one everyone reads. The workbook's ReadMe tab is the long one with the secret rules the judges care about.

**Hard requirements**

1. Deck of **10 slides or fewer**, a **7-minute** talk, and **every member speaks** and answers questions.
2. **One** primary recommendation, plus any options it depends on.
3. A **functional interactive prototype** using the supplied data, with:
   - useful outputs
   - an employee review step
   - an HSE hold/authorization step
   - a workflow or architecture visual

   Static mockups fail.
4. Upfront **and** annual costs, including prerequisites, training and the open HSE actions in scope.
5. Estimated **annual avoided unplanned downtime hours**, using the Solutions sheet's **base** fractions and only its eligible causes and stages.
6. A twelve-month roadmap using `lead_months`, staffing (`available_project_hours`), training (technicians × hours), and KPIs.
7. **HSE gate:** a site with an open potential-severity-5 action **cannot enter the pilot** until the site HSE supervisor verifies closure.
8. Keep a raw copy and a cleaning log.

**A conflict between the two rule books.** The packet says a prototype is *optional* ("Teams may also choose…"). The workbook ReadMe (Revision 5, Oct 21, which is newer) says it is **required**. **Decision: treat it as required.** That is the safer reading, and the prototype is worth 20 rubric points either way.

**Scoring weights.** Data 20, Tech 20, Problem 15, HSE 15, Implementation 10, Costs 10, Presentation 10, plus a 5-point storytelling bonus. That makes **HSE worth as much as choosing the problem**.

## 6. Preliminary data observations (from the earlier exploratory pass, to be re-verified in Phase 2)

These numbers come from a quick scratch analysis. **They are not final.** Phase 2 will reproduce them with logged, tested cleaning code.

- **Dirty-data issues found:**
  - Events: mixed asset IDs (`a010`, `8`, `A09`), 2 duplicate rows, 4 missing `stopped_hours`, 14 parts invoices pending.
  - Production: 2 duplicate rows, 3 missing `potential`.
  - Readings: the export is doubled, 18 tags use legacy `LEG-` names, 8 temperatures are in °F, 682 values missing, 116 flagged suspect, up to 30 hours of ingestion delay.
  - HSE: every row appears twice.
- **2025 unplanned downtime:** about 6,599 hours across 313 events, about $5.6M in lost contribution margin.
- **Downtime by stage:** repair 35%, **parts wait 24%**, dispatch 18%, detection 15%, restart 7%.
- **Arroyo (S04)** has the most downtime, the lowest spare-parts fill (42%), the lowest network uptime (92.8%), and the fewest technicians (2).
- **HSE:** 11 actions are open, all past due as of the 2026-10-01 snapshot. 6 are severity 5, at Mesa, Arroyo and Prairie, so **those sites start out blocked** from a pilot.

## 7. Open questions, assumptions, risks

| # | Type | Item | Proposed handling |
|---|---|---|---|
| Q1 | Question | Who is on the team, and who presents which slides? | Need names. Every member must speak. |
| Q2 | ~~Question~~ Resolved | Push access | Use the `Sp00keee` account, which already has push access. |
| Q3 | Question | Is there an official, more detailed rubric than the packet table? | Check Discord. Until then, use the packet table. |
| A1 | Assumption | The prototype is required (ReadMe Rev 5 overrides the packet) | Documented above. |
| A2 | Assumption | The prototype runs live on a laptop at judging; no cloud hosting needed | Revisit if the organizers want a URL. |
| R1 | Risk | **Time.** About 24 hours remain, and some of that is sleep. | Keep the app small and reliable. Freeze features by Saturday noon. |
| R2 | Risk | Teammates pushing to `main` at the same time | Use short-lived branches and PRs. |
| R3 | Risk | Over-claiming benefits (the judges' rules forbid ROI fantasies or injury-rate claims) | Show only base-fraction hours and observed history, clearly labeled. |
| R4 | Risk | Live-demo failure | Add tests, a pinned environment, and screenshots as a backup. |

## 8. Decision needed: prototype technology

> **Like I'm 5:** We need to pick which crayons to draw with. Some are fancy but slow. Some are simple and always work.

| Option | Pros | Cons |
|---|---|---|
| **A. Python + Streamlit (recommended)** | One language for cleaning, analysis, app and tests (pytest). Interactive in hours. Runs on any teammate's laptop with `uv`. | Looks "Streamlit-y" unless styled. |
| B. React/Vite web app + Python data prep | Most polished look | Two codebases, much slower to build, more to break in under 24 hours |
| C. Excel workbook | Familiar to judges | Excel isn't installed here; HSE gating and an approval workflow are clunky; hard to test |

**Recommendation: A.** Streamlit is a supported Python dashboard library. The packet explicitly accepts "Python" and "web applications".

### Proposed repo layout (to be created in Phase 2, pending your OK)

```
CaseQuest2026/
├── Dataset-Rules/                 # raw inputs, never modified
├── data/processed/                # cleaned outputs (generated, reproducible)
├── docs/                          # phase reports, cleaning log, assumptions, sources
├── src/casequest/                 # cleaning, metrics, solution model, HSE gate
├── app/                           # Streamlit prototype (Phase 6)
├── tests/                         # pytest: cleaning rules, formulas, HSE gate
├── pyproject.toml                 # uv-managed, Python 3.12
└── README.md                      # how to run, team, summary
```

## 9. Acceptance criteria for Phase 1

- [x] Team repo cloned into the project folder; history, branches and files listed
- [x] Every packet page and the workbook ReadMe and Dictionary read
- [x] Packet `.md` verified against the PDF
- [x] Tooling inventoried; constraints identified (no Excel, Python 3.12 via uv)
- [x] Raw files fingerprinted
- [x] Rule conflicts, risks and open questions written down
- [x] Tech-stack decision presented with options, **not yet committed**

## 10. Status and exact next step

**Status:** Phase 1 is done. The only file added is this report. Nothing has been committed or pushed.

**Next step: Phase 2, data audit.**
1. Set up the `uv` Python 3.12 project.
2. Write `src/casequest/clean.py`, which turns the raw workbook into cleaned tables plus `docs/cleaning-log.md`, with a test for each cleaning rule.
3. Reconcile the cleaned Events against Production using the ReadMe formulas. This proves the cleaning is right.

Phase 2 starts once the tech stack (section 8) is confirmed.
