import numpy as np, math, sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
from multiprocessing import Pool
from tl2 import *

W, H = 1080, 1920
A = '/home/user/royaleapi/cr-api-assets/'
OUT = 'frames'
FONT = '/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf'
INK = (22, 12, 40)
BEATS = beats()
NF = int(DUR * FPS)

# ------------------------------------------------------------------ assets (official renders)
def load(rel, trim=True):
    im = Image.open(A + rel).convert('RGBA')
    if not trim: return im, (0, 0, im.width, im.height)
    bb = im.getchannel('A').point(lambda v: 255 if v > 10 else 0).getbbox()
    return im.crop(bb), bb
HERO = {}
def reg(key, rel, anchors=None):
    im, bb = load(rel); HERO[key] = dict(im=im, bb=bb, anc=anchors or {})
reg('spark', 'chr/sparky_dl.png', {'tip': (610, 215)})
reg('musk', 'chr/three_musketeers_dl.png', {'m1': (190, 590), 'm2': (440, 770), 'm3': (1065, 765)})
reg('golem', 'chr/golem_dl.png', {'eyeL': (487, 345), 'eyeR': (592, 345), 'chest': (560, 520)})
reg('skarmy', 'chr/skeleton_army_dl.png'); reg('skel', 'chr/skeletons_dl.png')
CARD = {k: Image.open(A + f'cards/{f}.png').convert('RGBA') for k, f in
        [('spark', 'sparky'), ('golem', 'golem'), ('musk', 'three-musketeers'), ('skel', 'skeletons'), ('army', 'skeleton-army')]}
BADGE, _ = load('arenas/league10.png')
TEX = np.asarray(Image.open(A + 'ui/ui-tex-2.png').convert('RGB').resize((196, 196), Image.LANCZOS))

# ------------------------------------------------------------------ helpers
_f = {}
def font(sz):
    sz = int(sz)
    if sz not in _f: _f[sz] = ImageFont.truetype(FONT, sz)
    return _f[sz]
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def sstep(x): x = clamp(x); return x * x * (3 - 2 * x)
def lerp(a, b, u): return a + (b - a) * u
def pulse_at(t):
    p = 0.0
    for b in BEATS:
        for off, amp in ((0, 1.0), (0.2, 0.6)):
            dt = t - (b + off)
            if 0 <= dt < 0.5: p = max(p, amp * math.exp(-dt / 0.09))
    return p
def impact(t, times, decay=0.28, amps=None):
    a = 0.0
    for i, ts in enumerate(times):
        dt = t - ts
        if 0 <= dt < 1.6: a += (amps[i] if amps else 1.0) * math.exp(-dt / decay)
    return a
def shake_off(amp, fi):
    r = np.random.default_rng(fi * 7 + 1); return tuple(r.normal(0, amp, 2)) if amp > .3 else (0.0, 0.0)

def sprite(im, w, h=None):
    h = h if h else int(im.height * w / im.width)
    return im.resize((max(1, int(w)), max(1, int(h))), Image.LANCZOS)
def paste(img, sp, x0, y0, alpha=1.0):
    if alpha < 1: sp = sp.copy(); sp.putalpha(sp.getchannel('A').point(lambda v: int(v * alpha)))
    img.paste(sp, (int(x0), int(y0)), sp)
