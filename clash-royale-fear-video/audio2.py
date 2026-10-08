import numpy as np, wave, subprocess
from tl2 import *
SR = 44100; N = int(SR * DUR); rng = np.random.default_rng(7)
A = '/home/user/royaleapi/cr-api-assets/'
dry = np.zeros((2, N)); send = np.zeros((2, N))
def tt(d): return np.arange(int(d * SR)) / SR
def put(buf, t0, sig, g=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N or i < 0 or len(sig) == 0: return
    j = min(N, i + len(sig)); seg = sig[:j - i]; a = (pan + 1) * np.pi / 4
    buf[0, i:j] += seg * g * np.cos(a); buf[1, i:j] += seg * g * np.sin(a)
def noise(d): return rng.standard_normal(int(d * SR))
def filt(x, lo=None, hi=None, n=4):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR) + 1e-9
    if lo: X *= 1 / np.sqrt(1 + (f / lo) ** (2 * n))
    if hi: X *= 1 / np.sqrt(1 + (hi / f) ** (2 * n))
    return np.fft.irfft(X, len(x))
def decay(d, k, a=0.003): t = tt(d); return np.minimum(t / a, 1) * np.exp(-t * k)
def sweep(f0, f1, d):
    t = tt(d); f = f0 * (f1 / f0) ** (t / d); return np.sin(2 * np.pi * np.cumsum(f) / SR)
def norm(x): return x / (np.max(np.abs(x)) + 1e-9)
def saw(f, d, vib=0.0): t = tt(d); return 2 * ((f * t + vib * np.sin(2 * np.pi * 5.2 * t) / 5.2 * .02 * f) % 1) - 1
def boom(d=3.0, f0=120, f1=30, nz=.5, k=1.6):
    x = sweep(f0, f1, d) * decay(d, k) + .4 * sweep(f0 * 2, f1 * 1.5, d) * decay(d, k * 2) + filt(noise(d), lo=260) * decay(d, k * 2.2) * nz
    c = filt(noise(.05), hi=800) * decay(.05, 60) * .6; x[:len(c)] += c; return norm(x)
def lub(t0, g=1.0):
    put(dry, t0, norm(sweep(95, 42, .35) * decay(.35, 11)), .9 * g); put(dry, t0 + .2, norm(sweep(80, 38, .3) * decay(.3, 13)), .6 * g)
def pad(t0, t1, notes, fc, g0, g1, trem=0, wave_='saw', fade=.5):
    d = t1 - t0; t = tt(d); x = np.zeros_like(t)
    for f in notes:
        for cents in (-7, 0, 7):
            ff = f * 2 ** (cents / 1200); x += saw(ff, d, 1) if wave_ == 'saw' else np.sin(2 * np.pi * ff * t)
    x = filt(x, lo=fc, hi=30)
    if trem: x *= .65 + .35 * np.sin(2 * np.pi * trem * t)
    x = norm(x) * np.interp(t, [0, d], [g0, g1]) * np.minimum(np.minimum(t / fade, (d - t) / fade), 1); put(dry, t0, x); put(send, t0, x, .5)
def choir(f, d, g=.2, t0=0):
    t = tt(d); x = np.zeros_like(t); vib = 1 + .006 * np.sin(2 * np.pi * 5.5 * t + rng.random() * 6)
    for h in range(1, 24):
        fr = f * h; amp = np.exp(-((fr - 750) / 380) ** 2) + .7 * np.exp(-((fr - 1150) / 450) ** 2) + .25 / h; x += amp * np.sin(2 * np.pi * fr * t * vib + h)
    x = norm(x) * np.minimum(np.minimum(t / .8, (d - t) / .8), 1) * g; put(dry, t0, x, 1, rng.uniform(-.5, .5)); put(send, t0, x, .9)

# ---------- real in-game sound effects (official assets)
_cache = {}
def sfx(name, folder='sfx'):
    if name not in _cache:
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f'{A}{folder}/{name}.ogg', '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout
        x = np.frombuffer(raw, np.float32).astype(np.float64); _cache[name] = x / (np.abs(x).max() + 1e-9)
    return _cache[name]
