# Current Status And Handoff

Last updated: 2026-06-14 Asia/Singapore.

## Repository State

Root:

```text
/Users/saumil/Downloads/winners
```

Top-level folders:

```text
site/
winners/
```

`site/` is the Astro app. `winners/` is the local project/slides/source archive.

P23 was removed because it was a mistaken entry.

## Site Work Completed

- Replaced the initial plain HTML direction with an Astro app.
- Added BuildingBloCS-inspired dark theme.
- Added Pangolin font.
- Added archive-style card grid.
- Added detail pages for all tracked winners.
- Added award tags.
- Added custom PDF renderer with PDF.js.
- Added full-source collapsible cards.
- Removed PPTX links from UI.
- Removed ZIP links from UI.
- Removed fake browser-game preview after user rejected it.
- Restored play panel to exact-build-only state.

## Current Site Files

```text
site/src/components/GameCard.astro
site/src/components/PdfDeckViewer.astro
site/src/data/games.ts
site/src/data/showcaseAssets.ts
site/src/layouts/Layout.astro
site/src/pages/index.astro
site/src/pages/games/[slug].astro
site/src/styles/global.css
```

## Dependencies Added

```text
@fontsource/pangolin
pdfjs-dist
@types/node
```

`@fontsource-variable/playfair-display` is still in `package.json` from an earlier version but is no longer used by `global.css`. It can be removed in a cleanup pass.

## Verification Status

Known passing before the final docs pass:

```bash
NODE_OPTIONS=--max-old-space-size=8192 npx astro check
npm run build
```

After the very latest changes, these should be rerun:

```bash
cd /Users/saumil/Downloads/winners/site
NODE_OPTIONS=--max-old-space-size=8192 npx astro check
npm run build
```

The dev server process was still running on port 4321 during the handoff:

```text
http://127.0.0.1:4321/
```

## P15 Update

User provided:

```text
Canva: https://canva.link/98uh6yd6bafy8o7
Drive: https://drive.google.com/drive/folders/1OsGrXgaKk1ubVFdC_sObmB-xfaob-Jlb
Local PDF: /Users/saumil/Downloads/P15 Game Jam Where The Path Used to Be.pdf
```

Copied PDF to:

```text
winners/P15 - Pygame Runner-up - Finding Way Home/slides/p15 - Canva/P15 Game Jam Where The Path Used to Be.pdf
```

Updated `site/src/data/showcaseAssets.ts` so P15 has a `slidePdf`.

An attempted `gdown` download of the P15 Drive folder was interrupted by the user. The lingering `gdown` process was killed. The partial folder may contain assets, but no `.py` files were found during the last check.

Partial P15 source folder:

```text
winners/P15 - Pygame Runner-up - Finding Way Home/src/p15 - Drive/
```

Observed there:

- image assets
- fonts
- Python cache files
- no `.py` source files found yet

Next P15 step: finish/retry Drive download or ask user to manually download the full folder if Google Drive blocks CLI access.

## Project Inventory

### Main Track

P6 - Pygame Winner

- Title: `ALARM CLOCK: Tick's Timebomb`
- Folder: `winners/P6 - Pygame Winner - ALARM CLOCK Ticks Timebomb`
- Slides PDF exists.
- Source file shown: `alarm_clock.py`
- Browser export status: likely feasible with `pygbag`, but current `pygbag` attempts did not emit a complete runnable HTML shell.

P15 - Pygame Runner-up

- Title: `Finding Way Home`
- Folder: `winners/P15 - Pygame Runner-up - Finding Way Home`
- User-provided PDF copied in.
- Source incomplete after interrupted Drive download.
- Browser export status: blocked until actual source is recovered.

P26 - Pygame Second Runner-up

- Title: `Homebound`
- Folder: `winners/P26 - Pygame Second Runner-up - Homebound`
- Source file shown: `homebound.py`
- Browser export status: likely feasible after staging `main.py` and adding async loop/yield.

U8 - Unity Winner

- Title: `The Trash Won't Take Itself Out!`
- Folder: `winners/U8 - Unity Winner - Trash Wont Take Itself Out`
- Slides PDF exists.
- Source files shown: `PlayerController.cs`, `PlayerSpit.cs`, `GameManager.cs`
- Unity requested version from audit: `6000.3.13f1`
- Installed exact match: no
- Browser export status: blocked unless upgraded to installed Unity with WebGL, likely `6000.4.11f1`, or exact editor/module is installed.

U4 - Unity Runner-up

- Title: `5 More Minutes`
- Folder: `winners/U4 - Unity Runner-up - 5 More Minutes`
- Source files shown: `FirstPersonController.cs`, `NarratorManager.cs`, `KitchenSequenceManager.cs`
- Unity requested version from audit: `6000.4.10f1`
- Installed nearest: `6000.4.11f1` with WebGL
- Browser export status: likely feasible with patch-forward risk and a generated build script.

U2 - Unity Second Runner-up + Best Art

