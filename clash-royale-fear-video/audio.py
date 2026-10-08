import numpy as np, wave
from timeline import *
SR = 44100
N = int(SR * DUR)
rng = np.random.default_rng(7)
dry = np.zeros((2, N)); send = np.zeros((2, N))

def tt(d): return np.arange(int(d * SR)) / SR
def put(buf, t0, sig, g=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N or i < 0: return
    j = min(N, i + len(sig)); seg = sig[:j - i]
    a = (pan + 1) * np.pi / 4
    buf[0, i:j] += seg * g * np.cos(a); buf[1, i:j] += seg * g * np.sin(a)
def noise(d): return rng.standard_normal(int(d * SR))
def filt(x, lo=None, hi=None, n=4):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR) + 1e-9
    if lo: X *= 1 / np.sqrt(1 + (f / lo) ** (2 * n))
    if hi: X *= 1 / np.sqrt(1 + (hi / f) ** (2 * n))
    return np.fft.irfft(X, len(x))
def decay(d, k, a=0.003):
    t = tt(d); return np.minimum(t / a, 1) * np.exp(-t * k)
def sweep(f0, f1, d, exp=True):
    t = tt(d); u = t / d
    f = f0 * (f1 / f0) ** u if exp else f0 + (f1 - f0) * u
    return np.sin(2 * np.pi * np.cumsum(f) / SR)
def norm(x): return x / (np.max(np.abs(x)) + 1e-9)
def saw(f, d, vib=0.0):
    t = tt(d); ph = f * t + vib * np.sin(2 * np.pi * 5.2 * t) / 5.2 * 0.02 * f
    return 2 * (ph % 1) - 1
def boom(d=3.0, f0=120, f1=30, nz=0.5, k=1.6):
    s = sweep(f0, f1, d) * decay(d, k) + 0.4 * sweep(f0 * 2, f1 * 1.5, d) * decay(d, k * 2)
    n = filt(noise(d), lo=260) * decay(d, k * 2.2) * nz
    c = filt(noise(0.05), hi=800) * decay(0.05, 60) * 0.6
    x = s + n; x[:len(c)] += c
    return norm(x)
def lub(t0, g=1.0):
    put(dry, t0, norm(sweep(95, 42, 0.35) * decay(0.35, 11)), 0.9 * g)
    put(dry, t0 + 0.2, norm(sweep(80, 38, 0.3) * decay(0.3, 13)), 0.6 * g)
def ramp(t, pts): return np.interp(t, [p[0] for p in pts], [p[1] for p in pts])
def pad(t0, t1, notes, fc, g0, g1, trem=0, wave_='saw', fade=0.5, pan=0.0):
    d = t1 - t0; t = tt(d); x = np.zeros_like(t)
    for f in notes:
        for cents in (-7, 0, 7):
            ff = f * 2 ** (cents / 1200)
            x += saw(ff, d, 1) if wave_ == 'saw' else np.sin(2 * np.pi * ff * t)
    x = filt(x, lo=fc, hi=30)
    if trem: x *= 0.65 + 0.35 * np.sin(2 * np.pi * trem * t)
    env = np.interp(t, [0, d], [g0, g1]) * np.minimum(np.minimum(t / fade, (d - t) / fade), 1)
    x = norm(x) * env
    put(dry, t0, x, 1, pan); put(send, t0, x, 0.5, pan)
def choir(f, d, g=0.2, t0=0):
    t = tt(d); x = np.zeros_like(t)
    vib = 1 + 0.006 * np.sin(2 * np.pi * 5.5 * t + rng.random() * 6)
    for h in range(1, 24):
        fr = f * h; amp = np.exp(-((fr - 750) / 380) ** 2) + 0.7 * np.exp(-((fr - 1150) / 450) ** 2) + 0.25 / h
        x += amp * np.sin(2 * np.pi * fr * t * vib + h)
    x = norm(x) * np.minimum(np.minimum(t / 0.8, (d - t) / 0.8), 1) * g
    put(dry, t0, x, 1, rng.uniform(-.5, .5)); put(send, t0, x, 0.9)

# ---------------- 0-7: dread
n = filt(noise(7.2), lo=1100, hi=250); put(dry, 0, n * np.interp(tt(7.2), [0, 3, 7.2], [0.05, 0.25, 0.1]) / n.std() * 0.1)
pad(0, 7.0, [55, 82.4, 110], 380, 0, 0.30, fade=1.5)
pad(3.2, 7.0, [130.8, 164.8], 900, 0, 0.14, trem=0.25, fade=1.0)
for tk in (4.0, 5.0, 6.0):   # overtime clock ticks
    tick = norm(sweep(1900, 1500, 0.06) * decay(0.06, 70)); put(dry, tk, tick, 0.18); put(send, tk, tick, 0.2)
