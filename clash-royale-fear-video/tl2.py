import numpy as np
FPS = 30
DUR = 34.0
T_SPARKY, T_MUSK, T_GOLEM, T_SKEL, T_MONT, T_END = 4.5, 10.0, 15.0, 20.5, 25.5, 29.5
ZAP = T_SPARKY + 4.0
SHOTS = [T_MUSK + 2.6, T_MUSK + 2.8, T_MUSK + 3.0]
STOMPS = [T_GOLEM + 1.9, T_GOLEM + 2.8, T_GOLEM + 3.7, T_GOLEM + 4.5]
MONT = ['spark', 'musk', 'golem', 'skel', 'spark', 'golem', 'musk', 'all']
MONT_CUTS = [T_MONT + 0.5 * k for k in range(8)]
def _iv(t):
    pts = [(0, 1.0), (4.2, .9), (5, .8), (10, .7), (15, .6), (20.5, .5), (25.5, .34), (29.4, .34)]
    return float(np.interp(t, [p[0] for p in pts], [p[1] for p in pts]))
def beats():
    out, t = [], 0.5
    while t < 29.4:
        if not (4.15 < t < 4.5): out.append(t)
        t += _iv(t)
    return out + [30.2, 31.1]