- Title: `Taking OUT Trash`
- Folder: `winners/U2 - Unity Second Runner-up + Best Art - Taking OUT Trash`
- Source files shown: `PlayerController.cs`, `EnemySpawner.cs`, `Navigation.cs`
- Unity requested version from audit: `6000.3.17f1`
- Installed exact: yes
- WebGL module for exact: no
- Browser export status: blocked until WebGL module is installed for `6000.3.17f1`, or project is opened/upgraded using another Unity editor.

### Special Prizes

P17 - CSIT Prize

- Title: `BREACH`
- Folder: `winners/P17 - CSIT Prize - BREACH`
- Slides PDF exists.
- Source files shown: `client.py`, `server.py`, `game_rules.py`
- Browser export status: not straightforward. It is multiplayer and depends on a WebSocket server. Needs hosted server and browser-compatible client port.

U16 - Most Original Concept

- Title: `A Day in the Life of a Blind Person`
- Folder: `winners/U16 - Most Original Concept - A Day in Life of Blind Person`
- Source files shown: `PlayerController.cs`, `CaneTap.cs`, `QuestManager.cs`
- Unity requested version from audit: `6000.4.10f1`
- Installed nearest: `6000.4.11f1` with WebGL
- Browser export status: likely feasible with patch-forward risk and a generated build script.

P14 - Most Lines of Code

- Title: `Daily Life Reimagined`
- Folder: `winners/P14 - Most Lines of Code - Daily Life Reimagined`
- Slides PDF exists.
- Source file shown: `FinalGame.py`
- Browser export status: difficult as-is. Audit found hardcoded `/Users/...` paths, macOS TTS/subprocess usage, threading, and multiple blocking loops.

P1 - Sensory Overload

- Title: `School Subway Surfers`
- Folder: `winners/P1 - Sensory Overload - School Subway Surfers`
- Slides PDF exists.
- Source file shown: `Schools Subway Surfers.py`
- Browser export status: likely feasible with `pygbag`.
- Staged port exists: `site/playable-src/p1/main.py`
- Staged file compiles with Python.
- `pygbag` attempts produced only package files, not a confirmed runnable browser build.

P8 - Most Silly

- Title: `Bleach Rush`
- Folder: `winners/P8 - Most Silly - Bleach Rush`
- Slides PDF exists.
- Source file shown: `bleach_rush.py`
- Browser export status: blocked by hardcoded Windows/OneDrive paths and cutscene loop cleanup.

U13 - Most Overengineered

- Title: `TinyExplorer`
- Folder: `winners/U13 - Most Overengineered - TinyExplorer`
- Source files shown: `PlayerController.cs`, `waterRIsing.cs`, `keyTrigger.cs`
- Unity requested version from audit: `6000.4.10f1`
- Installed nearest: `6000.4.11f1` with WebGL
- Browser export status: likely feasible with patch-forward risk and a generated build script.

## Pygbag Findings

Installed:

```bash
python3 -m pip install --user pygbag
```

Version installed:

```text
pygbag 0.9.3
```

Staged ports:

```text
site/playable-src/p1/main.py
site/playable-src/p6/main.py
```

Both staged files were patched for async browser loop behavior and compiled locally with:

```bash
python3 -m py_compile site/playable-src/p1/main.py site/playable-src/p6/main.py
```

However:

- `python3 -m pygbag --build .` produced `.apk` / `.tar.gz`, not confirmed runnable HTML.
- `python3 -m pygbag --build --html ...` produced a tiny incomplete HTML file in one attempt.
- full pygbag runs hung until killed.

Do not embed these outputs until a real browser page loads and runs the exact game.

## Unity Findings

Installed Unity editors from audit:

```text
6000.0.77f1 - WebGL yes
6000.3.17f1 - WebGL no
6000.4.11f1 - WebGL yes
```

No project had a checked-in WebGL build script using `BuildPipeline.BuildPlayer`.

Recommended Unity direction:

1. Add temporary/staged build script per Unity project, not in original archive unless acceptable.
2. Use `6000.4.11f1` first for U4/U13/U16.
3. Build to `site/public/play/<slug>/`.
4. Embed only after Chrome confirms `index.html` loads and canvas is not blank.

Generic CLI shape:

```bash
/Applications/Unity/Hub/Editor/<version>/Unity.app/Contents/MacOS/Unity \
  -batchmode -nographics -quit \
  -projectPath "<project-root>" \
  -buildTarget WebGL \
  -executeMethod <BuildClass>.BuildWebGL
```

## Immediate Next Steps

1. Rerun Astro verification after docs and latest patches.
2. Inspect P15 partial Drive folder and complete source recovery.
3. Remove unused dependency `@fontsource-variable/playfair-display` if confirmed unused.
4. Decide browser-build order:
   - fastest likely Pygame: P1, P6, P26
   - fastest likely Unity: U4, U13, U16
5. Fix `pygbag` build process or switch to a known-good pygame-web template.
6. Generate exact builds only.
7. Wire `asset.playUrl` or equivalent into `showcaseAssets.ts` only after a build is confirmed.
8. Replace `Export pending` panel with an iframe only for confirmed exact builds.
