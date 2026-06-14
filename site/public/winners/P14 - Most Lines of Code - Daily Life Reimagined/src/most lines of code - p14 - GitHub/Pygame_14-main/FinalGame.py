import pygame
import sys
import random
import math

# ==========================================================================
# SHARED WINDOW + THEME
# One window for the whole game. Each level is drawn onto its own native-size
# canvas and then centred over a shared purple-gradient + starfield backdrop,
# so every level keeps its own design while the game looks like one piece.
# ==========================================================================
pygame.init()

WIN_W, WIN_H = 1300, 700
window = pygame.display.set_mode((WIN_W, WIN_H))
pygame.display.set_caption("Daily Life Reimagined")
clock = pygame.time.Clock()


# ==========================================================================
# SOUND EFFECTS  —  synthesized in-memory (no audio files needed) and shared
# across every screen / level via play_sfx("name").
# ==========================================================================
import array

SOUND_ON = False
try:
    if pygame.mixer.get_init() is None:
        pygame.mixer.init(44100, -16, 2, 512)
    SOUND_ON = pygame.mixer.get_init() is not None
except Exception:
    SOUND_ON = False

_SR = 44100


def _tone(freq, dur, vol=0.5, wave="sine", decay=True):
    """One mono tone segment as a list of float samples in [-1, 1]."""
    n = max(1, int(_SR * dur))
    out = []
    for i in range(n):
        t = i / _SR
        if   wave == "square": v = 1.0 if math.sin(2*math.pi*freq*t) >= 0 else -1.0
        elif wave == "saw":    v = 2.0 * ((freq*t) % 1.0) - 1.0
        elif wave == "noise":  v = random.uniform(-1.0, 1.0)
        else:                  v = math.sin(2*math.pi*freq*t)
        env = (1.0 - i/n) if decay else 1.0          # linear fade-out
        atk = min(1.0, i / (0.005*_SR + 1))          # tiny attack, avoids clicks
        out.append(v * vol * env * atk)
    return out


def _make_sound(segments):
    """Concatenate mono float segments into a stereo 16-bit pygame Sound."""
    if not SOUND_ON:
        return None
    data = array.array("h")
    for seg in segments:
        for s in seg:
            v = int(max(-1.0, min(1.0, s)) * 32767)
            data.append(v); data.append(v)           # duplicate L / R
    try:
        return pygame.mixer.Sound(buffer=data.tobytes())
    except Exception:
        return None


def _seq(notes, wave="sine", vol=0.5, dur=0.09):
    return _make_sound([_tone(f, dur, vol, wave) for f in notes])


SFX = {}
if SOUND_ON:
    SFX["click"]   = _seq([880],                         dur=0.06, vol=0.40)
    SFX["select"]  = _seq([523, 784],                    dur=0.07, vol=0.40)
    SFX["confirm"] = _seq([660, 990],                    dur=0.09, vol=0.45)
    SFX["correct"] = _seq([523, 659, 784, 1047],         dur=0.09, vol=0.45)
    SFX["wrong"]   = _seq([220, 165],     wave="square", dur=0.15, vol=0.35)
    SFX["win"]     = _seq([523, 659, 784, 1047, 1319],   dur=0.12, vol=0.50)
    SFX["lose"]    = _seq([392, 330, 262, 196], wave="saw", dur=0.16, vol=0.40)
    SFX["catch"]   = _seq([1047, 1568],                  dur=0.05, vol=0.45)
    SFX["hit"]     = _make_sound([_tone(140, 0.20, 0.55, "noise")])
    SFX["alarm"]   = _make_sound([_tone(1000, 0.12, 0.40, "square"),
                                  _tone(1, 0.06, 0.0),
                                  _tone(1000, 0.12, 0.40, "square"),
                                  _tone(1, 0.30, 0.0)])


def play_sfx(name):
    """Play a named effect once; silent no-op if audio is unavailable."""
    s = SFX.get(name)
    if s is not None:
        try: s.play()
        except Exception: pass


def loop_sfx(name):
    """Play a named effect on repeat (e.g. the alarm)."""
    s = SFX.get(name)
    if s is not None:
        try: s.play(loops=-1)
        except Exception: pass


def stop_sfx(name):
    """Stop a looping effect."""
    s = SFX.get(name)
    if s is not None:
        try: s.stop()
        except Exception: pass


# ==========================================================================
# BACKGROUND MUSIC  —  synthesized looping tracks (no audio files).
# A sine wavetable keeps generation fast enough to build at startup.
#   chase     — Level 4.2 (pen chase) and Level 5 (escape to the bedroom)
#   compete   — Level 2.2 (catch the toothpaste)
#   celebrate — the completion / end screen
# ==========================================================================
_TS = 4096
_SINE = [math.sin(2 * math.pi * i / _TS) for i in range(_TS)]
MUSIC = {}
_music_channel = None
if SOUND_ON:
    try:
        pygame.mixer.set_num_channels(24)
        _music_channel = pygame.mixer.Channel(20)
        _music_channel.set_volume(0.55)        # sit under the sound effects
    except Exception:
        _music_channel = None


def _midi(m):
    return 440.0 * (2.0 ** ((m - 69) / 12.0))


def _add_note(buf, start, dur, freq, vol, wave="harm"):
    n = len(buf)
    s = int(start * _SR); ln = int(dur * _SR); e = min(n, s + ln)
    if e <= s:
        return
    atk = max(1, int(0.008 * _SR)); rel = max(1, int(0.05 * _SR))
    inc = freq * _TS / _SR
    ph = 0.0
    mask = _TS - 1
    for i in range(s, e):
        j = i - s
        if   j < atk:        env = j / atk
        elif j > ln - rel:   env = max(0.0, (ln - j) / rel)
        else:                env = 1.0
        idx = int(ph)
        if   wave == "harm":
            v = (_SINE[idx & mask] + 0.28 * _SINE[(idx * 2) & mask]
                 + 0.12 * _SINE[(idx * 3) & mask]) * 0.62
        elif wave == "saw":
            v = 2.0 * ((ph / _TS) % 1.0) - 1.0
        elif wave == "square":
            v = 1.0 if _SINE[idx & mask] >= 0 else -1.0
        else:
            v = _SINE[idx & mask]
        buf[i] += v * vol * env
        ph += inc


def _add_drum(buf, start, kind):
    n = len(buf); s = int(start * _SR)
    if kind == "kick":
        ln = int(0.13 * _SR)
        for i in range(s, min(n, s + ln)):
            j = i - s; env = max(0.0, 1 - j / ln)
            f = 130 * (1 - 0.55 * j / ln)         # pitch drop = punch
            buf[i] += math.sin(2 * math.pi * f * (j / _SR)) * 0.55 * env
    elif kind == "snare":
        ln = int(0.10 * _SR)
        for i in range(s, min(n, s + ln)):
            j = i - s; env = max(0.0, 1 - j / ln)
            buf[i] += (random.uniform(-1, 1) * 0.38 +
                       math.sin(2 * math.pi * 190 * (j / _SR)) * 0.18) * env
    elif kind == "hat":
        ln = int(0.035 * _SR)
        for i in range(s, min(n, s + ln)):
            j = i - s; env = max(0.0, 1 - j / ln)
            buf[i] += random.uniform(-1, 1) * 0.16 * env


def _finalize(buf, gain=0.85):
    if not SOUND_ON:
        return None
    peak = 1e-6
    for x in buf:
        if abs(x) > peak: peak = abs(x)
    scale = gain / peak
    data = array.array("h")
    for x in buf:
        v = int(max(-1.0, min(1.0, x * scale)) * 32767)
        data.append(v); data.append(v)
    try:
        return pygame.mixer.Sound(buffer=data.tobytes())
    except Exception:
        return None


def _compose(bpm, prog, third, melody, lead_wave="harm", bass_wave="saw"):
    """Build a looping track. prog: chord roots (one bar each). third: 3 minor /
    4 major. melody: (start_beat, midi, dur_beats) over the whole loop."""
    beat = 60.0 / bpm; bar = 4 * beat
    n = int(bar * len(prog) * _SR) + 8
    buf = [0.0] * n
    for bi, root in enumerate(prog):
        t0 = bi * bar
        for cn in (root, root + third, root + 7):        # sustained chord pad
            _add_note(buf, t0, bar * 0.97, _midi(cn), 0.13, wave="harm")
        for k in range(8):                                # eighth-note bass
            _add_note(buf, t0 + k * (beat / 2), (beat / 2) * 0.9,
                      _midi(root - 12), 0.5, wave=bass_wave)
        for k in range(4):                                # beat
            _add_drum(buf, t0 + k * beat, "kick")
            _add_drum(buf, t0 + k * beat + beat / 2, "hat")
            if k % 2 == 1:
                _add_drum(buf, t0 + k * beat, "snare")
    for (sb, mn, db) in melody:                           # lead melody
        _add_note(buf, sb * beat, db * beat * 0.95, _midi(mn), 0.26, wave=lead_wave)
    return _finalize(buf)


def _arp_melody(prog, patterns):
    """Eighth-note ostinato: 8 notes per bar from a per-root pattern."""
    mel = []
    for bi, root in enumerate(prog):
        pat = patterns[root]
        for k in range(8):
            mel.append((bi * 4 + k * 0.5, pat[k], 0.5))
    return mel


def build_music():
    if not SOUND_ON:
        return
    # ── compete: bright, sporty C major ─────────────────────────────────────
    cp = [60, 67, 69, 65]                                 # C  G  Am F
    MUSIC["compete"] = _compose(132, cp, 4, _arp_melody(cp, {
        60: [72, 76, 79, 76, 72, 74, 76, 79],
        67: [71, 74, 79, 74, 71, 74, 79, 83],
        69: [69, 72, 76, 72, 69, 72, 76, 81],
        65: [77, 81, 84, 81, 77, 81, 84, 81]}))
    # ── chase: tense, driving A minor ───────────────────────────────────────
    ch = [57, 57, 62, 64]                                 # Am Am Dm E
    MUSIC["chase"] = _compose(150, ch, 3, _arp_melody(ch, {
        57: [69, 72, 76, 72, 69, 72, 76, 79],
        62: [74, 77, 81, 77, 74, 77, 81, 84],
        64: [76, 80, 83, 80, 76, 80, 83, 86]}),
        lead_wave="square")
    # ── celebrate: triumphant C major fanfare ───────────────────────────────
    ce = [60, 65, 67, 60]                                 # C  F  G  C
    MUSIC["celebrate"] = _compose(120, ce, 4, [
        (0, 72, 1), (1, 76, 1), (2, 79, 1), (3, 84, 1),
        (4, 81, 1), (5, 77, 1), (6, 81, 1), (7, 84, 1),
        (8, 83, 1), (9, 79, 1), (10, 86, 1), (11, 83, 1),
        (12, 84, 1), (13, 79, 1), (14, 76, 1), (15, 72, 2)])


def play_music(name):
    """Loop a named background track on the dedicated music channel."""
    if _music_channel is None:
        return
    s = MUSIC.get(name)
    if s is None:
        return
    try:
        _music_channel.play(s, loops=-1)
    except Exception:
        pass


def stop_music():
    if _music_channel is not None:
        try: _music_channel.stop()
        except Exception: pass


build_music()


def _build_backdrop():
    # purple gradient (same look as the start / end screens)
    surf = pygame.Surface((WIN_W, WIN_H))
    for y in range(WIN_H):
        ratio = y / WIN_H
        r = int(35 + ratio * 30)
        g = int(20 + ratio * 10)
        b = int(90 + ratio * 90)
        pygame.draw.line(surf, (r, g, b), (0, y), (WIN_W, y))
    # static starfield
    for _ in range(180):
        x = random.randint(0, WIN_W)
        y = random.randint(0, WIN_H)
        s = random.randint(1, 3)
        pygame.draw.circle(surf, (255, 255, 255), (x, y), s)
    return surf


BACKDROP = _build_backdrop()


