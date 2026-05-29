# IEEE CARS 2025/2026 AI-Assisted Cybersecurity Paper

This repository contains an IEEE conference-paper scaffold for a defensive AI-assisted malware/cybersecurity research manuscript.
The project is intentionally scoped to **analysis and defensive research framing only** (no exploit-building, evasive guidance, payload code, or operational malware workflow content).

## Repository layout

- `main.tex` — IEEE conference paper driver file (`\documentclass[conference]{IEEEtran}`)
- `title.tex` — paper title (single source)
- `abstract.tex` — abstract (single source)
- `authors.tex` — author block (single source)
- `sections/` — paper body split into modular files:
  - `01_introduction.tex`
  - `02_background_related_work.tex`
  - `03_research_questions_study_design.tex`
  - `04_methodology.tex`
  - `05_results.tex`
  - `06_discussion.tex`
  - `07_conclusion.tex`
- `references/references.bib` — bibliography file placeholder (for future real citations)
- `template/` — IEEE template and sample files
- `figures/` — paper figures
- `.gitignore` and `.gitattributes` — clean source control and line ending normalization
- `IEEEtran.cls` — conference class at repo root

## Build instructions

For now, paper compiles without mandatory bibliography tooling:

```bash
pdflatex main.tex
pdflatex main.tex
```

If/when real citations are added and `\cite{}` calls are introduced, switch to BibTeX workflow:

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Research scope and safety posture

The intended framing is:

- AI-assisted cybersecurity workflows
- malware-analysis research design
- measurable defensive artifacts
- static/dynamic analysis comparison
- detection/analysis outcomes
- limitations and ethics

The scaffold supports a paper-first, defensively oriented workflow: clear threat-model framing, controlled experiments, and explicit limitations.

## Branch and merge workflow

- `main` is the canonical branch for consolidated work.
- Feature/integration branches should be short-lived and merged via PR or squash into `main`.
- After a branch is fully merged, delete it locally and remotely to keep history clean.

### Current status

- Mainline includes the Overleaf/cleanup integration.
- Stale branches used during this phase (`paper-structure-cleanup`, `overleaf-2026-05-29-0655`) have been merged and removed.

## Author and template notes

- Author and front-matter blocks are split into dedicated files (`authors.tex`, `title.tex`, `abstract.tex`) to match IEEE submission expectations and make iterative writing easier.
- If title/abstract/author formatting needs a final submission pass, keep all edits in these dedicated files and include them from `main.tex`.