def pitch(x, r): return np.interp(np.arange(0, len(x) - 1, r), np.arange(len(x)), x)
def real(name, t0, g=1.0, pan=0.0, rate=1.0, wet=.25, folder='sfx', dur=None):
    x = sfx(name, folder); x = pitch(x, rate) if rate != 1 else x
    if dur: x = x[:int(dur * SR)] * np.minimum(1, (len(x[:int(dur * SR)]) - np.arange(len(x[:int(dur * SR)]))) / (.05 * SR))
    put(dry, t0, x, g, pan); put(send, t0, x, wet, pan)

# =============== 0-4.2 HOOK
put(dry, 0, filt(noise(4.5), lo=1100, hi=250) * np.interp(tt(4.5), [0, 2, 4.5], [.05, .25, .1]) / .5 * .1)
pad(0, 4.4, [55, 82.4, 110], 380, 0, .3, fade=1.2); pad(1.8, 4.3, [130.8, 164.8], 900, 0, .14, trem=.25, fade=.6)
put(dry, 0.0, boom(2.5, 130, 34, .8, 2.0), .95); put(send, 0.0, boom(2.5, 130, 34, .8, 2.0), .6)
put(dry, 0.3, norm(filt(noise(3.9), lo=6000, hi=700) * np.linspace(0, 1, int(3.9 * SR)) ** 2.2), .28)
for i in range(4):
    ts = 2.1 + .35 * i
    real('card_fly_in_06', ts - .05, .6, [-.6, -.2, .2, .6][i]); put(dry, ts, boom(1.2, 110, 40, .5, 3), .55); real('tex_whoosh_02', ts - .15, .35)
real('text_whoosh_in_03', 0.0, .5); real('text_whoosh_in_03', 2.0, .5)
for b in beats(): lub(b, g=.55 if b < 4.2 else 1.0)
# =============== SPARKY (4.5)
def sc_open(t0, g=1.0): put(dry, t0, boom(3.5, 100, 24, .9, 1.4), .95 * g); put(send, t0, boom(3.5, 100, 24, .9, 1.4), .6); real('text_whoosh_in_03', t0 + .75, .5)
sc_open(T_SPARKY); real('new_leg_reveal_01', T_SPARKY, .45, wet=.5)
pad(T_SPARKY, T_MUSK, [55, 58.3, 116.5, 164.8], 1300, .12, .3, fade=.4)
t0c = T_SPARKY + 1.3; w = ZAP - t0c; u = tt(w) / w
whine = np.sin(2 * np.pi * np.cumsum(180 * (3200 / 180) ** (u ** 1.3)) / SR) * (.1 + .9 * u); put(dry, t0c, whine, .16); put(send, t0c, whine, .2)
real('zap_machine_charge_06', t0c, .9, wet=.35); real('zap_machine_charge_06', t0c + 1.3, .9, rate=1.12, wet=.35)
for k in range(int((ZAP - t0c) / .88) + 1): real('zap_machine_run_loop_04', t0c + .2 + k * .88, .3 + .5 * k / 3, dur=.9)
for k in range(int(w * 40)):
    ti = t0c + rng.random() ** .6 * w; put(dry, ti, norm(filt(noise(.03), hi=2500) * decay(.03, 120)), .08 + .22 * (ti - t0c) / w, rng.uniform(-1, 1))
real('zap_discarge_03', ZAP, 1.0, wet=.5); real('tesla_zap_01', ZAP, .9, wet=.4); real('lightning_02', ZAP + .02, .8, wet=.5)
put(dry, ZAP, boom(5, 150, 24, .9, 1.0), 1.0); put(send, ZAP, boom(5, 150, 24, .9, 1.0), .8)
put(dry, ZAP, norm(filt(noise(1.6), hi=1500) * decay(1.6, 3.2, .001)), .7)
# =============== THREE MUSKETEERS (10)
sc_open(T_MUSK); real('musketeer_deploy_01', T_MUSK + .75, .9, wet=.4)
pad(T_MUSK, T_GOLEM, [110, 164.8, 220, 261.6], 1900, .1, .28, trem=3, fade=.4)
tm = T_MUSK + .75; k = 0
while tm < SHOTS[0] - .05:
    put(dry, tm, boom(.8, 110, 45, .3, 4.5), (.45 + .08 * k) * (1 if k % 2 == 0 else .7)); put(send, tm, boom(.8, 110, 45, .3, 4.5), .3)
    put(dry, tm + .02, norm(filt(noise(.12), lo=1800, hi=400) * decay(.12, 28)), .2); tm += .5; k += 1