def present(screen):
    """Composite a level's native canvas, centred, over the themed backdrop."""
    window.blit(BACKDROP, (0, 0))
    window.blit(screen, ((WIN_W - screen.get_width()) // 2,
                         (WIN_H - screen.get_height()) // 2))
    pygame.display.flip()


def quit_game():
    pygame.quit()
    sys.exit()


# ==========================================================================
# CHOSEN CHARACTER  —  selected on the start screen, used as the player token
# in Level 4.2 (catch the pen) and Level 5 (escape the monsters).
# ==========================================================================
CHARACTER_IMAGE_FILES = ["harry.png", "lebron.png", "ronaldo.png",
                         "johnwick.png", "spiderman.png"]
SELECTED_CHARACTER = None          # index into CHARACTER_IMAGE_FILES
_char_sprite_cache = {}


def set_selected_character(idx):
    """Remember which character the player picked on the start screen."""
    global SELECTED_CHARACTER
    SELECTED_CHARACTER = idx


def character_sprite(size):
    """Return the chosen character's image scaled to fit a size x size box
    (aspect preserved), or None if no character / image is unavailable."""
    if SELECTED_CHARACTER is None:
        return None
    key = (SELECTED_CHARACTER, size)
    if key in _char_sprite_cache:
        return _char_sprite_cache[key]
    spr = None
    try:
        img = pygame.image.load(CHARACTER_IMAGE_FILES[SELECTED_CHARACTER]).convert_alpha()
        iw, ih = img.get_size()
        scale = min(size / iw, size / ih)
        spr = pygame.transform.smoothscale(img, (max(1, int(iw * scale)),
                                                 max(1, int(ih * scale))))
    except (pygame.error, FileNotFoundError, IndexError, TypeError):
        spr = None
    _char_sprite_cache[key] = spr
    return spr


def draw_player_character(surf, cx, cy, size, fallback_color):
    """Draw the chosen character centred at (cx, cy). Falls back to the old
    coloured token when no character image is available."""
    spr = character_sprite(size)
    if spr is not None:
        surf.blit(spr, spr.get_rect(center=(int(cx), int(cy))))
    else:
        r = size // 2
        pygame.draw.circle(surf, fallback_color, (int(cx), int(cy)), r)
        pygame.draw.circle(surf, (255, 255, 255), (int(cx), int(cy)), r, 3)


# ==========================================================================
# LEVEL 2 — "Brush & Dodge!"  (defined at module level, unique names)
# ==========================================================================
WIDTH, HEIGHT = 900, 650
FPS = 60

WHITE       = (255, 255, 255)
BLACK       = (  0,   0,   0)
DARK_BG     = ( 12,  10,  30)
SHADOW_COL  = ( 15,  15,  35)
MINT        = ( 80, 220, 180)
CYAN        = (  0, 200, 255)
BLUE_PASTE  = ( 40, 120, 220)
WHITE_PASTE = (230, 240, 255)
YELLOW      = (255, 220,  60)
RED         = (220,  50,  50)
GREEN       = ( 60, 200,  80)
ORANGE      = (255, 150,  40)
PINK        = (255, 100, 160)
LIGHT_GREY  = (180, 180, 210)
PANEL_DARK  = ( 10,  12,  35)

font_big   = pygame.font.SysFont("Arial", 42, bold=True)
font_med   = pygame.font.SysFont("Arial", 26, bold=True)
font_small = pygame.font.SysFont("Arial", 19)
font_tiny  = pygame.font.SysFont("Arial", 15)

# ── Visual helpers ──────────────────────────────────────────────────────────
def vgradient(surf, top, bottom, rect=None):
    """Smooth vertical gradient fill."""
    if rect is None:
        x, y, w, h = 0, 0, surf.get_width(), surf.get_height()
    else:
        x, y, w, h = rect
    for i in range(h):
        t = i / max(1, h - 1)
        col = (int(top[0] + (bottom[0]-top[0])*t),
               int(top[1] + (bottom[1]-top[1])*t),
               int(top[2] + (bottom[2]-top[2])*t))
        pygame.draw.line(surf, col, (x, y+i), (x+w, y+i))

def wrap_lines(font, text, max_w):
    """Split text into lines that each fit within max_w pixels."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if font.size(trial)[0] <= max_w:
            cur = trial
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def round_panel(surf, rect, fill, border=None, radius=18, border_w=2, alpha=255):
    """Translucent rounded panel with optional border."""
    x, y, w, h = rect
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(s, (*fill, alpha), (0, 0, w, h), border_radius=radius)
    if border:
        pygame.draw.rect(s, (*border, 255), (0, 0, w, h), border_w, border_radius=radius)
    surf.blit(s, (x, y))

# Gradient palettes
BG_TOP   = ( 24,  18,  54)
BG_BOT   = (  8,   6,  22)
SKY_TOP  = ( 10,  30,  40)
SKY_BOT  = (  4,  12,  10)

STATE_TITLE      = "title"
STATE_SHADOW     = "shadow"
STATE_TRANSITION = "transition"
STATE_STORY      = "story"
STATE_CATCH      = "catch"
STATE_GAMEOVER   = "gameover"
STATE_WIN        = "win"

# ── Shadow shapes ─────────────────────────────────────────────────────────────
def draw_toothbrush_shadow(surf, cx, cy, scale=1.0):
    s = pygame.Surface((240, 90), pygame.SRCALPHA)
    c = (*SHADOW_COL, 255)
    pygame.draw.rect(s, c, (0, 32, 170, 26), border_radius=13)
    pygame.draw.rect(s, c, (162, 10, 70, 68), border_radius=11)
    for i in range(6):
        pygame.draw.rect(s, c, (168 + i*9, 2, 6, 22), border_radius=3)
    sc = pygame.transform.rotozoom(s, 0, scale)
    surf.blit(sc, (cx - sc.get_width()//2, cy - sc.get_height()//2))

def draw_fork_shadow(surf, cx, cy, scale=1.0):
    s = pygame.Surface((90, 220), pygame.SRCALPHA)
    c = (*SHADOW_COL, 255)
    pygame.draw.rect(s, c, (36, 90, 18, 130), border_radius=9)
    for i in range(4):
        pygame.draw.rect(s, c, (12 + i*17, 0, 10, 100), border_radius=5)
    sc = pygame.transform.rotozoom(s, 0, scale)
    surf.blit(sc, (cx - sc.get_width()//2, cy - sc.get_height()//2))

def draw_comb_shadow(surf, cx, cy, scale=1.0):
    s = pygame.Surface((220, 90), pygame.SRCALPHA)
    c = (*SHADOW_COL, 255)
    pygame.draw.rect(s, c, (0, 0, 220, 32), border_radius=8)
    for i in range(15):
        pygame.draw.rect(s, c, (8 + i*14, 30, 9, 58), border_radius=4)
    sc = pygame.transform.rotozoom(s, 0, scale)
    surf.blit(sc, (cx - sc.get_width()//2, cy - sc.get_height()//2))

def draw_scissors_shadow(surf, cx, cy, scale=1.0):
    s = pygame.Surface((170, 170), pygame.SRCALPHA)
    c = (*SHADOW_COL, 255)
    pygame.draw.polygon(s, c, [(85,85),(32,8),(55,8),(85,85)])
    pygame.draw.polygon(s, c, [(85,85),(115,8),(138,8),(85,85)])
    pygame.draw.ellipse(s, c, (28,95,46,60))
    pygame.draw.ellipse(s, DARK_BG, (37,107,28,38))
    pygame.draw.ellipse(s, c, (96,95,46,60))
    pygame.draw.ellipse(s, DARK_BG, (105,107,28,38))
    sc = pygame.transform.rotozoom(s, 0, scale)
    surf.blit(sc, (cx - sc.get_width()//2, cy - sc.get_height()//2))

def draw_spoon_shadow(surf, cx, cy, scale=1.0):
    s = pygame.Surface((90, 220), pygame.SRCALPHA)
    c = (*SHADOW_COL, 255)
    pygame.draw.rect(s, c, (36, 80, 18, 140), border_radius=9)
    pygame.draw.ellipse(s, c, (18, 8, 54, 80))
    sc = pygame.transform.rotozoom(s, 0, scale)
    surf.blit(sc, (cx - sc.get_width()//2, cy - sc.get_height()//2))

SHADOW_OPTIONS = [
    {"name": "Toothbrush", "draw": draw_toothbrush_shadow},
    {"name": "Fork",       "draw": draw_fork_shadow},
    {"name": "Comb",       "draw": draw_comb_shadow},
    {"name": "Scissors",   "draw": draw_scissors_shadow},
    {"name": "Spoon",      "draw": draw_spoon_shadow},
]

# ── Monster ───────────────────────────────────────────────────────────────────
def draw_monster(surf, cx, cy, anim, size=1.0):
    def sc(v): return int(v * size)
    blob_pts = []
    for a in range(0, 360, 10):
        rad = math.radians(a)
        wobble = 1 + 0.08 * math.sin(anim * 2 + a * 0.08)
        blob_pts.append((cx + sc(62) * wobble * math.cos(rad),
                         cy + sc(72) * wobble * math.sin(rad)))
    pygame.draw.polygon(surf, BLUE_PASTE, blob_pts)
    for offset in [0, 1.2, 2.4]:
        swirl_pts = []
        for a in range(0, 340, 8):
            rad = math.radians(a)
            dist = sc(45 + 14 * math.sin(a * 0.035 + offset + anim * 0.4))
            swirl_pts.append((cx + dist * math.cos(rad), cy + dist * math.sin(rad)))
        if len(swirl_pts) >= 2:
            pygame.draw.lines(surf, WHITE_PASTE, False, swirl_pts, sc(5))
    for side, sign in [(-1, -1), (1, 1)]:
        drape = []
        for i in range(8):
            t = i / 7
            drape.append((cx + sign * sc(55 + 10 * math.sin(t * math.pi)),
                          cy + sc(30) + int(t * sc(55))))
        drape += [(cx + sign * sc(20), cy + sc(88)), (cx, cy + sc(70))]
        if len(drape) >= 3:
            pygame.draw.polygon(surf, BLUE_PASTE, drape)
            pygame.draw.lines(surf, WHITE_PASTE, False, drape[:6], sc(4))
    spike_pts = [(cx + sc(int(8 * math.sin(i/19 * math.pi * 3))),
                  cy - sc(72) - int(i/19 * sc(38))) for i in range(20)]
    if len(spike_pts) >= 2:
        pygame.draw.lines(surf, BLUE_PASTE, False, spike_pts, sc(9))
        pygame.draw.lines(surf, WHITE_PASTE, False, spike_pts, sc(3))
    for ex_off in [-sc(22), sc(22)]:
        ex, ey = cx + ex_off, cy - sc(18)
        pygame.draw.circle(surf, (200, 220, 255), (ex, ey), sc(17))
        pygame.draw.circle(surf, (30, 120, 220), (ex, ey), sc(10))
        pygame.draw.circle(surf, BLACK, (ex, ey), sc(5))
        pygame.draw.circle(surf, WHITE, (ex + sc(4), ey - sc(4)), sc(3))
        pygame.draw.circle(surf, (10, 40, 120), (ex, ey), sc(17), sc(2))
    pygame.draw.line(surf, BLACK, (cx-sc(35), cy-sc(36)), (cx-sc(12), cy-sc(30)), sc(4))
    pygame.draw.line(surf, BLACK, (cx+sc(12), cy-sc(30)), (cx+sc(35), cy-sc(36)), sc(4))
    mouth_open = sc(int(14 + 8 * abs(math.sin(anim))))
    pygame.draw.ellipse(surf, (10, 10, 20),
                        pygame.Rect(cx-sc(32), cy+sc(10), sc(64), mouth_open+sc(10)))
    for i in range(5):
        tx = cx - sc(28) + i * sc(14)
        pygame.draw.polygon(surf, WHITE, [(tx, cy+sc(12)), (tx+sc(12), cy+sc(12)), (tx+sc(6), cy+sc(26))])
    for i in range(4):
        tx = cx - sc(22) + i * sc(14)
        pygame.draw.polygon(surf, WHITE, [
            (tx, cy+sc(10)+mouth_open+sc(8)),
            (tx+sc(12), cy+sc(10)+mouth_open+sc(8)),
            (tx+sc(6), cy+sc(10)+mouth_open-sc(2))])
    pygame.draw.polygon(surf, (10, 40, 120), blob_pts, sc(3))


# ── Blob  —  SLOWER speeds ────────────────────────────────────────────────────
class Blob:
    WAVE_COLOURS = [
        [(80, 220, 180), (255, 255, 255)],
        [(40, 120, 220), (200, 240, 255)],
        [(255, 100, 160), (255, 220, 60)],
        [(180, 60, 220), (255, 120, 40)],
        [(220, 30, 30),  (255, 200, 0)],
    ]
    def __init__(self, wave):
        wave = min(wave, len(self.WAVE_COLOURS) - 1)
        self.colour  = random.choice(self.WAVE_COLOURS[wave])
        self.x       = random.randint(60, WIDTH - 60)
        self.y       = -25
        self.r       = random.randint(12, 22)
        # ── SLOWER: was ~2.8-5.0; now 1.2-2.2 (+tiny wave bonus) ──────────
        self.vy      = random.uniform(1.2 + wave * 0.2, 2.2 + wave * 0.2)
        self.vx      = random.uniform(-0.5 - wave * 0.08, 0.5 + wave * 0.08)
        self.wobble  = random.uniform(0, math.pi * 2)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.wobble += 0.18

    def draw(self, surf):
        # squarish droplet — rounded square that gently squashes/stretches
        side   = self.r * 2 + 2*math.sin(self.wobble)          # subtle breathing
        half   = side / 2
        radius = max(3, int(side * 0.32))                       # rounded corners
        x, y   = int(self.x), int(self.y)
        # body
        body = pygame.Rect(0, 0, int(side), int(side))
        body.center = (x, y)
        pygame.draw.rect(surf, self.colour, body, border_radius=radius)
        pygame.draw.rect(surf, WHITE, body, 1, border_radius=radius)
        # glossy highlight in the upper-left
        hl = max(2, int(self.r * 0.42))
        pygame.draw.rect(surf, WHITE,
                         (x - int(half*0.55), y - int(half*0.55), hl, hl),
                         border_radius=max(1, hl//2))


# ── Particle ──────────────────────────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, col):
        self.x = x; self.y = y
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-5, -1)
        self.col = col
        self.life = random.randint(20, 40)
    def update(self):
        self.x += self.vx; self.y += self.vy
        self.vy += 0.25; self.life -= 1
    def draw(self, surf):
        a = max(0, int(255 * self.life / 40))
        s = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.col, a), (5, 5), 5)
        surf.blit(s, (int(self.x)-5, int(self.y)-5))


# ── Shadow game ───────────────────────────────────────────────────────────────
class ShadowGame:
    ROUNDS_TO_WIN = 1
    def __init__(self):
        self.total_score = 0
        self.rounds_won  = 0
        self.reset_round()

    def reset_round(self):
        self.tries_left = 2; self.answered = False
        self.result_msg = ""; self.result_col = WHITE
        self.result_timer = 0; self.pulse = 0.0
        # Always the toothbrush — short-answer question
        self.current = next(o for o in SHADOW_OPTIONS if o["name"] == "Toothbrush")
        self.input_text = ""

    def submit(self):
        if self.answered: return
        answer = self.input_text.strip().lower()
        if not answer:
            return
        if answer == self.current["name"].lower():
            pts = 10 if self.tries_left == 2 else 5
            self.total_score += pts
            self.result_msg = f"✓ Correct! +{pts} pts"
            self.result_col = GREEN; self.answered = True
            self.rounds_won += 1; self.result_timer = int(FPS * 1.6)
            play_sfx("correct")
        else:
            self.tries_left -= 1
            self.input_text = ""
            play_sfx("wrong")
            if self.tries_left == 0:
                self.result_msg = f"✗ It was a {self.current['name']}!"
                self.result_col = RED; self.answered = True
                self.result_timer = int(FPS * 1.8)
            else:
                self.result_msg = "✗ Wrong — 1 try left!"
                self.result_col = ORANGE; self.result_timer = int(FPS * 1.0)

    @property
    def finished(self): return self.rounds_won >= self.ROUNDS_TO_WIN

    def update(self):
        self.pulse += 0.05
        if self.result_timer > 0:
            self.result_timer -= 1
            if self.result_timer <= 0 and self.answered:
                self.reset_round()

    def draw(self, surf):
        vgradient(surf, (18, 22, 48), (6, 8, 22))
        t = font_med.render("🔦  SHADOW GAME", True, MINT)
        surf.blit(t, (WIDTH//2 - t.get_width()//2, 14))
        prog = font_small.render(
            f"Rounds: {self.rounds_won}/{self.ROUNDS_TO_WIN}   "
            f"Score: {self.total_score}   "
            f"Tries: {'●'*self.tries_left}{'○'*(2-self.tries_left)}", True, YELLOW)
        surf.blit(prog, (WIDTH//2 - prog.get_width()//2, 50))
        cx, cy, r = WIDTH//2, 220, 140
        for dr in range(r, r-35, -4):
            a = int(50*(r-dr)/35)
            g = pygame.Surface((dr*2, dr*2), pygame.SRCALPHA)
            pygame.draw.circle(g, (255,255,180,a), (dr,dr), dr)
            surf.blit(g, (cx-dr, cy-dr))
        pygame.draw.circle(surf, (45, 45, 75), (cx, cy), r)
        self.current["draw"](surf, cx, cy, scale=1.0+0.05*math.sin(self.pulse))
        inst = font_tiny.render("What everyday object casts this shadow?", True, LIGHT_GREY)
        surf.blit(inst, (WIDTH//2 - inst.get_width()//2, 328))
        # ── Short-answer text box ─────────────────────────────────────────
        box_w, box_h = 360, 52
        box_x = WIDTH//2 - box_w//2
        box_y = 372
        pygame.draw.rect(surf, (55,55,95), (box_x, box_y, box_w, box_h), border_radius=12)
        pygame.draw.rect(surf, MINT, (box_x, box_y, box_w, box_h), 2, border_radius=12)
        caret = "|" if (int(self.pulse*2) % 2 == 0 and not self.answered) else ""
        if self.input_text:
            it = font_med.render(self.input_text + caret, True, WHITE)
        else:
            it = font_med.render("Type your answer..." + caret, True, (120,120,150))
        surf.blit(it, (box_x + 16, box_y + box_h//2 - it.get_height()//2))
        if self.result_msg:
            rt = font_med.render(self.result_msg, True, self.result_col)
            surf.blit(rt, (WIDTH//2 - rt.get_width()//2, 446))
        hint = font_tiny.render("Type the object's name and press  ENTER", True, (90,90,120))
        surf.blit(hint, (WIDTH//2 - hint.get_width()//2, 500))
        bar_w = 500; bar_x = WIDTH//2 - bar_w//2
        pygame.draw.rect(surf, (50,50,80), (bar_x, HEIGHT-28, bar_w, 12), border_radius=6)
        fill = int(bar_w * self.rounds_won / self.ROUNDS_TO_WIN)
        if fill > 0:
            pygame.draw.rect(surf, GREEN, (bar_x, HEIGHT-28, fill, 12), border_radius=6)
        lbl = font_tiny.render("Identify the shadow to unlock the Catch game!", True, (100,100,140))
        surf.blit(lbl, (WIDTH//2 - lbl.get_width()//2, HEIGHT-48))


# ── Catch game  —  MONSTER FIRES 20 FAST SHOTS, CATCH 4 TO QUALIFY ────────────
class CatchGame:
    SHOTS_TO_FIRE = 20
    QUALIFY       = 6           # need to catch more now
    FIRE_INTERVAL = 10          # frames between shots — faster barrage

    def __init__(self, shadow_score=0):
        self.score         = shadow_score
        self.caught        = 0
        self.shots_fired   = 0
        self.fire_timer    = FPS          # short delay before the first shot
        self.blobs      : list[Blob]     = []
        self.particles  : list[Particle] = []
        self.monster_x  = WIDTH // 2
        self.monster_dir = 1
        self.monster_spd = 6.0      # faster, more erratic patrol
        self.anim        = 0.0
        self.done        = False

    def init_player(self):
        self.px = WIDTH // 2
        self.py = HEIGHT - 70

    @property
    def qualified(self):
        return self.caught >= self.QUALIFY

    def update(self, keys):
        if self.done: return
        self.anim += 0.07

        # monster patrol
        self.monster_x += self.monster_spd * self.monster_dir
        if self.monster_x > WIDTH - 70: self.monster_dir = -1
        if self.monster_x < 70:         self.monster_dir = 1

        # player — left / right only
        spd = 6
        if (keys[pygame.K_a] or keys[pygame.K_LEFT])  and self.px - 30 > 0:     self.px -= spd
        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and self.px + 30 < WIDTH: self.px += spd

        # ── Monster fires 20 fast shots ───────────────────────────────────
        if self.shots_fired < self.SHOTS_TO_FIRE:
            if self.fire_timer > 0:
                self.fire_timer -= 1
            else:
                b = Blob(random.randint(0, len(Blob.WAVE_COLOURS) - 1))
                b.x  = self.monster_x
                b.y  = 130
                b.vy = random.uniform(8.5, 11.0)       # really fast
                b.vx = random.uniform(-2.5, 2.5)       # more horizontal drift
                self.blobs.append(b)
                self.shots_fired += 1
                self.fire_timer = self.FIRE_INTERVAL

        # update blobs
        for b in self.blobs[:]:
            b.update()
            if abs(b.x - self.px) < 26 and abs(b.y - self.py) < 18:
                self.blobs.remove(b)
                self.caught += 1
                self.score += 1
                play_sfx("catch")
                for _ in range(10): self.particles.append(Particle(b.x, b.y, b.colour))
                if self.qualified:        # caught 4 — advance to next level right away
                    self.done = True
                    return
            elif b.y > HEIGHT + 30:
                self.blobs.remove(b)

        # particles
        for p in self.particles[:]:
            p.update()
            if p.life <= 0: self.particles.remove(p)

        # finished once all shots are fired and off the screen
        if self.shots_fired >= self.SHOTS_TO_FIRE and len(self.blobs) == 0:
            self.done = True

    def draw(self, surf):
        vgradient(surf, SKY_TOP, SKY_BOT)
        random.seed(42)
        for _ in range(70):
            sx, sy = random.randint(0, WIDTH), random.randint(0, HEIGHT)
            c = random.randint(50, 110)
            pygame.draw.circle(surf, (c, c, c+30), (sx, sy), 1)
        random.seed()

        # subtle ground glow at the player's lane
        glow = pygame.Surface((WIDTH, 120), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (40, 90, 70, 60), (-50, 40, WIDTH+100, 120))
        surf.blit(glow, (0, HEIGHT-120))

        title = font_small.render("Catch the toothpaste!", True, CYAN)
        surf.blit(title, (WIDTH//2 - title.get_width()//2, 10))
        sc_t = font_small.render(f"Score: {self.score}", True, YELLOW)
        surf.blit(sc_t, (10, 10))

        col = GREEN if self.qualified else WHITE
        caught_t = font_small.render(f"Caught: {self.caught} / {self.QUALIFY} needed", True, col)
        surf.blit(caught_t, (WIDTH - caught_t.get_width() - 10, 10))
        shots_t = font_small.render(f"Shots: {self.shots_fired}/{self.SHOTS_TO_FIRE}", True, LIGHT_GREY)
        surf.blit(shots_t, (WIDTH - shots_t.get_width() - 10, 32))

        draw_monster(surf, int(self.monster_x), 100, self.anim)

        for b in self.blobs:  b.draw(surf)
        for p in self.particles: p.draw(surf)

        px, py = int(self.px), int(self.py)
        pygame.draw.rect(surf, (200,160,80), (px-6, py-36, 12, 36), border_radius=5)
        pygame.draw.rect(surf, WHITE,        (px-26, py-14, 52, 20), border_radius=7)
        pygame.draw.rect(surf, MINT,         (px-26, py-14, 52, 20), 2, border_radius=7)
        for i in range(7):
            pygame.draw.line(surf, MINT, (px-23+i*8, py-14), (px-23+i*8, py-24), 2)

        hint = font_tiny.render("A / D  or  ← / →  to move your toothbrush", True, (60,140,80))
        surf.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT-24))


# ── Title ─────────────────────────────────────────────────────────────────────
def draw_title(surf, anim):
    vgradient(surf, BG_TOP, BG_BOT)
    # drifting starfield
    random.seed(7)
    for _ in range(90):
        sx = random.randint(0, WIDTH)
        sy = random.randint(0, HEIGHT)
        tw = 0.5 + 0.5*math.sin(anim*1.5 + sx*0.05)
        c = int(120 + 120*tw)
        pygame.draw.circle(surf, (c, c, min(255, c+40)), (sx, sy), 1)
    random.seed()

    t1 = font_big.render("🪥  BRUSH & DODGE!", True, CYAN)
    surf.blit(t1, (WIDTH//2 - t1.get_width()//2, 80))
    draw_monster(surf, WIDTH//2+180, 270, anim, size=1.3)
    draw_toothbrush_shadow(surf, WIDTH//2-160, 270, scale=1.2)
    ql = font_small.render("Can you identify its shadow?", True, LIGHT_GREY)
    surf.blit(ql, (WIDTH//2-160 - ql.get_width()//2, 340))

    round_panel(surf, (WIDTH//2-300, 392, 600, 80), PANEL_DARK,
                border=(60, 70, 130), radius=16, alpha=180)
    for i, line in enumerate([
        "STAGE 1 — Shadow Game: Identify the mystery shadow",
        "STAGE 2 — Catch Game:  Catch 6 of the monster's 20 shots!",
    ]):
        lt = font_small.render(line, True, LIGHT_GREY)
        surf.blit(lt, (WIDTH//2 - lt.get_width()//2, 404+i*34))

    pulse = 1.0 + 0.1 * math.sin(anim * 3)
    s2 = font_med.render("Press  ENTER  to start", True, YELLOW)
    sc2 = pygame.transform.rotozoom(s2, 0, pulse)
    surf.blit(sc2, (WIDTH//2 - sc2.get_width()//2, 524))


# ── Transition ────────────────────────────────────────────────────────────────
def draw_transition(surf, anim, shadow_score, timer, total=FPS*3):
    vgradient(surf, (16, 30, 24), (6, 10, 18))
    draw_monster(surf, WIDTH//2, HEIGHT//2-20, anim, size=1.5)
    t1 = font_big.render("STAGE CLEAR!", True, GREEN)
    surf.blit(t1, (WIDTH//2 - t1.get_width()//2, 60))
    t2 = font_med.render(f"Shadow Score: {shadow_score} pts", True, YELLOW)
    surf.blit(t2, (WIDTH//2 - t2.get_width()//2, 120))
    t3 = font_small.render("Catch at least 6 of the monster's 20 shots!", True, LIGHT_GREY)
    surf.blit(t3, (WIDTH//2 - t3.get_width()//2, 165))
    bar_w = 400; fill = int(bar_w * timer / total)
    pygame.draw.rect(surf, (50,50,80), (WIDTH//2-bar_w//2, HEIGHT-60, bar_w, 16), border_radius=8)
    pygame.draw.rect(surf, CYAN,       (WIDTH//2-bar_w//2, HEIGHT-60, fill, 16), border_radius=8)
    ct = font_tiny.render("Starting catch game...", True, (80,80,110))
    surf.blit(ct, (WIDTH//2 - ct.get_width()//2, HEIGHT-38))


# ── Story scene ───────────────────────────────────────────────────────────────
STORY_TEXT = ("You go to brush your teeth and your toothpaste becomes a monster. "
              "You have to catch 6 drops of toothpaste to revert your toothpaste "
              "back and to brush your teeth.")

def draw_story(surf, anim):
    vgradient(surf, (20, 16, 46), (6, 6, 20))
    draw_monster(surf, WIDTH//2, 190, anim, size=1.3)

    lines = wrap_lines(font_med, STORY_TEXT, 720)
    block_h = len(lines) * 38
    panel_y = 320
    round_panel(surf, (WIDTH//2-380, panel_y-20, 760, block_h+50), PANEL_DARK,
                border=(70, 80, 150), radius=18, alpha=190)
    for i, ln in enumerate(lines):
        lt = font_med.render(ln, True, WHITE_PASTE)
        surf.blit(lt, (WIDTH//2 - lt.get_width()//2, panel_y + i*38))

    pulse = 1.0 + 0.08 * math.sin(anim * 3)
    cont = font_small.render("Press  ENTER  to continue", True, YELLOW)
    sc = pygame.transform.rotozoom(cont, 0, pulse)
    surf.blit(sc, (WIDTH//2 - sc.get_width()//2, HEIGHT-70))


# ── level 5 ──────────────────────────────────────────────────────────────────
def run_level5():
    game_time = monsters = monster_timer = game_over = won = lose_msg = player = proceed_btn = None
    pygame.init()

    # Constants
    TILE, COLS, ROWS = 20, 65, 35
    SW, SH = 1300, 700
    FPS, GAME_SECS, SPEED = 60, 20, 2.75

    # Colors
    WHITE, BLACK, RED, GREEN, BLUE = (255,255,255), (0,0,0), (220,50,50), (60,210,80), (80,140,255)
    FLOOR, WALL, LASER_COLOR = (160,140,120), (100,60,50), (100, 255, 150)

    screen = pygame.display.set_mode((SW, SH))
    pygame.display.set_caption("Escape the Haunted House!")
    clock = pygame.time.Clock()
    fL, fM, fS = pygame.font.Font(None, 72), pygame.font.Font(None, 40), pygame.font.Font(None, 26)

    # ── EXTENDED MAZE MAP ──────────────────────────────────────────────────────
    def make_map():
        g = [[0]*COLS for _ in range(ROWS)]

        def wall(r1, c1, r2, c2):
            for r in range(max(0,r1), min(ROWS,r2+1)):
                for c in range(max(0,c1), min(COLS,c2+1)):
                    g[r][c] = 1

        # Border
        for r in range(ROWS):
            g[r][0] = g[r][COLS-1] = 1
        for c in range(COLS):
            g[0][c] = g[ROWS-1][c] = 1

        # ── EXTENSIVE WALLS (many obstacles) ──
        # Horizontal barriers
        wall(7, 5, 7, 15)
        wall(7, 22, 7, 32)
        wall(7, 40, 7, 50)
        wall(7, 58, 7, 63)

        wall(14, 8, 14, 18)
        wall(14, 28, 14, 38)
        wall(14, 48, 14, 58)

        wall(21, 6, 21, 16)
        wall(21, 26, 21, 36)
        wall(21, 44, 21, 54)
        wall(21, 60, 21, 63)

        wall(28, 10, 28, 20)
        wall(28, 32, 28, 42)
        wall(28, 52, 28, 62)

        # Vertical barriers
        for r in range(5, 12):
            g[r][20] = 1
        for r in range(5, 12):
            g[r][35] = 1
        for r in range(5, 12):
            g[r][52] = 1

        for r in range(12, 19):
            g[r][12] = 1
        for r in range(12, 19):
            g[r][42] = 1
        for r in range(12, 19):
            g[r][60] = 1

        for r in range(20, 27):
            g[r][22] = 1
        for r in range(20, 27):
            g[r][50] = 1

        # Additional maze complexity
        wall(10, 35, 13, 35)
        wall(17, 20, 20, 20)
        wall(24, 38, 27, 38)
        wall(30, 12, 33, 12)

        return g

    tile_grid = make_map()

    # ── SPIKE OBSTACLES (always deadly) ────────────────────────────────────────
    class Spike:
        def __init__(self, r, c):
            """Spike trap at grid position (r, c)"""
            self.rect = pygame.Rect(c*TILE, r*TILE, TILE, TILE)

        def draw(self, surf):
            # Draw spike pattern
            pygame.draw.rect(surf, (200, 80, 80), self.rect)
            # Draw spikes
            cx, cy = self.rect.centerx, self.rect.centery
            pygame.draw.polygon(surf, (255, 100, 100), [(cx, cy-6), (cx+6, cy+4), (cx-6, cy+4)])
            pygame.draw.polygon(surf, (255, 100, 100), [(cx-5, cy-4), (cx-8, cy+5), (cx, cy+3)])
            pygame.draw.polygon(surf, (255, 100, 100), [(cx+5, cy-4), (cx+8, cy+5), (cx, cy+3)])

    # ── LASER OBSTACLES (on/off toggle) ────────────────────────────────────────
    class Laser:
        def __init__(self, r, c, direction, length):
            """
            direction: 'h' (horizontal) or 'v' (vertical)
            length: how many tiles it spans
            """
            self.r = r
            self.c = c
            self.direction = direction
            self.length = length
            self.on_time = 0.0
            self.cycle_time = 4.0  # 2 sec on, 2 sec off
            self.is_on = False

        def update(self, dt):
            self.on_time += dt
            if self.on_time >= self.cycle_time:
                self.on_time = 0.0
            # On for first 2 seconds of cycle
            self.is_on = self.on_time < 2.0

        def get_rects(self):
            """Return list of tile rects occupied by this laser."""
            rects = []
            if self.direction == 'h':
                for i in range(self.length):
                    rects.append(pygame.Rect((self.c + i)*TILE, self.r*TILE, TILE, TILE))
            else:  # vertical
                for i in range(self.length):
                    rects.append(pygame.Rect(self.c*TILE, (self.r + i)*TILE, TILE, TILE))
            return rects

        def draw(self, surf):
            if self.is_on:
                for rect in self.get_rects():
                    pygame.draw.rect(surf, LASER_COLOR, rect)
                    pygame.draw.rect(surf, (200, 255, 200), rect, 2)

    # Create laser obstacles throughout the map
    lasers = [
        Laser(5, 25, 'h', 8),
        Laser(8, 12, 'v', 6),
        Laser(11, 38, 'h', 8),
        Laser(14, 5, 'v', 8),
        Laser(15, 48, 'h', 7),
        Laser(18, 15, 'v', 7),
        Laser(18, 55, 'v', 6),
        Laser(22, 30, 'h', 8),
        Laser(25, 28, 'h', 7),
        Laser(28, 10, 'v', 6),
    ]

    # Create spike obstacles throughout the map
    spikes = [
        Spike(6, 12),
        Spike(9, 28),
        Spike(9, 52),
        Spike(13, 42),
        Spike(16, 8),
        Spike(19, 30),
        Spike(24, 18),
        Spike(27, 45),
        Spike(30, 25),
    ]

    # Render background
    bg_surf = pygame.Surface((SW, SH))
    for r in range(ROWS):
        for c in range(COLS):
            col = WALL if tile_grid[r][c] else FLOOR
            pygame.draw.rect(bg_surf, col, (c*TILE, r*TILE, TILE, TILE))

    # ── BEDROOM (destination) ──────────────────────────────────────────────────
    BED_RECT = pygame.Rect(1*TILE, 1*TILE, 10*TILE, 6*TILE)

    def draw_bedroom(surf):
        bx, by, bw, bh = BED_RECT.x, BED_RECT.y, BED_RECT.w, BED_RECT.h
        pygame.draw.rect(surf, (200, 180, 150), BED_RECT)
        pygame.draw.rect(surf, (150, 100, 50), (bx+6, by+6, bw-12, 20), 0, 2)
        pygame.draw.rect(surf, (100, 150, 200), (bx+6, by+28, bw-12, bh-36), 0, 2)
        pygame.draw.rect(surf, GREEN, BED_RECT, 3)
        lbl = fS.render("BEDROOM", True, (120, 255, 130))
        surf.blit(lbl, (bx + bw//2 - lbl.get_width()//2, by + bh//2))

    static_surf = bg_surf.copy()
    draw_bedroom(static_surf)

    # ── HELPERS ────────────────────────────────────────────────────────────────
    def check_laser_collision(rect):
        """Check if rect hits any active laser."""
        for laser in lasers:
            if laser.is_on:
                for l_rect in laser.get_rects():
                    if rect.colliderect(l_rect):
                        return True
        return False

    def check_spike_collision(rect):
        """Check if rect hits any spike."""
        for spike in spikes:
            if rect.colliderect(spike.rect):
                return True
        return False

    def collide_walls(rect, dx, dy):
        rect.x += dx
        for tr in range(max(0, rect.top//TILE), min(ROWS, (rect.bottom+TILE-1)//TILE)):
            for tc in range(max(0, rect.left//TILE), min(COLS, (rect.right+TILE-1)//TILE)):
                if tile_grid[tr][tc] == 1:
                    wr = pygame.Rect(tc*TILE, tr*TILE, TILE, TILE)
                    if rect.colliderect(wr):
                        if dx > 0: rect.right = wr.left
                        if dx < 0: rect.left = wr.right

        rect.y += dy
        for tr in range(max(0, rect.top//TILE), min(ROWS, (rect.bottom+TILE-1)//TILE)):
            for tc in range(max(0, rect.left//TILE), min(COLS, (rect.right+TILE-1)//TILE)):
                if tile_grid[tr][tc] == 1:
                    wr = pygame.Rect(tc*TILE, tr*TILE, TILE, TILE)
                    if rect.colliderect(wr):
                        if dy > 0: rect.bottom = wr.top
                        if dy < 0: rect.top = wr.bottom

    # ── MONSTER FIGURE (wooden chair-creature, like the reference image) ─────────
    def draw_monster_figure(surf, rect, glow=1.0):
        """Draw a hulking creature built out of wooden chairs/furniture,
        scaled to fit `rect`. Used both for the giant intro display and the
        tiny in-game monsters (same drawing, different size)."""
        x, y, w, h = rect.x, rect.y, rect.width, rect.height
        # Darker, more menacing palette
        wood   = (88, 54, 28)
        wood_d = (50, 28, 14)
        wood_l = (140, 96, 52)
        bone   = (210, 195, 165)
        lw = max(1, int(w * 0.02))

        def R(fx, fy, fw, fh):
            return pygame.Rect(int(x + fx*w), int(y + fy*h),
                               max(1, int(fw*w)), max(1, int(fh*h)))

        def poly(pts, col):
            pygame.draw.polygon(surf, col, [(x + px*w, y + py*h) for px, py in pts])

        rad = max(1, int(w * 0.04))

        # Hunched legs + clawed feet
        pygame.draw.rect(surf, wood_d, R(0.28, 0.72, 0.15, 0.28))
        pygame.draw.rect(surf, wood_d, R(0.57, 0.72, 0.15, 0.28))
        poly([(0.22, 1.0), (0.30, 0.94), (0.48, 1.0)], wood)
        poly([(0.52, 1.0), (0.70, 0.94), (0.78, 1.0)], wood)

        # Long menacing arms ending in big splayed claws
        arm_w = max(2, int(w * 0.08))
        la, le = (x + w*0.24, y + h*0.38), (x + w*0.01, y + h*0.72)
        ra, re = (x + w*0.76, y + h*0.38), (x + w*0.99, y + h*0.74)
        pygame.draw.line(surf, wood, la, le, arm_w)
        pygame.draw.line(surf, wood, ra, re, arm_w)

        def claws(px, py, direction):
            for i in range(4):
                ang = math.radians(35 + i * 32)
                ex = px + direction * math.cos(ang) * w * 0.17
                ey = py + math.sin(ang) * h * 0.17
                pygame.draw.line(surf, bone, (px, py), (ex, ey), max(1, int(w*0.025)))
                # sharpened tip
                pygame.draw.circle(surf, bone, (int(ex), int(ey)), max(1, int(w*0.012)))
        claws(le[0], le[1], -1)
        claws(re[0], re[1], 1)

        # Bulky torso with vertical chair slats + cracks
        body = R(0.22, 0.32, 0.56, 0.44)
        pygame.draw.rect(surf, wood, body, border_radius=rad)
        pygame.draw.rect(surf, wood_d, body, lw, border_radius=rad)
        for i in range(3):
            sx = body.x + int(body.w * (0.25 + 0.25*i))
            pygame.draw.line(surf, wood_d, (sx, body.y+lw), (sx, body.bottom-lw), max(1, int(w*0.015)))
        # jagged ribcage cracks
        pygame.draw.line(surf, wood_d, (body.centerx, body.y + body.h*0.15),
                         (body.centerx - body.w*0.12, body.bottom - body.h*0.1), max(1, int(w*0.01)))

        # Hunched spiky shoulders
        poly([(0.18, 0.40), (0.30, 0.28), (0.34, 0.40)], wood_d)
        poly([(0.66, 0.40), (0.70, 0.28), (0.82, 0.40)], wood_d)

        # Head (a chair back) with jagged crown of spikes/horns
        head = R(0.36, 0.07, 0.28, 0.30)
        pygame.draw.rect(surf, wood, head, border_radius=max(1, int(w*0.05)))
        pygame.draw.rect(surf, wood_d, head, lw, border_radius=max(1, int(w*0.05)))
        # horns
        poly([(0.34, 0.10), (0.28, -0.04), (0.40, 0.06)], wood_d)
        poly([(0.66, 0.10), (0.72, -0.04), (0.60, 0.06)], wood_d)
        # spiky crown
        for sx in (0.42, 0.50, 0.58):
            poly([(sx-0.03, 0.07), (sx, -0.02), (sx+0.03, 0.07)], wood_l)

        # Gaping maw with jagged fangs (top + bottom)
        mouth = R(0.38, 0.24, 0.24, 0.10)
        pygame.draw.rect(surf, (15, 8, 6), mouth)
        nf = 6
        for i in range(nf):
            fx = mouth.x + mouth.w * (i / nf)
            fx2 = mouth.x + mouth.w * ((i + 0.5) / nf)
            # upper fang pointing down
            pygame.draw.polygon(surf, bone, [(fx, mouth.y), (fx2, mouth.y + mouth.h*0.7),
                                             (fx + mouth.w/nf, mouth.y)])
            # lower fang pointing up
            pygame.draw.polygon(surf, bone, [(fx, mouth.bottom), (fx2, mouth.bottom - mouth.h*0.7),
                                             (fx + mouth.w/nf, mouth.bottom)])

        # Furious glowing eyes (angled, with brow + bright core)
        er = max(1, int(w * 0.05))
        eye_y = int(y + h * 0.16)
        eye_col = (255, 170, 40)
        for sgn, ex in ((-1, int(x + w*0.45)), (1, int(x + w*0.55))):
            if w > 26:  # soft glow on anything but the very tiniest render
                g = pygame.Surface((er*8, er*8), pygame.SRCALPHA)
                for k in range(6, 0, -1):
                    a = int(30 * glow * (k/6))
                    pygame.draw.circle(g, (255, 120, 20, a), (er*4, er*4), int(er*1.4*k))
                surf.blit(g, (ex - er*4, eye_y - er*4))
            pygame.draw.circle(surf, eye_col, (ex, eye_y), er)
            pygame.draw.circle(surf, (255, 255, 230), (ex, eye_y), max(1, int(er*0.4)))
            # angry brow slashing down toward the nose
            pygame.draw.line(surf, wood_d, (ex - sgn*er*1.4, eye_y - er*1.3),
                             (ex + sgn*er*1.4, eye_y - er*0.2), max(1, int(w*0.022)))


    # ── MONSTER ────────────────────────────────────────────────────────────────
    class Monster:
        def __init__(self, x, y):
            self.rect = pygame.Rect(x, y, 32, 32)  # 100% bigger (they phase through walls anyway)
            self.speed = SPEED / 1.1  # 10% slower than player (player is 10% faster)

        def update(self, player_rect):
            dx = player_rect.centerx - self.rect.centerx
            dy = player_rect.centery - self.rect.centery
            dist = math.sqrt(dx*dx + dy*dy)

            if dist > 0:
                self.rect.x += (dx / dist) * self.speed
                self.rect.y += (dy / dist) * self.speed
                collide_walls(self.rect, 0, 0)

        def draw(self, surf):
            draw_monster_figure(surf, self.rect)

    # ── PLAYER ────────────────────────────────────────────────────────────────
    player = pygame.Rect(SW - 40, SH - 40, 16, 16)

    # ── GAME STATE ────────────────────────────────────────────────────────────
    game_state = "title"  # "title", "intro", "playing", "game_over"
    game_time = 0.0
    monsters = []
    monster_timer = 0.0
    game_over = False
    won = False
    lose_msg = ""

    def reset():
        nonlocal game_time, monsters, monster_timer, game_over, won, lose_msg, player
        game_time = 0.0
        monsters = []
        monster_timer = 0.0
        game_over = False
        won = False
        lose_msg = ""
        player = pygame.Rect(SW - 40, SH - 40, 16, 16)

    # ── INTRO ANIMATION (chairs assemble into the monster) ──────────────────────
    intro_time = 0.0
    proceed_btn = None
    INTRO_ASSEMBLE = 2.8  # seconds for the chairs to converge

    MONSTER_BOX = pygame.Rect(SW//2 - 170, SH//2 - 140, 340, 380)

    # Pre-generate the flying chairs: each starts off-screen and homes in on a
    # target point inside the monster's silhouette.
    intro_chairs = []
    for _ in range(16):
        edge = random.choice(['l', 'r', 't', 'b'])
        if edge == 'l':   sx, sy = -80, random.randint(0, SH)
        elif edge == 'r': sx, sy = SW + 80, random.randint(0, SH)
        elif edge == 't': sx, sy = random.randint(0, SW), -80
        else:             sx, sy = random.randint(0, SW), SH + 80
        intro_chairs.append({
            'sx': sx, 'sy': sy,
            'tx': random.randint(MONSTER_BOX.left + 30, MONSTER_BOX.right - 30),
            'ty': random.randint(MONSTER_BOX.top + 30, MONSTER_BOX.bottom - 30),
            'size': random.randint(28, 46),
        })

    def draw_chair(surf, cx, cy, s, alpha=255):
        """Draw a small wooden chair centered at (cx, cy)."""
        w_, h_ = s, int(s * 1.4)
        chair = pygame.Surface((w_, h_), pygame.SRCALPHA)
        col, cold = (110, 72, 40), (74, 46, 24)
        pygame.draw.rect(chair, col,  (w_*0.15, 0,        w_*0.70, h_*0.55), border_radius=2)  # back
        pygame.draw.rect(chair, cold, (w_*0.10, h_*0.50,  w_*0.80, h_*0.18))                    # seat
        pygame.draw.rect(chair, col,  (w_*0.15, h_*0.65,  w_*0.12, h_*0.35))                    # leg
        pygame.draw.rect(chair, col,  (w_*0.73, h_*0.65,  w_*0.12, h_*0.35))                    # leg
        if alpha < 255:
            chair.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(chair, (cx - w_/2, cy - h_/2))

    def draw_intro_screen():
        """Animate the chairs assembling into the monster, then show the
        message and a PROCEED button."""
        nonlocal proceed_btn
        screen.fill((12, 8, 14))

        p = min(1.0, intro_time / INTRO_ASSEMBLE)
        ease = 1 - (1 - p) ** 3                       # ease-out
        monster_alpha = max(0.0, min(1.0, (p - 0.65) / 0.35))
        chair_alpha = int(255 * (1 - monster_alpha))

        # Chairs converging on the monster's silhouette
        if chair_alpha > 0:
            for ch in intro_chairs:
                cx = ch['sx'] + (ch['tx'] - ch['sx']) * ease
                cy = ch['sy'] + (ch['ty'] - ch['sy']) * ease
                draw_chair(screen, cx, cy, ch['size'], chair_alpha)

        # Monster fading in as the chairs lock together
        if monster_alpha > 0:
            ms = pygame.Surface((MONSTER_BOX.w, MONSTER_BOX.h), pygame.SRCALPHA)
            draw_monster_figure(ms, pygame.Rect(0, 0, MONSTER_BOX.w, MONSTER_BOX.h), glow=monster_alpha)
            ms.fill((255, 255, 255, int(255 * monster_alpha)), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(ms, (MONSTER_BOX.x, MONSTER_BOX.y))

        # Message appears near the end of the assembly
        if p > 0.75:
            ta = int(255 * min(1.0, (p - 0.75) / 0.25))
            msg = fM.render("This is the monster you will be facing. Good luck", True, (235, 80, 70))
            msg.set_alpha(ta)
            screen.blit(msg, (SW//2 - msg.get_width()//2, 40))

        # PROCEED button once the monster is fully formed
        proceed_btn = None
        if p >= 1.0:
            btn = pygame.Rect(0, 0, 240, 64)
            btn.center = (SW//2, SH - 70)
            hover = btn.collidepoint(pygame.mouse.get_pos())
            pygame.draw.rect(screen, (60, 150, 70) if hover else (40, 110, 55), btn, border_radius=10)
            pygame.draw.rect(screen, (120, 255, 140), btn, 3, border_radius=10)
            bt = fM.render("PROCEED", True, WHITE)
            screen.blit(bt, (btn.centerx - bt.get_width()//2, btn.centery - bt.get_height()//2))
            proceed_btn = btn

        pygame.display.flip()

    def draw_title_screen():
        """Draw the title/start screen."""
        screen.fill(BLACK)

        # Title
        title = fL.render("THE JOURNEY TO THE ROOM!", True, (100, 255, 110))
        screen.blit(title, (SW//2 - title.get_width()//2, 80))

        # Description (wrap text)
        desc_lines = [
            "Guide your player into the bedroom from the hall.",
            "Beware! Monsters and traps are there to prevent",
            "you from achieving your goal!",
            "",
            "All the best!"
        ]

        y_pos = 220
        for line in desc_lines:
            desc = fM.render(line, True, WHITE)
            screen.blit(desc, (SW//2 - desc.get_width()//2, y_pos))
            y_pos += 50

        # Continue button
        button_text = fM.render("PRESS SPACE TO CONTINUE", True, (255, 200, 100))
        button_rect = button_text.get_rect(center=(SW//2, SH - 100))
        pygame.draw.rect(screen, (100, 100, 100), button_rect.inflate(30, 20), 2)
        screen.blit(button_text, button_rect)

        pygame.display.flip()

    # ── MAIN LOOP ──────────────────────────────────────────────────────────────
    running = True
    L5_PROCEED_BTN = pygame.Rect(SW // 2 - 130, SH // 2 + 100, 260, 56)
    while running:
        dt = min(clock.tick(FPS) / 1000.0, 0.05)

        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                quit_game()
            if evt.type == pygame.KEYDOWN:
                if evt.key == pygame.K_ESCAPE:
                    quit_game()
                if evt.key == pygame.K_SPACE and game_state == "title":
                    game_state = "intro"
                    intro_time = 0.0
                # Skip past / confirm the intro once the monster has assembled
                if game_state == "intro" and evt.key in (pygame.K_SPACE, pygame.K_RETURN) \
                        and intro_time >= INTRO_ASSEMBLE:
                    reset()
                    game_state = "playing"
                    play_music("chase")
                if evt.key == pygame.K_r and game_state == "game_over" and not won:
                    reset()
                    game_state = "playing"
                    play_music("chase")
                if game_state == "game_over" and won and evt.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    stop_music()
                    return
            if evt.type == pygame.MOUSEBUTTONDOWN and game_state == "intro":
                if proceed_btn and proceed_btn.collidepoint(evt.pos):
                    reset()
                    game_state = "playing"
                    play_music("chase")
            if evt.type == pygame.MOUSEBUTTONDOWN and game_state == "game_over" and won:
                if L5_PROCEED_BTN.collidepoint(evt.pos):
                    stop_music()
                    return

        # ── TITLE SCREEN ───────────────────────────────────────────────────────
        if game_state == "title":
            draw_title_screen()
            continue

        # ── INTRO ANIMATION ────────────────────────────────────────────────────
        if game_state == "intro":
            intro_time += dt
            draw_intro_screen()
            continue

        # ── PLAYING STATE ──────────────────────────────────────────────────────
        if game_state == "playing" and not game_over:
            game_time += dt
            monster_timer += dt

            # Update lasers
            for laser in lasers:
                laser.update(dt)

            # Spawn one monster every 0.5 seconds
            if monster_timer >= 0.5:
                while True:
                    rc = random.randint(2, COLS-4)
                    rr = random.randint(2, ROWS-4)
                    if tile_grid[rr][rc] == 0:
                        monsters.append(Monster(rc*TILE + 2, rr*TILE + 2))
                        break
                monster_timer = 0.0
                if len(monsters) > 10:
                    monsters.pop(0)

            # Update monsters
            for m in monsters:
                m.update(player)

            # Player movement
            keys = pygame.key.get_pressed()
            dx = ((keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])) * SPEED
            dy = ((keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])) * SPEED
            collide_walls(player, dx, dy)

            # Check laser collision
            if check_laser_collision(player):
                game_over = True
                game_state = "game_over"
                lose_msg = "Zapped by laser!"
                play_sfx("hit")

            # Check spike collision
            if check_spike_collision(player):
                game_over = True
                game_state = "game_over"
                lose_msg = "Hit a spike trap!"
                play_sfx("hit")

            # Win: reach bedroom
            if player.colliderect(BED_RECT):
                game_over = True
                game_state = "game_over"
                won = True
                play_sfx("win")

            # Lose: hit by monster
            for m in monsters:
                if player.colliderect(m.rect):
                    game_over = True
                    game_state = "game_over"
                    lose_msg = "Caught by a monster!"
                    play_sfx("hit")

            # Lose: time up
            if game_time >= GAME_SECS:
                game_over = True
                game_state = "game_over"
                lose_msg = "Time's up!"
                play_sfx("lose")

            # The chase is over — silence the chase music (win or lose)
            if game_over:
                stop_music()

        # ── DRAW ───────────────────────────────────────────────────────────────
        screen.blit(static_surf, (0, 0))

        # Draw spike obstacles
        for spike in spikes:
            spike.draw(screen)

        # Draw laser obstacles
        for laser in lasers:
            laser.draw(screen)

        # Draw monsters
        for m in monsters:
            m.draw(screen)

        # Draw player — the character chosen on the start screen
        draw_player_character(screen, player.centerx, player.centery, 34, BLUE)

        # ── HUD ────────────────────────────────────────────────────────────────
        time_left = max(0.0, GAME_SECS - game_time)
        timer = fM.render(f"Time: {time_left:.1f}s", True, WHITE)
        pygame.draw.rect(screen, BLACK, timer.get_rect(topleft=(12,10)).inflate(14, 8))
        screen.blit(timer, (19, 14))

        m_count = fM.render(f"Monsters: {len(monsters)}", True, RED)
        pygame.draw.rect(screen, BLACK, m_count.get_rect(topleft=(SW-m_count.get_width()-12, 10)).inflate(14, 8))
        screen.blit(m_count, (SW-m_count.get_width()-5, 14))

        # Instructions (first 2 seconds)
        if game_time < 2.0 and not game_over:
            tip1 = fS.render("WASD/Arrows to move – Reach the BEDROOM in top-left!", True, WHITE)
            tip2 = fS.render("Avoid monsters, GREEN LASERS (on/off), and RED SPIKES! 20 seconds!", True, (255, 160, 160))
            for tip, y in ((tip1, SH-55), (tip2, SH-28)):
                bg = pygame.Surface((tip.get_width()+12, tip.get_height()+6))
                bg.set_alpha(180); bg.fill(BLACK)
                screen.blit(bg, (SW//2 - bg.get_width()//2, y - 3))
                screen.blit(tip, (SW//2 - tip.get_width()//2, y))

        # Game over
        if game_over:
            ov = pygame.Surface((SW, SH), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 200))
            screen.blit(ov, (0, 0))

            if won:
                t1 = fL.render("YOU ESCAPED!", True, (100, 255, 110))
                t2 = fM.render(f"Made it in {game_time:.1f}s!", True, WHITE)
            else:
                t1 = fL.render("GAME OVER", True, RED)
                t2 = fM.render(lose_msg, True, WHITE)

            screen.blit(t1, (SW//2 - t1.get_width()//2, SH//2 - 90))
            screen.blit(t2, (SW//2 - t2.get_width()//2, SH//2 - 10))
            rr = fS.render("R – Restart        ESC – Quit", True, (180, 180, 180))
            screen.blit(rr, (SW//2 - rr.get_width()//2, SH//2 + 60))
            if won:
                hov = L5_PROCEED_BTN.collidepoint(pygame.mouse.get_pos())
                pygame.draw.rect(screen, (40, 160, 75) if hov else (26, 110, 55),
                                 L5_PROCEED_BTN, border_radius=12)
                pygame.draw.rect(screen, (120, 255, 150), L5_PROCEED_BTN, 3, border_radius=12)
                _bt = fM.render("PROCEED", True, WHITE)
                screen.blit(_bt, (L5_PROCEED_BTN.centerx - _bt.get_width()//2,
                                  L5_PROCEED_BTN.centery - _bt.get_height()//2))

        pygame.display.flip()


# ── End screen ────────────────────────────────────────────────────────────────
# "Proceed to the end page" button shown on the Level 2 win screen.
# Coordinates are in Level 2's native canvas (WIDTH x HEIGHT).
L2_PROCEED_BTN = pygame.Rect(WIDTH // 2 - 130, HEIGHT - 88, 260, 56)

def draw_end(surf, anim, won, score):
    if won:
        # celebratory success screen
        vgradient(surf, (10, 40, 26), (4, 10, 8))
        # gentle confetti sparkle
        random.seed(99)
        for _ in range(80):
            sx, sy = random.randint(0, WIDTH), random.randint(0, HEIGHT)
            tw = 0.5 + 0.5*math.sin(anim*2 + sx*0.04)
            col = random.choice([GREEN, YELLOW, CYAN, PINK, MINT])
            r = 2 if tw > 0.7 else 1
            pygame.draw.circle(surf, col, (sx, sy), r)
        random.seed()
        t1 = font_big.render("YOU HAVE SUCCESSFULLY", True, GREEN)
        t2 = font_big.render("BRUSHED YOUR TEETH", True, GREEN)
        surf.blit(t1, (WIDTH//2 - t1.get_width()//2, HEIGHT//2 - 90))
        surf.blit(t2, (WIDTH//2 - t2.get_width()//2, HEIGHT//2 - 34))
        t3 = font_med.render("IT IS LUNCH TIME. YOU WILL NOW GO EAT.", True, YELLOW)
        surf.blit(t3, (WIDTH//2 - t3.get_width()//2, HEIGHT//2 + 30))

        # PROCEED button -> end page (hover uses mouse pos mapped into the canvas)
        mx, my = pygame.mouse.get_pos()
        lx, ly = mx - (WIN_W - WIDTH)//2, my - (WIN_H - HEIGHT)//2
        hover = L2_PROCEED_BTN.collidepoint(lx, ly)
        pygame.draw.rect(surf, (40, 160, 75) if hover else (26, 110, 55),
                         L2_PROCEED_BTN, border_radius=12)
        pygame.draw.rect(surf, (120, 255, 150), L2_PROCEED_BTN, 3, border_radius=12)
        bt = font_med.render("PROCEED", True, WHITE)
        surf.blit(bt, (L2_PROCEED_BTN.centerx - bt.get_width()//2,
                       L2_PROCEED_BTN.centery - bt.get_height()//2))
        return
    vgradient(surf, (40, 14, 18), (10, 6, 14))
    draw_monster(surf, WIDTH//2, HEIGHT//2+20, anim, size=1.6)
    t1 = font_big.render("GAME OVER", True, RED)
    surf.blit(t1, (WIDTH//2 - t1.get_width()//2, 70))
    sc_t = font_med.render(f"Final Score: {score}", True, YELLOW)
    surf.blit(sc_t, (WIDTH//2 - sc_t.get_width()//2, 130))
    mt = font_small.render("You didn't catch enough toothpaste...", True, LIGHT_GREY)
    surf.blit(mt, (WIDTH//2 - mt.get_width()//2, 175))
    rt = font_small.render("Press  R  to try again", True, CYAN)
    surf.blit(rt, (WIDTH//2 - rt.get_width()//2, HEIGHT-60))


def run_level2():
    screen = pygame.Surface((WIDTH, HEIGHT))
    state       = STATE_TITLE
    shadow_game = ShadowGame()
    catch_game  = None
    anim        = 0.0
    trans_timer = FPS * 3
    TRANS_TOTAL = FPS * 3

    while True:
        keys = pygame.key.get_pressed()
        anim += 0.06

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()

            # Click the PROCEED button on the win screen -> go to the end page
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and state == STATE_WIN:
                mx, my = event.pos
                lx, ly = mx - (WIN_W - WIDTH)//2, my - (WIN_H - HEIGHT)//2
                if L2_PROCEED_BTN.collidepoint(lx, ly):
                    return   # continue to the end screen

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit_game()
                if state == STATE_TITLE and event.key == pygame.K_RETURN:
                    state = STATE_SHADOW; shadow_game = ShadowGame()
                elif state == STATE_SHADOW and not shadow_game.answered:
                    if event.key == pygame.K_RETURN:
                        shadow_game.submit()
                    elif event.key == pygame.K_BACKSPACE:
                        shadow_game.input_text = shadow_game.input_text[:-1]
                    elif event.unicode and event.unicode.isprintable() and len(shadow_game.input_text) < 20:
                        shadow_game.input_text += event.unicode
                elif state == STATE_STORY and event.key == pygame.K_RETURN:
                    state = STATE_CATCH
                    play_music("compete")          # competitive music for the catch game
                elif state == STATE_WIN and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    stop_music()
                    return   # continue to the end screen
                elif state == STATE_GAMEOVER:
                    if event.key == pygame.K_r:
                        state = STATE_TITLE; shadow_game = ShadowGame()
                        catch_game = None; trans_timer = TRANS_TOTAL

        if state == STATE_SHADOW:
            shadow_game.update()
            if shadow_game.finished:
                state = STATE_TRANSITION; trans_timer = TRANS_TOTAL
                catch_game = CatchGame(shadow_score=shadow_game.total_score)
                catch_game.init_player()
        elif state == STATE_TRANSITION:
            trans_timer -= 1
            if trans_timer <= 0: state = STATE_STORY
        elif state == STATE_CATCH:
            catch_game.update(keys)
            if catch_game.done:
                stop_music()
                if catch_game.qualified:
                    state = STATE_WIN
                    play_sfx("win")
                else:
                    state = STATE_GAMEOVER
                    play_sfx("lose")

        if   state == STATE_TITLE:      draw_title(screen, anim)
        elif state == STATE_SHADOW:     shadow_game.draw(screen)
        elif state == STATE_TRANSITION: draw_transition(screen, anim, shadow_game.total_score, trans_timer, TRANS_TOTAL)
        elif state == STATE_STORY:      draw_story(screen, anim)
        elif state == STATE_CATCH:      catch_game.draw(screen)
        elif state in (STATE_WIN, STATE_GAMEOVER):
            draw_end(screen, anim, won=(state==STATE_WIN),
                     score=catch_game.score if catch_game else 0)

        present(screen)
        clock.tick(FPS)


# ==========================================================================
# START SCREEN + CHARACTER SELECT  (drawn directly on the full window)
# ==========================================================================
def run_start():
    screen = window

    TITLE_FONT = pygame.font.SysFont("arial", 110, bold=True)
    DESC_FONT = pygame.font.SysFont("arial", 32, bold=True)
    BUTTON_FONT = pygame.font.SysFont("arial", 60, bold=True)
    FOOTER_FONT = pygame.font.SysFont("arial", 24)
    SELECT_TITLE_FONT = pygame.font.SysFont("arial", 70, bold=True)
    NAME_FONT = pygame.font.SysFont("arial", 26, bold=True)

    # Drop image files next to this script with these names to show real
    # pictures. If a file is missing, a placeholder card is drawn.
    CHARACTERS = [
        {"name": "Harry Potter",      "image": "harry.png"},
        {"name": "LeBron James",      "image": "lebron.png"},
        {"name": "Cristiano Ronaldo", "image": "ronaldo.png"},
        {"name": "John Wick",         "image": "johnwick.png"},
        {"name": "Spider-Man",        "image": "spiderman.png"},
    ]

    # Every card uses the same look
    CARD_COLOR = (25, 25, 60)

    def fit_text(text, max_width, max_size=26, min_size=12, color=(255, 255, 255)):
        """Render text at the largest bold size that fits within max_width."""
        size = max_size
        while size > min_size:
            font = pygame.font.SysFont("arial", size, bold=True)
            surface = font.render(text, True, color)
            if surface.get_width() <= max_width:
                return surface
            size -= 1
        font = pygame.font.SysFont("arial", min_size, bold=True)
        return font.render(text, True, color)

    # Card layout
    CARD_W = 200
    CARD_H = 320
    CARD_GAP = 40
    CARD_Y = 260

    total_w = len(CHARACTERS) * CARD_W + (len(CHARACTERS) - 1) * CARD_GAP
    start_x = WIN_W // 2 - total_w // 2

    for i, char in enumerate(CHARACTERS):
        x = start_x + i * (CARD_W + CARD_GAP)
        char["rect"] = pygame.Rect(x, CARD_Y, CARD_W, CARD_H)

        # Try to load the image; scale it to fit the card while keeping its
        # aspect ratio (so tall/wide/square pictures don't get stretched).
        try:
            img = pygame.image.load(char["image"]).convert_alpha()

            max_w = CARD_W - 20
            max_h = CARD_H - 70
            iw, ih = img.get_size()
            scale = min(max_w / iw, max_h / ih)

            char["sprite"] = pygame.transform.smoothscale(
                img,
                (int(iw * scale), int(ih * scale))
            )
        except (pygame.error, FileNotFoundError):
            char["sprite"] = None

    # Currently selected character (index), set when the player clicks a card
    selected_index = None

    particles = []
    for _ in range(120):
        particles.append([
            random.randint(0, WIN_W),
            random.randint(0, WIN_H),
            random.randint(2, 5),
            random.uniform(0.3, 1.2)
        ])

    button_rect = pygame.Rect(
        WIN_W // 2 - 250,
        520,
        500,
        110
    )

    # Which screen we're on: "start" or "select"
    state = "start"

    while True:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                quit_game()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                quit_game()

            if event.type == pygame.MOUSEBUTTONDOWN:

                if state == "start":

                    if button_rect.collidepoint(mouse_pos):
                        # Go to the character selection screen
                        play_sfx("click")
                        state = "select"

                elif state == "select":

                    for i, char in enumerate(CHARACTERS):
                        if char["rect"].collidepoint(mouse_pos):
                            selected_index = i
                            print("SELECTED:", char["name"])
                            # Show the confirmation screen
                            play_sfx("select")
                            state = "chosen"

                elif state == "chosen":

                    if button_rect.collidepoint(mouse_pos):
                        print("START GAME with:", CHARACTERS[selected_index]["name"])
                        play_sfx("confirm")
                        return selected_index

        # =========================
        # BACKGROUND GRADIENT
        # =========================
        for y in range(WIN_H):

            blend = y / WIN_H

            r = int(35 + blend * 30)
            g = int(20 + blend * 10)
            b = int(90 + blend * 90)

            pygame.draw.line(
                screen,
                (r, g, b),
                (0, y),
                (WIN_W, y)
            )

        # =========================
        # PARTICLES / STARS
        # =========================
        for particle in particles:

            particle[1] -= particle[3]

            if particle[1] < -10:
                particle[1] = WIN_H + 10
                particle[0] = random.randint(0, WIN_W)

            pygame.draw.circle(
                screen,
                (255, 255, 255),
                (int(particle[0]), int(particle[1])),
                particle[2]
            )

        if state == "start":

            shadow = TITLE_FONT.render(
                "Daily Life Reimagined",
                True,
                (0, 0, 0)
            )

            screen.blit(
                shadow,
                (
                    WIN_W // 2 - shadow.get_width() // 2 + 5,
                    85
                )
            )

            title = TITLE_FONT.render(
                "Daily Life Reimagined",
                True,
                (255, 255, 255)
            )

            screen.blit(
                title,
                (
                    WIN_W // 2 - title.get_width() // 2,
                    80
                )
            )

            desc_box = pygame.Rect(
                WIN_W // 2 - 500,
                250,
                1000,
                150
            )

            pygame.draw.rect(
                screen,
                (25, 25, 60),
                desc_box,
                border_radius=25
            )

            pygame.draw.rect(
                screen,
                (255, 255, 255),
                desc_box,
                4,
                border_radius=25
            )

            line1 = DESC_FONT.render(
                "See everyday tasks in new and different ways,",
                True,
                (255, 255, 255)
            )

            line2 = DESC_FONT.render(
                "while having fun and honing your skills.",
                True,
                (255, 255, 255)
            )

            screen.blit(
                line1,
                (
                    WIN_W // 2 - line1.get_width() // 2,
                    290
                )
            )

            screen.blit(
                line2,
                (
                    WIN_W // 2 - line2.get_width() // 2,
                    340
                )
            )

            hover = button_rect.collidepoint(mouse_pos)

            if hover:
                button_color = (255, 220, 0)
            else:
                button_color = (255, 190, 0)

            pygame.draw.rect(
                screen,
                button_color,
                button_rect,
                border_radius=30
            )

            pygame.draw.rect(
                screen,
                (255, 255, 255),
                button_rect,
                5,
                border_radius=30
            )

            button_text = BUTTON_FONT.render(
                "CLICK TO START",
                True,
                (0, 0, 0)
            )

            screen.blit(
                button_text,
                (
                    button_rect.centerx - button_text.get_width() // 2,
                    button_rect.centery - button_text.get_height() // 2
                )
            )

            footer = FOOTER_FONT.render(
                "Daily Tasks Final Boss",
                True,
                (220, 220, 220)
            )

            screen.blit(
                footer,
                (
                    WIN_W // 2 - footer.get_width() // 2,
                    660
                )
            )

        elif state == "select":

            select_title = SELECT_TITLE_FONT.render(
                "CHOOSE YOUR CHARACTER",
                True,
                (255, 255, 255)
            )

            screen.blit(
                select_title,
                (
                    WIN_W // 2 - select_title.get_width() // 2,
                    110
                )
            )

            for char in CHARACTERS:

                rect = char["rect"]
                hover = rect.collidepoint(mouse_pos)

                # Card background (same color/design for every card)
                pygame.draw.rect(
                    screen,
                    CARD_COLOR,
                    rect,
                    border_radius=20
                )

                # Image or placeholder text
                if char["sprite"] is not None:
                    sprite = char["sprite"]
                    # Center inside the image area (above the name label)
                    area_top = rect.y + 10
                    area_h = CARD_H - 70
                    screen.blit(
                        sprite,
                        (
                            rect.centerx - sprite.get_width() // 2,
                            area_top + (area_h - sprite.get_height()) // 2
                        )
                    )
                else:
                    placeholder = NAME_FONT.render(
                        "(no image)",
                        True,
                        (255, 255, 255)
                    )
                    screen.blit(
                        placeholder,
                        (
                            rect.centerx - placeholder.get_width() // 2,
                            rect.centery - placeholder.get_height() // 2
                        )
                    )

                # Name label (auto-shrunk so it always fits inside the card)
                name_text = fit_text(char["name"], CARD_W - 16)
                screen.blit(
                    name_text,
                    (
                        rect.centerx - name_text.get_width() // 2,
                        rect.bottom - 38
                    )
                )

                # Border (brighter / thicker when hovered)
                if hover:
                    border_color = (255, 220, 0)
                    border_width = 6
                else:
                    border_color = (255, 255, 255)
                    border_width = 3

                pygame.draw.rect(
                    screen,
                    border_color,
                    rect,
                    border_width,
                    border_radius=20
                )

        elif state == "chosen":

            chosen = CHARACTERS[selected_index]

            heading = SELECT_TITLE_FONT.render(
                "YOU CHOSE",
                True,
                (255, 255, 255)
            )
            screen.blit(
                heading,
                (
                    WIN_W // 2 - heading.get_width() // 2,
                    40
                )
            )

            if chosen["sprite"] is not None:
                big = pygame.transform.smoothscale(
                    chosen["sprite"],
                    (
                        chosen["sprite"].get_width() * 2,
                        chosen["sprite"].get_height() * 2
                    )
                )
                # Clamp height so it stays in the available area
                if big.get_height() > 280:
                    ratio = 280 / big.get_height()
                    big = pygame.transform.smoothscale(
                        big,
                        (int(big.get_width() * ratio), 280)
                    )
                screen.blit(
                    big,
                    (
                        WIN_W // 2 - big.get_width() // 2,
                        130 + (280 - big.get_height()) // 2
                    )
                )

            name = SELECT_TITLE_FONT.render(
                chosen["name"],
                True,
                (255, 220, 0)
            )
            # Shrink if the name is wider than the screen
            if name.get_width() > WIN_W - 80:
                ratio = (WIN_W - 80) / name.get_width()
                name = pygame.transform.smoothscale(
                    name,
                    (int(name.get_width() * ratio), int(name.get_height() * ratio))
                )
            screen.blit(
                name,
                (
                    WIN_W // 2 - name.get_width() // 2,
                    430
                )
            )

            hover = button_rect.collidepoint(mouse_pos)
            button_color = (255, 220, 0) if hover else (255, 190, 0)

            pygame.draw.rect(screen, button_color, button_rect, border_radius=30)
            pygame.draw.rect(screen, (255, 255, 255), button_rect, 5, border_radius=30)

            continue_text = BUTTON_FONT.render(
                "CONTINUE",
                True,
                (0, 0, 0)
            )
            screen.blit(
                continue_text,
                (
                    button_rect.centerx - continue_text.get_width() // 2,
                    button_rect.centery - continue_text.get_height() // 2
                )
            )

        pygame.display.flip()


# ==========================================================================
# LEVEL 1 — "Turn Off The Alarm!"  (native 800x600 canvas)
# ==========================================================================
def run_level1():
    WIDTH, HEIGHT = 800, 600
    screen = pygame.Surface((WIDTH, HEIGHT))

    # Fonts
    key_font = pygame.font.Font(None, 120)
    big_font = pygame.font.Font(None, 84)
    msg_font = pygame.font.Font(None, 46)
    prompt_font = pygame.font.Font(None, 48)
    hud_font = pygame.font.Font(None, 40)
    small_font = pygame.font.Font(None, 30)

    # Colors
    WHITE = (240, 240, 245)
    MUTED = (155, 155, 175)
    ACCENT = (90, 150, 255)
    GREEN = (70, 220, 120)
    RED = (235, 80, 80)

    TOTAL_WAVES = 5

    # Countdown bar geometry
    BAR_WIDTH = 560
    BAR_HEIGHT = 26
    BAR_X = (WIDTH - BAR_WIDTH) // 2
    BAR_Y = 490

    def make_gradient(top, bottom):
        surf = pygame.Surface((WIDTH, HEIGHT))
        for y in range(HEIGHT):
            t = y / HEIGHT
            color = [int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)]
            pygame.draw.line(surf, color, (0, y), (WIDTH, y))
        return surf

    background = make_gradient((30, 28, 60), (12, 12, 24))

    def fit_image(surf, max_w, max_h):
        w, h = surf.get_size()
        scale = min(max_w / w, max_h / h)
        return pygame.transform.smoothscale(surf, (int(w * scale), int(h * scale)))

    CLOCK_CENTER = (WIDTH // 2, 175)
    try:
        clock_img = pygame.image.load("OIP.jpeg").convert_alpha()
        clock_img = fit_image(clock_img, 280, 220)
    except (pygame.error, FileNotFoundError):
        clock_img = None

    def draw_text(text, font, color, center):
        surf = font.render(text, True, color)
        screen.blit(surf, surf.get_rect(center=center))

    def draw_wrapped(text, font, color, center_x, top_y, max_width, spacing=12):
        words = text.split()
        lines, cur = [], ""
        for w in words:
            test = (cur + " " + w).strip()
            if font.size(test)[0] <= max_width:
                cur = test
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        y = top_y
        for line in lines:
            surf = font.render(line, True, color)
            screen.blit(surf, surf.get_rect(center=(center_x, y)))
            y += surf.get_height() + spacing

    def draw_panel(rect, color, radius=24):
        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(s, color, s.get_rect(), border_radius=radius)
        screen.blit(s, rect.topleft)

    def draw_clock(center=CLOCK_CENTER):
        if clock_img:
            screen.blit(clock_img, clock_img.get_rect(center=center))
        else:
            # Fallback so the game still works without the image file
            pygame.draw.circle(screen, (235, 230, 220), center, 95)
            pygame.draw.circle(screen, (40, 40, 55), center, 95, 6)
            pygame.draw.line(screen, (40, 40, 55), center,
                             (center[0], center[1] - 55), 6)
            pygame.draw.line(screen, (40, 40, 55), center,
                             (center[0] + 40, center[1]), 6)

    keys_pool = list(range(pygame.K_a, pygame.K_z + 1))  # every letter A–Z
    key_names = {k: chr(k).upper() for k in keys_pool}

    def time_limit_for(wave):
        return 3000  # 3 seconds per wave

    def new_round(wave):
        return random.choice(keys_pool), pygame.time.get_ticks(), time_limit_for(wave)

    state = "intro"            # "intro", "playing", "won", "gameover"
    wave = 1
    target_key, round_start, time_limit = new_round(wave)
    flash_color = None
    flash_until = 0

    def trigger_flash(color, now, duration=220):
        nonlocal flash_color, flash_until
        flash_color, flash_until = color, now + duration

    def start_game():
        nonlocal state, wave, target_key, round_start, time_limit
        state, wave = "playing", 1
        target_key, round_start, time_limit = new_round(wave)
        loop_sfx("alarm")          # the alarm keeps ringing until you clear it

    while True:
        now = pygame.time.get_ticks()
        elapsed = now - round_start

        # Time out
        if state == "playing" and elapsed > time_limit:
            state = "gameover"
            trigger_flash(RED, now)
            stop_sfx("alarm"); play_sfx("lose")

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit_game()
                elif state == "intro" and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    start_game()
                elif state == "playing":
                    if event.key == target_key:
                        trigger_flash(GREEN, now)
                        play_sfx("correct")
                        if wave >= TOTAL_WAVES:
                            state = "won"
                            stop_sfx("alarm"); play_sfx("win")
                        else:
                            wave += 1
                            target_key, round_start, time_limit = new_round(wave)
                    elif event.key in keys_pool:
                        state = "gameover"
                        trigger_flash(RED, now)
                        stop_sfx("alarm"); play_sfx("wrong")
                elif state == "won" and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    return   # continue to level 2
                elif state == "gameover" and event.key == pygame.K_r:
                    start_game()

        # ── Drawing ──────────────────────────────────────────────────────────
        screen.blit(background, (0, 0))

        if state == "intro":
            draw_text("TURN OFF THE ALARM!", big_font, WHITE, (WIDTH // 2, 50))
            draw_clock(center=(WIDTH // 2, 230))
            draw_text("HOW TO PLAY", prompt_font, ACCENT, (WIDTH // 2, 365))
            draw_wrapped(
                "Your alarm is blaring! A random letter key appears each wave. "
                "Press the matching key before the timer runs out. "
                "Clear all 5 waves to shut the alarm off and start your day.",
                small_font, MUTED, WIDTH // 2, 405, 620)
            # Gentle pulse on the call-to-action
            pulse = 0.5 + 0.5 * math.sin(now / 250)
            glow = (int(MUTED[0] + (WHITE[0] - MUTED[0]) * pulse),
                    int(MUTED[1] + (WHITE[1] - MUTED[1]) * pulse),
                    int(MUTED[2] + (WHITE[2] - MUTED[2]) * pulse))
            draw_text("Press  ENTER  to begin", prompt_font, glow, (WIDTH // 2, 500))
            draw_text("ESC to quit", small_font, MUTED, (WIDTH // 2, 550))

        elif state == "playing":
            draw_text(f"WAVE  {wave} / {TOTAL_WAVES}", hud_font, WHITE, (WIDTH // 2, 40))
            draw_clock()

            remaining = max(0.0, min(1.0, 1 - elapsed / time_limit))

            # Key card with a gentle pulse
            pulse = 1 + 0.04 * math.sin(now / 120)
            size = int(150 * pulse)
            card = pygame.Rect(0, 0, size, size)
            card.center = (WIDTH // 2, 385)
            draw_panel(card, (255, 255, 255, 22), radius=26)
            pygame.draw.rect(screen, ACCENT, card, width=4, border_radius=26)
            draw_text("PRESS", prompt_font, MUTED, (WIDTH // 2, 300))
            draw_text(key_names[target_key], key_font, WHITE, card.center)

            # Timer bar: track + color-shifting fill
            pygame.draw.rect(screen, (50, 50, 65), (BAR_X, BAR_Y, BAR_WIDTH, BAR_HEIGHT),
                             border_radius=13)
            red = int(235 + (70 - 235) * remaining)
            green = int(80 + (220 - 80) * remaining)
            fill_w = int(BAR_WIDTH * remaining)
            if fill_w > 0:
                pygame.draw.rect(screen, (red, green, 90), (BAR_X, BAR_Y, fill_w, BAR_HEIGHT),
                                 border_radius=13)
            draw_text("Press the highlighted letter key", small_font, MUTED, (WIDTH // 2, BAR_Y + 60))

        elif state == "won":
            draw_text("ALARM OFF!", big_font, GREEN, (WIDTH // 2, 150))
            draw_wrapped(
                "You have woken up and you are now going to the bathroom to brush your teeth.",
                msg_font, WHITE, WIDTH // 2, 250, 660)
            draw_text("Press  ENTER  to move on",
                      small_font, MUTED, (WIDTH // 2, 470))

        else:  # gameover
            draw_clock()
            draw_text("THE ALARM KEPT RINGING!", big_font, RED, (WIDTH // 2, 360))
            draw_text(f"You reached wave {wave} of {TOTAL_WAVES}",
                      prompt_font, WHITE, (WIDTH // 2, 430))
            draw_text("Press  R  to try again      ·      ESC to quit",
                      small_font, MUTED, (WIDTH // 2, 490))

        # Feedback flash overlay
        if flash_color and now < flash_until:
            alpha = int(110 * (flash_until - now) / 220)
            flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash.fill((*flash_color, alpha))
            screen.blit(flash, (0, 0))

        present(screen)
        clock.tick(60)


# ==========================================================================
# END SCREEN  (drawn directly on the full window)
# ==========================================================================
def run_end():
    screen = window
    play_sfx("win")          # victory fanfare on the completion screen
    play_music("celebrate")  # celebration music loops on the end screen

    # Colors
    PURPLE_TOP = (35, 20, 110)
    PURPLE_BOTTOM = (70, 35, 180)
    WHITE = (255, 255, 255)
    DARK_BOX = (20, 20, 80)

    # Fonts
    title_font = pygame.font.SysFont("Arial", 90, bold=True)
    message_font = pygame.font.SysFont("Arial", 30, bold=True)
    footer_font = pygame.font.SysFont("Arial", 20)

    # Stars
    stars = []
    for _ in range(180):
        x = random.randint(0, WIN_W)
        y = random.randint(0, WIN_H)
        size = random.randint(1, 4)
        stars.append((x, y, size))

    def draw_gradient():
        for y in range(WIN_H):
            ratio = y / WIN_H

            r = int(PURPLE_TOP[0] * (1 - ratio) + PURPLE_BOTTOM[0] * ratio)
            g = int(PURPLE_TOP[1] * (1 - ratio) + PURPLE_BOTTOM[1] * ratio)
            b = int(PURPLE_TOP[2] * (1 - ratio) + PURPLE_BOTTOM[2] * ratio)

            pygame.draw.line(screen, (r, g, b), (0, y), (WIN_W, y))

    def draw_stars():
        for x, y, size in stars:
            pygame.draw.circle(screen, WHITE, (x, y), size)

    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                quit_game()

        draw_gradient()
        draw_stars()

        # Main Title (NO black shadow)
        title1 = title_font.render(
            "You have completed",
            True,
            WHITE
        )

        title2 = title_font.render(
            "Daily Life Reimagined!",
            True,
            WHITE
        )

        screen.blit(
            title1,
            title1.get_rect(center=(WIN_W // 2, 170))
        )

        screen.blit(
            title2,
            title2.get_rect(center=(WIN_W // 2, 290))
        )

        # Message Box
        box_width = 950
        box_height = 180
        box_x = (WIN_W - box_width) // 2
        box_y = 380

        pygame.draw.rect(
            screen,
            DARK_BOX,
            (box_x, box_y, box_width, box_height),
            border_radius=30
        )

        pygame.draw.rect(
            screen,
            WHITE,
            (box_x, box_y, box_width, box_height),
            4,
            border_radius=30
        )

        line1 = message_font.render(
            "Congrats on completing Daily Life Reimagined!",
            True,
            WHITE
        )

        line2 = message_font.render(
            "You are a real pro! Hope to see you again soon!",
            True,
            WHITE
        )

        screen.blit(
            line1,
            line1.get_rect(center=(WIN_W // 2, box_y + 70))
        )

        screen.blit(
            line2,
            line2.get_rect(center=(WIN_W // 2, box_y + 120))
        )

        footer = footer_font.render(
            "• Daily Tasks Final Boss •",
            True,
            (220, 220, 220)
        )

        screen.blit(
            footer,
            footer.get_rect(center=(WIN_W // 2, 660))
        )

        pygame.display.flip()
        clock.tick(60)


# ==========================================================================
# TITLE CARD  —  a level-name screen shown between stages
# ==========================================================================
def run_title_card(title, level_no=None):
    stop_music()             # make sure no level's music bleeds across the card
    screen = window
    prompt_font = pygame.font.SysFont("Arial", 32, bold=True)
    level_font = pygame.font.SysFont("Arial", 30, bold=True)

    # Pick the largest title size that fits the window width
    size = 110
    while size > 40:
        title_font = pygame.font.SysFont("Arial", size, bold=True)
        if title_font.size(title)[0] <= WIN_W - 160:
            break
        size -= 4

    anim = 0.0
    while True:
        anim += 0.06

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit_game()
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    play_sfx("confirm")
                    return

        screen.blit(BACKDROP, (0, 0))

        # Small "LEVEL N" label above the title
        if level_no is not None:
            lvl = level_font.render(f"LEVEL {level_no}", True, (255, 215, 90))
            screen.blit(lvl, lvl.get_rect(center=(WIN_W // 2, WIN_H // 2 - 110)))

        # Title (soft black drop shadow for depth)
        shadow = title_font.render(title, True, (0, 0, 0))
        screen.blit(shadow, shadow.get_rect(center=(WIN_W // 2 + 4, WIN_H // 2 - 16)))
        text = title_font.render(title, True, (255, 255, 255))
        screen.blit(text, text.get_rect(center=(WIN_W // 2, WIN_H // 2 - 20)))

        # Pulsing "Press ENTER to continue" at the bottom
        pulse = 0.5 + 0.5 * math.sin(anim * 3)
        c = int(150 + 105 * pulse)
        prompt = prompt_font.render("Press  ENTER  to continue", True, (c, c, 60))
        screen.blit(prompt, prompt.get_rect(center=(WIN_W // 2, WIN_H - 70)))

        pygame.display.flip()
        clock.tick(60)


# ==========================================================================
# MAIN — run every screen in order
# ==========================================================================
def main():
    set_selected_character(run_start())           # start screen + character select
    run_title_card("THE ALARM CLOCK", 1)          # Level 1
    run_level1()
    run_title_card("BRUSH OR GET BRUSHED", 2)      # Level 2
    run_level2()
    run_title_card("LUNCH GONE WRONG", 3)               # Level 3
    run_level3()
    run_title_card("STATIONERY MAYHEM", 4)             # Level 4
    run_level4()
    run_title_card("JOURNEY TO THE BEDROOM", 5)  # Level 5
    run_level5()
    run_end()                                      # completion screen


#level 3

import pygame
import sys
import random
import math
import datetime
import subprocess
import threading
import io
import wave
import struct

pygame.init()
try:
    pygame.mixer.init()
except Exception:
    pass

# ── Constants ─────────────────────────────────────────────────────────────────

SCREEN_W, SCREEN_H = 1300, 700
FPS = 60

WHITE        = (255, 255, 255)
BLACK        = (0,   0,   0  )
GRAY         = (140, 140, 140)
DARK_GRAY    = (72,  75,  90 )
RED          = (220, 55,  55 )
DARK_RED     = (155, 28,  28 )
GREEN        = (45,  200, 80 )
DARK_GREEN   = (25,  125, 45 )
BLUE         = (60,  118, 220)
LIGHT_BLUE   = (105, 162, 255)
YELLOW       = (232, 198, 48 )
ORANGE       = (238, 138, 38 )
PURPLE       = (152, 78,  205)
DARK_PURPLE  = (102, 38,  155)
CYAN         = (0,   212, 232)
TABLE_COL    = (160, 100, 45 )
TABLE_DARK   = (118, 73,  28 )
PLATE_COL    = (245, 240, 230)

# Phone / UI palette
PH_BODY      = (16,  18,  32 )
PH_BEZEL     = (38,  42,  68 )
PH_SCREEN    = (6,   8,   20 )
NOTIF_BG     = (24,  26,  44 )
CALL_HEADER  = (14,  18,  40 )

# Difficulty knobs
SCANNER_ACC  = 0.72    # scanner is only ~72 % reliable
CHOOSE_SECS  = 10.0    # seconds to pick a food before auto-death

# Game states
S_START   = "start"
S_NOTIF   = "notif"
S_CALL    = "call"
S_DIAG    = "diag"
S_GAME    = "game"
S_CHOOSE  = "choose"
S_WIN     = "win"
S_DEATH   = "death"
S_OVER    = "over"

EV_SCAN_POP = pygame.USEREVENT + 1
EV_ALL_DONE = pygame.USEREVENT + 2

# Food data
FOOD_NAMES = ["Nasi Lemak", "Laksa", "Biryiani", "Chicken Rice", "Mee Goreng"]
FOOD_IMG_PATHS = [
    "/Users/adnankhiljimohammad/Nasi lemak.jpeg",
    "/Users/adnankhiljimohammad/Laksa.jpeg",
    "/Users/adnankhiljimohammad/Biryiani.jpeg",
    "/Users/adnankhiljimohammad/Chicken Rice.jpeg",
    "/Users/adnankhiljimohammad/Mee goreng.jpeg",
]
FOOD_COLORS = [          # fallback colours if an image fails to load
    (230, 148, 78),
    (178, 220, 98),
    (232, 78,  78),
    (220, 200, 118),
    (148, 178, 220),
]

# TTS text read aloud when dialogue appears
VOICE_TEXT = (
    "Hello. Four of the five foods in front of you have been poisoned. "
    "To use the Food Scanner, click the scanner button, then click a food. "
    "Warning — the scanner can malfunction. "
    "To use the Potion, click the potion button, then click a food. "
    "If the food turns red, it is poisoned. If it turns green, it is safe. "
    "You may only use each tool twice. "
    "Once all tools are used, you will have ten seconds to choose a food to eat. "
    "Choose wisely."
)

# ── Fonts ─────────────────────────────────────────────────────────────────────
font_title  = pygame.font.SysFont("Arial", 42, bold=True)
font_xl     = pygame.font.SysFont("Arial", 34, bold=True)
font_large  = pygame.font.SysFont("Arial", 28, bold=True)
font_medium = pygame.font.SysFont("Arial", 22)
font_small  = pygame.font.SysFont("Arial", 17)
font_tiny   = pygame.font.SysFont("Arial", 13)
font_wall   = pygame.font.SysFont("Arial", 58, bold=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def draw_cx(surf, text, font, color, cx, cy):
    s = font.render(text, True, color)
    surf.blit(s, s.get_rect(center=(cx, cy)))


def rrect(surf, color, rect, radius, alpha=255):
    """Draw a filled rounded rectangle, optionally with transparency."""
    if alpha < 255:
        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(s, (*color, alpha), (0, 0, rect.width, rect.height),
                         border_radius=radius)
        surf.blit(s, rect.topleft)
    else:
        pygame.draw.rect(surf, color, rect, border_radius=radius)


def dim(surf, r, g, b, a):
    ov = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    ov.fill((r, g, b, a))
    surf.blit(ov, (0, 0))


def phone_icon(surf, cx, cy, size, color):
    """Draw a minimal phone handset icon."""
    r = size // 2
    pygame.draw.circle(surf, color, (cx - r // 2, cy - r // 2), r // 3)
    pygame.draw.circle(surf, color, (cx + r // 2, cy + r // 2), r // 3)
    pygame.draw.line(surf, color, (cx - r // 2, cy - r // 2),
                     (cx + r // 2, cy + r // 2), max(2, size // 8))


def person_silhouette(surf, cx, cy, radius, col=(100, 115, 155)):
    """Draw a simple head-and-shoulders silhouette inside a circle avatar."""
    head_r  = int(radius * 0.33)
    head_cy = int(cy - radius * 0.22)
    pygame.draw.circle(surf, col, (cx, head_cy), head_r)
    # Shoulders — upper half of an ellipse blitted via SRCALPHA surface
    sw = int(radius * 0.78)
    sh = int(radius * 0.52)
    s_surf = pygame.Surface((sw * 2, sh), pygame.SRCALPHA)
    pygame.draw.ellipse(s_surf, (*col, 255), (0, 0, sw * 2, sh))
    surf.blit(s_surf, (cx - sw, int(cy + radius * 0.18)))


_tts_proc = None

def speak(text):
    """Fire-and-forget macOS TTS (Samantha voice) in a daemon thread."""
    global _tts_proc
    stop_speak()  # Kill any existing voice first
    def _run():
        global _tts_proc
        try:
            _tts_proc = subprocess.Popen(
                ['say', '-v', 'Samantha', '-r', '175', text]
            )
            _tts_proc.wait()
        except Exception:
            pass
    threading.Thread(target=_run, daemon=True).start()

def stop_speak():
    """Stop the currently playing voice immediately."""
    global _tts_proc
    if _tts_proc is not None:
        try:
            _tts_proc.terminate()
            _tts_proc.wait(timeout=0.5)
        except Exception:
            pass
        _tts_proc = None


def make_ring_sound():
    """Synthesize a looping 'brrring … brrring' phone ring as a pygame Sound.

    Built in-memory with the stdlib (no external audio file needed). Returns
    None if the mixer is unavailable so callers can degrade silently.
    """
    try:
        rate = 22050
        amp  = 11000
        # One loop = two short rings then a gap, like a classic phone.
        pattern = [(0.4, True), (0.2, False), (0.4, True), (1.2, False)]
        frames  = bytearray()
        n = 0
        for dur, on in pattern:
            count = int(rate * dur)
            for i in range(count):
                if on:
                    t = (n + i) / rate
                    v = (math.sin(2 * math.pi * 440 * t) +
                         math.sin(2 * math.pi * 480 * t)) * 0.5
                    frames += struct.pack('<h', int(v * amp))
                else:
                    frames += struct.pack('<h', 0)
            n += count

        buf = io.BytesIO()
        with wave.open(buf, 'wb') as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(rate)
            w.writeframes(bytes(frames))
        buf.seek(0)
        return pygame.mixer.Sound(buf)
    except Exception:
        return None


# ── Button ────────────────────────────────────────────────────────────────────

class Button:
    def __init__(self, x, y, w, h, label, col, hcol, tcol=WHITE, font=None):
        self.rect    = pygame.Rect(x, y, w, h)
        self.label   = label
        self.col     = col
        self.hcol    = hcol
        self.tcol    = tcol
        self.font    = font or font_medium
        self.hovered = False
        self._t      = 0.0     # pulse timer

    def tick(self, dt):  self._t = (self._t + dt * 2.2) % (2 * math.pi)
    def hover(self, pos): self.hovered = self.rect.collidepoint(pos)
    def hit(self, pos):   return self.rect.collidepoint(pos)

    def draw(self, surf, glow=False):
        if glow:
            a = int(72 + 56 * math.sin(self._t))
            rrect(surf, self.col, self.rect.inflate(18, 18), 18, a)
        c = self.hcol if self.hovered else self.col
        rrect(surf, c,         self.rect, 10)
        pygame.draw.rect(surf, DARK_GRAY, self.rect, 2, border_radius=10)
        draw_cx(surf, self.label, self.font, self.tcol, *self.rect.center)


# ── Food ──────────────────────────────────────────────────────────────────────

class Food:
    def __init__(self, idx, x, y, w, h, img=None, name=None):
        self.idx         = idx
        self.rect        = pygame.Rect(x, y, w, h)
        self.is_poisoned = True
        self.base_col    = FOOD_COLORS[idx]
        self.label       = name or f"Food {idx + 1}"
        self.img         = img       # pre-scaled surface or None
        self.clickable   = False
        self.hovered     = False
        self.scan_t      = 0.0
        self.pour_t      = 0.0
        self.flash_t     = 0.0
        self.flash_col   = None

    def trigger_scan(self): self.scan_t = 0.85
    def trigger_pour(self, poison):
        self.pour_t    = 0.85
        self.flash_col = RED if poison else GREEN

    def update(self, dt):
        prev        = self.pour_t
        self.scan_t  = max(0.0, self.scan_t  - dt)
        self.pour_t  = max(0.0, self.pour_t  - dt)
        self.flash_t = max(0.0, self.flash_t - dt)
        if prev > 0 and self.pour_t == 0 and self.flash_col:
            self.flash_t = 1.6

    def draw(self, surf):
        # Plate shadow + plate rim
        pl = self.rect.inflate(22, 12)
        pygame.draw.ellipse(surf, (172, 142, 102), pl.move(5, 5))
        pygame.draw.ellipse(surf, PLATE_COL, pl)
        pygame.draw.ellipse(surf, (205, 200, 188), pl, 3)

        inner = self.rect.inflate(-10, -10)

        if self.img:
            # Clip image to inner rect bounds
            old_clip = surf.get_clip()
            surf.set_clip(inner)
            surf.blit(self.img, inner.topleft)
            surf.set_clip(old_clip)
            pygame.draw.rect(surf, (200, 192, 175), inner, 1, border_radius=4)
        else:
            pygame.draw.rect(surf, self.base_col, inner, border_radius=8)

        # Red/green flash overlay when potion is used
        if self.flash_t > 0 and self.flash_col:
            if self.flash_t > 1.3:
                a = int(200 * (1.6 - self.flash_t) / 0.3)
            elif self.flash_t < 0.4:
                a = int(180 * self.flash_t / 0.4)
            else:
                a = 180
            rrect(surf, self.flash_col, inner, 8, max(0, min(255, a)))

        # Scanner sweep line
        if self.scan_t > 0:
            prog = 1.0 - (self.scan_t / 0.85)
            sy   = self.rect.top + int(prog * self.rect.height)
            tint = pygame.Surface((self.rect.width, max(1, sy - self.rect.top)),
                                  pygame.SRCALPHA)
            tint.fill((0, 200, 255, 52))
            surf.blit(tint, (self.rect.left, self.rect.top))
            pygame.draw.line(surf, CYAN,
                             (self.rect.left, sy), (self.rect.right, sy), 3)

        # Potion drop animation
        if self.pour_t > 0:
            p  = 1.0 - (self.pour_t / 0.85)
            dy = self.rect.top - 42 + int(p * 62)
            pygame.draw.circle(surf, PURPLE, (self.rect.centerx, dy), 9)

        # Hover highlight when food is selectable
        if self.clickable and self.hovered:
            pygame.draw.rect(surf, YELLOW, self.rect.inflate(26, 14), 3, border_radius=6)

        draw_cx(surf, self.label, font_small, BLACK,
                self.rect.centerx, self.rect.bottom + 22)


# ── Level 3 ───────────────────────────────────────────────────────────────────

class Level3:

    # ── Phone frame geometry ──────────────────────────────────────────────────
    _PH_W, _PH_H = 318, 618
    _PH_X = SCREEN_W // 2 - _PH_W // 2
    _PH_Y = SCREEN_H // 2 - _PH_H // 2

    @property
    def _pr(self):
        return pygame.Rect(self._PH_X, self._PH_Y, self._PH_W, self._PH_H)

    @property
    def _scr(self):
        return pygame.Rect(self._PH_X + 10, self._PH_Y + 42,
                           self._PH_W - 20, self._PH_H - 66)

    # ── Init ──────────────────────────────────────────────────────────────────
    def __init__(self):
        self.screen         = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Level 3: Poisoned Lunch")
        self.clock          = pygame.time.Clock()
        self.level_complete = False
        self.attempts       = 1
        self.ring_snd       = make_ring_sound()   # synthesized phone ring

        # Load food images once at startup; missing files get None (fallback colour)
        self._food_imgs = []
        for path in FOOD_IMG_PATHS:
            try:
                img = pygame.image.load(path).convert_alpha()
                self._food_imgs.append(img)
            except Exception:
                self._food_imgs.append(None)

        self._reset()
        # Skip the "LUNCH GONE WRONG" title page — start straight at the phone
        # call. _prev_state differs from the S_NOTIF start state so the ring
        # sound triggers on the first update frame.
        self._prev_state = S_START

    def _reset(self):
        pygame.time.set_timer(EV_SCAN_POP, 0)
        pygame.time.set_timer(EV_ALL_DONE, 0)

        self.state        = S_NOTIF
        self.scanner_uses = 2
        self.potion_uses  = 2
        self.equipped     = None
        self.popup_msg    = None
        self.popup_t      = 0.0
        self.choose_t     = 0.0
        self._pending     = None
        self._start_delay = None   # countdown from ENTER → phone rings

        if getattr(self, "ring_snd", None):
            self.ring_snd.stop()

        # Phone animation state
        self.ring_t     = 0.0
        self.call_t     = 0.0
        self.dot_t      = 0.0
        self.dot_n      = 0
        self.slide      = 0.0    # 0 → 1 notification slide-in
        self.slide_done = False

        # Randomise safe food — uniform pick, changes every round
        safe  = random.randint(0, 4)
        fw, fh = 148, 98
        gap   = 32
        total = 5 * fw + 4 * gap
        sx    = (SCREEN_W - total) // 2
        fy    = SCREEN_H // 2 - 32

        self.foods = []
        for i in range(5):
            raw = self._food_imgs[i] if i < len(self._food_imgs) else None
            img = None
            if raw is not None:
                img = pygame.transform.smoothscale(raw, (fw - 10, fh - 10))
            f = Food(i, sx + i * (fw + gap), fy, fw, fh,
                     img=img, name=FOOD_NAMES[i])
            f.is_poisoned = (i != safe)
            self.foods.append(f)

        self._mk_buttons()

    def _mk_buttons(self):
        cx, cy = SCREEN_W // 2, SCREEN_H // 2
        scr    = self._scr

        self.btn_pickup   = Button(cx - 90, scr.bottom - 120, 180, 52,
                                   "PICK UP", GREEN, DARK_GREEN, font=font_large)
        self.btn_continue = Button(cx - 72, scr.bottom - 50, 144, 42,
                                   "Continue", BLUE, (38, 88, 178))
        self.btn_scanner  = Button(448,  SCREEN_H - 128, 162, 58,
                                   "Food Scanner", BLUE, (38, 88, 178), font=font_small)
        self.btn_potion   = Button(630, SCREEN_H - 128, 162, 58,
                                   "Potion", PURPLE, DARK_PURPLE, font=font_small)
        self.btn_proceed  = Button(cx - 122, cy + 78, 244, 52,
                                   "Proceed to Level 4", GREEN, DARK_GREEN)
        self.btn_restart  = Button(cx - 100, cy + 78, 200, 52,
                                   "Restart", RED, DARK_RED)

    # ── Run loop ──────────────────────────────────────────────────────────────
    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                self._event(ev)
            self._update(dt)
            self._draw()
            pygame.display.flip()
            if self.level_complete:
                return True

    # ── Events ────────────────────────────────────────────────────────────────
    def _event(self, ev):
        if ev.type == pygame.MOUSEMOTION:
            p = ev.pos
            for f in self.foods: f.hovered = f.rect.collidepoint(p) and f.clickable
            for b in self._all_btns(): b.hover(p)

        elif ev.type == EV_SCAN_POP:
            pygame.time.set_timer(EV_SCAN_POP, 0)
            if self._pending:
                self._pop(self._pending, 1.6)
                self._pending = None

        elif ev.type == EV_ALL_DONE:
            pygame.time.set_timer(EV_ALL_DONE, 0)
            self.state    = S_CHOOSE
            self.choose_t = CHOOSE_SECS
            self._clickable(True)

        elif ev.type == pygame.KEYDOWN:
            if (self.state == S_START and self._start_delay is None
                    and ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER)):
                self._start_delay = 2.0   # phone rings 2s after ENTER
                self.slide = 0.0          # reset the notification slide-in

        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            self._click(ev.pos)

    def _click(self, pos):
        s = self.state

        if s == S_NOTIF:
            bw, bh = 492, 98
            bx = SCREEN_W // 2 - bw // 2
            by = 16 + int((self.slide - 1.0) * 130)
            if pygame.Rect(bx, by, bw, bh).collidepoint(pos):
                self.state = S_CALL

        elif s == S_CALL:
            if self.btn_pickup.hit(pos):
                self.state  = S_DIAG
                self.call_t = 0.0
                speak(VOICE_TEXT)   # read instructions aloud via macOS TTS

        elif s == S_DIAG:
            if self.btn_continue.hit(pos): self.state = S_GAME

        elif s == S_GAME:    self._game_click(pos)

        elif s == S_CHOOSE:
            for i, f in enumerate(self.foods):
                if f.rect.collidepoint(pos) and f.clickable:
                    self._pick(i); break

        elif s == S_WIN:
            if self.btn_proceed.hit(pos): self.level_complete = True

        elif s == S_DEATH:   self._reset()

        elif s == S_OVER:
            if self.btn_restart.hit(pos):
                self.attempts = 1; self._reset()

    def _game_click(self, pos):
        if self.btn_scanner.hit(pos) and self.scanner_uses > 0:
            self.equipped = None if self.equipped == "scanner" else "scanner"
            self._clickable(self.equipped is not None); return
        if self.btn_potion.hit(pos) and self.potion_uses > 0:
            self.equipped = None if self.equipped == "potion" else "potion"
            self._clickable(self.equipped is not None); return
        if self.equipped:
            for i, f in enumerate(self.foods):
                if f.rect.collidepoint(pos) and f.clickable:
                    self._use(i); return

    def _use(self, idx):
        f    = self.foods[idx]
        tool = self.equipped
        self.equipped = None
        self._clickable(False)

        if tool == "scanner":
            self.scanner_uses -= 1
            f.trigger_scan()
            # Scanner lies ~28 % of the time
            result = f.is_poisoned
            if random.random() > SCANNER_ACC:
                result = not result
            self._pending = ("Foreign substance detected." if result
                             else "Food appears safe.")
            pygame.time.set_timer(EV_SCAN_POP, 920)

        elif tool == "potion":
            self.potion_uses -= 1
            f.trigger_pour(f.is_poisoned)   # potion always truthful

        if self.scanner_uses == 0 and self.potion_uses == 0:
            pygame.time.set_timer(EV_ALL_DONE, 2100)

    def _pick(self, idx):
        self._clickable(False)
        if not self.foods[idx].is_poisoned:
            self.state = S_WIN
        else:
            self.attempts -= 1
            self.state = S_OVER if self.attempts <= 0 else S_DEATH

    def _clickable(self, v):
        for f in self.foods: f.clickable = v

    def _pop(self, msg, dur=2.6):
        self.popup_msg = msg
        self.popup_t   = dur

    def _all_btns(self):
        return (self.btn_pickup, self.btn_continue, self.btn_scanner,
                self.btn_potion, self.btn_proceed, self.btn_restart)

    # ── Update ────────────────────────────────────────────────────────────────
    def _update(self, dt):
        for f in self.foods: f.update(dt)
        for b in self._all_btns(): b.tick(dt)

        # Stop voice if we exit the dialogue state
        if self.state != S_DIAG:
            stop_speak()

        # Wait 2s after ENTER, then let the phone start ringing
        if self._start_delay is not None:
            self._start_delay -= dt
            if self._start_delay <= 0:
                self._start_delay = None
                self.state = S_NOTIF

        # Ring while the call banner / call screen is showing; silence elsewhere.
        # Trigger the sound the moment we enter the notification state.
        if self.state != self._prev_state:
            if self.state == S_NOTIF and self.ring_snd:
                try: self.ring_snd.play(loops=-1)
                except Exception: pass
            self._prev_state = self.state
        if self.state not in (S_NOTIF, S_CALL) and self.ring_snd:
            self.ring_snd.stop()

        if self.popup_t > 0:
            self.popup_t -= dt
            if self.popup_t <= 0: self.popup_msg = None

        self.ring_t = (self.ring_t + dt) % 3.0
        self.call_t += dt
        self.dot_t  += dt
        if self.dot_t >= 0.42:
            self.dot_t = 0.0
            self.dot_n = (self.dot_n + 1) % 4

        # Notification slides DOWN from above the screen
        if self.state == S_NOTIF:
            self.slide = min(1.0, self.slide + dt * 3.5)

        # Countdown while choosing food
        if self.state == S_CHOOSE:
            self.choose_t -= dt
            if self.choose_t <= 0:
                self._clickable(False)
                self.attempts -= 1
                self.state = S_OVER if self.attempts <= 0 else S_DEATH

    # ── Draw dispatch ─────────────────────────────────────────────────────────
    def _draw(self):
        if self.state == S_START:
            # During the 2s ENTER→ring delay, show the lunch scene for suspense;
            # otherwise show the title screen.
            if self._start_delay is None:
                self._draw_start()
            else:
                self._draw_scene()
            return

        self._draw_scene()

        if   self.state == S_NOTIF:   self._draw_notif()
        elif self.state == S_CALL:    self._draw_call()
        elif self.state == S_DIAG:    self._draw_diag()
        elif self.state == S_GAME:    self._draw_tools(); self._draw_popup()
        elif self.state == S_CHOOSE:  self._draw_choose(); self._draw_popup()
        elif self.state == S_WIN:     self._draw_win()
        elif self.state == S_DEATH:   self._draw_death()
        elif self.state == S_OVER:    self._draw_over()

    # ── Title / start screen ──────────────────────────────────────────────────
    def _draw_start(self):
        cx, cy = SCREEN_W // 2, SCREEN_H // 2

        # Dark vertical gradient backdrop
        for y in range(SCREEN_H):
            t = y / SCREEN_H
            pygame.draw.line(self.screen,
                             (int(30 + t * 26), int(12 + t * 10), int(8 + t * 6)),
                             (0, y), (SCREEN_W, y))

        # Title in a styled box matching the in-game warning panels
        title = font_wall.render("LUNCH GONE WRONG", True, (255, 220, 80))
        tr    = title.get_rect(center=(cx, cy - 56))
        box   = pygame.Rect(tr.left - 44, tr.top - 28, tr.width + 88, tr.height + 56)
        rrect(self.screen, (60, 30, 0), box, 18)
        pygame.draw.rect(self.screen, (240, 160, 40), box, 4, border_radius=18)
        self.screen.blit(title, tr)

        draw_cx(self.screen, "Level 3", font_large, (205, 185, 150), cx, cy + 18)

        # Pulsing "Press ENTER to start" prompt
        pulse = (math.sin(self.ring_t * 3.0) + 1) / 2
        shade = int(150 + 105 * pulse)
        draw_cx(self.screen, "Press ENTER to start", font_xl,
                (shade, shade, shade), cx, cy + 104)

    # ── Scene (wall + table + foods) ──────────────────────────────────────────
    def _draw_scene(self):
        # Wall background
        self.screen.fill((208, 192, 168))

        # "Guess to survive!" — prominent styled box like the tool warning
        ws_text = font_wall.render("Guess to survive!", True, (255, 220, 80))
        ws_r = ws_text.get_rect(center=(SCREEN_W // 2, 96))
        ws_bg = pygame.Rect(ws_r.left - 28, ws_r.top - 14, ws_r.width + 56, ws_r.height + 28)
        rrect(self.screen, (60, 30, 0), ws_bg, 12)
        pygame.draw.rect(self.screen, (240, 160, 40), ws_bg, 3, border_radius=12)
        self.screen.blit(ws_text, ws_r)

        # Table surface
        pygame.draw.rect(self.screen, TABLE_COL,
                         pygame.Rect(0, SCREEN_H // 2 - 22, SCREEN_W, SCREEN_H))
        pygame.draw.rect(self.screen, TABLE_DARK,
                         pygame.Rect(0, SCREEN_H // 2 - 22, SCREEN_W, 15))
        for i in range(0, SCREEN_W, 82):
            pygame.draw.line(self.screen, (146, 86, 34),
                             (i, SCREEN_H // 2), (i + 54, SCREEN_H), 1)

        for f in self.foods: f.draw(self.screen)

        self.screen.blit(
            font_large.render("Level 3: Poisoned Lunch", True, DARK_GRAY), (18, 18))
        self.screen.blit(
            font_small.render(f"Attempts: {self.attempts}/1", True, DARK_GRAY), (18, 58))

    # ── Phone shell ───────────────────────────────────────────────────────────
    def _draw_shell(self):
        pr  = self._pr
        scr = self._scr

        for i in range(6, 0, -1):
            sh = pr.inflate(i * 2, i * 2).move(i, i + 2)
            rrect(self.screen, (0, 0, 0), sh, 40, int(35 * (i / 6)))

        rrect(self.screen, PH_BODY, pr, 38)
        top_strip = pygame.Rect(pr.left + 2, pr.top + 2, pr.width - 4, pr.height // 3)
        rrect(self.screen, (28, 32, 52), top_strip, 36, 60)
        pygame.draw.rect(self.screen, PH_BEZEL, pr, 2, border_radius=38)
        rrect(self.screen, PH_SCREEN, scr, 26)

        nw, nh = 108, 22
        notch = pygame.Rect(SCREEN_W // 2 - nw // 2, scr.top, nw, nh)
        rrect(self.screen, PH_BODY, notch, 11)
        pygame.draw.circle(self.screen, (28, 32, 52),
                           (notch.right - 16, notch.centery), 5)

        for oy in (68, 108):
            rrect(self.screen, PH_BEZEL,
                  pygame.Rect(pr.left - 4, pr.top + oy, 4, 30), 2)
        rrect(self.screen, PH_BEZEL,
              pygame.Rect(pr.right, pr.top + 90, 4, 52), 2)

        rrect(self.screen, (55, 60, 98),
              pygame.Rect(SCREEN_W // 2 - 46, scr.bottom - 10, 92, 4), 2)

        self._draw_status(scr)

    def _draw_status(self, scr):
        t_str = datetime.datetime.now().strftime("%H:%M")
        self.screen.blit(font_tiny.render(t_str, True, (172, 178, 210)),
                         (scr.left + 10, scr.top + 5))
        for j in range(4):
            bh = 3 + j * 3
            bx = scr.right - 56 + j * 7
            pygame.draw.rect(self.screen, (155, 162, 200),
                             pygame.Rect(bx, scr.top + 13 - bh, 5, bh), border_radius=1)
        br = pygame.Rect(scr.right - 24, scr.top + 4, 20, 10)
        pygame.draw.rect(self.screen, (155, 162, 200), br, 1, border_radius=2)
        pygame.draw.rect(self.screen, (88, 198, 108),
                         pygame.Rect(br.left + 2, br.top + 2, 12, 6), border_radius=1)
        pygame.draw.rect(self.screen, (155, 162, 200),
                         pygame.Rect(br.right, br.top + 3, 2, 4))

    # ── iOS-style incoming call banner (slides down from top) ─────────────────
    def _draw_notif(self):
        bw, bh = 492, 98
        bx = SCREEN_W // 2 - bw // 2
        by = 16 + int((self.slide - 1.0) * 130)   # negative → above screen edge
        nr = pygame.Rect(bx, by, bw, bh)

        # Drop shadow
        rrect(self.screen, (0, 0, 0), nr.move(0, 6), 24, 58)

        # iOS dark frosted-glass body
        rrect(self.screen, (28, 28, 40), nr, 24)
        rrect(self.screen, (255, 255, 255), nr, 24, 18)   # subtle top highlight
        pygame.draw.rect(self.screen, (72, 78, 108), nr, 1, border_radius=24)

        # Thin green accent line at very top of banner
        rrect(self.screen, (38, 200, 85),
              pygame.Rect(nr.left + 30, nr.top, nr.width - 60, 3), 2)

        # Green app-icon circle with phone glyph
        ico_cx, ico_cy = nr.left + 54, nr.centery
        pygame.draw.circle(self.screen, (38, 200, 88), (ico_cx, ico_cy), 26)
        pygame.draw.circle(self.screen, (28, 158, 68), (ico_cx, ico_cy), 26, 2)
        phone_icon(self.screen, ico_cx, ico_cy, 24, WHITE)

        # Text
        tx = nr.left + 94
        self.screen.blit(
            font_large.render("Anonymous Caller", True, WHITE), (tx, nr.top + 13))
        self.screen.blit(
            font_small.render("Incoming Call  ·  now", True, (152, 158, 202)),
            (tx, nr.top + 45))

        # Accept / Decline pills — appear once banner is mostly visible
        if self.slide > 0.78:
            dec_r = pygame.Rect(nr.right - 152, nr.centery - 15, 65, 30)
            acc_r = pygame.Rect(nr.right - 80,  nr.centery - 15, 65, 30)
            rrect(self.screen, (185, 38, 38), dec_r, 15)
            rrect(self.screen, (36, 178, 72), acc_r, 15)
            draw_cx(self.screen, "Decline", font_tiny, WHITE,
                    dec_r.centerx, dec_r.centery)
            draw_cx(self.screen, "Accept",  font_tiny, WHITE,
                    acc_r.centerx, acc_r.centery)
            self.screen.blit(
                font_tiny.render("tap to answer  ›", True, (96, 104, 148)),
                (tx, nr.bottom - 18))

        # Pulsing glow outline
        pulse = (math.sin(self.ring_t * 3.0) + 1) / 2
        rrect(self.screen, (38, 198, 84),
              nr.inflate(int(pulse * 10), int(pulse * 10)), 26,
              int(28 + 22 * pulse))

    # ── Incoming call screen ──────────────────────────────────────────────────
    def _draw_call(self):
        dim(self.screen, 4, 6, 18, 235)
        self._draw_shell()
        scr = self._scr
        cx  = SCREEN_W // 2

        # Gradient fill inside screen
        grad_h = scr.height - 22
        for y in range(grad_h):
            t = y / grad_h
            pygame.draw.line(self.screen,
                             (int(6 + t * 10), int(8 + t * 14), int(20 + t * 30)),
                             (scr.left, scr.top + 22 + y),
                             (scr.right - 1, scr.top + 22 + y))

        avatar_cy = scr.top + 170

        # Animated expanding rings
        for i in range(4):
            phase  = ((self.ring_t / 1.5) + i * 0.25) % 1.0
            radius = int(56 + phase * 88)
            alpha  = int(150 * (1.0 - phase))
            rs = pygame.Surface((radius * 2 + 6, radius * 2 + 6), pygame.SRCALPHA)
            pygame.draw.circle(rs, (42, 195, 90, alpha),
                               (radius + 3, radius + 3), radius, 2)
            self.screen.blit(rs, (cx - radius - 3, avatar_cy - radius - 3))

        # Avatar circle + person silhouette
        pygame.draw.circle(self.screen, (22, 26, 52), (cx, avatar_cy), 56)
        pygame.draw.circle(self.screen, (38, 168, 82), (cx, avatar_cy), 56, 2)
        person_silhouette(self.screen, cx, avatar_cy, 56)

        draw_cx(self.screen, "Anonymous Caller", font_large, WHITE,
                cx, avatar_cy + 82)
        dots = "•" * self.dot_n + " " * (3 - self.dot_n)
        draw_cx(self.screen, f"Incoming call {dots}", font_small, (138, 148, 200),
                cx, avatar_cy + 116)

        # Decline (visual only)
        dec_cx = cx - 88
        pygame.draw.circle(self.screen, (60, 28, 28), (dec_cx, scr.bottom - 78), 28)
        phone_icon(self.screen, dec_cx, scr.bottom - 78, 26, (180, 60, 60))
        draw_cx(self.screen, "Decline", font_tiny, (155, 80, 80),
                dec_cx, scr.bottom - 42)

        # Accept (pulsing, clickable)
        acc_cx = cx + 88
        pulse_a = int(90 + 70 * math.sin(self.ring_t * 3))
        rrect(self.screen, GREEN,
              pygame.Rect(acc_cx - 36, scr.bottom - 106, 72, 56), 28, pulse_a)
        pygame.draw.circle(self.screen, DARK_GREEN, (acc_cx, scr.bottom - 78), 28)
        phone_icon(self.screen, acc_cx, scr.bottom - 78, 26, WHITE)
        draw_cx(self.screen, "Accept", font_tiny, (130, 220, 130),
                acc_cx, scr.bottom - 42)

        # Reposition btn_pickup rect over the accept circle for hit-detection
        self.btn_pickup.rect.centerx = acc_cx
        self.btn_pickup.rect.centery = scr.bottom - 78
        self.btn_pickup.rect.width   = 56
        self.btn_pickup.rect.height  = 56

    # ── In-call dialogue ──────────────────────────────────────────────────────
    def _draw_diag(self):
        dim(self.screen, 4, 6, 18, 235)
        self._draw_shell()
        scr = self._scr
        cx  = SCREEN_W // 2

        for y in range(scr.height - 22):
            t = y / (scr.height - 22)
            pygame.draw.line(self.screen,
                             (int(6 + t * 8), int(8 + t * 12), int(20 + t * 28)),
                             (scr.left, scr.top + 22 + y),
                             (scr.right - 1, scr.top + 22 + y))

        hdr = pygame.Rect(scr.left, scr.top + 22, scr.width, 36)
        rrect(self.screen, CALL_HEADER, hdr, 0)
        mins, secs = divmod(int(self.call_t), 60)
        draw_cx(self.screen, f"{mins:02d}:{secs:02d}", font_tiny, GREEN,
                cx, hdr.centery + 8)
        draw_cx(self.screen, "Anonymous Caller", font_small, (165, 172, 218),
                cx, scr.top + 31)

        # Small avatar + person silhouette
        pygame.draw.circle(self.screen, (22, 26, 52), (cx, scr.top + 82), 28)
        pygame.draw.circle(self.screen, (38, 168, 82), (cx, scr.top + 82), 28, 2)
        person_silhouette(self.screen, cx, scr.top + 82, 28, (85, 100, 150))

        # Message bubble
        bub = pygame.Rect(scr.left + 12, scr.top + 118, scr.width - 24, 368)
        rrect(self.screen, (18, 22, 46), bub, 14)
        pygame.draw.rect(self.screen, (38, 42, 78), bub, 1, border_radius=14)
        tail = [(bub.left + 18, bub.top),
                (bub.left + 4,  bub.top - 12),
                (bub.left + 34, bub.top)]
        pygame.draw.polygon(self.screen, (18, 22, 46), tail)

        # Dialogue — explains both tools and their colour-coded results
        dialogue = [
            ("Hello. Four of the five foods",          WHITE),
            ("have been poisoned.",                     WHITE),
            ("",                                        WHITE),
            ("FOOD SCANNER: tap it, then tap",         CYAN),
            ("a food. Scans for poison.",               CYAN),
            ("May give false readings (28%).",          CYAN),
            ("",                                        WHITE),
            ("POTION: tap it, then tap a food.",        (155, 215, 255)),
            ("RED flash = Poisoned.",                   RED),
            ("GREEN flash = Safe.",                     GREEN),
            ("Potion never lies.",                      (155, 215, 255)),
            ("",                                        WHITE),
            ("2 uses each. Scanner may lie —",          ORANGE),
            ("cross-check with the Potion!",            ORANGE),
            ("",                                        WHITE),
            ("10 secs to choose. Good luck.",           RED),
        ]
        y = bub.top + 12
        for line, col in dialogue:
            if line == "":
                y += 5; continue
            self.screen.blit(font_tiny.render(line, True, col), (bub.left + 12, y))
            y += font_tiny.get_linesize() + 1

        self.btn_continue.rect.centerx = cx
        self.btn_continue.rect.bottom  = scr.bottom - 20
        self.btn_continue.draw(self.screen)

    # ── Tool UI ───────────────────────────────────────────────────────────────
    def _draw_tools(self):
        pan = pygame.Surface((448, 156), pygame.SRCALPHA)
        pan.fill((26, 26, 46, 172))
        self.screen.blit(pan, (426, SCREEN_H - 168))
        pygame.draw.rect(self.screen, DARK_GRAY,
                         pygame.Rect(426, SCREEN_H - 168, 448, 156), 2, border_radius=10)

        equipped_scan = self.equipped == "scanner"
        sc = LIGHT_BLUE if equipped_scan else (BLUE if self.scanner_uses > 0 else DARK_GRAY)
        sh = (138, 188, 255) if self.scanner_uses > 0 else DARK_GRAY
        self.btn_scanner.col  = sc
        self.btn_scanner.hcol = sh
        self.btn_scanner.draw(self.screen, glow=equipped_scan)
        self.screen.blit(font_tiny.render(f"Uses: {self.scanner_uses}/2", True, WHITE),
                         (450, SCREEN_H - 60))

        equipped_pot = self.equipped == "potion"
        pc = (198, 118, 255) if equipped_pot else (PURPLE if self.potion_uses > 0 else DARK_GRAY)
        ph = (168, 78, 222)  if self.potion_uses > 0 else DARK_GRAY
        self.btn_potion.col  = pc
        self.btn_potion.hcol = ph
        self.btn_potion.draw(self.screen, glow=equipped_pot)
        self.screen.blit(font_tiny.render(f"Uses: {self.potion_uses}/2", True, WHITE),
                         (632, SCREEN_H - 60))

        # Equipped hint — sits highest so it never overlaps the warning below it
        if self.equipped:
            hint = font_small.render(
                f"{self.equipped.title()} equipped — click a food to use", True, YELLOW)
            hint_r = hint.get_rect(center=(SCREEN_W // 2, SCREEN_H - 226))
            hint_bg = pygame.Rect(hint_r.left - 14, hint_r.top - 5,
                                  hint_r.width + 28, hint_r.height + 10)
            rrect(self.screen, (20, 20, 40), hint_bg, 8)
            pygame.draw.rect(self.screen, YELLOW, hint_bg, 2, border_radius=8)
            self.screen.blit(hint, hint_r)

        # Prominent scanner vs potion reliability warning with background
        warn_txt = font_small.render(
            "⚠  Scanner may malfunction (28% error)  •  Potion is reliable  ✓",
            True, (255, 220, 80))
        warn_r = warn_txt.get_rect(center=(SCREEN_W // 2, SCREEN_H - 188))
        warn_bg = pygame.Rect(warn_r.left - 16, warn_r.top - 6, warn_r.width + 32, warn_r.height + 12)
        rrect(self.screen, (60, 30, 0), warn_bg, 8)
        pygame.draw.rect(self.screen, (240, 160, 40), warn_bg, 2, border_radius=8)
        self.screen.blit(warn_txt, warn_r)

    # ── Choose prompt + countdown bar ─────────────────────────────────────────
    def _draw_choose(self):
        msg = font_large.render("Choose a food to eat.", True, WHITE)
        mr  = msg.get_rect(center=(SCREEN_W // 2, SCREEN_H - 158))
        bg  = pygame.Surface((mr.width + 48, mr.height + 24), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 162))
        self.screen.blit(bg,  (mr.left - 24, mr.top - 12))
        self.screen.blit(msg, mr)

        frac    = max(0.0, self.choose_t / CHOOSE_SECS)
        bar_w   = 304
        bx      = SCREEN_W // 2 - bar_w // 2
        by      = SCREEN_H - 116
        bar_col = GREEN if frac > 0.45 else (ORANGE if frac > 0.22 else RED)
        pygame.draw.rect(self.screen, DARK_GRAY,
                         pygame.Rect(bx, by, bar_w, 14), border_radius=7)
        pygame.draw.rect(self.screen, bar_col,
                         pygame.Rect(bx, by, int(bar_w * frac), 14), border_radius=7)
        pygame.draw.rect(self.screen, GRAY,
                         pygame.Rect(bx, by, bar_w, 14), 2, border_radius=7)
        draw_cx(self.screen, f"{max(0.0, self.choose_t):.1f}s", font_small, WHITE,
                SCREEN_W // 2, by + 30)

    def _draw_popup(self):
        if not self.popup_msg or self.popup_t <= 0: return
        pr = pygame.Rect(SCREEN_W // 2 - 272, SCREEN_H // 2 - 56, 544, 112)
        rrect(self.screen, (16, 18, 36), pr, 12)
        pygame.draw.rect(self.screen, WHITE, pr, 2, border_radius=12)
        draw_cx(self.screen, self.popup_msg, font_medium, WHITE,
                SCREEN_W // 2, SCREEN_H // 2)

    def _draw_win(self):
        dim(self.screen, 0, 26, 0, 172)
        pr = pygame.Rect(SCREEN_W // 2 - 302, SCREEN_H // 2 - 162, 604, 326)
        rrect(self.screen, (10, 44, 14), pr, 15)
        pygame.draw.rect(self.screen, GREEN, pr, 3, border_radius=15)
        draw_cx(self.screen, "Correct. You survived.", font_xl, GREEN,
                SCREEN_W // 2, SCREEN_H // 2 - 88)
        draw_cx(self.screen, "Congratulations, you completed Level 3.",
                font_medium, WHITE, SCREEN_W // 2, SCREEN_H // 2 - 32)
        self.btn_proceed.rect.centerx = SCREEN_W // 2
        self.btn_proceed.rect.top     = SCREEN_H // 2 + 18
        self.btn_proceed.draw(self.screen)

    def _draw_death(self):
        dim(self.screen, 56, 0, 0, 188)
        pr = pygame.Rect(SCREEN_W // 2 - 262, SCREEN_H // 2 - 132, 524, 264)
        rrect(self.screen, (46, 6, 6), pr, 15)
        pygame.draw.rect(self.screen, RED, pr, 3, border_radius=15)
        draw_cx(self.screen, "You died. Try again.", font_xl, RED,
                SCREEN_W // 2, SCREEN_H // 2 - 54)
        draw_cx(self.screen, f"Attempts remaining: {self.attempts}",
                font_medium, WHITE, SCREEN_W // 2, SCREEN_H // 2 + 4)
        draw_cx(self.screen, "Click anywhere to continue.",
                font_small, GRAY, SCREEN_W // 2, SCREEN_H // 2 + 50)

    def _draw_over(self):
        dim(self.screen, 16, 0, 0, 215)
        pr = pygame.Rect(SCREEN_W // 2 - 232, SCREEN_H // 2 - 132, 464, 264)
        rrect(self.screen, (30, 4, 4), pr, 15)
        pygame.draw.rect(self.screen, DARK_RED, pr, 3, border_radius=15)
        draw_cx(self.screen, "GAME OVER", font_title, RED,
                SCREEN_W // 2, SCREEN_H // 2 - 40)
        self.btn_restart.rect.centerx = SCREEN_W // 2
        self.btn_restart.rect.top     = SCREEN_H // 2 + 28
        self.btn_restart.draw(self.screen)


# ── Entry ─────────────────────────────────────────────────────────────────────

def run_level3():
    Level3().run()

#level 4

def run_level4():
    attempts = selected_item = scene = scene_start = sfx_fired = target_sprite = target_x = target_y = player_x = player_y = last_teleport = target_vx = target_vy = wp_x = wp_y = wp_time = None
    import pygame
    import random
    import sys
    import math
    import array

    try:
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        pygame.mixer.init()
        SOUND_ON = True
    except Exception:
        pygame.init()
        SOUND_ON = False

    WIDTH, HEIGHT = 1300, 700
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Level 4.1 + 4.2")

    FONT = pygame.font.SysFont(None, 40)
    SMALL_FONT = pygame.font.SysFont(None, 30)
    BIG_FONT = pygame.font.SysFont(None, 70)
    WRITE_FONT = pygame.font.SysFont("comicsansms", 54, bold=True)
    WRITE_FONT_SM = pygame.font.SysFont("comicsansms", 34, bold=True)
    clock = pygame.time.Clock()

    # ----------------------------------------------------------------------
    # SOUND EFFECTS  (synthesised at runtime - no audio files needed)
    # ----------------------------------------------------------------------
    def _snd(samples):
        buf = array.array('h')
        for s in samples:
            v = int(max(-1.0, min(1.0, s)) * 28000)
            buf.append(v)
            buf.append(v)
        return pygame.mixer.Sound(buffer=buf.tobytes())

    def _gen_pencil():         # graphite: rough, dry, low scratching
        n = int(44100 * 0.5)
        out = []
        for i in range(n):
            am = 0.4 + 0.6 * abs(math.sin(2*math.pi*11*i/44100))   # slow rough strokes
            out.append(random.uniform(-1, 1) * am * (0.4 + 0.5 * random.random()) * 0.5)
        return out

    def _gen_pen():            # ballpoint: smoother, quieter glide with a faint hum
        n = int(44100 * 0.5)
        out = []
        for i in range(n):
            am = 0.5 + 0.5 * math.sin(2*math.pi*30*i/44100)        # faster, smoother
            hum = 0.15 * math.sin(2*math.pi*230*i/44100)
            out.append((random.uniform(-1, 1) * 0.22 + hum) * am * 0.4)
        return out

    def _gen_fire():           # more realistic: low roar + sharp crackle pops + hiss
        n = int(44100 * 1.0)
        out = []
        brown = 0.0
        crack = 0.0
        for i in range(n):
            white = random.uniform(-1, 1)
            brown = (brown + 0.02 * white) * 0.996      # brown noise -> low roar
            if random.random() < 0.010:                 # randomly ignite a pop
                crack = random.uniform(-1, 1) * random.uniform(0.5, 1.0)
            crack *= 0.99                               # pop decays over a few ms
            out.append(brown * 3.0 + crack * 0.6 + white * 0.05)
        return out

    def _gen_tear():           # paper ripping
        n = int(44100 * 0.6)
        out = []
        for i in range(n):
            t = i / n
            crack = random.uniform(-1, 1) if random.random() < (0.05 + 0.35 * t) else 0.0
            out.append((random.uniform(-1, 1) * 0.35 + crack * 0.65) * math.sin(math.pi * t))
        return out

    def _gen_tap():            # dull stick tap
        n = int(44100 * 0.2)
        return [math.sin(2*math.pi*170*i/44100) * math.exp(-11*i/n) * 0.7
                + random.uniform(-1, 1) * 0.1 * math.exp(-11*i/n) for i in range(n)]

    SND = {}
    if SOUND_ON:
        try:
            SND = {"pencil": _snd(_gen_pencil()), "pen": _snd(_gen_pen()),
                   "fire": _snd(_gen_fire()), "tear": _snd(_gen_tear()), "tap": _snd(_gen_tap())}
        except Exception:
            SOUND_ON = False

    # ----------------------------------------------------------------------
    # COLOURS
    # ----------------------------------------------------------------------
    BG          = (216, 216, 220)
    SHADOW      = (44, 44, 50)
    PAPER       = (252, 252, 248)
    PAPER_LINE  = (200, 210, 235)

    # Emoji default skin tone (the yellow / golden cartoon colour)
    SKIN        = (245, 200, 80)
    SKIN_LINE   = (203, 158, 52)

    # ----------------------------------------------------------------------
    # ITEM DRAWING  (tip is at (tx, ty), the tool extends DOWNWARD)
    # Each function can draw a flat dark silhouette (shadow=True) or the
    # real colourful object (shadow=False).
    # ----------------------------------------------------------------------
    def _poly(surf, color, pts, outline=None, w=2):
        pts = [(int(p[0]), int(p[1])) for p in pts]
        pygame.draw.polygon(surf, color, pts)
        if outline:
            pygame.draw.polygon(surf, outline, pts, w)

    def _rrect(surf, color, rect, radius=0, outline=None, w=2):
        rect = pygame.Rect(rect)
        pygame.draw.rect(surf, color, rect, border_radius=radius)
        if outline:
            pygame.draw.rect(surf, outline, rect, w, border_radius=radius)

    def draw_pencil(surf, tx, ty, shadow):
        if shadow:
            _poly(surf, SHADOW, [(tx, ty), (tx-7, ty+16), (tx+7, ty+16)])
            _poly(surf, SHADOW, [(tx-7, ty+16), (tx+7, ty+16), (tx+13, ty+40), (tx-13, ty+40)])
            _rrect(surf, SHADOW, (tx-13, ty+40, 26, 150))
            _rrect(surf, SHADOW, (tx-13, ty+188, 26, 28), radius=6)
            return
        # graphite tip
        _poly(surf, (60, 60, 60), [(tx, ty), (tx-7, ty+16), (tx+7, ty+16)])
        # wood
        _poly(surf, (228, 192, 140), [(tx-7, ty+16), (tx+7, ty+16), (tx+13, ty+40), (tx-13, ty+40)], (150,110,60), 2)
        # body
        _rrect(surf, (247, 206, 55), (tx-13, ty+40, 26, 148), outline=(180,150,40))
        pygame.draw.line(surf, (180, 150, 40), (tx-4, ty+44), (tx-4, ty+184), 2)
        pygame.draw.line(surf, (180, 150, 40), (tx+5, ty+44), (tx+5, ty+184), 2)
        # metal band
        _rrect(surf, (190, 190, 200), (tx-13, ty+188, 26, 12), outline=(140,140,150))
        # eraser
        _rrect(surf, (242, 140, 150), (tx-13, ty+200, 26, 16), radius=6, outline=(200,100,110))

    def draw_pen(surf, tx, ty, shadow):
        if shadow:
            _poly(surf, SHADOW, [(tx, ty), (tx-6, ty+24), (tx+6, ty+24)])
            _rrect(surf, SHADOW, (tx-12, ty+24, 24, 192), radius=8)
            _rrect(surf, SHADOW, (tx+6, ty+150, 7, 50), radius=3)
            return
        # nib
        _poly(surf, (120, 120, 130), [(tx, ty), (tx-6, ty+24), (tx+6, ty+24)], (80,80,90), 2)
        # grip
        _rrect(surf, (25, 25, 40), (tx-9, ty+24, 18, 20), radius=4)
        # body
        _rrect(surf, (30, 95, 210), (tx-12, ty+44, 24, 116), radius=6, outline=(20,60,150))
        # cap
        _rrect(surf, (20, 22, 45), (tx-13, ty+158, 26, 58), radius=8, outline=(0,0,20))
        # clip
        _rrect(surf, (200, 200, 215), (tx+6, ty+162, 7, 46), radius=3, outline=(150,150,165))

    def draw_lighter(surf, tx, ty, shadow, flame=False):
        if shadow:
            _rrect(surf, SHADOW, (tx-15, ty, 30, 12), radius=3)
            _rrect(surf, SHADOW, (tx-12, ty+12, 24, 16))
            _rrect(surf, SHADOW, (tx-17, ty+26, 34, 124), radius=10)
            return
        if flame:
            # live flame above the lighter
            _poly(surf, (255, 170, 40), [(tx, ty-46), (tx-12, ty-6), (tx+12, ty-6)])
            _poly(surf, (255, 90, 20),  [(tx, ty-30), (tx-8, ty-4), (tx+8, ty-4)])
            _poly(surf, (90, 150, 255), [(tx, ty-14), (tx-5, ty-2), (tx+5, ty-2)])
        # metal hood
        _rrect(surf, (185, 185, 195), (tx-15, ty, 30, 12), radius=3, outline=(140,140,150))
        _rrect(surf, (160, 160, 170), (tx-12, ty+12, 24, 16), outline=(120,120,130))
        pygame.draw.circle(surf, (140, 140, 150), (tx+6, ty+14), 5)
        # body
        _rrect(surf, (205, 45, 45), (tx-17, ty+26, 34, 124), radius=10, outline=(150,20,20))
        _rrect(surf, (255, 255, 255), (tx-9, ty+60, 16, 60), radius=4)  # fuel window

    def draw_stick(surf, tx, ty, shadow):
        body = [(tx-4, ty), (tx+4, ty+6), (tx+9, ty+60), (tx+5, ty+120),
                (tx+11, ty+200), (tx-3, ty+200), (tx-9, ty+120),
                (tx-5, ty+60), (tx-10, ty+8)]
        twig = [(tx+7, ty+72), (tx+32, ty+56), (tx+35, ty+63), (tx+9, ty+84)]
        if shadow:
            _poly(surf, SHADOW, body)
            _poly(surf, SHADOW, twig)
            return
        _poly(surf, (120, 82, 45), body, (85, 55, 28), 2)
        _poly(surf, (120, 82, 45), twig, (85, 55, 28), 2)
        for yy in range(20, 190, 26):
            pygame.draw.line(surf, (90, 60, 32), (tx-4, ty+yy), (tx+3, ty+yy+8), 2)

    def draw_knife(surf, tx, ty, shadow):
        blade = [(tx-6, ty+8), (tx, ty), (tx+6, ty+12), (tx+16, ty+118), (tx-6, ty+118)]
        if shadow:
            _poly(surf, SHADOW, blade)
            _rrect(surf, SHADOW, (tx-9, ty+118, 28, 14))
            _rrect(surf, SHADOW, (tx-9, ty+132, 28, 80), radius=10)
            return
        _poly(surf, (208, 210, 218), blade, (160, 162, 172), 2)
        pygame.draw.line(surf, (235, 236, 242), (tx, ty+4), (tx+13, ty+114), 2)  # shine
        _rrect(surf, (150, 150, 160), (tx-9, ty+118, 28, 14), outline=(110,110,120))
        _rrect(surf, (95, 55, 30), (tx-9, ty+132, 28, 80), radius=10, outline=(60,35,18))
        pygame.draw.circle(surf, (60, 60, 60), (tx+5, ty+152), 4)
        pygame.draw.circle(surf, (60, 60, 60), (tx+5, ty+182), 4)

    DRAWERS = {
        "Pencil":  draw_pencil,
        "Pen":     draw_pen,
        "Lighter": draw_lighter,
        "Stick":   draw_stick,
        "Knife":   draw_knife,
    }
    # vertical length of each tool (used to centre it nicely)
    LENGTHS = {"Pencil": 216, "Pen": 216, "Lighter": 150, "Stick": 200, "Knife": 212}

    def draw_tool(surf, name, tx, ty, shadow, flame=False):
        if name == "Lighter":
            draw_lighter(surf, tx, ty, shadow, flame=flame)
        else:
            DRAWERS[name](surf, tx, ty, shadow)

    # slight rotation per item so orientation gives less away
    SHADOW_ANGLE = {"Pencil": -13, "Pen": 9, "Lighter": -7, "Stick": 17, "Knife": -16}

    def draw_shadow(name, box):
        # render the silhouette, then blur it (down/up scale) and fade it so the
        # exact shape is hard to read - just a soft, ambiguous dark blob.
        surf = pygame.Surface((box.w, box.h), pygame.SRCALPHA)
        draw_tool(surf, name, box.w // 2, (box.h - LENGTHS[name]) // 2, shadow=True)
        blur = pygame.transform.smoothscale(surf, (max(1, box.w // 12), max(1, box.h // 12)))
        blur = pygame.transform.smoothscale(blur, (box.w, box.h))
        blur = pygame.transform.rotate(blur, SHADOW_ANGLE[name])
        blur.set_alpha(130)
        screen.blit(blur, blur.get_rect(center=box.center).topleft)

    # ----------------------------------------------------------------------
    # HAND  (yellow emoji skin tone, wrist -> palm -> fingers gripping tool)
    # grip point (gx, gy) sits on the tool; wrist runs down-right.
    # ----------------------------------------------------------------------
    def draw_hand(surf, gx, gy):
        gx, gy = int(gx), int(gy)
        # forearm / wrist coming up from the bottom-right
        pygame.draw.line(surf, SKIN_LINE, (gx+6, gy+8), (gx+90, gy+200), 56)
        pygame.draw.line(surf, SKIN,      (gx+6, gy+8), (gx+90, gy+200), 48)
        # palm
        pygame.draw.ellipse(surf, SKIN_LINE, (gx-26, gy+18, 78, 78))
        pygame.draw.ellipse(surf, SKIN,      (gx-22, gy+22, 70, 70))
        # thumb on the left side of the tool
        pygame.draw.ellipse(surf, SKIN_LINE, (gx-30, gy-12, 22, 50))
        pygame.draw.ellipse(surf, SKIN,      (gx-28, gy-10, 18, 46))
        # four fingers curling over the front of the tool
        for i in range(4):
            fy = gy - 22 + i * 17
            pygame.draw.ellipse(surf, SKIN_LINE, (gx-18, fy, 40, 18))
            pygame.draw.ellipse(surf, SKIN,      (gx-16, fy+1, 36, 15))

    # ----------------------------------------------------------------------
    # CHASE TARGET SPRITE (colourful pen/pencil, pre-rendered + rotated)
    # ----------------------------------------------------------------------
    def make_tool_sprite(name):
        s = pygame.Surface((90, 240), pygame.SRCALPHA)
        draw_tool(s, name, 45, 12, shadow=False)
        s = pygame.transform.rotozoom(s, -35, 0.40)
        return s

    # ----------------------------------------------------------------------
    # GAME STATE
    # ----------------------------------------------------------------------
    items = ["Pencil", "Pen", "Knife", "Lighter", "Stick"]
    CORRECT = {"Pencil", "Pen"}
    SUCCESS_LINES = ["Congratulations,", "You can now go", "do your homework"]

    attempts = 2
    selected_item = None
    outcome_after = "retry"      # where to go after a wrong-answer animation
    scene = "guess"
    scene_start = 0
    sfx_fired = set()           # one-shot sound effects already played this scene

    # selection buttons
    buttons = []
    box_w, box_h = 150, 260
    gap = (WIDTH - 5 * box_w) // 6
    for i in range(5):
        x = gap + i * (box_w + gap)
        buttons.append(pygame.Rect(x, 230, box_w, box_h))

    # paper
    paper = pygame.Rect(400, 130, 500, 410)

    # button shown on the success screen to enter level 4.2
    go_button = pygame.Rect(WIDTH // 2 - 170, 575, 340, 62)

    # tear seam (deterministic jagged line down the paper centre)
    SEAM = [0, 20, -16, 24, -12, 18, -22, 14, -18, 22, -10, 16, 0]

    # 4.2 chase  -  bedroom obstacles the pen can hide behind
    # furniture is spread out with wide gaps between pieces, leaving big open lanes
    # for the pen to roam through
    OBSTACLES = [
        {"type": "bed",        "rect": pygame.Rect(60, 480, 250, 150)},    # bottom-left
        {"type": "nightstand", "rect": pygame.Rect(150, 150, 90, 110)},    # top-left
        {"type": "books",      "rect": pygame.Rect(540, 110, 200, 70)},    # top-centre
        {"type": "shelf",      "rect": pygame.Rect(1050, 140, 180, 110)},  # top-right
        {"type": "table",      "rect": pygame.Rect(420, 470, 200, 120)},   # bottom-centre
        {"type": "shelf",      "rect": pygame.Rect(1000, 480, 210, 150)},  # bottom-right
    ]

    def draw_obstacles():
        for o in OBSTACLES:
            r = o["rect"]
            t = o["type"]
            if t == "bed":
                _rrect(screen, (110, 80, 60), r, radius=10)                       # frame
                _rrect(screen, (90, 130, 200), (r.x+10, r.y+30, r.w-20, r.h-40), radius=8)  # blanket
                _rrect(screen, (245, 245, 250), (r.x+18, r.y+12, 120, 60), radius=8)        # pillow
            elif t == "table":
                pygame.draw.rect(screen, (120, 85, 55), (r.x+12, r.y+30, 16, r.h-30))
                pygame.draw.rect(screen, (120, 85, 55), (r.right-28, r.y+30, 16, r.h-30))
                _rrect(screen, (150, 105, 65), (r.x, r.y, r.w, 34), radius=4, outline=(100, 70, 40))
            elif t == "nightstand":
                _rrect(screen, (140, 100, 60), r, radius=6, outline=(95, 65, 38))
                pygame.draw.line(screen, (95, 65, 38), (r.x+8, r.centery), (r.right-8, r.centery), 3)
                pygame.draw.circle(screen, (60, 45, 30), (r.centerx, r.y + 28), 5)
            elif t == "shelf":
                _rrect(screen, (130, 95, 58), r, radius=4, outline=(90, 62, 36))
                cols = [(200,60,60),(60,120,200),(70,170,90),(220,180,60),(160,90,200)]
                for si, sy in enumerate(range(r.y + 8, r.bottom - 30, 70)):
                    pygame.draw.line(screen, (90, 62, 36), (r.x, sy + 56), (r.right, sy + 56), 5)
                    for bi in range(5):
                        bx = r.x + 8 + bi * ((r.w - 16) / 5)
                        bh = 40 + (bi % 3) * 6
                        pygame.draw.rect(screen, cols[(si + bi) % 5], (bx, sy + 56 - bh, (r.w - 24) / 5, bh))
            elif t == "books":
                cols = [(200,60,60),(60,120,200),(70,170,90),(220,180,60),(160,90,200),(230,130,40)]
                for bi in range(6):
                    bx = r.x + bi * (r.w / 6)
                    bh = r.h - (bi % 3) * 10
                    pygame.draw.rect(screen, cols[bi % 6], (bx, r.bottom - bh, r.w / 6 - 4, bh))
                    pygame.draw.rect(screen, (40, 40, 40), (bx, r.bottom - bh, r.w / 6 - 4, bh), 2)

    player_radius = 24
    player_x, player_y = WIDTH // 2, HEIGHT // 2
    player_speed = 470
    target_sprite = None
    target_x, target_y = 0, 0
    target_vx, target_vy = 0.0, 0.0     # the pen's current heading (roams the map)
    target_speed = player_speed / 1.1   # the pen is nearly as fast as the player (hard!)
    wp_x, wp_y, wp_time = 0, 0, 0       # roaming waypoint the pen heads toward
    last_teleport = 0                   # pen also teleports every 5 seconds
    CHASE_TIME = 30.0                   # seconds to catch the pen before you lose it

    def stop_sounds():
        if SOUND_ON:
            pygame.mixer.stop()

    def set_scene(name):
        nonlocal scene, scene_start, sfx_fired
        if scene == "writing" and name != "writing":
            stop_sounds()            # cut looping write / fire sounds
        scene = name
        scene_start = pygame.time.get_ticks()
        if name == "writing":
            sfx_fired = set()
        # chase music plays only during the 4.2 pen chase
        if name == "chase":
            play_music("chase")
        else:
            stop_music()

    def reset_level():
        nonlocal attempts, selected_item, scene
        attempts = 2
        selected_item = None
        set_scene("guess")

    def start_chase():
        nonlocal target_sprite, target_x, target_y, player_x, player_y, last_teleport
        target_sprite = make_tool_sprite(selected_item)
        player_x, player_y = WIDTH // 2, HEIGHT - 80
        spawn_target()
        last_teleport = pygame.time.get_ticks()
        set_scene("chase")

    def spawn_target():
        # initial placement: the valid (obstacle-free) spot farthest from the player
        nonlocal target_x, target_y, target_vx, target_vy, wp_x, wp_y, wp_time
        ang = random.uniform(0, 2 * math.pi)
        target_vx, target_vy = math.cos(ang) * target_speed, math.sin(ang) * target_speed
        wp_x, wp_y = random.randint(70, WIDTH - 70), random.randint(90, HEIGHT - 60)
        wp_time = pygame.time.get_ticks()
        sw, sh = target_sprite.get_size()
        candidates = []
        for _ in range(200):
            tx = random.randint(40, WIDTH - 40 - sw)
            ty = random.randint(80, HEIGHT - 40 - sh)
            r = pygame.Rect(tx, ty, sw, sh)
            if not any(r.colliderect(o["rect"].inflate(14, 14)) for o in OBSTACLES):
                candidates.append((tx, ty))
                if len(candidates) >= 25:
                    break
        if candidates:
            target_x, target_y = max(candidates, key=lambda c: math.hypot(
                (c[0] + sw / 2) - player_x, (c[1] + sh / 2) - player_y))
        else:
            target_x, target_y = WIDTH - 40 - sw, HEIGHT - 40 - sh

    def teleport_pen():
        # the pen blinks AWAY from the player: an obstacle-free spot, as far as possible
        nonlocal target_x, target_y, target_vx, target_vy, wp_x, wp_y, wp_time, last_teleport
        sw, sh = target_sprite.get_size()
        candidates = []
        for _ in range(200):
            tx = random.randint(40, WIDTH - 40 - sw)
            ty = random.randint(80, HEIGHT - 40 - sh)
            if not any(pygame.Rect(tx, ty, sw, sh).colliderect(o["rect"].inflate(14, 14))
                       for o in OBSTACLES):
                candidates.append((tx, ty))
                if len(candidates) >= 25:
                    break
        if candidates:
            target_x, target_y = max(candidates, key=lambda c: math.hypot(
                (c[0] + sw / 2) - player_x, (c[1] + sh / 2) - player_y))
        ang = random.uniform(0, 2 * math.pi)
        target_vx, target_vy = math.cos(ang) * target_speed, math.sin(ang) * target_speed
        wp_x, wp_y = random.randint(70, WIDTH - 70), random.randint(90, HEIGHT - 60)
        wp_time = last_teleport = pygame.time.get_ticks()

    # ----------------------------------------------------------------------
    # DRAWING THE 4.1 WRITING SCENE
    # ----------------------------------------------------------------------
    def draw_paper(rect=None):
        r = rect or paper
        _rrect(screen, (180, 180, 185), (r.x+6, r.y+8, r.w, r.h), radius=6)  # shadow
        _rrect(screen, PAPER, r, radius=6, outline=(170, 170, 175))
        for ly in range(r.y + 60, r.bottom - 20, 40):
            pygame.draw.line(screen, PAPER_LINE, (r.x + 25, ly), (r.right - 25, ly), 2)

    def render_writing():
        elapsed = pygame.time.get_ticks() - scene_start
        entry = max(0, 200 * (1 - min(1.0, elapsed / 400.0)))   # slide-up on entry
        name = selected_item

        if name in CORRECT:
            draw_paper()
            prog = max(0.0, min(1.0, (elapsed - 400) / 2600.0))
            lines = SUCCESS_LINES
            total = sum(len(l) for l in lines)
            shown_n = int(prog * total)
            base_x, base_y, line_h = paper.x + 30, paper.y + 70, 56

            # draw each line up to the current number of revealed characters
            rem = shown_n
            for li, line in enumerate(lines):
                take = max(0, min(len(line), rem))
                if take > 0:
                    surf = WRITE_FONT_SM.render(line[:take], True, (20, 60, 200))
                    screen.blit(surf, (base_x, base_y + li * line_h))
                rem -= take

            # locate the pen tip at the end of the currently active line
            rem = shown_n
            active = len(lines) - 1
            chars = len(lines[-1])
            for li, line in enumerate(lines):
                if rem <= len(line):
                    active, chars = li, rem
                    break
                rem -= len(line)
            tip_x = base_x + WRITE_FONT_SM.render(lines[active][:chars], True, (0, 0, 0)).get_width() + 4
            tip_y = base_y + active * line_h + 6 + entry
            draw_tool(screen, name, tip_x, tip_y, shadow=False)
            draw_hand(screen, tip_x, tip_y + 120)
            return

        # ---- wrong items: tool sits at the centre of the paper ----
        cx = paper.centerx
        tip_y = paper.y + 70 + entry

        if name == "Lighter":
            fp = max(0.0, min(1.0, (elapsed - 600) / 1800.0))
            draw_paper()
            # char rising from the bottom of the paper
            ch = int(fp * paper.h)
            if ch > 0:
                _rrect(screen, (25, 20, 18), (paper.x, paper.bottom - ch, paper.w, ch), radius=6)
                glow_y = paper.bottom - ch
                for gx in range(paper.x, paper.right, 18):
                    pygame.draw.line(screen, (255, 120, 30),
                                     (gx, glow_y + random.randint(-3, 3)),
                                     (gx + 9, glow_y + random.randint(-3, 3)), 3)
            draw_tool(screen, name, cx, tip_y, shadow=False, flame=True)
            draw_hand(screen, cx, tip_y + 90)
            # flames
            t = pygame.time.get_ticks()
            for i in range(11):
                fx = paper.x + 30 + i * (paper.w - 60) / 10
                fl = math.sin(t / 90.0 + i)
                h = (40 + 150 * fp) * (0.7 + 0.3 * fl)
                by = paper.bottom - ch + 10
                _poly(screen, (200, 40, 0),  [(fx, by), (fx-16, by), (fx-8, by-h)])
                _poly(screen, (255, 140, 0), [(fx, by), (fx-12, by), (fx-6, by-h*0.7)])
                _poly(screen, (255, 230, 120), [(fx-3, by), (fx-9, by), (fx-6, by-h*0.4)])
            return

        if name == "Knife":
            tp = max(0.0, min(1.0, (elapsed - 600) / 1300.0))
            dx = int(tp * 120)
            step = paper.h / (len(SEAM) - 1)
            seam = [(paper.centerx + SEAM[i], paper.y + i * step) for i in range(len(SEAM))]
            left = [(paper.x, paper.y)] + seam + [(paper.x, paper.bottom)]
            right = [(paper.right, paper.y)] + seam + [(paper.right, paper.bottom)]
            _poly(screen, PAPER, [(x - dx, y) for x, y in left], (170, 170, 175), 2)
            _poly(screen, PAPER, [(x + dx, y) for x, y in right], (170, 170, 175), 2)
            draw_tool(screen, name, cx, tip_y, shadow=False)
            draw_hand(screen, cx, tip_y + 100)
            return

        # Stick -> nothing happens
        draw_paper()
        if elapsed > 700:
            nope = SMALL_FONT.render("...nothing happens.", True, (120, 120, 120))
            screen.blit(nope, (paper.centerx - nope.get_width() // 2, paper.y + 80))
        draw_tool(screen, name, cx, tip_y, shadow=False)
        draw_hand(screen, cx, tip_y + 90)

    WRONG_END = {"Lighter": 3200, "Knife": 2600, "Stick": 2200}
    EFFECT_TEXT = {"Lighter": "The lighter set the paper on fire!",
                   "Knife":   "The knife tore the paper apart!",
                   "Stick":   "The stick can't write anything!"}

    # ----------------------------------------------------------------------
    # MAIN LOOP
    # ----------------------------------------------------------------------
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        now = pygame.time.get_ticks()
        mouse = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if scene == "level_complete":
                    return
                if scene == "guess":
                    for i, rect in enumerate(buttons):
                        if rect.collidepoint(event.pos):
                            selected_item = items[i]
                            if selected_item not in CORRECT:
                                attempts -= 1
                                outcome_after = "retry" if attempts > 0 else "died"
                            set_scene("reveal")
                            break
                elif scene == "retry":
                    set_scene("guess")
                elif scene == "success":
                    if go_button.collidepoint(event.pos):
                        set_scene("intro")
                elif scene == "intro":
                    start_chase()
                elif scene == "gameover":
                    reset_level()
                elif scene == "timeup":
                    start_chase()

        # ---- timed scene transitions ----
        if scene == "reveal" and now - scene_start >= 900:
            set_scene("writing")
        elif scene == "writing":
            el = now - scene_start
            if SOUND_ON:
                it = selected_item
                if it in CORRECT and "w" not in sfx_fired and el >= 400:
                    sfx_fired.add("w")
                    SND["pen" if it == "Pen" else "pencil"].play(loops=-1)   # until done
                elif it == "Lighter" and "f" not in sfx_fired and el >= 600:
                    sfx_fired.add("f"); SND["fire"].play(loops=-1)    # crackle while burning
                elif it == "Knife" and "t" not in sfx_fired and el >= 600:
                    sfx_fired.add("t"); SND["tear"].play()            # one rip
                elif it == "Stick" and "s" not in sfx_fired and el >= 700:
                    sfx_fired.add("s"); SND["tap"].play()             # dull tap
            if selected_item in CORRECT:
                if el >= 3700:
                    set_scene("success")
            elif el >= WRONG_END[selected_item]:
                set_scene(outcome_after)
        elif scene == "died" and now - scene_start >= 1600:
            set_scene("gameover")

        # ==================================================================
        # RENDER
        # ==================================================================
        screen.fill(BG)

        if scene == "guess":
            title = BIG_FONT.render("Which one can WRITE?", True, (30, 30, 40))
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 70))
            sub = SMALL_FONT.render("Guess the writing tool from its shadow", True, (90, 90, 100))
            screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 140))
            tries = FONT.render(f"Attempts left: {attempts}", True, (160, 40, 40))
            screen.blit(tries, (20, 20))
            for i, rect in enumerate(buttons):
                hovered = rect.collidepoint(mouse)
                _rrect(screen, (235, 235, 240), rect, radius=12,
                       outline=(255, 170, 60) if hovered else (160, 160, 170), w=4)
                draw_shadow(items[i], rect)

        elif scene == "reveal":
            info = FONT.render(f"It's a {selected_item}!", True, (30, 30, 40))
            screen.blit(info, (WIDTH // 2 - info.get_width() // 2, 120))
            tip_y = HEIGHT // 2 - LENGTHS[selected_item] // 2
            draw_tool(screen, selected_item, WIDTH // 2, tip_y, shadow=False)

        elif scene == "writing":
            render_writing()

        elif scene == "success":
            draw_paper()
            for li, line in enumerate(SUCCESS_LINES):
                surf = WRITE_FONT_SM.render(line, True, (20, 60, 200))
                screen.blit(surf, (paper.x + 30, paper.y + 70 + li * 56))
            hovered = go_button.collidepoint(mouse)
            _rrect(screen, (40, 170, 70) if hovered else (30, 140, 55), go_button,
                   radius=14, outline=(255, 255, 255), w=3)
            bt = FONT.render("Go to Level 4.2  >", True, (255, 255, 255))
            screen.blit(bt, (go_button.centerx - bt.get_width() // 2,
                             go_button.centery - bt.get_height() // 2))

        elif scene == "intro":
            screen.fill((18, 20, 30))
            story = [
                "While doing your homework, your pen suddenly",
                "jumps out of your hand and starts to run",
                "around the room!",
                "",
                "You have 30 seconds to catch it,",
                "or else you will lose it.",
            ]
            for li, line in enumerate(story):
                col = (255, 220, 90) if li >= 4 else (235, 235, 245)
                surf = FONT.render(line, True, col)
                screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, 180 + li * 56))
            prompt = SMALL_FONT.render("Click anywhere to start the chase", True, (150, 150, 165))
            screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, 560))

        elif scene == "retry":
            eff = BIG_FONT.render(EFFECT_TEXT[selected_item], True, (200, 50, 30))
            screen.blit(eff, (WIDTH // 2 - eff.get_width() // 2, 250))
            again = FONT.render(f"Wrong tool! 1 attempt left - click to try again.",
                                True, (30, 30, 40))
            screen.blit(again, (WIDTH // 2 - again.get_width() // 2, 360))

        elif scene == "died":
            screen.fill((20, 0, 0))
            dead = BIG_FONT.render("YOU HAVE DIED", True, (220, 30, 30))
            screen.blit(dead, (WIDTH // 2 - dead.get_width() // 2, HEIGHT // 2 - 40))

        elif scene == "gameover":
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            box = pygame.Rect(WIDTH // 2 - 260, HEIGHT // 2 - 120, 520, 240)
            _rrect(screen, (245, 245, 245), box, radius=16, outline=(200, 50, 50), w=5)
            go = BIG_FONT.render("GAME OVER", True, (200, 40, 40))
            screen.blit(go, (WIDTH // 2 - go.get_width() // 2, box.y + 50))
            r = FONT.render("Click to restart this level", True, (40, 40, 40))
            screen.blit(r, (WIDTH // 2 - r.get_width() // 2, box.y + 140))

        # ---------------- LEVEL 4.2 : CHASE ----------------
        elif scene == "chase":
            keys = pygame.key.get_pressed()
            dx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
            dy = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
            # normalise so moving diagonally isn't a free speed boost
            dlen = math.hypot(dx, dy) or 1.0
            mvx, mvy = dx / dlen * player_speed * dt, dy / dlen * player_speed * dt

            def hits_obstacle():
                pr = pygame.Rect(player_x - player_radius, player_y - player_radius,
                                 player_radius * 2, player_radius * 2)
                return any(pr.colliderect(o["rect"]) for o in OBSTACLES)

            # move each axis separately so we slide along furniture
            player_x = max(player_radius, min(WIDTH - player_radius, player_x + mvx))
            if hits_obstacle():
                player_x -= mvx
            player_y = max(player_radius, min(HEIGHT - player_radius, player_y + mvy))
            if hits_obstacle():
                player_y -= mvy

            # the pen ROAMS the map: it wanders, bounces off walls/furniture, and
            # steers away from the player when close (player is 1.5x faster, so catchable)
            sw, sh = target_sprite.get_size()

            def target_hits(nx, ny):
                r = pygame.Rect(nx, ny, sw, sh)
                return any(r.colliderect(o["rect"]) for o in OBSTACLES)

            # every 5 seconds the pen teleports away from the player
            if now - last_teleport >= 5000:
                teleport_pen()

            cx, cy = target_x + sw / 2, target_y + sh / 2

            # pick a new roaming waypoint once reached (or after a while) -> covers the whole map
            if math.hypot(cx - wp_x, cy - wp_y) < 90 or now - wp_time > 2500:
                wp_x, wp_y = random.randint(70, WIDTH - 70), random.randint(90, HEIGHT - 60)
                wp_time = now

            d = math.hypot(cx - player_x, cy - player_y) or 1.0
            if d < 380:                          # senses player early -> flee, but avoid corners
                ax, ay = (cx - player_x) / d, (cy - player_y) / d   # away from player
                rx = ry = 0.0                                       # push away from nearby walls
                MG = 200
                if cx < MG:          rx += (MG - cx) / MG
                if cx > WIDTH - MG:  rx -= (cx - (WIDTH - MG)) / MG
                if cy < MG:          ry += (MG - cy) / MG
                if cy > HEIGHT - MG: ry -= (cy - (HEIGHT - MG)) / MG
                des, turn = math.atan2(ay + ry * 1.8, ax + rx * 1.8), 9.0
            else:                                                # otherwise patrol toward waypoint
                des, turn = math.atan2(wp_y - cy, wp_x - cx), 3.5
            heading = math.atan2(target_vy, target_vx)
            diff = (des - heading + math.pi) % (2 * math.pi) - math.pi
            heading += diff * turn * dt + random.uniform(-1, 1) * 1.0 * dt
            target_vx = math.cos(heading) * target_speed
            target_vy = math.sin(heading) * target_speed

            # bounce off walls and furniture; teleporting happens ONLY on the 5s timer
            nx = target_x + target_vx * dt
            if nx < 20 or nx > WIDTH - 20 - sw or target_hits(nx, target_y):
                target_vx = -target_vx
                alt = target_x + target_vx * dt
                nx = alt if (20 <= alt <= WIDTH - 20 - sw and not target_hits(alt, target_y)) else target_x
            target_x = nx
            ny = target_y + target_vy * dt
            if ny < 70 or ny > HEIGHT - 20 - sh or target_hits(target_x, ny):
                target_vy = -target_vy
                alt = target_y + target_vy * dt
                ny = alt if (70 <= alt <= HEIGHT - 20 - sh and not target_hits(target_x, alt)) else target_y
            target_y = ny

            screen.fill((120, 130, 140))
            draw_obstacles()
            txt = FONT.render(f"Catch the {selected_item}!  (WASD / Arrow keys)", True, (255, 255, 255))
            screen.blit(txt, (20, 20))

            # 30 second countdown - run out of time and you restart the chase
            remaining = max(0.0, CHASE_TIME - (now - scene_start) / 1000.0)
            tcol = (255, 90, 90) if remaining <= 10 else (255, 255, 255)
            timer = FONT.render(f"Time: {remaining:4.1f}s", True, tcol)
            screen.blit(timer, (WIDTH - timer.get_width() - 20, 20))
            if remaining <= 0:
                set_scene("timeup")

            sw, sh = target_sprite.get_size()
            screen.blit(target_sprite, (target_x, target_y))

            # player — the character chosen on the start screen
            draw_player_character(screen, player_x, player_y, player_radius * 2, (40, 90, 245))

            # tight hitbox: must actually touch the pen near its centre (the rotated
            # sprite's bounding box is mostly empty), so it's much harder to catch
            if math.hypot(player_x - (target_x + sw / 2), player_y - (target_y + sh / 2)) < player_radius + 16:
                set_scene("level_complete")

        elif scene == "level_complete":
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(190)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            t = BIG_FONT.render("LEVEL 4 COMPLETED!", True, (255, 230, 90))
            screen.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - 50))
            s = FONT.render(f"You caught the {selected_item}!", True, (255, 255, 255))
            screen.blit(s, (WIDTH // 2 - s.get_width() // 2, HEIGHT // 2 + 30))
            _l4pb = pygame.Rect(WIDTH // 2 - 130, HEIGHT // 2 + 100, 260, 56)
            _hov = _l4pb.collidepoint(mouse)
            pygame.draw.rect(screen, (40, 160, 75) if _hov else (26, 110, 55), _l4pb, border_radius=12)
            pygame.draw.rect(screen, (120, 255, 150), _l4pb, 3, border_radius=12)
            _bt = FONT.render("PROCEED", True, (255, 255, 255))
            screen.blit(_bt, (_l4pb.centerx - _bt.get_width() // 2, _l4pb.centery - _bt.get_height() // 2))

        elif scene == "timeup":
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            box = pygame.Rect(WIDTH // 2 - 280, HEIGHT // 2 - 120, 560, 240)
            _rrect(screen, (245, 245, 245), box, radius=16, outline=(220, 140, 30), w=5)
            t = BIG_FONT.render("TIME'S UP!", True, (220, 140, 30))
            screen.blit(t, (WIDTH // 2 - t.get_width() // 2, box.y + 45))
            r = FONT.render("You didn't catch the pen - click to restart", True, (40, 40, 40))
            screen.blit(r, (WIDTH // 2 - r.get_width() // 2, box.y + 145))

        pygame.display.flip()

#level 5


if __name__ == "__main__":
    main()