def glow_from(G, sp, x0, y0, col, blur=34, k=1.0):
    m = Image.new('L', (W // 2, H // 2), 0)
    a = sp.getchannel('A').resize((max(1, sp.width // 2), max(1, sp.height // 2)))
    m.paste(a, (int(x0 // 2), int(y0 // 2))); m = m.filter(ImageFilter.GaussianBlur(blur // 2))
    col = tuple(int(c * k) for c in col)
    G.paste(ImageChops.add(G, Image.composite(Image.new('RGB', G.size, col), Image.new('RGB', G.size, (0, 0, 0)), m)))
def radial(G, x, y, r, col): ImageDraw.Draw(G).ellipse([(x - r) / 2, (y - r) / 2, (x + r) / 2, (y + r) / 2], fill=col)
def shadow(img, cx, cy, rx, ry, a=150):
    l = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(l).ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(0, 0, 0, a))
    l = l.filter(ImageFilter.GaussianBlur(22)); img.paste(l, (0, 0), l)

class Hero:
    """official render placed with bottom-centre anchor; exposes screen coords of image-space anchors"""
    def __init__(s, key, img, G, cx, by, w, bob=0.0, squash=0.0, alpha=1.0, glow=None, gk=1.0, shadow_on=True):
        d = HERO[key]; im = d['im']; sc = w / im.width
        hh = im.height * sc * (1 + squash); ww = w * (1 - squash * .5)
        sp = sprite(im, ww, hh); x0 = cx - sp.width / 2; y0 = by - sp.height - bob
        if shadow_on: shadow(img, cx, by + 8, ww * .42, ww * .06)
        if glow: glow_from(G, sp, x0, y0, glow, 40, gk)
        paste(img, sp, x0, y0, alpha)
        s.x0, s.y0, s.sx, s.sy, s.bb = x0, y0, ww / im.width, hh / im.height, d['bb']; s.anc = d['anc']
    def at(s, name):
        ax, ay = s.anc[name]; return (s.x0 + (ax - s.bb[0]) * s.sx, s.y0 + (ay - s.bb[1]) * s.sy)

# ------------------------------------------------------------------ text
def text(img, txt, cx, cy, size, fill=(255, 255, 255), stroke=INK, sw=None, alpha=1.0, scale=1.0, rot=0, shadow_on=True):
    if alpha <= 0.01: return
    sw = sw if sw is not None else max(4, int(size * 0.09)); f = font(size)
    tmp = Image.new('RGBA', (int(W * 1.5), int(size * 5)), (0, 0, 0, 0)); d = ImageDraw.Draw(tmp); c = (tmp.width // 2, tmp.height // 2)
    if shadow_on: d.multiline_text((c[0] + size * .04, c[1] + size * .07), txt, font=f, anchor='mm', align='center', fill=(0, 0, 0, 190), stroke_width=sw, stroke_fill=(0, 0, 0, 190))
    d.multiline_text(c, txt, font=f, anchor='mm', align='center', fill=fill, stroke_width=sw, stroke_fill=stroke, spacing=int(size * .05))
    bb = tmp.getbbox()
    if not bb: return
    tmp = tmp.crop(bb)
    if scale != 1: tmp = tmp.resize((max(1, int(tmp.width * scale)), max(1, int(tmp.height * scale))), Image.BICUBIC)
    if rot: tmp = tmp.rotate(rot, expand=True, resample=Image.BICUBIC)
    if alpha < 1: tmp.putalpha(tmp.getchannel('A').point(lambda v: int(v * alpha)))
    img.paste(tmp, (int(cx - tmp.width / 2), int(cy - tmp.height / 2)), tmp)
def caption(img, t, t0, t1, txt, cy, size, fill=(255, 255, 255), rot=-2):
    if not (t0 <= t <= t1): return
    p = clamp((t - t0) / .2); o = clamp((t1 - t) / .2)
    text(img, txt, W / 2, cy, size, fill, alpha=min(p, o), scale=1 + .35 * (1 - p) ** 2, rot=rot)
def slam(img, t, t0, t1, txt, cy, size, fill, rot=-3, seed=0):
    if not (t0 <= t <= t1): return
    u = t - t0; sc = 1 + 2.0 * max(0, 1 - u / .11) ** 2 + .05 * math.exp(-u * 6) * math.sin(u * 30)
    r = np.random.default_rng(int(u * 60) + seed); sh = r.normal(0, 9 * max(0, 1 - u / .4), 2)
    text(img, txt, W / 2 + sh[0], cy + sh[1], size, fill, alpha=min(1, (u + .02) / .05) * clamp((t1 - t) / .2), scale=sc, rot=rot)

# ------------------------------------------------------------------ backdrop
def floor_rows(t, speed, hh=420):
    ys = np.arange(1, hh + 1, dtype=np.float32); z = 52.0 / ys
    xs = np.arange(540, dtype=np.float32) - 270
    U = xs[None, :] * z[:, None] * .55 + 40; V = z[:, None] * 330 - t * speed
    f = TEX[(V.astype(np.int32)) % 196, (U.astype(np.int32)) % 196].astype(np.float32)
    fade = np.clip(ys / hh * 1.7, 0, 1)[:, None, None] ** 1.3
    return f * fade
def backdrop(t, top, mid, hz=1090, floor_speed=26.0, floor_k=.42):
    col = np.zeros((H, 3), np.float32)
    y = np.arange(H, dtype=np.float32)
    for c in range(3):
        col[:, c] = np.interp(y, [0, hz * .55, hz, H], [top[c], mid[c] * .6, mid[c], top[c] * .25])
    a = np.repeat(col[:, None, :], W, axis=1)
    fl = floor_rows(t, floor_speed)
    flb = np.asarray(Image.fromarray(fl.astype(np.uint8)).resize((W, fl.shape[0] * 2), Image.BILINEAR)).astype(np.float32)
    n = flb.shape[0]; y1 = min(H, hz + n)
    a[hz:y1] = a[hz:y1] * (1 - floor_k) + flb[:y1 - hz] * floor_k * (np.array(mid, np.float32) / 120 + .35)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
def rays(G, t, x, y, col, n=7, spread=1.2, length=1900, k=1.0):
    d = ImageDraw.Draw(G)
    for i in range(n):
        ang = math.pi / 2 + (i - (n - 1) / 2) * spread / n + math.sin(t * .6 + i * 1.7) * .05
        w = .07 + .03 * math.sin(t * .9 + i)
        pts = [(x / 2, y / 2), ((x + math.cos(ang - w) * length) / 2, (y + math.sin(ang - w) * length) / 2), ((x + math.cos(ang + w) * length) / 2, (y + math.sin(ang + w) * length) / 2)]
        d.polygon(pts, fill=tuple(int(c * k * (.6 + .4 * math.sin(t * 1.3 + i * 2.1))) for c in col))
_r = np.random.default_rng(11)
def _fogtex():
    a = _r.random((60, 120)).astype(np.float32); im = Image.fromarray((a * 255).astype(np.uint8)).resize((480, 240), Image.BICUBIC).filter(ImageFilter.GaussianBlur(14))
    b = np.asarray(im).astype(np.float32); return (b - b.min()) / (b.max() - b.min())
FOG = _fogtex()
def fog(img, t, strength, col=(120, 140, 180), speed=24):
    ox = int((t * speed) % 240); win = np.concatenate([FOG, FOG], 1)[:, ox:ox + 240]
    m = Image.fromarray((np.clip(win, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
    m = (np.asarray(m).astype(np.float32) / 255) ** 1.5 * strength
    a = np.asarray(img).astype(np.float32); c = np.array(col, np.float32)
    return Image.fromarray(np.clip(a * (1 - m[..., None]) + c * m[..., None], 0, 255).astype(np.uint8))
def embers(G, t, n=60, col=(255, 150, 50), seed=1, speed=60, size=(2.5, 6)):
    r = np.random.default_rng(seed); d = ImageDraw.Draw(G)
    for i in range(n):
        x0, y0, ph, sp, rr = r.random() * W, r.random() * H, r.random() * 6, r.uniform(.5, 1.6), r.uniform(*size)
        y = (y0 - sp * speed * t) % (H + 40); x = x0 + math.sin(t * sp + ph) * 40; tw = .5 + .5 * math.sin(t * 7 * sp + ph)
        d.ellipse([(x - rr) / 2, (y - rr) / 2, (x + rr) / 2, (y + rr) / 2], fill=tuple(int(v * tw) for v in col))
def bokeh(G, t, col, n=14, seed=5):
    r = np.random.default_rng(seed); d = ImageDraw.Draw(G)
    for i in range(n):
        x0, y0, sp, rr = r.random() * W, r.random() * H, r.uniform(8, 30), r.uniform(30, 90)
        y = (y0 - sp * t) % (H + 200) - 100; x = x0 + math.sin(t * .4 + i) * 60
        d.ellipse([(x - rr) / 2, (y - rr) / 2, (x + rr) / 2, (y + rr) / 2], fill=tuple(int(c * .22) for c in col))

# ------------------------------------------------------------------ fx
def bolt(p0, p1, rng, jag=60, depth=6):
    pts = [p0, p1]
    for lvl in range(depth):
        new = [pts[0]]
        for a, b in zip(pts[:-1], pts[1:]):
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2; L = math.hypot(b[0] - a[0], b[1] - a[1]) + 1e-6
            nx, ny = -(b[1] - a[1]) / L, (b[0] - a[0]) / L; off = rng.normal(0, jag / (1.6 ** lvl)); new += [(mx + nx * off, my + ny * off), b]
        pts = new
    return pts
def draw_bolt(img, G1, G2, p0, p1, rng, w=8, col=(120, 200, 255), jag=70, branches=3):
    d, g1, g2 = ImageDraw.Draw(img), ImageDraw.Draw(G1), ImageDraw.Draw(G2)
    lines = [(bolt(p0, p1, rng, jag), w)]
    for _ in range(branches):
        pts = lines[0][0]; i = int(rng.integers(len(pts) // 5, len(pts) * 4 // 5)); a = pts[i]; ang = rng.uniform(0, 6.28); L = rng.uniform(120, 380)
        lines.append((bolt(a, (a[0] + math.cos(ang) * L, a[1] + math.sin(ang) * L), rng, jag * .6, 5), w * .5))
    for pts, ww in lines:
        s1 = [(x / 2, y / 2) for x, y in pts]
        g1.line(s1, fill=col, width=int(ww * 2.4), joint='curve'); g2.line(s1, fill=col, width=int(ww * .9), joint='curve')
        d.line(pts, fill=col, width=int(ww * 1.3), joint='curve'); d.line(pts, fill=(255, 255, 255), width=max(2, int(ww * .55)), joint='curve')
def ring(G, x, y, r, w, col):
    if r > 1: ImageDraw.Draw(G).ellipse([(x - r) / 2, (y - r * .32) / 2, (x + r) / 2, (y + r * .32) / 2], outline=col, width=max(1, int(w / 2)))
def dust(img, t, x, y, t0, seed=1, n=14, col=(150, 130, 120), spread=700):
    u = t - t0
    if not (0 <= u < 1.2): return
    r = np.random.default_rng(seed); l = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(l)
    for j in range(n):
        a = r.uniform(0, 6.28); L = u * r.uniform(.3, 1) * spread; rad = 30 + u * 90
        cx, cy = x + math.cos(a) * L, y + math.sin(a) * L * .32 - u * 50
        d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=col + (int(150 * (1 - u / 1.2)),))
    l = l.filter(ImageFilter.GaussianBlur(14)); img.paste(l, (0, 0), l)
def muzzle(img, G1, G2, x, y, u, rng, big=1.0):
    if not (0 <= u < .14): return
    f = 1 - u / .14; d = ImageDraw.Draw(img); pts = []
    for a in range(12):
        ang = a * .5236 + rng.random() * .3; L = (170 if a % 2 == 0 else 60) * f * big; pts.append((x + math.cos(ang) * L, y + math.sin(ang) * L))
    d.polygon(pts, fill=(255, 235, 150)); d.ellipse([x - 40 * f * big, y - 40 * f * big, x + 40 * f * big, y + 40 * f * big], fill=(255, 255, 240))
    radial(G1, x, y, 260 * f * big, (110, 80, 36)); radial(G2, x, y, 200 * f * big, (255, 220, 120))
def zoom_blur(img, amt, cx=W / 2, cy=H / 2, n=6):
    if amt <= .004: return img
    acc = np.asarray(img).astype(np.float32)
    for k in range(1, n):
        s = 1 + amt * k / n; im = img.resize((W, H), Image.BILINEAR, box=(cx - cx / s, cy - cy / s, cx - cx / s + W / s, cy - cy / s + H / s)); acc += np.asarray(im)
    return Image.fromarray((acc / n).astype(np.uint8))

# ------------------------------------------------------------------ post
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
R2 = (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)[..., None] / 2
def post(img, G1, G2, tint=(1, 1, 1), sat=1.0, con=1.1, bright=1.0, vig=.7, flash=0.0, flashcol=(1, 1, 1), ca=0, glitch=0.0, seed=0, redpulse=0.0, fade=1.0, shake=(0, 0)):
    a = np.asarray(img).astype(np.float32) / 255
    g1 = np.asarray(G1.filter(ImageFilter.GaussianBlur(26)).resize((W, H), Image.BILINEAR)).astype(np.float32) / 255
    g2 = np.asarray(G2.filter(ImageFilter.GaussianBlur(7)).resize((W, H), Image.BILINEAR)).astype(np.float32) / 255
    a = a * bright + g1 + g2 * 1.2
    sm = np.asarray(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).resize((270, 480), Image.BILINEAR)).astype(np.float32) / 255
    bl = np.asarray(Image.fromarray((np.clip(np.clip(sm - .62, 0, 1) * 2.0, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(7)).resize((W, H), Image.BILINEAR)).astype(np.float32) / 255
    a = (a + bl * .7) * np.array(tint, np.float32)
    lum = a.mean(2, keepdims=True); a = lum + (a - lum) * sat; a = (a - .45) * con + .45
    a = a * (1 - np.clip(R2 * vig * 1.3, 0, 1) ** 1.3)
    if redpulse > 0: a = a + np.array([.30, 0, .02], np.float32) * redpulse * np.clip(R2 * 1.4, 0, 1) ** 1.5
    if shake[0] or shake[1]: a = np.roll(a, (int(shake[1]), int(shake[0])), (0, 1))
    if ca: a[..., 0] = np.roll(a[..., 0], ca, 1); a[..., 2] = np.roll(a[..., 2], -ca, 1)
    if glitch > 0:
        r = np.random.default_rng(seed)
        for _ in range(int(3 + 9 * glitch)):
            y0 = int(r.integers(0, H - 60)); h = int(r.integers(8, 90)); a[y0:y0 + h] = np.roll(a[y0:y0 + h], int(r.normal(0, 60 * glitch)), 1)
    if flash > 0: a = a * (1 - flash) + np.array(flashcol, np.float32) * flash
    gr = np.asarray(Image.fromarray(np.random.default_rng(seed + 99).normal(0, .03, (480, 270)).astype(np.float32)).resize((W, H), Image.BILINEAR))[..., None]
    return Image.fromarray((np.clip((a + gr) * fade, 0, 1) * 255).astype(np.uint8))

def layers(): return Image.new('RGB', (W // 2, H // 2)), Image.new('RGB', (W // 2, H // 2))

# ------------------------------------------------------------------ card slam (real card art)
RARITY = {'spark': ('LEGENDARY', (255, 120, 220)), 'musk': ('RARE', (255, 160, 60)), 'golem': ('EPIC', (190, 110, 255)), 'skel': ('COMMON', (150, 190, 255)), 'army': ('EPIC', (190, 110, 255))}
ELIXIR = {'spark': 6, 'musk': 9, 'golem': 8, 'skel': 1, 'army': 3}
NAMES = {'spark': 'SPARKY', 'musk': 'THREE MUSKETEERS', 'golem': 'GOLEM', 'skel': 'SKELETON ARMY'}
def card_slam(img, G1, key, u, cx=540, cy=960, w=560):
    """0..0.75: card slams in and holds; 0.75..1.05: blows up into the hero"""
    if u < 0 or u > 1.05: return 0.0
    card = CARD[key]
    if u < .75:
        k = 1 + 1.8 * max(0, 1 - u / .1) ** 2; a = clamp(u / .05)
    else:
        v = (u - .75) / .3; k = 1 + 2.2 * v ** 1.6; a = 1 - v
    sp = sprite(card, w * k); glow_from(G1, sp, cx - sp.width / 2, cy - sp.height / 2, RARITY[key][1], 60, .3 * a)
    paste(img, sp, cx - sp.width / 2, cy - sp.height / 2, a)
    return a
def cardtag(img, key, t, t0, t1, y):
    r, col = RARITY[key]
    caption(img, t, t0, t1, f'{r}  -  {ELIXIR[key]} ELIXIR', y, 54, col, rot=0)

# ------------------------------------------------------------------ scenes
def scene_hook(t, fi):
    p = pulse_at(t); G1, G2 = layers()
    img = backdrop(t, (6, 4, 18), (46, 22, 86), floor_speed=20)
    rays(G1, t, 540, -80, (30, 18, 60), 6, 1.1, 2000, 1.0); embers(G2, t, 45, (170, 110, 255), 3, 30); bokeh(G1, t, (140, 90, 255))
    img = fog(img, t, .3, (60, 40, 100))
    sk = 30 * max(0, 1 - t / .3) + p * 3
    if t < 2.1:  # the best players: Ultimate Champion badge (official art)
        k = 1 + .25 * max(0, 1 - t / .35) ** 2 + .02 * p; a = clamp(t / .1) * clamp((2.1 - t) / .25)
        sp = sprite(BADGE, 560 * k); glow_from(G1, sp, 540 - sp.width / 2, 1040 - sp.height / 2, (150, 70, 255), 70, .8 * a)
        paste(img, sp, 540 - sp.width / 2, 1040 - sp.height / 2, a)
    else:  # ...are still afraid of these four cards
        order = ['spark', 'musk', 'golem', 'skel']; r = np.random.default_rng(fi)
        for i, key in enumerate(order):
            t0 = 2.1 + .35 * i; u = t - t0
            if u < 0: continue
            k = 1 + 1.4 * max(0, 1 - u / .12) ** 2; a = clamp(u / .06)
            tr = (1.5 + 4 * clamp((t - 3.2) / 1)) * (1 + p)
            w = 232; sp = sprite(CARD[key], w * k); x = 135 + i * 270 + r.normal(0, tr); y = 1060 + r.normal(0, tr) + (-30 if i % 2 else 0)
            glow_from(G1, sp, x - sp.width / 2, y - sp.height / 2, RARITY[key][1], 50, .45 * a); paste(img, sp, x - sp.width / 2, y - sp.height / 2, a)
    slam(img, t, -.1, 2.0, 'NO MATTER HOW\nGOOD YOU ARE...', 480, 118, (255, 255, 255))
    slam(img, t, 2.0, 4.3, 'THESE 4 CARDS\nSTILL MAKE YOU SWEAT', 480, 82, (255, 214, 80), seed=3)
    fl = clamp(1 - t / .1) * .35 + sum(clamp(1 - (t - (2.1 + .35 * i)) / .1) * .4 for i in range(4) if t >= 2.1 + .35 * i)
    return post(img, G1, G2, tint=(.95, .9, 1.1), sat=1.0, con=1.15, bright=.9, vig=.85, flash=min(fl, .6), ca=int(10 * max(0, 1 - t / .25)), seed=fi, redpulse=p * .5, shake=shake_off(sk, fi))

def scene_spark(t, fi):
    u = t - T_SPARKY; p = pulse_at(t); G1, G2 = layers(); rr = np.random.default_rng(fi)
    c = clamp((u - 1.3) / 2.7) ** 1.6; after = t - ZAP
    amp = c * 8 + impact(t, [ZAP], .25) * 50 + (28 * max(0, 1 - u / .12) if u < .12 else 0)
    img = backdrop(t, (4, 8, 22), (18, 60, 130), floor_speed=40)
    rays(G1, t, 540, -60, (14, 50, 110), 7, 1.3, 2000, 1.0 + c); bokeh(G1, t, (80, 170, 255)); embers(G2, t, 70, (120, 200, 255), 4, 80)
    img = fog(img, t, .3, (40, 70, 130))
    card_slam(img, G1, 'spark', u)
    if u >= .7:
        v = sstep((u - .7) / .5); bob = math.sin(t * 3) * 8
        pre = ZAP - .2 < t < ZAP
        h = Hero('spark', img, G1, 540 + 10 * math.sin(t * 40) * c, 1400 + (1 - v) * 60, lerp(1500, 1150, v) * (1 + c * .015), bob, -.012 * c, glow=(60, 130, 255), gk=.12 + .2 * c)
        tip = h.at('tip')
        if c > .05 and after < 0:
            for _ in range(int(2 + 9 * c)):
                ang = rr.uniform(-2.8, .5); L = rr.uniform(90, 420) * (.5 + c); p1 = (tip[0] + math.cos(ang) * L, tip[1] + math.sin(ang) * L)
                draw_bolt(img, G1, G2, tip, p1, rr, 4 + 5 * c, jag=L * .25, branches=0)
        radial(G1, tip[0], tip[1], 80 + 170 * c, (28, 70, 150)); radial(G2, tip[0], tip[1], 20 + 90 * c, (150, 200, 255))
        if 0 <= after < .5:
            far = (rr.uniform(-100, 400), H + 100)
            draw_bolt(img, G1, G2, tip, far, rr, 16, jag=90, branches=5); draw_bolt(img, G1, G2, tip, (W + 100, rr.uniform(300, 900)), rr, 12, jag=90, branches=4)
            radial(G1, tip[0], tip[1], 520 * (1 - after / .5), (60, 100, 170))
    img = zoom_blur(img, .06 * clamp(1 - after / .35) if 0 <= after < .35 else (.05 * max(0, 1 - (u - .7) / .25) if .7 < u < .95 else 0))
    slam(img, t, T_SPARKY + .75, T_SPARKY + 5.4, 'SPARKY', 290, 215, (110, 205, 255), seed=1)
    cardtag(img, 'spark', t, T_SPARKY + 1.0, T_SPARKY + 5.4, 450)
    caption(img, t, T_SPARKY + 2.0, T_SPARKY + 3.9, "DON'T LET IT CHARGE.", 1500, 84, (200, 235, 255))
    caption(img, t, T_SPARKY + 4.15, T_SPARKY + 5.5, 'ONE SHOT. THAT\'S ALL IT TAKES.', 1500, 70, (255, 255, 255))
    fl = clamp(1 - after / .4) ** 2 if after >= 0 else (.4 * max(0, 1 - u / .08) if u < .08 else 0)
    if ZAP - .22 < t < ZAP: img = Image.eval(img, lambda v: int(v * .45))
    return post(img, G1, G2, tint=(.92, 1.0, 1.15), sat=1.0, con=1.22, bright=.85, vig=.95, flash=fl, flashcol=(.85, .93, 1), ca=int(amp * .22), glitch=clamp(1 - after / .4) * .8 if 0 <= after < .4 else 0, seed=fi, redpulse=p * .25, shake=shake_off(amp, fi))

def scene_musk(t, fi):
    u = t - T_MUSK; p = pulse_at(t); G1, G2 = layers(); rr = np.random.default_rng(fi)
    amp = impact(t, SHOTS, .16) * 30 + 3 + (28 * max(0, 1 - u / .12) if u < .12 else 0)
    img = backdrop(t, (14, 4, 22), (110, 30, 100), floor_speed=34)
    rays(G1, t, 540, -60, (90, 24, 80), 7, 1.3, 2000, 1.0); bokeh(G1, t, (255, 110, 200)); embers(G2, t, 60, (255, 130, 210), 6, 60)
    img = fog(img, t, .3, (100, 50, 110))
    card_slam(img, G1, 'musk', u)
    if u >= .7:
        v = sstep((u - .7) / .6); push = 1 + .05 * clamp((u - .7) / 4.2)
        march = abs(math.sin(math.pi * (u - .7) / .55)) * 14 * (1 - clamp((u - 2.2) / .4))
        h = Hero('musk', img, G1, 540, 1450 + (1 - v) * 700, 1260 * push, march, 0, glow=(255, 70, 190), gk=.14)
        for i, nm in enumerate(['m1', 'm2', 'm3']):
            ms = SHOTS[i]; x, y = h.at(nm); muzzle(img, G1, G2, x, y, t - ms, rr, 1.3)
            if 0 <= t - ms < .6:
                f = 1 - (t - ms) / .6; radial(G1, x, y, 300 * f, (140, 70, 40))
                for _ in range(6): ImageDraw.Draw(img).line([(x, y), (x + rr.normal(0, 260), y + rr.uniform(300, 900))], fill=(255, 230, 150), width=5)
    img = zoom_blur(img, .05 * sum(clamp(1 - (t - s0) / .2) for s0 in SHOTS if t >= s0))
    slam(img, t, T_MUSK + .75, T_MUSK + 5.0, 'THREE\nMUSKETEERS', 330, 170, (255, 120, 205), seed=2)
    cardtag(img, 'musk', t, T_MUSK + 1.0, T_MUSK + 5.0, 560)
    caption(img, t, T_MUSK + 1.4, T_MUSK + 2.55, 'THREE GUNS.', 1500, 100, (255, 225, 245))
    caption(img, t, T_MUSK + 3.3, T_MUSK + 4.95, 'ONE PUSH. NO WAY OUT.', 1500, 80, (255, 255, 255))
    fl = max([clamp(1 - (t - s0) / .1) for s0 in SHOTS if t >= s0] + [0]) * .4 + (.35 * max(0, 1 - u / .08) if u < .08 else 0)
    return post(img, G1, G2, tint=(1.08, .9, 1.1), sat=1.0, con=1.2, bright=.85, vig=.95, flash=fl, flashcol=(1, .85, .95), ca=int(amp * .2), seed=fi, redpulse=p * .35, shake=shake_off(amp, fi))

def scene_golem(t, fi):
    u = t - T_GOLEM; p = pulse_at(t); G1, G2 = layers(); rr = np.random.default_rng(fi)
    amp = impact(t, STOMPS, .3, [1, 1.1, 1.3, 2.4]) * 24 + 3 + (28 * max(0, 1 - u / .12) if u < .12 else 0)
    img = backdrop(t, (12, 6, 10), (110, 50, 20), floor_speed=14)
    rays(G1, t, 540, -60, (90, 40, 14), 7, 1.3, 2000, 1.0); bokeh(G1, t, (255, 140, 60)); embers(G2, t, 70, (255, 130, 40), 7, 55)
    img = fog(img, t, .38, (100, 70, 55), 16)
    card_slam(img, G1, 'golem', u)
    if u >= .7:
        v = sstep((u - .7) / .5); k = 1 + .08 * clamp((u - .7) / 4.0)
        sq = sum(.05 * math.exp(-(t - s0) / .2) * math.cos((t - s0) * 18) for s0 in STOMPS if t >= s0)
        eye = clamp(.3 + .15 * math.sin(t * 5) + impact(t, STOMPS[-1:], .5))
        h = Hero('golem', img, G1, 540, 1450 + (1 - v) * 500, 1240 * k, 0, sq, glow=(255, 120, 60), gk=.1 + .12 * eye)
        for nm in ('eyeL', 'eyeR'):
            x, y = h.at(nm); radial(G1, x, y, 60 + 110 * eye, (130, 25, 110)); radial(G2, x, y, 16 + 44 * eye, (255, 150, 255))
        for s0 in STOMPS:
            d0 = t - s0
            if 0 <= d0 < 1.1: ring(G2, 540, 1570, d0 * 1900, 26 * (1 - d0), (255, 180, 100))
            dust(img, t, 540, 1560, s0, int(s0 * 10))
    img = zoom_blur(img, .05 * sum(clamp(1 - (t - s0) / .22) for s0 in STOMPS if t >= s0))
    slam(img, t, T_GOLEM + .75, T_GOLEM + 5.4, 'GOLEM', 290, 240, (255, 160, 70), seed=4)
    cardtag(img, 'golem', t, T_GOLEM + 1.0, T_GOLEM + 5.4, 450)
    caption(img, t, T_GOLEM + 1.3, T_GOLEM + 2.6, 'SLOW.', 1500, 110, (255, 235, 210))
    caption(img, t, T_GOLEM + 2.65, T_GOLEM + 3.5, 'HEAVY.', 1500, 110, (255, 235, 210))
    caption(img, t, T_GOLEM + 3.6, T_GOLEM + 5.4, 'UNSTOPPABLE.', 1500, 100, (255, 255, 255))
    fl = clamp(1 - (t - STOMPS[-1]) / .2) * .5 if t >= STOMPS[-1] else (.35 * max(0, 1 - u / .08) if u < .08 else 0)
    return post(img, G1, G2, tint=(1.1, .95, .9), sat=1.0, con=1.22, bright=.85, vig=1.0, flash=fl, flashcol=(1, .85, .7), ca=int(amp * .15), seed=fi, redpulse=p * .4, shake=shake_off(amp, fi))

_sk = np.random.default_rng(21)
SKP = [(x, d, 1.0, ph, 0) for x, d, ph in [(300, .0, 0.), (540, .12, 1.7), (780, .05, 3.1)]] + [(float(_sk.uniform(60, 1020)), float(1.9 + _sk.uniform(0, 1.3)), float(_sk.uniform(.8, 1.2)), float(_sk.uniform(0, 6)), int(_sk.integers(0, 2))) for _ in range(15)]
def scene_skel(t, fi):
    u = t - T_SKEL; p = pulse_at(t); G1, G2 = layers(); rr = np.random.default_rng(fi)
    amp = 6 + 8 * clamp(u / 4) + (28 * max(0, 1 - u / .12) if u < .12 else 0)
    img = backdrop(t, (4, 12, 10), (24, 110, 70), floor_speed=60)
    rays(G1, t, 540, -60, (14, 80, 40), 7, 1.3, 2000, 1.0); bokeh(G1, t, (110, 255, 160)); embers(G2, t, 70, (130, 255, 170), 8, 50)
    img = fog(img, t, .42, (40, 100, 70), 30)
    card_slam(img, G1, 'skel', u, 330, 960, 440); card_slam(img, G1, 'army', u, 750, 960, 440)
    if u >= .7:
        w = u - .7; items = []
        for (x0, d, sp, ph, flip) in SKP:
            tt = w - d
            if tt < 0: continue
            y = 1000 + (tt * 520 * sp) ** 1.0 - 120
            s = clamp((y + 200) / 1500); items.append((y, x0, 160 + 360 * s ** 1.3, ph, flip, tt))
        for y, x0, ww, ph, flip, tt in sorted(items):
            x = 540 + (x0 - 540) * (.35 + 1.2 * clamp((y + 200) / 1500)); hop = abs(math.sin(t * 9 + ph)) * ww * .06
            sp_ = HERO['skel']['im']
            sp = sprite(sp_, ww)
            if flip: sp = sp.transpose(Image.FLIP_LEFT_RIGHT)
            shadow(img, x, y + 6, ww * .3, ww * .05, 120); glow_from(G1, sp, x - sp.width / 2, y - sp.height - hop, (40, 255, 130), 30, .1)
            paste(img, sp, x - sp.width / 2, y - sp.height - hop)
    img = zoom_blur(img, .05 * max(0, 1 - (u - .7) / .25) if .7 < u < .95 else 0)
    slam(img, t, T_SKEL + .75, T_SKEL + 5.0, 'SKELETONS', 300, 160, (225, 255, 215), seed=5)
    caption(img, t, T_SKEL + 1.0, T_SKEL + 5.0, 'COMMON - 1 ELIXIR   |   EPIC - 3 ELIXIR', 450, 40, (200, 220, 255), rot=0)
    caption(img, t, T_SKEL + 1.4, T_SKEL + 2.6, '3 SKELETONS. 1 ELIXIR.', 1500, 84, (255, 255, 255))
    caption(img, t, T_SKEL + 2.7, T_SKEL + 3.7, 'NOW 15 FOR 3.', 1500, 96, (190, 255, 210))
    caption(img, t, T_SKEL + 3.7, T_SKEL + 5.0, "AND YOU'RE ALREADY LATE.", 1500, 70, (255, 255, 255))
    fl = .35 * max(0, 1 - u / .08) if u < .08 else 0
    return post(img, G1, G2, tint=(.9, 1.08, .95), sat=1.0, con=1.2, bright=.88, vig=1.0, flash=fl, ca=int(amp * .12), seed=fi, redpulse=p * .3, shake=shake_off(amp, fi))

def scene_mont(t, fi):
    k = max(i for i, c in enumerate(MONT_CUTS) if t >= c); kind = MONT[k]; lt = t - MONT_CUTS[k]; p = pulse_at(t)
    G1, G2 = layers(); amp = 18 * math.exp(-lt * 8)
    col = {'spark': (60, 140, 255), 'musk': (255, 70, 190), 'golem': (255, 130, 50), 'skel': (60, 255, 130), 'all': (255, 40, 60)}[kind]
    img = backdrop(t, (6, 4, 14), tuple(int(c * .45) for c in col), floor_speed=70 + 20 * k)
    rays(G1, t, 540, -60, tuple(int(c * .35) for c in col), 7, 1.4, 2000, 1.0); embers(G2, t, 60, col, 9 + k, 90); bokeh(G1, t, col)
    z = 1 + .22 * (1 - sstep(lt / .45)); bob = math.sin(t * 6) * 6
    if kind == 'spark':
        h = Hero('spark', img, G1, 540, 1400, 1150 * z, bob, glow=col, gk=.2); tip = h.at('tip'); rr = np.random.default_rng(fi)
        for _ in range(6): draw_bolt(img, G1, G2, tip, (tip[0] + rr.normal(0, 400), tip[1] + rr.normal(0, 400)), rr, 6, jag=90, branches=0)
    elif kind == 'musk': Hero('musk', img, G1, 540, 1470, 1260 * z, bob, glow=col, gk=.18)
    elif kind == 'golem': Hero('golem', img, G1, 540, 1480, 1240 * z, bob, glow=col, gk=.16)
    elif kind == 'skel': Hero('skarmy', img, G1, 540, 1480, 1100 * z, bob, glow=col, gk=.18)
    else:
        for i, key in enumerate(['spark', 'musk', 'golem', 'skel']):
            sp = sprite(CARD[key], 238); x = 135 + i * 270; y = 960 + (-40 if i % 2 else 0) + np.random.default_rng(fi + i).normal(0, 5)
            glow_from(G1, sp, x - sp.width / 2, y - sp.height / 2, RARITY[key][1], 50, .6); paste(img, sp, x - sp.width / 2, y - sp.height / 2)
    img = zoom_blur(img, .06 * math.exp(-lt * 14))
    nm = {'spark': 'SPARKY', 'musk': 'THREE\nMUSKETEERS', 'golem': 'GOLEM', 'skel': 'SKELETONS', 'all': 'FEAR.'}[kind]
    sz = {'spark': 215, 'musk': 140, 'golem': 240, 'skel': 170, 'all': 300}[kind]
    tc = (255, 255, 255) if kind == 'all' else tuple(min(255, int(c * .5 + 140)) for c in col)
    text(img, nm, W / 2 + np.random.normal(0, 3), 330 if kind != 'all' else 560, sz, tc, scale=1 + .5 * max(0, 1 - lt / .1), rot=-3)
    fl = clamp(1 - lt / .1) * .28
    if kind == 'all' and t > T_END - .15: fl = clamp((t - (T_END - .15)) / .12)
    return post(img, G1, G2, tint=(1.0, .97, 1.02), sat=1.05, con=1.25, bright=.88, vig=1.0, flash=fl, ca=int(8 * math.exp(-lt * 8)) + 2, glitch=.45 * math.exp(-lt * 12), seed=fi, redpulse=p * .7, shake=shake_off(amp, fi))

def scene_end(t, fi):
    G1, G2 = layers(); p = pulse_at(t); u = t - T_END; o = clamp((DUR - t) / .35)
    img = backdrop(t, (4, 3, 10), (50, 20, 60), floor_speed=10)
    rays(G1, t, 540, -60, (40, 16, 50), 6, 1.1, 2000, 1.0); embers(G2, t, 40, (170, 110, 255), 9, 25)
    slam(img, t, T_END + .1, DUR, 'WHICH ONE SCARES\nYOU THE MOST?', 480, 100, (255, 255, 255), seed=7)
    for i, key in enumerate(['spark', 'musk', 'golem', 'skel']):
        a = clamp((u - .5 - .18 * i) / .2)
        if a <= 0: continue
        sp = sprite(CARD[key], 238); x = 135 + i * 270; y = 1010 + (-30 if i % 2 else 0) + math.sin(t * 2 + i) * 6
        glow_from(G1, sp, x - sp.width / 2, y - sp.height / 2, RARITY[key][1], 50, .5 * a * o); paste(img, sp, x - sp.width / 2, y - sp.height / 2, a * o)
        text(img, str(i + 1), x, y + 240, 90, RARITY[key][1], alpha=a * o)
    caption(img, t, T_END + 1.7, DUR - .1, 'COMMENT 1, 2, 3 OR 4', 1360, 70, (255, 214, 80), rot=-2)
    if u > 2.2: text(img, 'Fan-made tribute. Clash Royale (c) Supercell. Not affiliated.', W / 2, 1470, 26, (170, 160, 190), sw=2, shadow_on=False, alpha=clamp((u - 2.2) / .5) * o)
    return post(img, G1, G2, tint=(.95, .92, 1.08), vig=1.0, bright=.85, seed=fi, redpulse=p * .45, fade=o)

def render(fi):
    t = fi / FPS
    if t < T_SPARKY - .3: im = scene_hook(t, fi)
    elif t < T_SPARKY: im = Image.new('RGB', (W, H), (0, 0, 0))
    elif t < T_MUSK: im = scene_spark(t, fi)
    elif t < T_GOLEM: im = scene_musk(t, fi)
    elif t < T_SKEL: im = scene_golem(t, fi)
    elif t < T_MONT: im = scene_skel(t, fi)
    elif t < T_END: im = scene_mont(t, fi)
    else: im = scene_end(t, fi)
    im.save(f'{OUT}/f{fi:05d}.jpg', quality=93); return fi

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        for tm in [float(x) for x in sys.argv[2:]]: render(int(tm * FPS))
    else:
        with Pool(4) as pool:
            for i, _ in enumerate(pool.imap_unordered(render, range(NF), chunksize=6)):
                if i % 100 == 0: print(i, flush=True)
