import numpy as np, math, sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from multiprocessing import Pool
from timeline import *

W, H = 1080, 1920
WW, WH = 1080, 2400
NF = int(DUR * FPS)
OUT = 'frames'
FONT = '/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf'
INK = (22, 12, 40)
BEATS = beats()

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
        if 0 <= dt < 1.5: a += (amps[i] if amps else 1.0) * math.exp(-dt / decay)
    return a

def poly(d, pts, fill, w=6, ol=INK):
    d.polygon(pts, fill=fill)
    d.line(list(pts) + [pts[0]], fill=ol, width=int(w), joint='curve')
def ell(d, cx, cy, rx, ry, fill, w=6, ol=INK):
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=fill, outline=ol, width=int(w))
def rrect(d, x0, y0, x1, y1, r, fill, w=6, ol=INK):
    d.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=fill, outline=ol, width=int(w))

# ------------------------------------------------------------------ world
def tower(d, x, y, s, team):
    roof = (205, 55, 60) if team == 'r' else (60, 110, 225)
    roof2 = (240, 90, 90) if team == 'r' else (110, 160, 255)
    rrect(d, x - 75 * s, y - 20 * s, x + 75 * s, y + 95 * s, 10, (150, 150, 168), 6)
    for i in range(6):
        d.line([x - 75 * s + i * 30 * s, y + 40 * s, x - 75 * s + i * 30 * s + 18 * s, y + 40 * s], fill=(120, 120, 140), width=4)
    rrect(d, x - 60 * s, y - 70 * s, x + 60 * s, y - 15 * s, 8, (170, 170, 188), 6)
    for i in range(4):
        rrect(d, x - 60 * s + i * 33 * s, y - 92 * s, x - 60 * s + i * 33 * s + 27 * s, y - 68 * s, 3, (170, 170, 188), 5)
    poly(d, [(x - 50 * s, y - 92 * s), (x, y - 160 * s), (x + 50 * s, y - 92 * s)], roof, 6)
    poly(d, [(x - 25 * s, y - 110 * s), (x, y - 160 * s), (x + 8 * s, y - 118 * s)], roof2, 3, roof)
    ell(d, x, y + 30 * s, 17 * s, 25 * s, (20, 15, 35), 4)
    ell(d, x, y - 45 * s, 12 * s, 14 * s, (255, 200, 80), 3)

