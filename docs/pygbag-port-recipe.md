# Pygame → browser (pygbag 0.9.3) port recipe

This is the exact, proven process used to turn a submitted Pygame project into a
browser-playable build under `site/public/play/<slug>/`. Follow it precisely.

Inputs you are given: the **raw source path** (under `winners/_incoming/<CODE>/`)
and the **slug** (lowercase team code, e.g. `p16`).

## 1. Stage the source
- `mkdir -p site/playable-src/<slug>`
- Copy the game's code + asset folders into it. The entry script must end up as
  `site/playable-src/<slug>/main.py`. If the repo's entry file has another name,
  copy it to `main.py`. Keep relative asset paths working (copy `assets/`,
  images, fonts, etc. alongside `main.py`).

## 2. Fix assets for WASM (case-sensitive FS!)
- WASM's filesystem is **case-sensitive**. If code loads `assets/car.png` but the
  file is `Car.png`, rename the file to match the code (or fix the path). Check
  every `pygame.image.load(...)` / font / sound path.
- **Audio:** SDL2_mixer in pygbag reliably plays **OGG (Vorbis), stereo**. Convert
  every `.mp3` / `.wav` the game loads to `.ogg` and repoint the load calls:
  `ffmpeg -y -loglevel error -i in.mp3 -ac 2 -c:a vorbis -strict -2 out.ogg`
  (this ffmpeg has no libvorbis — use `-c:a vorbis -strict -2`). Delete the heavy
  original mp3/wav from the staged dir once converted.

## 3. Async-convert main.py (REQUIRED for pygbag)
- `import asyncio` at the top.
- Find the main loop (`while running:` / `while True:`). Make the function that
  contains it `async def`, and add exactly one `await asyncio.sleep(0)` per
  iteration of that loop (yields to the browser each frame).
- Entry point becomes:
  ```python
  async def main():
      await <existing entry>()   # e.g. await game.run(), or inline the loop
  if __name__ == "__main__":
      asyncio.run(main())
  ```
- `pygame.display.set_mode(...)` must have an explicit size (never empty).
- Remove/avoid: `import wave` (triggers a junk PyPI fetch in WASM), blocking
  `input()`, threads that block, and `sys.exit()` mid-loop (let the loop end).
- If the game spans multiple files, keep them in the slug dir; only the top-level
  frame loop and entry need the async treatment. `import`s of sibling modules
  work as long as they sit next to main.py.

## 4. Build with pygbag
```
cd site/playable-src/<slug>
python3 -m pygbag --build main.py     # runs in background; it WILL hang on a
                                       # leftover server after writing the apk
```
- Wait until `build/web/<slug>.apk` exists, then **kill pygbag**
  (`pkill -f pygbag`) — it leaves a server listening, that's expected.
- pygbag 0.9.3 here writes the `.apk` + `.tar.gz` but NOT `index.html`. That's
  fine — we use a known-good template (next step).

## 5. Assemble the served build
- `mkdir -p site/public/play/<slug>`
- Copy `build/web/<slug>.apk` → `site/public/play/<slug>/<slug>.apk`
- Copy `site/public/play/p1/favicon.png` → `site/public/play/<slug>/favicon.png`
- Clone the template, swapping the bundle name (p1 → your slug). The 8 tokens to
  replace in `site/public/play/p1/index.html`:
  ```
  Loading p1 from p1.apk     apk = "p1.apk"      bundle = "p1"
  Title   : p1               Folder  : p1        /data/data/p1
  archive : "p1"             <title>p1</title>
  ```
  Use a perl/sed pass writing to `site/public/play/<slug>/index.html`.

## 6. Verify (no browser needed)
- `python3 -m py_compile main.py` (syntax).
- Native headless smoke test — must run the loop with **no traceback**:
  ```
  SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy timeout 4 python3 main.py 2>err.log
  ```
  Exit 124 (timeout) = it ran fine. Any `Traceback`/`Error` in err.log = a real
  bug to fix before declaring success.
- Confirm the apk contains your code: `unzip -l build/web/<slug>.apk | grep main.py`

## Notes
- The benign console lines `<slug>.apk 0`, `cannot download <slug>.apk`,
  `Received N of 0`, and the `statSync` uncaught-promise appear for EVERY pygbag
  build (including known-good p1) — they are NOT failures.
- `build/` is gitignored; only `main.py` + assets under `site/playable-src/<slug>/`
  and the served `site/public/play/<slug>/` get committed.
