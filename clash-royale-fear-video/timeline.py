import numpy as np
DUR = 39.5
FPS = 30
SPARKY_START, ZAP = 7.3, 10.6
MUSK_START, SHOTS = 13.0, [16.8, 17.0, 17.2]
GOLEM_START = 18.5
STOMPS = [19.2, 20.1, 21.0, 21.8, 22.5, 23.1]
SKEL_START = 24.5
MONT_START = 30.0
MONT = ['spark', 'musk', 'golem', 'skel', 'spark', 'golem', 'musk', 'all']
MONT_CUTS = [30.0 + 0.5 * k for k in range(8)]
END = 34.0

def _interval(t):
    pts = [(0, 1.15), (7, 1.0), (8, 0.8), (13, 0.7), (18.5, 0.62), (24.5, 0.5), (30, 0.34), (34, 0.34)]
    return float(np.interp(t, [p[0] for p in pts], [p[1] for p in pts]))

def beats():
    out, t = [], 1.0
    while t < 33.9:
        if not (6.95 < t < 7.35):
            out.append(t)
        t += _interval(t)
    return out + [34.8, 35.7]