for b in beats(): lub(b, g=0.55 if b < 7 else 1.0)
put(send, 6.0, noise(1.0) * 0 + norm(filt(noise(1.0), lo=2500, hi=300) * np.linspace(0, 1, SR) ** 2), 0.15)
# ---------------- SPARKY
put(dry, 7.3, boom(4, 90, 25), 0.9); put(send, 7.3, boom(4, 90, 25), 0.5)
pad(7.3, 13.0, [55, 58.3, 116.5, 164.8], 1300, 0.12, 0.3, fade=0.4)
w = 3.3; t = tt(w); u = t / w
f = 180 * (3200 / 180) ** (u ** 1.3)
whine = np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.1 + 0.9 * u) * (0.7 + 0.3 * np.sin(2 * np.pi * (6 + 22 * u) * t))
put(dry, 7.3, whine, 0.30, -0.2); put(send, 7.3, whine, 0.3)
for k in range(int(w * 40)):  # crackle
    ti = 7.3 + rng.random() ** 0.6 * w
    c = filt(noise(0.03), hi=2500) * decay(0.03, 120); put(dry, ti, norm(c), 0.1 + 0.25 * (ti - 7.3) / w, rng.uniform(-1, 1))
put(dry, 8.0, boom(2.5, 140, 38, 0.8), 0.6)
put(dry, 10.45, np.zeros(1), 0)
# zap
z = filt(noise(1.6), hi=1500) * decay(1.6, 3.2, 0.001); z = norm(z)
buzz = norm(saw(110, 1.6) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 50 * tt(1.6)))) * decay(1.6, 2.4, 0.001))
put(dry, 10.6, z, 0.95); put(dry, 10.6, buzz, 0.55); put(send, 10.6, z, 0.9)
put(dry, 10.6, boom(5, 150, 24, 0.9, 1.0), 1.0); put(send, 10.6, boom(5, 150, 24, 0.9, 1.0), 0.8)
put(dry, 10.6, norm(filt(noise(2.0), lo=500) * decay(2.0, 2.0)), 0.5)
# ---------------- 3 MUSKETEERS
put(dry, 13.0, boom(3, 100, 28), 0.8); put(send, 13.0, boom(3, 100, 28), 0.5)
pad(13.0, 18.5, [110, 164.8, 220, 261.6], 1900, 0.1, 0.28, trem=3, fade=0.4)
for k in range(8):
    tm = 13.0 + 0.5 * k + 0.5 * 0
    if tm > 16.7: break
    acc = 1.0 if k % 2 == 0 else 0.7
    b = boom(0.8, 110, 45, 0.3, 4.5); put(dry, tm, b, 0.55 * acc * (0.6 + k * 0.08)); put(send, tm, b, 0.3)
    step = norm(filt(noise(0.12), lo=1800, hi=400) * decay(0.12, 28)); put(dry, tm + 0.02, step, 0.2)
tm = 15.4
while tm < 16.75:  # snare roll
    sn = norm(filt(noise(0.12), hi=1400) * decay(0.12, 26)); put(dry, tm, sn, 0.2 + 0.4 * (tm - 15.4) / 1.35, rng.uniform(-.4, .4)); put(send, tm, sn, 0.2)
    tm += 0.16 - 0.1 * (tm - 15.4) / 1.35
for i, ts in enumerate(SHOTS):
    g = filt(noise(1.2), lo=7000) * decay(1.2, 5, 0.0008); g = norm(g)
    th = norm(sweep(220, 55, 0.5) * decay(0.5, 9)); crack = norm(filt(noise(0.04), hi=3000) * decay(0.04, 90))
    pn = [-0.7, 0.0, 0.7][i]
    put(dry, ts, g, 0.9, pn); put(dry, ts, th, 0.8, pn); put(dry, ts, crack, 0.8, pn)
    put(send, ts, g, 1.0, pn); put(send, ts + 0.12, norm(filt(noise(.6), lo=2500) * decay(.6, 6)), .4)  # impact
    put(dry, ts + 0.1, boom(1.5, 90, 35, .6, 3), 0.55)
# ---------------- GOLEM
put(dry, 18.5, boom(3.5, 90, 25), 0.8)
pad(18.5, 24.5, [43.65, 87.3, 130.8, 65.4], 650, 0.15, 0.4, fade=0.8)
choir(87.3 * 2, 5.4, 0.16, 18.8); choir(130.8, 5.0, 0.12, 19.0)
for k, ts in enumerate(STOMPS):
    big = 1.0 if k < 5 else 1.5
    b = boom(3.0 if k < 5 else 5.0, 85, 24, 0.9, 1.5 if k < 5 else 0.9)
    put(dry, ts, b, 0.85 * big); put(send, ts, b, 0.7 * big)
    rock = norm(filt(noise(1.1), lo=1600, hi=120) * decay(1.1, 4)); put(dry, ts + 0.02, rock, 0.5 * big)
    put(dry, ts + 0.15, norm(filt(noise(0.7), lo=3000, hi=900) * decay(0.7, 7) * (rng.random(int(.7 * SR)) > .85)), 0.25)
