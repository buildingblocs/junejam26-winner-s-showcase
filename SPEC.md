# June Jam Winners Showcase Spec

## Goal

Build a BuildingBloCS-style Astro website that showcases June Jam winning games, their teams, writeups, slides, source code, and exact browser-playable builds where possible.

## Audience

- June Jam participants
- BuildingBloCS organizers
- Visitors browsing winners and special prize projects
- Future maintainers preparing the site for GitHub/Astro deployment

## Site Structure

```text
/                         Winner's Showcase homepage
/games/[slug]/            Detail page for each winning entry
/winners/...              Static archive assets copied/symlinked into Astro public output
```

## Homepage Requirements

- Use dark BuildingBloCS-inspired visual language.
- Show a sticky nav with:
  - `Winners`
  - `Special Prizes`
- Hero:
  - eyebrow: `BuildingBloCS June Jam 2026`
  - heading: `Winner's Showcase`
  - no descriptive hero paragraph
  - no stats/metrics panel
- First card section:
  - eyebrow: `Ranked Awards`
  - heading: `Main track winners`
- Second card section:
  - eyebrow: `Special Prizes`
  - heading: `Special prize winners`
- Cards should be visual archive-like tiles:
  - cover image
  - tags
  - title
  - summary
  - team code/track

## Detail Page Requirements

Each detail page must show:

- Cover image
- Track and award tags
- Team code
- Game title
- Team members
- Team writeup
- Play panel
- Slides panel
- Full source panel

## Play Panel

The play panel must only embed a real browser build of the submitted game.

Allowed:

- Unity WebGL export generated from submitted Unity project
- Pygame browser export generated from submitted Python/Pygame code
- Exact web build from the team if provided

Not allowed:

- Abstract mini-game
- Recreated interpretation
- Placeholder canvas game
- Any experience that is not built from the submitted source

If no exact browser build exists yet, show:

- heading: `Exact browser build`
- status: `Export pending`
- a specific blocker in the note

## Slides Requirements

- Render PDFs inline using custom PDF.js renderer.
- Do not use the browser's default PDF iframe toolbar as the primary presentation view.
- Do not show PPTX links in the UI.
- If only PPTX exists and no PDF has been exported, show `PDF preview pending`.

Current custom renderer:

- `site/src/components/PdfDeckViewer.astro`
- Uses `pdfjs-dist`
- Themed toolbar with Prev/Next/Zoom controls
- Canvas render inside a dark grid stage

## Source Requirements

- Do not show ZIP links in the UI.
- Show selected readable source files inline.
- Source display should use full-source collapsible cards.
- For Pygame, show key `.py` files.
- For Unity, show gameplay `.cs` scripts, not the full Unity project tree.
- Keep raw source links for each displayed file.

## Font and Styling

- Primary site font: Pangolin via `@fontsource/pangolin`
- Accent color: BuildingBloCS orange `#ffa216`
- Background: dark navy/slate
- Avoid one-off fake game art or decorative filler.

## Deployment Assumptions

- Site will likely be deployed from `site/`.
- `site/public/winners` currently points at archive assets.
- `npm run build` should emit a static `dist/` with route HTML and static assets.
- Before GitHub deployment, ensure the `winners/` archive assets are committed or copied in a deployment-safe way. Do not rely on a local-only symlink if the deploy platform cannot follow it.

## Non-Goals

- Do not redesign into a marketing landing page.
- Do not convert all source into full GitHub repositories unless requested.
- Do not upload anything externally without explicit user approval.
- Do not rewrite games unless needed for browser export, and then only in staged port folders.
