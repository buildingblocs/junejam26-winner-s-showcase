# Winner Inventory

This file records the intended winners and special prize mappings.

## Ranked Awards

| Slug | Award | Title | Folder |
|---|---|---|---|
| `p6` | Pygame Winner | ALARM CLOCK: Tick's Timebomb | `winners/P6 - Pygame Winner - ALARM CLOCK Ticks Timebomb` |
| `p15` | Pygame Runner-up | Finding Way Home | `winners/P15 - Pygame Runner-up - Finding Way Home` |
| `p26` | Pygame Second Runner-up | Homebound | `winners/P26 - Pygame Second Runner-up - Homebound` |
| `u8` | Unity Winner | The Trash Won't Take Itself Out! | `winners/U8 - Unity Winner - Trash Wont Take Itself Out` |
| `u4` | Unity Runner-up | 5 More Minutes | `winners/U4 - Unity Runner-up - 5 More Minutes` |
| `u2` | Unity Second Runner-up + Best Art | Taking OUT Trash | `winners/U2 - Unity Second Runner-up + Best Art - Taking OUT Trash` |

## Special Prizes

| Slug | Award | Title | Folder |
|---|---|---|---|
| `p17` | CSIT Prize | BREACH | `winners/P17 - CSIT Prize - BREACH` |
| `u16` | Most Original Concept | A Day in the Life of a Blind Person | `winners/U16 - Most Original Concept - A Day in Life of Blind Person` |
| `p14` | Most Lines of Code | Daily Life Reimagined | `winners/P14 - Most Lines of Code - Daily Life Reimagined` |
| `p1` | Sensory Overload | School Subway Surfers | `winners/P1 - Sensory Overload - School Subway Surfers` |
| `p8` | Most Silly | Bleach Rush | `winners/P8 - Most Silly - Bleach Rush` |
| `u13` | Most Overengineered | TinyExplorer | `winners/U13 - Most Overengineered - TinyExplorer` |

## Notes

- `p23` was removed because the user said it was a mistake.
- `u2` appears in both ranked and special award context because it also won Best Art.
- `p15` was corrected from earlier confusion and now has a provided PDF.
- Some terminal output may visually drop small words such as `the` from displayed paths. Always verify path existence programmatically before changing data.

## Source Display Strategy

For Pygame:

- show key `.py` files
- prefer entrypoint or main gameplay module

For Unity:

- show selected gameplay `.cs` scripts
- avoid metadata, package files, imported asset scripts, and generated files

## Slide Display Strategy

- show `slidePdf` through `PdfDeckViewer`
- hide `.pptx` links from page UI
- if a project has only PPTX, export or obtain a PDF before enabling inline slides

## Playable Build Strategy

- exact source build only
- Pygame: `pygbag` or equivalent
- Unity: WebGL build
- no filler replacements