tm = SHOTS[0] - 1.2
while tm < SHOTS[0] - .05:
    put(dry, tm, norm(filt(noise(.12), hi=1400) * decay(.12, 26)), .2 + .4 * (tm - (SHOTS[0] - 1.2)) / 1.2, rng.uniform(-.4, .4)); tm += .16 - .1 * (tm - (SHOTS[0] - 1.2)) / 1.2
for i, ts in enumerate(SHOTS):
    pn = [-.7, 0, .7][i]; real('musket_fire_02', ts, 1.0, pn, wet=.5); real('musket_impact_01', ts + .1, .8, pn); put(dry, ts, boom(1.5, 90, 35, .6, 3), .6)
real('musketeer_reload_01', SHOTS[-1] + .5, .6)
# =============== GOLEM (15)
sc_open(T_GOLEM); real('golem_deploy_01', T_GOLEM + .6, 1.0, wet=.4); real('stone_golem_deploy_02', T_GOLEM + .7, .8)
pad(T_GOLEM, T_SKEL, [43.65, 87.3, 130.8, 65.4], 650, .15, .4, fade=.8); choir(174.6, 5.4, .16, T_GOLEM + .3); choir(130.8, 5.0, .12, T_GOLEM + .5)
for i, ts in enumerate(STOMPS):
    big = 1.0 if i < 3 else 1.5
    real('golem_walk_02', ts - .05, 1.0 * big, wet=.4, rate=.9); put(dry, ts, boom(3.0 if i < 3 else 5.0, 85, 24, .9, 1.5 if i < 3 else .9), .85 * big); put(send, ts, boom(3, 85, 24, .9, 1.5), .7 * big)
    put(dry, ts + .02, norm(filt(noise(1.1), lo=1600, hi=120) * decay(1.1, 4)), .5 * big)
real('golem_atk_hit_01', STOMPS[-1], 1.0, wet=.5, rate=.85)
# =============== SKELETON ARMY (20.5)
sc_open(T_SKEL); real('cemetary_deploy_01', T_SKEL + .7, .8, wet=.4); real('skeleton_deploy_03', T_SKEL + .75, 1.0, wet=.4); real('deploy_skeleton_01', T_SKEL + .85, .8)
pad(T_SKEL, T_MONT, [440, 466.2, 659.3, 698.5], 3500, 0, .2, trem=7.5, wave_='sine', fade=.4); pad(T_SKEL, T_MONT, [55, 58.3], 500, .1, .3, fade=.5)
choir(220, 5.0, .14, T_SKEL + .1); choir(233.1, 4.8, .1, T_SKEL + .2); choir(329.6, 4.5, .1, T_SKEL + .5)
tc = T_SKEL + .9
while tc < T_MONT - .1:
    dens = np.interp(tc, [T_SKEL + .9, T_MONT], [5, 14])
    real(['skeleton_step_02', 'skele_warrior_step_02'][int(rng.integers(0, 2))], tc, rng.uniform(.18, .5), rng.uniform(-1, 1), rate=rng.uniform(.9, 1.15), wet=.25); tc += rng.exponential(1 / dens)
