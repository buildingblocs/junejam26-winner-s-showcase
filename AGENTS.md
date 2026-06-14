# Agent Instructions

This repository is the June Jam winners archive and Astro showcase site.

## Workspace Layout

- Root: `/Users/saumil/Downloads/winners`
- Archive folder: `winners/`
- Astro site folder: `site/`
- Do not move winner folders unless the user asks.
- Do not remove original submitted files.
- If browser-build ports are needed, stage them under `site/playable-src/<slug>/` and keep originals untouched.

## User Requirements

- The site must be Astro, not plain HTML.
- Styling should stay close to the BuildingBloCS site/archive feel:
  - dark navy background
  - orange BuildingBloCS accent
  - archive-like image cards
  - sticky top nav
  - Pangolin-style friendly display font
- Homepage copy:
  - hero heading: `Winner's Showcase`
  - main section: `Main track winners`
  - special section: `Special prize winners`
- Do not show:
  - the old metric panel (`12 featured entries`, `6 ranked awards`, `6 special awards`)
  - footer text about local archive
  - BuildingBloCS archive reference footer link
  - PPTX links in the UI
  - ZIP links in the UI
- Slides should render inline using the custom PDF renderer, not the browser's default PDF iframe.
- Source should appear as full-source collapsible cards.
- Most important: do not show fake or abstracted games. The in-browser game area must only run the exact submitted game exported from its code. If an exact build is unavailable, say it is pending and explain the blocker.

## Current Important Files

- Homepage: `site/src/pages/index.astro`
- Detail page: `site/src/pages/games/[slug].astro`
- Cards: `site/src/components/GameCard.astro`
- Custom PDF viewer: `site/src/components/PdfDeckViewer.astro`
- Game metadata: `site/src/data/games.ts`
- PDF/source showcase metadata: `site/src/data/showcaseAssets.ts`
- Global styles: `site/src/styles/global.css`

## Verification Commands

Run from `site/`:

```bash
NODE_OPTIONS=--max-old-space-size=8192 npx astro check
npm run build
npm run dev -- --port 4321
```

The larger heap is intentional. Full source cards and PDF.js can make `astro check` memory-heavy on the default Node heap.

## Current Dev Server

The dev server has been running at:

```text
http://127.0.0.1:4321/
```

Check for stale processes before starting another:

```bash
ps -axo pid,command | rg 'astro dev|gdown|pygbag' | rg -v rg
```

## Guardrails

- Do not reintroduce `BrowserGame.astro` or any filler canvas game.
- Do not claim a game is playable until its actual submitted code loads in the browser.
- Do not link users to ZIP/PPTX in the UI unless the user reverses that requirement.
- Keep downloadable/raw source links acceptable, but prefer inline source display.
- Unity browser play means actual WebGL export.
- Pygame browser play means actual `pygbag` or equivalent browser export from the submitted Python code.