def build_world():
    rng = np.random.default_rng(3)
    im = Image.new('RGB', (WW, WH)); d = ImageDraw.Draw(im); T = 90
    for r in range(WH // T + 1):
        for c in range(WW // T):
            col = (40, 82, 70) if (r + c) % 2 == 0 else (33, 70, 62)
            d.rectangle([c * T, r * T, (c + 1) * T, (r + 1) * T], fill=col)
    for bx in (220, 860):  # stone paths
        d.rectangle([bx - 70, 560, bx + 70, 1100], fill=(122, 112, 98)); d.rectangle([bx - 70, 1300, bx + 70, 1900], fill=(122, 112, 98))
        for yy in list(range(560, 1100, 55)) + list(range(1300, 1900, 55)):
            d.line([bx - 70, yy, bx + 70, yy], fill=(98, 90, 80), width=3)
    d.rectangle([0, 1095, WW, 1305], fill=(24, 62, 98))
    for i in range(70):
        x = rng.integers(0, WW); y = rng.integers(1110, 1290)
        d.line([x, y, x + rng.integers(40, 120), y], fill=(70, 130, 175), width=4)
    d.rectangle([0, 1085, WW, 1100], fill=(86, 70, 52)); d.rectangle([0, 1300, WW, 1315], fill=(86, 70, 52))
    for bx in (220, 860):
        d.rectangle([bx - 90, 1075, bx + 90, 1325], fill=(126, 86, 50), outline=INK, width=6)
        for yy in range(1080, 1325, 30): d.line([bx - 90, yy, bx + 90, yy], fill=(92, 60, 34), width=4)
        d.rectangle([bx - 100, 1075, bx - 85, 1325], fill=(150, 150, 165), outline=INK, width=4)
        d.rectangle([bx + 85, 1075, bx + 100, 1325], fill=(150, 150, 165), outline=INK, width=4)
    for (x, y, s, tm) in [(220, 640, 1, 'r'), (860, 640, 1, 'r'), (540, 270, 1.5, 'r'), (220, 1860, 1, 'b'), (860, 1860, 1, 'b'), (540, 2130, 1.5, 'b')]:
        ell(d, x, y + 95 * s, 95 * s, 26 * s, (18, 40, 38), 0, (18, 40, 38))
        tower(d, x, y, s, tm)
    for i in range(46):  # trees
        side = rng.choice([0, 1]); x = rng.integers(-20, 70) if side == 0 else rng.integers(1010, 1100); y = rng.integers(0, WH); r = rng.integers(40, 78)
        ell(d, x, y, r, r, (22, 54, 44), 5); ell(d, x - r * .25, y - r * .3, r * .55, r * .5, (34, 78, 58), 0, (34, 78, 58))
    a = np.asarray(im).astype(np.float32)
    a += rng.normal(0, 4, a.shape[:2])[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
WORLD = build_world()

def cam_view(cx, cy, z, sx=0, sy=0):
    w, h = W / z, H / z
    x0 = min(max(cx - w / 2 + sx / z, 0), WW - w); y0 = min(max(cy - h / 2 + sy / z, 0), WH - h)
    img = WORLD.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + w, y0 + h))
    return img, (lambda x, y: ((x - x0) * z, (y - y0) * z))

# ------------------------------------------------------------------ fog / particles
_r = np.random.default_rng(11)
def _fogtex():
    a = _r.random((60, 120)).astype(np.float32); im = Image.fromarray((a * 255).astype(np.uint8)).resize((480, 240), Image.BICUBIC).filter(ImageFilter.GaussianBlur(14))
    b = np.asarray(im).astype(np.float32); b = (b - b.min()) / (b.max() - b.min()); return b
FOG = _fogtex()
def fog(img, t, strength, col=(120, 140, 180), speed=24):
    ox = int((t * speed) % 240); win = np.concatenate([FOG, FOG], 1)[:, ox:ox + 240]
    oy = int((t * speed * .4) % 120)
    win2 = np.concatenate([FOG, FOG], 0)[oy:oy + 120, :240] if False else win[:120]
    m = Image.fromarray((np.clip(win[:240, :240] if False else win, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
    m = (np.asarray(m).astype(np.float32) / 255) ** 1.5 * strength
    a = np.asarray(img).astype(np.float32); c = np.array(col, np.float32)
    return Image.fromarray(np.clip(a * (1 - m[..., None]) + c * m[..., None], 0, 255).astype(np.uint8))
def embers(G2, t, n=70, col=(255, 150, 50), seed=1, speed=60, up=True):
    r = np.random.default_rng(seed); d = ImageDraw.Draw(G2)
    for i in range(n):
        x0, y0, ph, sp, rr = r.random() * W, r.random() * H, r.random() * 6, r.uniform(.5, 1.6), r.uniform(2.5, 6)
        y = (y0 - sp * speed * t) % (H + 40) if up else (y0 + sp * speed * t) % (H + 40)
        x = x0 + math.sin(t * sp + ph) * 40; tw = .5 + .5 * math.sin(t * 7 * sp + ph)
        c = tuple(int(v * tw) for v in col); d.ellipse([(x - rr) / 2, (y - rr) / 2, (x + rr) / 2, (y + rr) / 2], fill=c)

# ------------------------------------------------------------------ text
def text(img, txt, cx, cy, size, fill=(255, 255, 255), stroke=INK, sw=None, alpha=1.0, scale=1.0, rot=0, shadow=True):
    if alpha <= 0.01: return
    sw = sw if sw is not None else max(4, int(size * 0.09)); f = font(size)
    tmp = Image.new('RGBA', (int(W * 1.4), int(size * 4.5)), (0, 0, 0, 0)); d = ImageDraw.Draw(tmp)
    c = (tmp.width // 2, tmp.height // 2)
    if shadow: d.multiline_text((c[0] + size * .04, c[1] + size * .07), txt, font=f, anchor='mm', align='center', fill=(0, 0, 0, 180), stroke_width=sw, stroke_fill=(0, 0, 0, 180))
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
    p = clamp((t - t0) / 0.22); o = clamp((t1 - t) / 0.25)
    text(img, txt, W / 2, cy, size, fill, alpha=min(p, o), scale=1 + 0.35 * (1 - p) ** 2, rot=rot)
def slam(img, t, t0, t1, txt, cy, size, fill, rot=-3):
    if not (t0 <= t <= t1): return
    u = t - t0; sc = 1 + 2.0 * max(0, 1 - u / 0.11) ** 2 + 0.06 * math.exp(-u * 6) * math.sin(u * 30)
    o = clamp((t1 - t) / 0.2); sh = (0, 0) if u > .4 else ((np.random.rand() - .5) * 26 * (1 - u / .4),) * 2
    text(img, txt, W / 2 + sh[0], cy + sh[1], size, fill, alpha=min(1, u / 0.05) * o, scale=sc, rot=rot)

# ------------------------------------------------------------------ fx
def bolt(p0, p1, rng, jag=60, depth=6):
    pts = [p0, p1]
    for lvl in range(depth):
        new = [pts[0]]
        for a, b in zip(pts[:-1], pts[1:]):
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2; L = math.hypot(b[0] - a[0], b[1] - a[1]) + 1e-6
            nx, ny = -(b[1] - a[1]) / L, (b[0] - a[0]) / L; off = rng.normal(0, jag / (1.6 ** lvl))
            new += [(mx + nx * off, my + ny * off), b]
        pts = new
    return pts
def draw_bolt(img, G1, G2, p0, p1, rng, w=8, col=(255, 225, 110), jag=70, branches=3):
    d, g1, g2 = ImageDraw.Draw(img), ImageDraw.Draw(G1), ImageDraw.Draw(G2)
    lines = [(bolt(p0, p1, rng, jag), w)]
    for _ in range(branches):
        pts = lines[0][0]; i = int(rng.integers(len(pts) // 5, len(pts) * 4 // 5)); a = pts[i]
        ang = rng.uniform(0, 6.28); L = rng.uniform(120, 360); lines.append((bolt(a, (a[0] + math.cos(ang) * L, a[1] + math.sin(ang) * L), rng, jag * .6, 5), w * .5))
    for pts, ww in lines:
        s1 = [(x / 2, y / 2) for x, y in pts]
        g1.line(s1, fill=col, width=int(ww * 2.4), joint='curve'); g2.line(s1, fill=col, width=int(ww * .9), joint='curve')
        d.line(pts, fill=col, width=int(ww * 1.3), joint='curve'); d.line(pts, fill=(255, 255, 255), width=max(2, int(ww * .55)), joint='curve')
def ring(G2, x, y, r, w, col):
    ImageDraw.Draw(G2).ellipse([(x - r) / 2, (y - r * .45) / 2, (x + r) / 2, (y + r * .45) / 2], outline=col, width=max(1, int(w / 2)))
def radial(G, x, y, r, col):
    ImageDraw.Draw(G).ellipse([(x - r) / 2, (y - r) / 2, (x + r) / 2, (y + r) / 2], fill=col)
def smoke(img, t, x, y, t0, n=14, seed=2, rise=140, col=(40, 38, 46)):
    if t < t0: return
    r = np.random.default_rng(seed); lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); u = t - t0
    for i in range(n):
        ox, sp, rr = r.normal(0, 55), r.uniform(.5, 1.3), r.uniform(40, 90)
        a = int(150 * clamp(1 - u / 3.5) * clamp(u * 3 + 0.2 - i * .02))
        cx, cy = x + ox + math.sin(u + i) * 20, y - u * rise * sp - i * 8; rad = rr * (1 + u * .35)
        d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=col + (a,))
    lay = lay.filter(ImageFilter.GaussianBlur(10)); img.paste(lay, (0, 0), lay)

# ------------------------------------------------------------------ characters
def sparky(d, G1, G2, x, y, s, charge, t):
    ell(d, x, y, 2.4 * s, .35 * s, (0, 0, 0, 130), 0, (0, 0, 0, 0))
    for dx in (-1.15, 1.15):
        ell(d, x + dx * s, y - .5 * s, .58 * s, .5 * s, (32, 32, 46), s * .05)
        ell(d, x + dx * s, y - .5 * s, .27 * s, .24 * s, (130, 130, 150), s * .04)
    rrect(d, x - 1.7 * s, y - 1.85 * s, x + 1.7 * s, y - .55 * s, s * .3, (62, 92, 176), s * .07)
    rrect(d, x - 1.5 * s, y - 1.8 * s, x + 1.5 * s, y - 1.3 * s, s * .22, (96, 136, 224), 0, (96, 136, 224))
    d.rectangle([x - 1.6 * s, y - 1.15 * s, x + 1.6 * s, y - .85 * s], fill=(244, 190, 40))
    for i in range(-8, 8): d.polygon([(x + i * .2 * s, y - 1.15 * s), (x + i * .2 * s + .1 * s, y - 1.15 * s), (x + i * .2 * s - .05 * s, y - .85 * s), (x + i * .2 * s - .15 * s, y - .85 * s)], fill=INK)
    d.line([x - 1.6 * s, y - 1.15 * s, x + 1.6 * s, y - 1.15 * s], fill=INK, width=int(s * .05)); d.line([x - 1.6 * s, y - .85 * s, x + 1.6 * s, y - .85 * s], fill=INK, width=int(s * .05))
    ell(d, x, y - 2.0 * s, .85 * s, .6 * s, (84, 118, 206), s * .07)
    rrect(d, x - .6 * s, y - 2.2 * s, x + .6 * s, y - 1.85 * s, s * .12, (14, 8, 24), s * .04)
    eye = (255, int(150 + 80 * charge), 40)
    for sgn in (-1, 1):
        poly(d, [(x + sgn * .12 * s, y - 2.02 * s), (x + sgn * .5 * s, y - 2.16 * s), (x + sgn * .46 * s, y - 2.0 * s)], eye, 0)
        radial(G2, x + sgn * .32 * s, y - 2.08 * s, .3 * s * (.4 + charge), (150, 80, 10))
    poly(d, [(x - .5 * s, y - 2.45 * s), (x - .28 * s, y - 4.3 * s), (x + .28 * s, y - 4.3 * s), (x + .5 * s, y - 2.45 * s)], (196, 118, 52), s * .06)
    for k in range(5):
        yy = y - 2.8 * s - k * .32 * s; hw = .44 * s - k * .035 * s
        d.line([x - hw, yy, x + hw, yy], fill=INK, width=int(s * .06)); d.line([x - hw, yy - .06 * s, x + hw, yy - .06 * s], fill=(255, 190, 110), width=int(s * .03))
    for sgn in (-1, 1):
        rrect(d, x + sgn * .55 * s - .1 * s, y - 3.6 * s, x + sgn * .55 * s + .1 * s, y - 2.5 * s, s * .05, (150, 150, 168), s * .04)
    ox, oy = x, y - 4.55 * s; r = (.25 + .32 * charge) * s
    radial(G1, ox, oy, r * 3.2, (90 + int(60 * charge), 70, 12)); radial(G2, ox, oy, r * 1.7, (170, 130, 50))
    ell(d, ox, oy, r, r, (255, 250, 210), max(2, s * .04), (255, 200, 60))
    if charge > .05:
        rr = np.random.default_rng(int(t * 60) % 997)
        for _ in range(int(2 + 8 * charge)):
            ang = rr.uniform(0, 6.28); L = r * rr.uniform(1.6, 3.2) * (.6 + charge)
            pts = bolt((ox, oy), (ox + math.cos(ang) * L, oy + math.sin(ang) * L), rr, L * .25, 4)
            d.line(pts, fill=(255, 245, 200), width=max(2, int(s * .035)), joint='curve')
            ImageDraw.Draw(G2).line([(a / 2, b / 2) for a, b in pts], fill=(255, 210, 90), width=max(2, int(s * .05)))
    return (ox, oy)

def musketeer(d, G2, x, y, s, t, aim=0.0, bob=0.0, ph=0.0):
    ell(d, x, y, 1.0 * s, .2 * s, (0, 0, 0, 130), 0, (0, 0, 0, 0))
    y = y - bob * s
    for dx in (-.28, .28): rrect(d, x + dx * s - .13 * s, y - .7 * s, x + dx * s + .13 * s, y, s * .05, (74, 46, 36), s * .05)
    for dx in (-.28, .28): ell(d, x + dx * s, y, .2 * s, .1 * s, (46, 30, 28), s * .04)
    poly(d, [(x - .55 * s, y - .6 * s), (x - .75 * s, y - 1.9 * s), (x + .75 * s, y - 1.9 * s), (x + .55 * s, y - .6 * s)], (70, 80, 186), s * .06)
    d.rectangle([x - .6 * s, y - 1.05 * s, x + .6 * s, y - .9 * s], fill=(250, 200, 60)); d.line([x - .6 * s, y - 1.05 * s, x + .6 * s, y - 1.05 * s], fill=INK, width=int(s * .04))
    poly(d, [(x - .5 * s, y - 2.3 * s), (x - .95 * s, y - 1.3 * s), (x - .6 * s, y - 1.1 * s), (x - .25 * s, y - 2.0 * s)], (140, 64, 176), s * .05)  # ponytail
    ell(d, x, y - 2.45 * s, .62 * s, .6 * s, (246, 206, 168), s * .06)
    poly(d, [(x - .62 * s, y - 2.5 * s), (x - .4 * s, y - 3.0 * s), (x + .4 * s, y - 3.0 * s), (x + .62 * s, y - 2.5 * s), (x + .35 * s, y - 2.75 * s), (x - .35 * s, y - 2.75 * s)], (140, 64, 176), s * .04)
    for sgn in (-1, 1):
        ell(d, x + sgn * .24 * s, y - 2.42 * s, .11 * s, .15 * s, (20, 14, 30), 0); ell(d, x + sgn * .22 * s, y - 2.46 * s, .04 * s, .05 * s, (255, 255, 255), 0)
        d.line([x + sgn * .46 * s, y - 2.72 * s, x + sgn * .08 * s, y - 2.58 * s], fill=INK, width=int(s * .06))
    d.arc([x - .14 * s, y - 2.25 * s, x + .14 * s, y - 2.1 * s], 200, 340, fill=INK, width=int(s * .04))
    ell(d, x, y - 2.95 * s, 1.0 * s, .26 * s, (120, 52, 164), s * .06); ell(d, x, y - 3.15 * s, .55 * s, .35 * s, (150, 70, 190), s * .06)
    poly(d, [(x + .3 * s, y - 3.3 * s), (x + 1.1 * s, y - 3.8 * s), (x + .85 * s, y - 3.1 * s)], (255, 110, 190), s * .04)
    hx, hy = x + .55 * s, y - 1.3 * s
    if aim > .5: tip = (x - .15 * s + 0.2 * s, y + .6 * s)   # pointing down at tower
    else: tip = (x + 1.05 * s, y - 2.3 * s)
    d.line([(hx - .1 * s, hy - .1 * s), tip], fill=(96, 62, 38), width=int(s * .2)); d.line([(hx - .1 * s, hy - .1 * s), tip], fill=INK, width=int(s * .04))
    mid = ((hx * .3 + tip[0] * .7), (hy * .3 + tip[1] * .7)); d.line([mid, tip], fill=(160, 160, 178), width=int(s * .12))
    ell(d, hx, hy, .17 * s, .17 * s, (246, 206, 168), s * .04)
    return tip

def golem(d, G2, x, y, s, t, eye=0.5, sway=0.0, seed=5):
    rr = np.random.default_rng(seed)
    x += sway * s
    ell(d, x, y, 3.4 * s, .5 * s, (0, 0, 0, 140), 0, (0, 0, 0, 0))
    for dx in (-.9, .9): rrect(d, x + dx * s - .55 * s, y - 1.9 * s, x + dx * s + .55 * s, y, s * .12, (92, 84, 82), s * .08)
    poly(d, [(x - 2.0 * s, y - 1.7 * s), (x - 2.3 * s, y - 3.8 * s), (x - 1.2 * s, y - 5.0 * s), (x + 1.2 * s, y - 5.0 * s), (x + 2.3 * s, y - 3.8 * s), (x + 2.0 * s, y - 1.7 * s)], (118, 108, 104), s * .09)
    for _ in range(14):
        cx, cy = x + rr.uniform(-1.8, 1.8) * s, y - rr.uniform(2.0, 4.8) * s; k = rr.uniform(.25, .6) * s
        poly(d, [(cx - k, cy), (cx - k * .2, cy - k), (cx + k, cy - k * .3), (cx + k * .4, cy + k * .7)], tuple(int(v) for v in rr.choice([[134, 124, 118], [100, 92, 90], [150, 138, 128]])), s * .04)
    for _ in range(5):
        cx, cy = x + rr.uniform(-1.4, 1.4) * s, y - rr.uniform(2.2, 4.4) * s
        pts = bolt((cx, cy), (cx + rr.uniform(-.6, .6) * s, cy + rr.uniform(.5, 1.2) * s), rr, s * .15, 3)
        d.line(pts, fill=(255, int(120 + 90 * eye), 30), width=max(2, int(s * .06)))
    for sgn in (-1, 1):
        ax = x + sgn * 2.6 * s
        poly(d, [(x + sgn * 2.1 * s, y - 4.6 * s), (ax + sgn * .5 * s, y - 4.0 * s), (ax + sgn * .4 * s, y - 1.6 * s), (x + sgn * 2.0 * s, y - 2.0 * s)], (108, 98, 96), s * .08)
        rrect(d, ax - .75 * s + sgn * .1 * s, y - 2.0 * s, ax + .75 * s + sgn * .1 * s, y - .35 * s, s * .15, (126, 116, 110), s * .09)
    poly(d, [(x - 1.0 * s, y - 5.0 * s), (x - .85 * s, y - 6.1 * s), (x + .85 * s, y - 6.1 * s), (x + 1.0 * s, y - 5.0 * s)], (130, 120, 114), s * .08)
    for sgn in (-1, 1):
        ex, ey = x + sgn * .38 * s, y - 5.65 * s
        poly(d, [(ex - .22 * s, ey + .05 * s), (ex + sgn * .22 * s, ey - .18 * s), (ex + sgn * .24 * s, ey + .08 * s)], (255, int(170 + 70 * eye), 50), 0)
        radial(G2, ex, ey, s * (.1 + .2 * eye), (190, 90, 10))
    d.line([x - .45 * s, y - 5.28 * s, x + .45 * s, y - 5.28 * s], fill=INK, width=int(s * .07))

def skeleton(d, G2, x, y, s, t, ph=0.0):
    w = math.sin(t * 9 + ph); y = y - abs(w) * .15 * s
    for sgn in (-1, 1):
        d.line([x + sgn * .2 * s, y - .8 * s, x + sgn * .25 * s + w * sgn * .1 * s, y], fill=INK, width=int(s * .2))
        d.line([x + sgn * .2 * s, y - .8 * s, x + sgn * .25 * s + w * sgn * .1 * s, y], fill=(232, 226, 205), width=int(s * .11))
        d.line([x + sgn * .5 * s, y - 1.5 * s, x + sgn * .85 * s, y - 1.0 * s - w * sgn * .2 * s], fill=INK, width=int(s * .2))
        d.line([x + sgn * .5 * s, y - 1.5 * s, x + sgn * .85 * s, y - 1.0 * s - w * sgn * .2 * s], fill=(232, 226, 205), width=int(s * .11))
    rrect(d, x - .42 * s, y - 1.7 * s, x + .42 * s, y - .75 * s, s * .1, (226, 220, 198), s * .06)
    for k in range(3): d.line([x - .3 * s, y - 1.5 * s + k * .27 * s, x + .3 * s, y - 1.5 * s + k * .27 * s], fill=(120, 112, 100), width=max(1, int(s * .05)))
    ell(d, x, y - 2.0 * s, .62 * s, .58 * s, (240, 234, 214), s * .07)
    rrect(d, x - .34 * s, y - 1.6 * s, x + .34 * s, y - 1.3 * s, s * .05, (230, 224, 204), s * .05)
    for k in range(-2, 3): d.line([x + k * .12 * s, y - 1.58 * s, x + k * .12 * s, y - 1.34 * s], fill=INK, width=max(1, int(s * .035)))
    for sgn in (-1, 1):
        ell(d, x + sgn * .24 * s, y - 2.05 * s, .17 * s, .21 * s, (16, 10, 24), 0)
        ell(d, x + sgn * .24 * s, y - 2.05 * s, .07 * s, .09 * s, (120, 255, 160), 0)
    G2d = ImageDraw.Draw(G2)
    for sgn in (-1, 1): G2d.ellipse([(x + sgn * .24 * s - s * .35) / 2, (y - 2.05 * s - s * .35) / 2, (x + sgn * .24 * s + s * .35) / 2, (y - 2.05 * s + s * .35) / 2], fill=(30, 120, 60))

# ------------------------------------------------------------------ UI
def ui(img, t, tremble):
    d = ImageDraw.Draw(img)
    rrect(d, 380, 60, 700, 150, 28, (30, 20, 50), 5, (190, 40, 60))
    text(img, 'OVERTIME', W / 2, 90, 34, (255, 90, 100), sw=3, shadow=False)
    sec = max(0, 9 - int(max(0, t - 4.0))); text(img, f'0:0{sec}', W / 2, 128, 40, (255, 255, 255), sw=3, shadow=False)
    r = np.random.default_rng(int(t * 30))
    for i in range(4):
        x0 = 70 + i * 240; jx, jy = r.normal(0, tremble, 2)
        rrect(d, x0 + jx, 1560 + jy, x0 + 200 + jx, 1790 + jy, 18, (46, 34, 84), 6, (150, 110, 230))
        ell(d, x0 + 100 + jx, 1680 + jy, 56, 56, (28, 20, 52), 4, (110, 80, 190))
        text(img, '?', x0 + 100 + jx, 1675 + jy, 70, (160, 130, 230), sw=3, shadow=False)
        ell(d, x0 + 30 + jx, 1580 + jy, 24, 24, (230, 80, 220), 4); text(img, str(3 + i), x0 + 30 + jx, 1578 + jy, 28, (255, 255, 255), sw=3, shadow=False)
    rrect(d, 70, 1830, 1010, 1880, 20, (24, 16, 44), 5, INK); rrect(d, 76, 1836, 1004, 1874, 16, (210, 70, 230), 0, (210, 70, 230))
    ell(d, 70, 1855, 42, 42, (230, 80, 240), 5); text(img, '10', 70, 1852, 44, (255, 255, 255), sw=4, shadow=False)

# ------------------------------------------------------------------ post
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
R2 = (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)[..., None] / 2
def post(img, G1, G2, tint=(1, 1, 1), sat=1.0, con=1.1, bright=1.0, vig=.7, flash=0.0, flashcol=(1, 1, 1), ca=0, glitch=0.0, seed=0, redpulse=0.0, fade=1.0):
    a = np.asarray(img).astype(np.float32) / 255
    g1 = np.asarray(G1.filter(ImageFilter.GaussianBlur(26)).resize((W, H), Image.BILINEAR)).astype(np.float32) / 255
    g2 = np.asarray(G2.filter(ImageFilter.GaussianBlur(7)).resize((W, H), Image.BILINEAR)).astype(np.float32) / 255
    a = a * bright + g1 * 1.0 + g2 * 1.2
    sm = np.asarray(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).resize((270, 480), Image.BILINEAR)).astype(np.float32) / 255
    br = np.clip(sm - .6, 0, 1) * 2.0
    bl = np.asarray(Image.fromarray((np.clip(br, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(7)).resize((W, H), Image.BILINEAR)).astype(np.float32) / 255
    a = a + bl * .8
    a = a * np.array(tint, np.float32)
    lum = a.mean(2, keepdims=True); a = lum + (a - lum) * sat
    a = (a - .45) * con + .45
    a = a * (1 - np.clip(R2 * vig * 1.3, 0, 1) ** 1.3)
    if redpulse > 0: a = a + np.array([.35, .0, .02], np.float32) * redpulse * np.clip(R2 * 1.4, 0, 1) ** 1.5
    if ca: a[..., 0] = np.roll(a[..., 0], ca, 1); a[..., 2] = np.roll(a[..., 2], -ca, 1)
    if glitch > 0:
        r = np.random.default_rng(seed)
        for _ in range(int(3 + 9 * glitch)):
            y0 = int(r.integers(0, H - 60)); h = int(r.integers(8, 90)); dx = int(r.normal(0, 60 * glitch)); a[y0:y0 + h] = np.roll(a[y0:y0 + h], dx, 1)
            if r.random() < .5: a[y0:y0 + h, :, 1] = np.roll(a[y0:y0 + h, :, 1], 14, 1)
    if flash > 0: a = a * (1 - flash) + np.array(flashcol, np.float32) * flash
    gr = np.random.default_rng(seed + 99).normal(0, .035, (480, 270)).astype(np.float32)
    gr = np.asarray(Image.fromarray(gr).resize((W, H), Image.BILINEAR))[..., None]
    a = a + gr
    return Image.fromarray((np.clip(a * fade, 0, 1) * 255).astype(np.uint8))

def shake_off(amp, fi):
    r = np.random.default_rng(fi * 7 + 1); return r.normal(0, amp, 2) if amp > .3 else (0.0, 0.0)

# ------------------------------------------------------------------ scenes
def new_layers(): return Image.new('RGBA', (W, H), (0, 0, 0, 0)), Image.new('RGB', (W // 2, H // 2), (0, 0, 0)), Image.new('RGB', (W // 2, H // 2), (0, 0, 0))
def comp(img, lay): img.paste(lay, (0, 0), lay); return img

def scene_intro(t, fi):
    p = pulse_at(t); G0 = Image.new('RGB', (W // 2, H // 2)); G1, G2 = G0.copy(), G0.copy()
    if t < 3.2:
        img = Image.new('RGB', (W, H), (4, 3, 10)); embers(G2, t, 40, (150, 40, 40), 3, 30)
        text(img, 'Chahe tum kitne bhi', W / 2, 800, 84, (230, 230, 245), alpha=clamp((t - .6) / .6) * clamp((3.1 - t) / .3), rot=0, shadow=False)
        text(img, 'BADE PLAYER ho...', W / 2, 940, 120, (255, 205, 70), alpha=clamp((t - 1.5) / .5) * clamp((3.1 - t) / .3), scale=1 + .3 * (1 - clamp((t - 1.5) / .3)), rot=-3)
        return post(img, G1, G2, vig=1.0, seed=fi, redpulse=p * .7, tint=(1, .95, 1.05))
    u = t - 3.2; z = lerp(1.0, 1.25, u / 3.8)
    sx, sy = shake_off(p * 3, fi)
    img, w2s = cam_view(540, lerp(1550, 1380, u / 3.8), z, sx, sy)
    img = fog(img, t, .35, (70, 90, 140))
    embers(G2, t, 50, (255, 140, 50), 4, 40)
    img = ui(img, t, .6 + 2.5 * clamp((t - 4) / 3)) or img
    ui_img = img
    caption(img, t, 4.1, 6.8, 'Phir bhi... kuch cards\ndil ki dhadkan\nrok dete hain.', 560, 82, (255, 255, 255))
    f = clamp(u / .9) * clamp((6.95 - t) / .2)
    return post(img, G1, G2, tint=(.78, .88, 1.15), sat=.8, con=1.15, bright=.78, vig=.9, seed=fi, redpulse=p * .6 * clamp((t - 4) / 2), fade=f)

def tower_pos(w2s, which):
    return w2s(*{'king': (540, 2090), 'pr': (860, 1800)}[which])

def scene_sparky(t, fi):
    u = t - SPARKY_START; p = pulse_at(t); c = clamp((t - 7.8) / (ZAP - 7.8)) ** 1.5
    after = t - ZAP
    amp = c * 9 + impact(t, [ZAP], .22) * 46
    sx, sy = shake_off(amp, fi)
    img, w2s = cam_view(540, 1450, 1.15, sx, sy)
    img = fog(img, t, .4, (60, 70, 110))
    lay, G1, G2 = new_layers(); d = ImageDraw.Draw(lay)
    ap = sstep(u / 3.3); s = lerp(88, 170, ap); gy = lerp(960, 1270, ap); sxp = lerp(500, 400, ap)
    radial(G1, sxp, gy - 3.0 * s, s * (1.6 + 1.2 * c), (60, 48, 6))
    tx, ty = tower_pos(w2s, 'king')
    pre = 10.42 < t < ZAP
    orb = sparky(d, G1, G2, sxp + sx * .3, gy + sy * .3, s, c if after < 0.55 else max(.4, 1 - after), t)
    img = comp(img, lay); dd = ImageDraw.Draw(img)
    if after >= 0 and after < .55:
        rr = np.random.default_rng(fi)
        wp = (orb[0] + 480, orb[1] + 60)
        draw_bolt(img, G1, G2, orb, wp, rr, 8, jag=60, branches=1); draw_bolt(img, G1, G2, wp, (tx, ty - 60), rr, 12, jag=80, branches=5)
        radial(G1, tx, ty - 40, 520 * clamp(1 - after / .6), (230, 190, 70))
    if after >= 0:
        for k in range(3): ring(G2, tx, ty + 60, (after * 1500 - k * 140) % 1500 if after * 1500 - k * 140 > 0 else 0, 14, (255, 220, 120)) if after < .9 else None
        radial(G1, tx, ty, 200 + 80 * math.sin(t * 40), (200, 70, 10)) if after < 3 else None
        smoke(img, t, tx, ty, ZAP + .3, 16, 2)
    embers(G2, t, 60, (255, 215, 90), 5, 50)
    dim = .45 if pre else 1.0
    fl = clamp(1 - after / .45) ** 2 if after >= 0 else 0
    slam(img, t, 8.0, 12.9, 'SPARKY', 300, 270, (255, 214, 64))
    caption(img, t, 8.9, 10.35, 'Dekho... charge ho raha hai...', 1560, 62, (255, 240, 200))
    caption(img, t, 11.0, 12.8, 'Ek shot. Sab khatam.', 1520, 100, (255, 255, 255))
    return post(img, G1, G2, tint=(1.0, .95, 1.08) if after < 0 else (1.05, .95, .9), sat=.95, con=1.2, bright=dim * .75, vig=.95, flash=fl, flashcol=(1, .96, .8), ca=int(amp * .25), glitch=clamp(1 - after / .5) if 0 <= after < .5 else 0, seed=fi, redpulse=p * .3)

def scene_musk(t, fi):
    u = t - MUSK_START; p = pulse_at(t)
    amp = impact(t, SHOTS, .2) * 30 + 3
    sx, sy = shake_off(amp, fi)
    img, w2s = cam_view(700, 1500, 1.2, sx, sy)
    img = fog(img, t, .4, (90, 50, 110))
    lay, G1, G2 = new_layers(); d = ImageDraw.Draw(lay)
    ap = sstep(u / 3.8); k = lerp(.8, 1.15, ap) if u < 3.8 else 1.15 + .0 * (u - 3.8)
    aim = 1.0 if t > 16.4 else 0.0
    gy = lerp(820, 1100, ap); s = 128 * k
    bob = abs(math.sin(math.pi * u / .5)) * .12 if u < 3.4 else 0
    pr = tower_pos(w2s, 'pr'); pos = [(-330, 30), (0, 80), (330, 30)] ; tips = []
    radial(G1, W / 2, gy - 1.5 * s, 560, (46, 12, 40))
    for i, (ox, oy) in enumerate(sorted(pos, key=lambda p: p[1])):
        pass
    order = sorted(range(3), key=lambda i: pos[i][1])
    for i in order:
        ox, oy = pos[i]; tip = musketeer(d, G2, W / 2 + ox * k + sx * .3, gy + oy * k, s, t, aim, bob, i); tips.append((i, tip))
    img = comp(img, lay); rr = np.random.default_rng(fi)
    d2 = ImageDraw.Draw(img)
    for i, tip in tips:
        ts = SHOTS[[0, 2, 1][i]] if False else SHOTS[i]
        dt = t - ts
        if 0 <= dt < .12:
            fx, fy = tip; 
            pts = []
            for a in range(10): ang = a * 0.628 + rr.random() * .4; L = (110 if a % 2 == 0 else 45) * (1 - dt / .12); pts.append((fx + math.cos(ang) * L, fy + math.sin(ang) * L))
            d2.polygon(pts, fill=(255, 230, 130)); radial(G1, fx, fy, 240, (150, 50, 110)); radial(G2, fx, fy, 160, (255, 230, 140))
            d2.line([tip, (pr[0], pr[1] - 40)], fill=(255, 240, 200), width=5); ImageDraw.Draw(G2).line([(tip[0] / 2, tip[1] / 2), (pr[0] / 2, (pr[1] - 40) / 2)], fill=(255, 150, 90), width=8)
        if 0.05 <= dt < .5:
            for _ in range(12):
                a = rr.uniform(0, 6.28); L = rr.uniform(30, 160) * (dt / .5 + .3); d2.line([(pr[0], pr[1] - 40), (pr[0] + math.cos(a) * L, pr[1] - 40 + math.sin(a) * L)], fill=(255, 220, 120), width=4)
            radial(G1, pr[0], pr[1] - 40, 260 * (1 - dt / .5), (200, 110, 40))
    if t > SHOTS[0]: smoke(img, t, pr[0], pr[1], SHOTS[0] + .1, 12, 3, 110)
    embers(G2, t, 50, (255, 110, 200), 6, 40)
    slam(img, t, 13.7, 18.3, '3 MUSKETEERS', 300, 128, (255, 98, 200))
    caption(img, t, 14.7, 16.3, 'Teen nishane. Ek saath.', 1540, 84, (255, 230, 250))
    caption(img, t, 17.45, 18.4, 'Bachne ka rasta nahi.', 1540, 84, (255, 255, 255))
    fl = max([clamp(1 - (t - s0) / .12) for s0 in SHOTS if t >= s0] + [0]) * .45
    return post(img, G1, G2, tint=(1.12, .86, 1.12), sat=.95, con=1.22, bright=.8, vig=.95, flash=fl, flashcol=(1, .8, .9), ca=int(amp * .2), seed=fi, redpulse=p * .4)

def golem_state(t):
    prog = sum(sstep((t - ts) / .4) for ts in STOMPS) / len(STOMPS)
    return prog
def scene_golem(t, fi):
    u = t - GOLEM_START; p = pulse_at(t); prog = golem_state(t)
    amp = impact(t, STOMPS, .3, [1, 1, 1.1, 1.2, 1.3, 2.2]) * 22
    sx, sy = shake_off(amp, fi)
    img, w2s = cam_view(540, 1400, 1.2, sx, sy)
    img = fog(img, t, .45, (110, 70, 50), 18)
    lay, G1, G2 = new_layers(); d = ImageDraw.Draw(lay)
    s = lerp(62, 160, prog); gy = lerp(850, 1400, prog) + sy * .3
    eye = clamp(.35 + prog * .6 + impact(t, STOMPS[-1:], .5) * .5)
    sway = math.sin(t * 2.4) * .04
    radial(G1, W / 2, gy - 2.5 * s, s * 3.4, (56, 22, 4)); radial(G1, W / 2, gy, s * 2.6, (60, 24, 4))
    golem(d, G2, W / 2 + sx * .3, gy, s, t, eye, sway)
    img = comp(img, lay)
    for ts in STOMPS:
        dt = t - ts
        if 0 <= dt < 1.1:
            ring(G2, W / 2, gy + 20, dt * 1700, 24 * (1 - dt), (255, 170, 80))
            dl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(dl); r = np.random.default_rng(int(ts * 10))
            for j in range(14):
                a = r.uniform(0, 6.28); L = dt * r.uniform(300, 800); rad = 30 + dt * 90
                cx, cy = W / 2 + math.cos(a) * L, gy + 10 + math.sin(a) * L * .35 - dt * 40
                dd.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=(140, 110, 90, int(150 * (1 - dt / 1.1))))
            dl = dl.filter(ImageFilter.GaussianBlur(14)); img.paste(dl, (0, 0), dl)
    embers(G2, t, 70, (255, 120, 30), 7, 55)
    slam(img, t, 19.3, 24.3, 'GOLEM', 300, 290, (255, 150, 44))
    caption(img, t, 20.3, 22.3, 'Dheere chalta hai...', 1560, 90, (255, 235, 210))
    caption(img, t, 22.5, 24.3, 'par rukta nahi.', 1560, 100, (255, 255, 255))
    fl = clamp(1 - (t - STOMPS[-1]) / .18) * .45 if t >= STOMPS[-1] else 0
    return post(img, G1, G2, tint=(1.08, .94, .86), sat=.95, con=1.25, bright=.82, vig=1.0, flash=fl, flashcol=(1, .85, .6), ca=int(amp * .15), seed=fi, redpulse=p * .5)

_sk = np.random.default_rng(21)
SK = [(float(_sk.uniform(-120, 1200)), float(_sk.uniform(0, 3.6)), float(_sk.uniform(.8, 1.25)), float(_sk.uniform(0, 6))) for _ in range(120)]
def scene_skel(t, fi):
    u = t - SKEL_START; p = pulse_at(t)
    amp = 4 + 10 * clamp(u / 5)
    sx, sy = shake_off(amp, fi)
    img, w2s = cam_view(540, 1400, 1.2, sx, sy)
    img = fog(img, t, .5, (50, 110, 80), 30)
    lay, G1, G2 = new_layers(); d = ImageDraw.Draw(lay)
    radial(G1, W / 2, 1100, 850, (6, 38, 18))
    items = []
    for (x0, dl, sp, ph) in SK:
        y = -120 + (u - dl) * 430 * sp
        if y < -150 or y > 2300: continue
        items.append((y, x0, sp, ph))
    for y, x0, sp, ph in sorted(items):
        s = 34 + 118 * clamp((y + 100) / 2200) ** 1.15
        x = x0 + (x0 - W / 2) * .12 * (y / 900)
        skeleton(d, G2, x + sx * .3, y + sy * .3, s, t, ph)
    img = comp(img, lay)
    embers(G2, t, 60, (120, 255, 170), 8, 40)
    slam(img, t, 25.3, 29.8, 'SKELETON\nARMY', 330, 190, (226, 255, 206))
    caption(img, t, 26.5, 28.2, 'Gino... gino...', 1580, 100, (255, 255, 255))
    caption(img, t, 28.4, 29.85, 'ginte reh jaoge.', 1580, 100, (190, 255, 210))
    return post(img, G1, G2, tint=(.85, 1.1, .95), sat=.9, con=1.2, bright=.8, vig=1.0, ca=int(amp * .12), seed=fi, redpulse=p * .3)

def scene_mont(t, fi):
    k = max(i for i, c in enumerate(MONT_CUTS) if t >= c); kind = MONT[k]; lt = t - MONT_CUTS[k]; p = pulse_at(t)
    zoom = 1.0 + .22 * (1 - sstep(lt / .45))
    sx, sy = shake_off(14 * math.exp(-lt * 8), fi)
    cy = [1450, 1400, 1450, 1400][k % 4]
    img, w2s = cam_view(540 + (k % 3 - 1) * 90, cy, 1.15 + .1 * (k % 2), sx, sy)
    img = fog(img, t, .45, (70, 50, 90), 30)
    lay, G1, G2 = new_layers(); d = ImageDraw.Draw(lay)
    glow = {'spark': (110, 90, 10), 'musk': (100, 25, 80), 'golem': (110, 45, 8), 'skel': (12, 80, 40), 'all': (120, 10, 20)}[kind]
    radial(G1, W / 2, 900, 760, tuple(int(c * .45) for c in glow))
    name, col = {'spark': ('SPARKY', (255, 214, 64)), 'musk': ('3 MUSKETEERS', (255, 98, 200)), 'golem': ('GOLEM', (255, 150, 44)), 'skel': ('SKELETON ARMY', (226, 255, 206)), 'all': ('DAR LAGTA HAI?', (255, 70, 80))}[kind]
    sc = zoom
    if kind == 'spark': sparky(d, G1, G2, W / 2, 1330, 215 * sc, 1.0, t)
    elif kind == 'musk':
        for ox, oy in [(-340, 40), (340, 40), (0, 110)]: musketeer(d, G2, W / 2 + ox * sc, 1250 + oy, 200 * sc, t, 0, 0, 0)
    elif kind == 'golem': golem(d, G2, W / 2, 1450, 190 * sc, t, 1.0, 0)
    elif kind == 'skel':
        for i in range(30):
            r = np.random.default_rng(i); y = 700 + r.random() * 900; s = 60 + (y - 600) * .17
            skeleton(d, G2, r.random() * W, y, s * sc, t, i)
    else:
        sparky(d, G1, G2, 200, 1300, 90, .8, t); golem(d, G2, 880, 1300, 70, t, 1.0); musketeer(d, G2, 440, 1290, 80, t); skeleton(d, G2, 640, 1290, 90, t, 1)
    img = comp(img, lay)
    text_sz = 150 if kind in ('musk', 'skel') else (230 if kind != 'all' else 130)
    text(img, name if kind != 'skel' else 'SKELETON\nARMY', W / 2 + np.random.normal(0, 4), 1580 if kind != 'all' else 1000, (text_sz if kind != 'musk' else 120) if kind != 'skel' else 150, col, alpha=1, scale=1 + .5 * max(0, 1 - lt / .1), rot=-3)
    if kind == 'all' and lt > .1:
        text(img, 'DAR.', W / 2, 330, 300, (255, 255, 255), alpha=clamp(lt * 3), rot=-3)
    fl = clamp(1 - lt / .1) * .5
    if kind == 'all' and t > 33.85: fl = clamp((t - 33.85) / .12)
    return post(img, G1, G2, tint=(1.05, .95, 1.0), sat=1.0, con=1.3, bright=.85, vig=1.0, flash=fl, ca=int(8 * math.exp(-lt * 8)) + 2, glitch=.7 * math.exp(-lt * 12), seed=fi, redpulse=p * .8)

def scene_end(t, fi):
    G1 = Image.new('RGB', (W // 2, H // 2)); G2 = G1.copy(); img = Image.new('RGB', (W, H), (3, 2, 7))
    p = pulse_at(t); embers(G2, t, 40, (150, 60, 60), 9, 25)
    radial(G1, W / 2, 900, 900 * (.8 + .2 * p), (30, 5, 10 + int(10 * p)))
    text(img, 'CLASH ROYALE', W / 2, 560, 130, (255, 205, 70), alpha=clamp((t - 34.4) / .5) * clamp((39.2 - t) / .3), rot=-3)
    text(img, 'DAR KA NAAM', W / 2, 700, 70, (255, 255, 255), alpha=clamp((t - 34.8) / .5) * clamp((39.2 - t) / .3), rot=-3)
    caption(img, t, 36.0, 39.3, 'Tumhe sabse zyada\nkaunsa card\ndarata hai?', 1100, 96, (255, 255, 255))
    caption(img, t, 37.2, 39.3, 'COMMENT KARO', 1450, 70, (255, 120, 90), rot=-2)
    if t > 37.0: text(img, 'Fan-made tribute  -  not affiliated with Supercell', W / 2, 1810, 30, (150, 140, 170), sw=2, shadow=False, rot=0, alpha=clamp((t - 37) / .6))
    return post(img, G1, G2, vig=1.0, seed=fi, redpulse=p * .5, fade=clamp((DUR - t) / .4))

def render(fi):
    t = fi / FPS
    if t < 7.0: im = scene_intro(t, fi)
    elif t < 7.3: im = Image.new('RGB', (W, H), (0, 0, 0))
    elif t < MUSK_START: im = scene_sparky(t, fi)
    elif t < GOLEM_START: im = scene_musk(t, fi)
    elif t < SKEL_START: im = scene_golem(t, fi)
    elif t < MONT_START: im = scene_skel(t, fi)
    elif t < END: im = scene_mont(t, fi)
    else: im = scene_end(t, fi)
    im.save(f'{OUT}/f{fi:05d}.jpg', quality=92)
    return fi

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        for tm in [float(x) for x in sys.argv[2:]]: render(int(tm * FPS))
    else:
        with Pool(4) as pool:
            for i, _ in enumerate(pool.imap_unordered(render, range(NF), chunksize=6)):
                if i % 100 == 0: print(i, flush=True)