real('king_laughter_01', T_SKEL + 2.9, .9, wet=.3); put(dry, T_SKEL + 4.0, boom(3, 120, 28, .9, 1.2), 1.0); put(send, T_SKEL + 4.0, boom(3, 120, 28, .9, 1.2), .6)
for ts in (T_SKEL + 3.4, T_SKEL + 4.0, T_SKEL + 4.5): real('skeleton_atk_03', ts, .6, rng.uniform(-.6, .6))
put(dry, T_SKEL + .8, norm(filt(noise(4.5), lo=700, hi=100) * np.linspace(.1, 1, int(4.5 * SR)) ** 1.5), .3)
for ts in (T_SKEL + 2.0, T_SKEL + 3.3, T_SKEL + 4.3): put(dry, ts, boom(1.5, 80, 28, .5, 2.5), .6)
# =============== MONTAGE (25.5)  -- real in-game battle music + hits
mus = sfx('2min_loop_battle_01', 'music'); seg = mus[:int(4.2 * SR)] * np.minimum(np.linspace(0, 1, int(4.2 * SR)) * 6, 1); put(dry, T_MONT - .1, seg, .55); put(send, T_MONT, seg, .15)
hitsfx = {'spark': 'zap_02', 'musk': 'musket_fire_02', 'golem': 'golem_atk_hit_01', 'skel': 'skeleton_atk_03', 'all': 'king_tower_gone_01'}
for k, ts in enumerate(MONT_CUTS):
    put(dry, ts, boom(1.6, 130, 30, .7, 2.2), .9); put(send, ts, boom(1.6, 130, 30, .7, 2.2), .5); put(dry, ts, norm(filt(noise(.2), hi=700) * decay(.2, 18, .001)), .5)
    real(hitsfx[MONT[k]], ts, .9, wet=.4)
pad(T_MONT, T_END, [110, 164.8, 220, 329.6], 2600, .25, .4, trem=4, fade=.2); pad(T_MONT, T_END, [87.3, 130.8, 174.6], 1500, .2, .3, fade=.2)
choir(220, 4, .2, T_MONT); choir(329.6, 4, .2, T_MONT); choir(440, 4, .16, T_MONT)
put(dry, T_MONT, norm(filt(noise(4), lo=9000, hi=2500) * np.linspace(0, 1, 4 * SR) ** 2.5), .25)
fin = boom(7, 150, 20, 1, .7); put(dry, T_END - .5, fin, 1.1); put(send, T_END - .5, fin, 1.0); real('king_tower_gone_02', T_END - .5, 1.0, wet=.6); real('building_destroyed_05', T_END - .5, .9, wet=.5)
# =============== END
pad(T_END + .1, DUR, [110, 165, 220, 247.5], 1400, 0, .12, wave_='sine', fade=1.2)
real('king_crying_01', T_END + 2.3, .9, wet=.3); real('king_crying_02', T_END + 3.5, .8, wet=.3)
put(send, T_END + .5, norm(sweep(1318.5, 1318.5, 3) * decay(3, 1.4, .002)), .08); put(dry, T_END + .5, norm(sweep(55, 55, 3.4) * decay(3.4, 1)), .5)
for b in beats():
    if b > T_END: lub(b, 1.0)

# =============== master
Nfft = 1 << 21; ir = filt(noise(3.0), lo=5500, hi=150) * np.exp(-tt(3.0) / .85); ir[:int(.02 * SR)] *= .2; irf = np.fft.rfft(ir, Nfft)
wet = np.stack([np.fft.irfft(np.fft.rfft(send[c], Nfft) * irf, Nfft)[:N] for c in range(2)])
mix = dry + wet * .0016 * (1 / ir.std() / 100 * 6)
duck = np.ones(N); ta = np.arange(N) / SR
def dip(a, b, d): m = (ta > a) & (ta < b); duck[m] = np.minimum(duck[m], d)
dip(T_SPARKY - .33, T_SPARKY, 0.0); dip(ZAP - .1, ZAP, .05); dip(T_END, T_END + .6, .12)
mix *= duck; mix = np.tanh(mix * 1.15) / np.tanh(1.15)
for c in range(2): mix[c] = filt(mix[c], hi=25, n=2)
mix = mix / np.max(np.abs(mix)) * .89
wv = wave.open('audio2.wav', 'wb'); wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(SR); wv.writeframes((mix.T * 32767).astype('<i2').tobytes()); wv.close()
print('rms', float(np.sqrt((mix ** 2).mean())), 'peak', float(np.abs(mix).max()))
