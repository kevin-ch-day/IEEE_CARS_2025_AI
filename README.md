# IEEE CARS 2026 AI-Assisted Cybersecurity Paper Scaffold

This repository contains an IEEE conference-paper scaffold for a defensive AI-assisted malware/cybersecurity research manuscript intended for [IEEE CARS 2026](https://www.ieee-cars.org/).
The project is intentionally scoped to **analysis and defensive research framing only** (no exploit-building, evasive guidance, payload code, or operational malware workflow content).

Author pages and conference rules were cross-checked against:
- [IEEE CARS 2026 authors and formatting guidance](https://www.ieee-cars.org/authors)
- [IEEE CARS call for papers](https://www.ieee-cars.org/call-for-papers)

## Repository layout

- `main.tex` — IEEE conference paper driver file (`\documentclass[conference]{IEEEtran}`)
- `preliminary/00_paper_header.tex` — title + authors + abstract + keywords front-matter block
- `sections/` — paper body split into modular files:
  - `01_introduction.tex`
  - `02_background_related_work.tex`
  - `03_research_questions_study_design.tex`
  - `04_methodology.tex`
  - `05_results.tex`
  - `06_discussion.tex`
  - `07_conclusion.tex`
  - `09_references.tex`
- `references/references.bib` — bibliography file placeholder (for future real citations)
- `template/` — IEEE template and sample files
- `figures/` — paper figures
- `.gitignore` and `.gitattributes` — clean source control and line ending normalization
- `IEEEtran.cls` — conference class file at repo root

## Build instructions

For now, paper compiles without mandatory bibliography tooling:

```bash
pdflatex main.tex
pdflatex main.tex
```

This path is for draft scaffolding and is controlled via `\setboolean{useBibTeX}{false}` in `main.tex`.

Quick build script:

```bash
./scripts/build_paper.ps1
```

If/when real citations are added and `\cite{}` calls are introduced, switch to BibTeX workflow:

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

### Submission readiness checklist (CARS pre-submit)

- [ ] `main.tex` compiles cleanly with `pdflatex` (2-pass) or BibTeX path when citations are final.
- [ ] All front-matter content remains in `preliminary/00_paper_header.tex`.
- [ ] One cohesive abstract paragraph in `preliminary/abstract.tex` states purpose, method, and outcomes without unsafe content.
- [ ] Section order and naming match IEEE CARS sequence.
- [ ] No unsafe or operational malware guidance; scope stays defensive and methodological.
- [ ] Placeholder references removed/replaced with real `\cite{}` + entries in `references/references.bib`.
- [ ] Final page budget targets 6 pages before any overflow.
- [ ] Figures/tables are IEEE-compatible (two-column width and concise captions).

## IEEE CARS 2026 policy notes (for pre-submission)

- Full-paper submission is IEEE 2-column conference format.
- Paper length: **6 pages (base limit)**.
- Extra pages (7–9) are available with extra-page charges.
- Submissions must be original and not under review elsewhere.
- Camera-ready stage includes IEEE PDF eXpress validation (Conference ID: 70730X).
- Current workflow keeps all front matter split into separate files for safe iterative edits.

## Research scope and safety posture

The intended framing is:

- AI-assisted cybersecurity workflows
- malware-analysis research design
- measurable defensive artifacts
- static/dynamic analysis comparison
- detection/analysis outcomes
- limitations and ethics

The scaffold is intentionally paper-first and defensive: clear threat-model framing, controlled experiments, and explicit limitations.

## Branch and merge workflow

- `main` is the canonical branch for consolidated work.
- Feature/integration branches should be short-lived and merged via PR or squash into `main`.
- After merge, delete stale branches locally and in GitHub to avoid clutter.

### Authoring policy for this repository

- Keep claims conservative and evidence-backed.
- If a result is only a trend or controlled observation, phrase it as such.
- Keep limitations explicit in every draft cycle.

### Current status

- `main` is the source of truth for ongoing writing.
- Cleanup branches are expected to remain closed after merging.

## Author and template notes

- Title/abstract/keywords/authors are split into dedicated files to match IEEE workflow and simplify submission edits.
- If final submission formatting is needed, keep final typography changes in these dedicated files and include them from `main.tex`.
