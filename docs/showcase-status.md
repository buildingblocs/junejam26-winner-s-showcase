# June Jam 2026 showcase — build status

Master snapshot of the showcase site (Astro → GitHub Pages,
`https://buildingblocs.github.io/junejam26-showcase`). Every June Jam entry has
a detail page at `/games/<id>/`; playable ones embed a browser build.

## How games are built & served

- **Pygame / Python → browser:** ported with **pygbag 0.9.3** per
  [pygbag-port-recipe.md](pygbag-port-recipe.md). Staged under
  `site/playable-src/<slug>/`, built to `site/public/play/<slug>/`
  (`index.html` + `favicon.png` + `<slug>.apk`). Small apks are committed;
  **big apks (>~20 MB) are hosted on R2** with the index.html `apk` var pointing
  at the r2.dev URL (e.g. P27).
- **Unity → WebGL:** built with `site/playable-src/unity/BuildWebGL.cs` via
  `Unity -batchmode -quit -projectPath … -executeMethod JuneJamWebGLBuilder.Build
  -customBuildPath …`. The big `*.wasm.unityweb` / `*.data.unityweb` go to **R2**
  (`tools/r2_put.py`); the small loader/framework/TemplateData + index.html are
  committed under `site/public/play/<slug>/`. Editor: **6000.4.11f1** (and
  **6000.3.17f1** for projects pinned to it, e.g. U11/U12). `BuildWebGL.cs` skips
  `SampleScene`/`Packages/`/`SceneTemplate`/Demo/Examples scenes.
- **Assets-only Unity projects** (no ProjectSettings) are reconstructed by
  grafting their Assets onto a working 2D-URP shell (u15a's ProjectSettings +
  Packages). Done for U7b; U15b partial.
- **R2 bucket:** `junejam-showcase` → `https://pub-be8869…r2.dev`. Free egress.
  Credentials in the gitignored `.r2_creds`. Raw downloaded sources live in the
  gitignored `winners/_incoming/` (not committed).

## Status of every entry

**12 award winners** (showcase, all playable): P1, P6, P8, P14, P15, P17, P26,
U2, U4, U8, U13, U16.

**Directory entries** (`site/src/data/allProjects.ts`):

| Playable (33) | |
|---|---|
| Pygame (19) | P3, P4, P5, P9, P10, P12, P16, P19, P20, P22, P23, P24, P25, P27, P28, P29, P31, P32, P33 |
| Unity (14) | U1, U3 (The Great Sink Escape), U6, U7a (Legend Blast), U7b, U9 (The Things We Leave Behind), U10 (Python), U11, U12, U14, U15 (Morning Routine), U15 (Cyberbound), U17 (Python), U18 |

| Not playable | Why |
|---|---|
| **P13** | No source link was ever submitted ("Track_P13") |
| **U5** | Source listed as "Nil" |

## Slides (`site/public/slides/<id>/`, embedded via `PdfDeckViewer`)

Each deck lives in its own folder: `<id>.pdf` (download fallback) plus
pre-rendered `slide-NN.jpg` (`pdftoppm -jpeg -scale-to-x 1100 -jpegopt quality=82`).
`getSlideImages()` finds the `slide-NN` siblings of `slidePdf`, so the viewer
runs in **image mode** — slides show on page load with progressive preloading,
no "Load deck" click — exactly like the winner decks. 446 images / 34 decks.

**34 of 35 directory entries have an embedded deck.** Google Slides decks
export cleanly with `curl …/export/pdf`. Canva/OneDrive/iCloud have no public
export URL (automated fetch hits a Cloudflare CAPTCHA / login), so the user
exported those by hand; pipeline on our side:
- **OneDrive `.pptx`** (P10, U18) → PDF via `soffice --headless --convert-to pdf`.
- **Oversized image-heavy decks** (P24 47 MB, U15 Cyberbound 37 MB, + a few
  mid-size) → compressed with `gs -dPDFSETTINGS=/ebook` (150 dpi); 47 MB → 3 MB.
- The two **U15** decks are `u15-morning.pdf` / `u15-cyberbound.pdf` (id-keyed).
- **Only P32 (Catching the Bus)** still lacks a deck.

## Known caveats
- **U9 "The Things We Leave Behind"**: shipped two files both declaring
  `class PlayerController` (a CS0111 compile error); removed the stray duplicate
  to build. Renders its real main menu (START / OPTIONS / HELP) and four scenes.
- **U7b "Day2Day!"**: menu + character-select render perfectly; entering a level
  shows an empty scene (team heavily downscoped levels).
- **P31** mapped from the "My Cosmic Game Hub" zip by elimination — confirm the
  team code if it matters.
- Several teams' submissions were missing assets they referenced (e.g. P9 socks,
  P23 SFX); those fall back to in-code drawing / silence, faithful to how the
  original ran.

## Tooling
- `tools/assemble_unity.py <slug> "<title>" [W H]` — build a served Unity play dir.
- `tools/r2_put.py <paths…>` — upload files to R2 (mirrors `site/public/` paths).
- `docs/pygbag-port-recipe.md` — the Pygame→browser recipe.
