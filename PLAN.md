# Implementation Plan

## Phase 1 - Stabilize Current Site

- Run:
  - `NODE_OPTIONS=--max-old-space-size=8192 npx astro check`
  - `npm run build`
- Confirm no fake playable preview remains:
  - `rg "BrowserGame|Playable web preview|browser-game" site/src`
- Confirm UI does not show PPTX or ZIP:
  - detail page filters `.pptx` and `.zip`
  - leave source/download metadata in data files only if hidden from UI
- Confirm P15 PDF renders in custom viewer.
- Remove unused `@fontsource-variable/playfair-display` dependency if no imports remain.

## Phase 2 - Complete P15 Recovery

- Inspect partial folder:
  - `winners/P15 - Pygame Runner-up - Finding Way Home/src/p15 - Drive/`
- If no `.py` files exist, retry Drive download:
  - `python3 -m gdown --folder "https://drive.google.com/drive/folders/1OsGrXgaKk1ubVFdC_sObmB-xfaob-Jlb" -O "<p15 src folder>"`
- If Google blocks CLI, ask user to manually download and place the folder.
- Once source exists:
  - identify entrypoint
  - add source files to `site/src/data/showcaseAssets.ts`
  - test local run if possible
  - assess browser export feasibility

## Phase 3 - Exact Pygame Browser Builds

Priority order:

1. P1 - source has `main()` and no external assets.
2. P6 - source has no external assets but top-level loop.
3. P26 - source has local assets and likely needs path/async cleanup.
4. P8 - hardcoded Windows/OneDrive paths need cleanup.
5. P14 - hardcoded `/Users/...` paths and macOS TTS/subprocess need removal or browser-safe substitutes.
6. P17 - requires WebSocket server deployment and client port.
7. P15 - depends on recovered source.

Rules:

- Stage ports in `site/playable-src/<slug>/`.
- Do not alter original `winners/.../src` submissions.
- Build outputs go to `site/public/play/<slug>/`.
- Only wire a play iframe after Chrome confirms the exact exported game loads.

Pygbag checklist:

- folder contains `main.py`
- main loop is `async def main()`
- every frame yields `await asyncio.sleep(0)`
- no `sys.exit()` in browser flow
- all assets are relative paths inside the staged folder
- browser audio behavior is tested

## Phase 4 - Exact Unity WebGL Builds

Priority order:

1. U4 with Unity `6000.4.11f1`
2. U13 with Unity `6000.4.11f1`
3. U16 with Unity `6000.4.11f1`
4. U2 after WebGL module is installed for `6000.3.17f1`, or after approved version upgrade
5. U8 after approved version upgrade or exact editor install

Rules:

- Build WebGL from the actual Unity project.
- Use staged editor build scripts if needed.
- Output to `site/public/play/<slug>/`.
- Verify in Chrome:
  - page loads
  - canvas is nonblank
  - no fatal console errors
  - game accepts input
- Only then add play URL to site data.

## Phase 5 - Site Integration For Playable Builds

Add a field to `showcaseAssets.ts`, for example:

```ts
playUrl?: string;
```

Detail page behavior:

- if `playUrl` exists: show iframe to exact build
- else: show `Export pending` with blocker note

Do not use abstract fallback gameplay.

## Phase 6 - Deployment Prep

- Ensure `site/public/winners` works for the chosen deployment.
- If GitHub Pages/Vercel cannot follow the symlink reliably, copy required archive assets into `site/public/winners`.
- Keep PDFs and source files available through stable site-relative paths.
- Run final:
  - `NODE_OPTIONS=--max-old-space-size=8192 npx astro check`
  - `npm run build`
- Browser-check homepage and representative detail pages:
  - P15 for newly added PDF
  - one Pygame with source
  - one Unity with source
  - one page with no playable build
  - any page with confirmed playable build