# ---------------- SKELETON ARMY
put(dry, 24.5, boom(3, 70, 30), 0.7)
pad(24.5, 30.0, [440, 466.2, 659.3, 698.5], 3500, 0.0, 0.2, trem=7.5, wave_='sine', fade=0.4)
pad(24.5, 30.0, [55, 58.3], 500, 0.1, 0.3, fade=0.5)
choir(220, 5.5, 0.14, 24.6); choir(233.1, 5.3, 0.1, 24.7); choir(329.6, 5.0, 0.1, 25.0)
tclk = 24.5
while tclk < 29.9:
    dens = np.interp(tclk, [24.5, 29.9], [7, 90])
    f0 = rng.uniform(700, 1900)
    tok = norm(sweep(f0, f0 * .6, 0.03) * decay(0.03, 110) + 0.5 * filt(noise(0.03), hi=2500) * decay(0.03, 160))
    put(dry, tclk, tok, rng.uniform(.1, .35) * (0.5 + tclk / 60), rng.uniform(-1, 1)); put(send, tclk, tok, .25, rng.uniform(-1, 1))
    tclk += rng.exponential(1 / dens)
put(dry, 24.5, norm(filt(noise(5.4), lo=700, hi=100) * np.linspace(.1, 1, int(5.4 * SR)) ** 1.5), 0.35)
for ts in (26.0, 27.5, 28.8, 29.4):  # marching boom
    put(dry, ts, boom(1.5, 80, 28, .5, 2.5), 0.6)
# ---------------- MONTAGE
for k, ts in enumerate(MONT_CUTS):
    hit = boom(1.6, 130, 30, 0.7, 2.2); put(dry, ts, hit, 0.9); put(send, ts, hit, 0.5)
    put(dry, ts, norm(filt(noise(0.2), hi=700) * decay(0.2, 18, .001)), 0.5)
    rs = norm(filt(noise(.5), lo=4000, hi=500) * np.linspace(0, 1, int(.5 * SR)) ** 2); put(dry, ts, rs, .15)
pad(30.0, 34.0, [110, 164.8, 220, 329.6], 2600, 0.25, 0.4, trem=4, fade=0.2)
pad(30.0, 34.0, [87.3, 130.8, 174.6], 1500, 0.2, 0.3, fade=0.2)
choir(220, 4, 0.2, 30.0); choir(329.6, 4, 0.2, 30.0); choir(440, 4, 0.16, 30.0)
tr = filt(noise(4), lo=9000, hi=2500) * np.linspace(0, 1, 4 * SR) ** 2.5; put(dry, 30.0, norm(tr), 0.25)
final = boom(7, 150, 20, 1, 0.7); put(dry, 33.5, final, 1.1); put(send, 33.5, final, 1.0)
put(dry, 33.5, norm(filt(noise(1.6), hi=1000) * decay(1.6, 2.5, .001)), .7)
# ---------------- END: silence, heartbeat, question
pad(34.6, 39.5, [110, 165, 220, 247.5], 1400, 0.0, 0.12, wave_='sine', fade=1.2)
put(send, 36.0, norm(sweep(1318.5, 1318.5, 3) * decay(3, 1.4, .002)), .08); put(send, 36.4, norm(sweep(1568, 1568, 3) * decay(3, 1.6, .002)), .06)
put(dry, 36.0, norm(sweep(55, 55, 3.4) * decay(3.4, 1.0)), 0.5)

# ---------------- master
Nfft = 1 << 21
ir = filt(noise(3.0), lo=5500, hi=150) * np.exp(-tt(3.0) / 0.85); ir[:int(.02 * SR)] *= 0.2
irf = np.fft.rfft(ir, Nfft)
wet = np.stack([np.fft.irfft(np.fft.rfft(send[c], Nfft) * irf, Nfft)[:N] for c in range(2)])
wet = np.roll(wet[::-1], 0, axis=0)
mix = dry + wet * 0.0016 * 1.0 * (1 / ir.std() / 100 * 6)
# duck: dramatic silence breaks
duck = np.ones(N); t_all = np.arange(N) / SR
def dip(a, b, depth): 
    m = (t_all > a) & (t_all < b); duck[m] = np.minimum(duck[m], depth)
dip(6.93, 7.3, 0.0); dip(10.5, 10.6, 0.05); dip(34.0, 34.6, 0.12)
mix *= duck
mix = np.tanh(mix * 1.15) / np.tanh(1.15)
for c in range(2): mix[c] = filt(mix[c], hi=25, n=2)
mix = mix / np.max(np.abs(mix)) * 0.89
fo = np.minimum(1, (DUR - t_all) / 1.5); mix *= fo
wv = wave.open('audio.wav', 'wb'); wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(SR)
wv.writeframes((mix.T * 32767).astype('<i2').tobytes()); wv.close()
print('rms', float(np.sqrt((mix ** 2).mean())), 'peak', float(np.abs(mix).max()))
