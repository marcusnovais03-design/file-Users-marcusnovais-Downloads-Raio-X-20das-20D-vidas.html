#!/usr/bin/env python3
"""Vídeo vertical 'Ajuste fiscal' — explicação desenhada à mão (papel bege, traço escuro, destaque laranja).

Uso:
  python3 render.py <dir_saida>                  # renderiza <dir_saida>/video_mudo.mp4 (lê timeline.json de lá)
  python3 render.py <dir_saida> --frame 12.5 f.png   # salva um quadro para conferência
"""
import sys, os, json, math, subprocess
from functools import lru_cache
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from roteiro import FALAS, CAPS

W, H, FPS, SS = 1080, 1920, 30, 2
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
PAPER = (236, 224, 209); INK = (44, 34, 29); ORANGE = (196, 92, 40); MUTED = (140, 128, 116)
DARK = (27, 22, 20); CREAM = (240, 230, 216)
ASSINATURA = 'Marcus Novais · @mnovais'
ASSINATURA_FIM = ASSINATURA

TLJ = json.load(open(os.path.join(OUT, 'timeline.json')))
TOTAL = TLJ['total']
FT = {f['id']: (f['t0'], f['t1']) for f in TLJ['falas']}
def T(fid, frac=0.0):
    a, b = FT[fid]; return a + frac * (b - a)
# início de cada capítulo
CH0 = {}
for f in TLJ['falas']:
    CH0.setdefault(f['cap'], max(0.0, f['t0'] - 0.42))
CH0[0] = 0.0
NCH = len(CAPS)
def ch_end(c): return CH0[c + 1] if c + 1 < NCH else TOTAL + 1
def chapter(t):
    c = 0
    for k in range(NCH):
        if t >= CH0[k]: c = k
    return c

# ---------------- fontes ----------------
@lru_cache(None)
def font(kind, size):
    size = int(round(size * SS))
    if kind == 'hand':
        f = ImageFont.truetype(os.path.join(HERE, 'fonts', 'Caveat.ttf'), size)
        try: f.set_variation_by_axes([600])
        except Exception: pass
        return f
    if kind.startswith('mono'):
        return ImageFont.truetype(f'/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-{kind[4:] or "Medium"}.ttf', size)
    fam = 'InterDisplay' if kind.startswith('D') else 'Inter'
    return ImageFont.truetype(f'/usr/share/fonts/opentype/inter/{fam}-{kind.lstrip("D")}.otf', size)

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_io(x): x = clamp(x); return 0.5 - 0.5 * math.cos(math.pi * x)
def mix(c0, c1, a): return tuple(int(round(c0[i] + (c1[i] - c0[i]) * a)) for i in range(3))

# ---------------- motor de desenho ----------------
_seed = [0]
def _rng():
    _seed[0] += 1; return np.random.default_rng(_seed[0] * 7919)

def wobble(pts, amp=2.0, step=9):
    """Polilinha -> pontos densos com tremido de traço à mão."""
    r = _rng(); out = []; s = 0.0
    p1, p2, p3 = r.uniform(0, 6.28, 3)
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        if L < 1e-6: continue
        n = max(2, int(L / step)); nx, ny = -(y1 - y0) / L, (x1 - x0) / L
        for i in range(n + (1 if (x1, y1) == pts[-1] else 0)):
            u = i / n; ss = s + u * L
            o = amp * (math.sin(ss / 41 + p1) + 0.55 * math.sin(ss / 15 + p2) + 0.3 * math.sin(ss / 6 + p3)) / 1.5
            out.append((x0 + (x1 - x0) * u + nx * o, y0 + (y1 - y0) * u + ny * o))
        s += L
    return out

class Scene:
    def __init__(self, bg=PAPER): self.el = []; self.bg = bg
    def add(self, t0, fn): self.el.append((t0, fn))
    def draw(self, d, t):
        for t0, fn in self.el:
            if t >= t0: fn(d, t - t0)

    # --- traços ---
    def stroke(self, pts, t0, dur=0.5, color=INK, w=4.5, amp=2.0, pre=False):
        P = [(x * SS, y * SS) for x, y in (pts if pre else wobble(pts, amp))]
        ww = int(round(w * SS)); r = ww / 2
        def fn(d, tl):
            n = max(2, int(ease_io(tl / dur) * len(P))) if dur > 0 else len(P)
            q = P[:n]
            d.line(q, fill=color, width=ww, joint='curve')
            for x, y in (q[0], q[-1]): d.ellipse((x - r, y - r, x + r, y + r), fill=color)
        self.add(t0, fn)
    def line(self, a, b, t0, dur=0.4, **k): self.stroke([a, b], t0, dur, **k)
    def rect(self, x, y, bw, bh, t0, dur=0.7, **k):
        o = 5
        self.stroke([(x - o, y), (x + bw, y), (x + bw, y + bh + o)], t0, dur * 0.5, **k)
        self.stroke([(x + bw + o, y + bh), (x, y + bh), (x, y - o)], t0 + dur * 0.5, dur * 0.5, **k)
    def circle(self, cx, cy, rx, t0, dur=0.6, ry=None, **k):
        ry = ry or rx; r = _rng(); a0 = r.uniform(0, 6.28); pts = []
        for i in range(49):
            a = a0 + 6.6 * i / 48; g = 1 + 0.035 * math.sin(a * 2 + a0) + 0.02 * i / 48
            pts.append((cx + rx * g * math.cos(a), cy + ry * g * math.sin(a)))
        self.stroke(pts, t0, dur, amp=k.pop('amp', 0.8), **k)
    def arrow(self, a, b, t0, dur=0.45, head=22, **k):
        self.stroke([a, b], t0, dur, **k)
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        for s in (2.55, -2.55):
            self.stroke([b, (b[0] + head * math.cos(ang + s), b[1] + head * math.sin(ang + s))], t0 + dur * 0.85, 0.14, **k)
    def dashed(self, a, b, t0, dur=0.6, dash=18, gap=13, **k):
        L = math.hypot(b[0] - a[0], b[1] - a[1]); n = int(L / (dash + gap)) + 1
        for i in range(n):
            u0 = i * (dash + gap) / L; u1 = min(1, u0 + dash / L)
            if u0 >= 1: break
            p = lambda u: (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)
            self.stroke([p(u0), p(u1)], t0 + dur * i / n, 0.08, **k)
    def arc(self, cx, cy, r, a0, a1, t0, dur=0.6, head=24, **k):
        pts = [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / 40)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / 40))) for i in range(41)]
        self.stroke(pts, t0, dur, amp=1.0, **k)
        b = pts[-1]; ang = math.radians(a1) + math.pi / 2 * (1 if a1 > a0 else -1)
        for s in (2.5, -2.5):
            self.stroke([b, (b[0] + head * math.cos(ang + s), b[1] + head * math.sin(ang + s))], t0 + dur * 0.9, 0.14, **k)
    def hatch(self, x, y, w, h, t0, dur=0.9, color=INK, gap=13, lw=2.4):
        r = _rng(); lines = []
        for k in np.arange(-h + gap * 0.5, w, gap):
            x0, y0, x1, y1 = x + k, y + h, x + k + h, y
            if x0 < x: y0 -= (x - x0); x0 = x
            if x1 > x + w: y1 += (x1 - (x + w)); x1 = x + w
            if y0 - y1 < 3: continue
            j = r.uniform(-1.5, 1.5, 4)
            lines.append(((x0 + j[0]) * SS, (y0 + j[1]) * SS, (x1 + j[2]) * SS, (y1 + j[3]) * SS))
        ww = int(round(lw * SS))
        def fn(d, tl):
            for L in lines[:int(ease_io(tl / dur) * len(lines) + 0.999)]: d.line(L, fill=color, width=ww)
        self.add(t0, fn)
    def fill(self, x, y, w, h, t0, dur=0.9, color=ORANGE):
        def fn(d, tl):
            hh = h * ease_io(tl / dur)
            d.rectangle((x * SS, (y + h - hh) * SS, (x + w) * SS, (y + h) * SS), fill=color)
        self.add(t0, fn)

    # --- textos ---
    def text(self, s, x, y, t0, kind='SemiBold', size=28, color=INK, anchor='mm', dur=0.35, track=0):
        f = font(kind, size); bg = self.bg
        def fn(d, tl):
            a = ease(tl / dur); c = mix(bg, color, a); yy = (y + 10 * (1 - a)) * SS
            if track:
                wd = sum(f.getlength(ch) + track * SS for ch in s) - track * SS
                xx = x * SS - (wd / 2 if anchor[0] == 'm' else wd if anchor[0] == 'r' else 0)
                for ch in s:
                    d.text((xx, yy), ch, font=f, fill=c, anchor='l' + anchor[1]); xx += f.getlength(ch) + track * SS
            else:
                d.text((x * SS, yy), s, font=f, fill=c, anchor=anchor)
        self.add(t0, fn)
    def rich(self, segs, x, y, t0, kind='DBold', size=96, dur=0.4):
        """segs = [(texto, cor)], alinhado à esquerda pela linha de base."""
        f = font(kind, size); bg = self.bg
        def fn(d, tl):
            a = ease(tl / dur); xx = x * SS; yy = (y + 14 * (1 - a)) * SS
            for s, col in segs:
                d.text((xx, yy), s, font=f, fill=mix(bg, col, a), anchor='ls'); xx += f.getlength(s)
        self.add(t0, fn)
    def hand(self, s, x, y, t0, size=48, color=ORANGE, anchor='mm', cps=28):
        f = font('hand', size)
        wd = f.getlength(s); x0 = x * SS - (wd / 2 if anchor[0] == 'm' else wd if anchor[0] == 'r' else 0)
        def fn(d, tl):
            n = min(len(s), int(tl * cps) + 1)
            d.text((x0, y * SS), s[:n], font=f, fill=color, anchor='l' + anchor[1])
        self.add(t0, fn)

    # --- ícones (cx, cy = centro; s = tamanho) ---
    def house(self, cx, cy, s, t0, **k):
        h = s / 2
        self.stroke([(cx - h * 0.8, cy + h), (cx - h * 0.8, cy - h * 0.1), (cx + h * 0.8, cy - h * 0.1), (cx + h * 0.8, cy + h), (cx - h * 0.8, cy + h)], t0, 0.5, **k)
        self.stroke([(cx - h * 1.05, cy - h * 0.02), (cx, cy - h), (cx + h * 1.05, cy - h * 0.02)], t0 + 0.3, 0.35, **k)
        self.stroke([(cx - h * 0.18, cy + h), (cx - h * 0.18, cy + h * 0.4), (cx + h * 0.18, cy + h * 0.4), (cx + h * 0.18, cy + h)], t0 + 0.5, 0.3, **k)
    def bank(self, cx, cy, s, t0, **k):
        h = s / 2
        self.stroke([(cx - h, cy - h * 0.35), (cx, cy - h), (cx + h, cy - h * 0.35), (cx - h, cy - h * 0.35)], t0, 0.45, **k)
        for i, dx in enumerate((-0.62, -0.2, 0.2, 0.62)):
            self.line((cx + dx * h, cy - h * 0.25), (cx + dx * h, cy + h * 0.7), t0 + 0.35 + 0.08 * i, 0.2, **k)
        self.stroke([(cx - h * 1.05, cy + h * 0.75), (cx + h * 1.05, cy + h * 0.75)], t0 + 0.7, 0.2, **k)
        self.stroke([(cx - h * 1.15, cy + h), (cx + h * 1.15, cy + h)], t0 + 0.8, 0.2, **k)
    def factory(self, cx, cy, s, t0, **k):
        h = s / 2
        self.stroke([(cx - h, cy + h * 0.8), (cx - h, cy - h * 0.1), (cx - h * 0.45, cy - h * 0.5), (cx - h * 0.45, cy - h * 0.1), (cx + h * 0.1, cy - h * 0.5),
                     (cx + h * 0.1, cy - h * 0.1), (cx + h * 0.5, cy - h * 0.1), (cx + h * 0.5, cy - h), (cx + h * 0.85, cy - h), (cx + h * 0.85, cy + h * 0.8), (cx - h, cy + h * 0.8)], t0, 0.8, **k)
    def envelope(self, cx, cy, s, t0, **k):
        h = s / 2
        self.stroke([(cx - h, cy - h * 0.6), (cx + h, cy - h * 0.6), (cx + h, cy + h * 0.6), (cx - h, cy + h * 0.6), (cx - h, cy - h * 0.6)], t0, 0.45, **k)
        self.stroke([(cx - h, cy - h * 0.6), (cx, cy + h * 0.1), (cx + h, cy - h * 0.6)], t0 + 0.35, 0.3, **k)
    def cross(self, cx, cy, s, t0, **k):
        h = s / 2; a = h * 0.33
        self.stroke([(cx - a, cy - h), (cx + a, cy - h), (cx + a, cy - a), (cx + h, cy - a), (cx + h, cy + a), (cx + a, cy + a), (cx + a, cy + h),
                     (cx - a, cy + h), (cx - a, cy + a), (cx - h, cy + a), (cx - h, cy - a), (cx - a, cy - a), (cx - a, cy - h)], t0, 0.7, **k)
    def book(self, cx, cy, s, t0, **k):
        h = s / 2
        self.stroke([(cx, cy - h * 0.55), (cx - h, cy - h * 0.75), (cx - h, cy + h * 0.55), (cx, cy + h * 0.75), (cx + h, cy + h * 0.55), (cx + h, cy - h * 0.75), (cx, cy - h * 0.55), (cx, cy + h * 0.75)], t0, 0.7, **k)
        for i, dy in enumerate((-0.25, 0.1)):
            self.line((cx - h * 0.75, cy + dy * h - 4), (cx - h * 0.25, cy + dy * h + 6), t0 + 0.6 + 0.1 * i, 0.15, w=2.5)
    def person(self, cx, cy, s, t0, cane=False, **k):
        h = s / 2
        self.circle(cx, cy - h * 0.72, h * 0.26, t0, 0.3, **k)
        self.line((cx, cy - h * 0.45), (cx, cy + h * 0.3), t0 + 0.25, 0.2, **k)
        self.stroke([(cx - h * 0.42, cy + h * 0.02), (cx, cy - h * 0.2), (cx + h * 0.42, cy + h * 0.02)], t0 + 0.4, 0.2, **k)
        self.stroke([(cx - h * 0.36, cy + h), (cx, cy + h * 0.3), (cx + h * 0.36, cy + h)], t0 + 0.55, 0.2, **k)
        if cane: self.stroke([(cx + h * 0.42, cy + h * 0.02), (cx + h * 0.62, cy + h)], t0 + 0.7, 0.2, **k)
    def card(self, cx, cy, s, t0, **k):
        h = s / 2
        self.stroke([(cx - h, cy - h * 0.62), (cx + h, cy - h * 0.62), (cx + h, cy + h * 0.62), (cx - h, cy + h * 0.62), (cx - h, cy - h * 0.62)], t0, 0.5, **k)
        self.hatch(cx - h, cy - h * 0.38, s, h * 0.26, t0 + 0.4, 0.3, gap=7)
        self.line((cx - h * 0.7, cy + h * 0.25), (cx - h * 0.1, cy + h * 0.25), t0 + 0.6, 0.15, w=3)
    def cart(self, cx, cy, s, t0, items=5, **k):
        h = s / 2
        self.stroke([(cx - h * 1.05, cy - h * 0.75), (cx - h * 0.75, cy - h * 0.75), (cx - h * 0.45, cy + h * 0.35), (cx + h * 0.7, cy + h * 0.35), (cx + h * 0.95, cy - h * 0.4), (cx - h * 0.65, cy - h * 0.4)], t0, 0.7, **k)
        self.circle(cx - h * 0.3, cy + h * 0.62, h * 0.12, t0 + 0.6, 0.2, **k)
        self.circle(cx + h * 0.55, cy + h * 0.62, h * 0.12, t0 + 0.7, 0.2, **k)
        slots = [(-0.35, 0.28, 0.42), (0.1, 0.34, 0.5), (0.52, 0.26, 0.38), (-0.12, 0.3, 0.4), (0.3, 0.26, 0.36)]
        for i, (dx, bw, bh) in enumerate(slots[:items]):
            row = 0 if i < 3 else 1
            bx = cx + dx * h - bw * h / 2; by = cy - h * 0.4 - (bh * h if row == 0 else bh * h + 0.46 * h)
            self.rect(bx, by, bw * h, bh * h, t0 + 0.85 + 0.12 * i, 0.3, w=3, amp=1.0)
            if i % 2 == 0: self.hatch(bx, by, bw * h, bh * h, t0 + 1.0 + 0.12 * i, 0.2, gap=8, lw=2)
    def scale(self, cx, cy, t0, tilt=0.0, half=230, wl=0.5, wr=1.0, **k):
        """Balança: cy = altura do pivô; tilt > 0 desce o lado direito."""
        self.line((cx, cy), (cx, cy + 290), t0, 0.35, **k)
        self.line((cx - 95, cy + 290), (cx + 95, cy + 290), t0 + 0.25, 0.25, **k)
        dy = half * math.sin(tilt); dx = half * math.cos(tilt)
        L = (cx - dx, cy - dy); R = (cx + dx, cy + dy)
        self.line(L, R, t0 + 0.45, 0.4, **k)
        self.circle(cx, cy, 9, t0 + 0.4, 0.15, **k)
        pans = []
        for i, (ex, ey) in enumerate((L, R)):
            py = ey + 135
            self.stroke([(ex - 85, py), (ex, ey), (ex + 85, py)], t0 + 0.8 + 0.1 * i, 0.3, w=3, amp=1.0)
            self.line((ex - 100, py), (ex + 100, py), t0 + 1.0 + 0.1 * i, 0.2, **k)
            pans.append((ex, py))
        (lx, ly), (rx, ry) = pans
        bl, br = 86 * wl, 86 * wr
        self.rect(lx - 46, ly - bl - 4, 92, bl, t0 + 1.25, 0.35, w=3.5)
        self.rect(rx - 46, ry - br - 4, 92, br, t0 + 1.45, 0.35, w=3.5)
        self.hatch(rx - 46, ry - br - 4, 92, br, t0 + 1.7, 0.4, gap=10)
        return pans
    def label_box(self, s, cx, cy, w, h, t0):
        self.rect(cx - w / 2, cy - h / 2, w, h, t0, 0.5)
        self.text(s, cx, cy, t0 + 0.25, 'monoBold', 30, track=3)

# ---------------- cenas ----------------
def build():
    S = [Scene() for _ in range(NCH)]

    # 00 — A PERGUNTA
    s = S[0]
    s.rich([('O GOVERNO', INK)], 50, 300, 0.15)
    s.rich([('PRECISA DE', INK)], 50, 398, 0.35)
    s.rich([('AJUSTE FISCAL', ORANGE), ('?', INK)], 50, 496, 0.55)
    pans = s.scale(540, 700, T('a1', 0.12), tilt=0.19)
    s.text('arrecadação', pans[0][0], pans[0][1] + 38, T('a1', 0.5), 'SemiBold', 27)
    s.text('gastos', pans[1][0], pans[1][1] + 38, T('a1', 0.62), 'SemiBold', 27)
    s.hand('é mesmo necessário?', 540, 1170, T('a2', 0.25), 70)
    s.stroke([(330, 1215), (480, 1228), (620, 1218), (760, 1226)], T('a2', 0.75), 0.4, color=ORANGE, w=3.5)

    # 01 — A CONTA
    s = S[1]
    s.house(540, 345, 190, T('b1', 0.05))
    s.arrow((150, 350), (400, 350), T('b1', 0.38), color=ORANGE)
    s.text('impostos', 275, 312, T('b1', 0.45), 'SemiBold', 30)
    s.hand('entra', 275, 392, T('b1', 0.42), 44)
    s.arrow((680, 350), (930, 350), T('b1', 0.72), color=ORANGE)
    s.text('gastos', 805, 312, T('b1', 0.82), 'SemiBold', 30)
    s.hand('sai', 805, 392, T('b1', 0.76), 44)
    s.text('DE CADA R$ 100 DE GASTO  ·  SEM JUROS', 90, 585, T('b2', 0.08), 'monoMedium', 24, MUTED, 'lm', track=2)
    s.rect(90, 620, 900, 120, T('b2', 0.1), 0.8)
    s.hatch(90, 620, 828, 120, T('b2', 0.62), 1.3)
    s.line((918, 615), (918, 745), T('b2', 0.62) + 1.2, 0.25)
    s.rich([('92% ', ORANGE), ('obrigatório', INK)], 90, 825, T('b2', 0.7), 'DBold', 58)
    s.hand('8% livre', 900, 880, T('b3', 0.55), 50, anchor='mm')
    s.arrow((925, 845), (952, 760), T('b3', 0.62), 0.3, color=ORANGE, w=3.5, head=16)
    icons = [(s.person, 'aposentadorias', dict(cane=True)), (s.envelope, 'salários', {}), (s.cross, 'saúde', {}), (s.book, 'educação', {})]
    for i, ((fn, lab, kw), fr) in enumerate(zip(icons, (0.0, 0.2, 0.32, 0.42))):
        x = 165 + 250 * i
        fn(x, 1065, 110 if i != 0 else 130, T('b3', fr), **kw)
        s.text(lab, x, 1165, T('b3', fr) + 0.3, 'SemiBold', 26)
    s.circle(954, 680, 62, T('b3', 0.72), 0.5, ry=92, color=ORANGE, w=4)

    # 02 — O BURACO
    s = S[2]
    BY = 1160
    s.line((110, BY), (970, BY), T('c1', 0.0), 0.4)
    s.rect(190, BY - 520, 250, 520, T('c1', 0.08), 0.6)
    s.text('ARRECADA', 315, BY + 42, T('c1', 0.15), 'monoBold', 28, track=3)
    s.rect(620, BY - 528, 250, 528, T('c1', 0.3), 0.6)
    s.text('GASTA', 745, BY + 42, T('c1', 0.38), 'monoBold', 28, track=3)
    s.text('gastos', 745, BY - 290, T('c1', 0.45), 'SemiBold', 28)
    s.text('sem juros', 745, BY - 252, T('c1', 0.45), 'SemiBold', 28)
    s.rect(620, BY - 528 - 138, 250, 138, T('c1', 0.68), 0.5, color=ORANGE)
    s.hatch(620, BY - 528 - 138, 250, 138, T('c1', 0.8), 0.7, color=ORANGE, gap=11)
    s.hand('juros', 935, BY - 600, T('c1', 0.85), 50)
    s.text('R$ 1,2 trilhão', 745, 360, T('c2', 0.42), 'DBold', 66, ORANGE)
    s.hand('só de juros, em 12 meses', 745, 425, T('c2', 0.72), 44, color=INK)
    s.dashed((445, BY - 520), (615, BY - 520), T('c3', 0.1), 0.4, color=ORANGE, w=3.5)
    s.arrow((530, BY - 530), (530, BY - 660), T('c3', 0.2), 0.3, color=ORANGE, w=3.5, head=16)
    s.text('−9,5% do PIB', 300, 500, T('c3', 0.3), 'DBold', 50, ORANGE)
    s.hand('o buraco de um ano', 300, 558, T('c3', 0.45), 44, color=INK)

    # 03 — A DÍVIDA
    s = S[3]
    s.rich([('82,9%', ORANGE)], 60, 360, T('d1', 0.33), 'DBold', 170)
    s.text('do PIB', 610, 318, T('d1', 0.55), 'DBold', 60, INK, 'lm')
    s.hand('R$ 11,1 trilhões', 64, 425, T('d1', 0.78), 56, anchor='lm')
    s.stroke([(140, 540), (140, 1130), (965, 1130)], T('d1', 0.0), 0.6)
    pts = [(200, 1010), (330, 985), (450, 940), (570, 905), (690, 850), (800, 790), (890, 720)]
    s.stroke(pts, T('d1', 0.15), 1.6, w=5.5, amp=1.2)
    s.circle(200, 1010, 9, T('d1', 0.15), 0.15)
    s.text('78,6%', 200, 962, T('d1', 0.18), 'Bold', 32)
    s.text('dez/25', 200, 1170, T('d1', 0.18), 'monoMedium', 24, MUTED)
    s.fill(878, 708, 24, 24, T('d1', 0.15) + 1.5, 0.15)
    s.text('set/26', 890, 1170, T('d1', 0.45), 'monoMedium', 24, MUTED)
    s.hand('+4,3 pontos só em 2026', 640, 1020, T('d1', 0.6), 46)
    s.dashed((905, 700), (990, 600), T('d2', 0.0), 0.4, color=ORANGE, w=4)
    s.arrow((975, 620), (1000, 588), T('d2', 0.35), 0.15, color=ORANGE, w=4)
    s.hand('e depois?', 900, 560, T('d2', 0.4), 50)

    # 04 — A INFLAÇÃO
    s = S[4]
    GY = 720; PP = 92           # px por ponto percentual
    s.line((110, GY), (640, GY), T('e1', 0.0), 0.4)
    s.dashed((130, GY - 3 * PP), (640, GY - 3 * PP), T('e1', 0.2), 0.5, w=3)
    s.text('meta 3%', 665, GY - 3 * PP, T('e1', 0.3), 'SemiBold', 30, INK, 'lm')
    s.dashed((130, GY - 4.5 * PP), (640, GY - 4.5 * PP), T('e1', 0.5), 0.5, w=3)
    s.text('teto 4,5%', 665, GY - 4.5 * PP, T('e1', 0.6), 'SemiBold', 30, INK, 'lm')
    s.text('IPCA · 12 MESES', 375, GY + 42, T('e1', 0.75), 'monoBold', 26, track=3)
    bh = 4.63 * PP
    s.fill(290, GY - bh, 170, bh, T('e2', 0.1), 1.6)
    s.rect(290, GY - bh, 170, bh, T('e2', 0.1) + 1.5, 0.4)
    s.text('4,63%', 375, GY - bh - 52, T('e2', 0.42), 'DBold', 68, ORANGE)
    s.hand('estourou o teto', 850, GY - bh - 50, T('e2', 0.75), 50)
    s.cart(270, 1040, 230, T('e3', 0.4), items=5)
    s.text('antes', 270, 1180, T('e3', 0.5), 'SemiBold', 28)
    s.arrow((455, 1020), (610, 1020), T('e3', 0.62), 0.3, color=ORANGE)
    s.cart(800, 1040, 230, T('e3', 0.7), items=2)
    s.text('hoje', 800, 1180, T('e3', 0.8), 'SemiBold', 28)
    s.hand('mesmo salário', 528, 968, T('e3', 0.5), 40)
    s.circle(805, 1020, 150, T('e4', 0.3), 0.6, ry=150, color=ORANGE, w=4)

    # 05 — OS JUROS
    s = S[5]
    s.bank(540, 330, 210, T('f1', 0.1))
    s.text('BANCO CENTRAL', 540, 478, T('f1', 0.22), 'monoBold', 28, track=3)
    s.text('13,75%', 540, 665, T('f1', 0.6), 'DBold', 200, ORANGE)
    s.text('SELIC  ·  AO ANO', 540, 800, T('f1', 0.75), 'monoMedium', 28, MUTED, track=3)
    for i, (fn, lab, fr) in enumerate(((s.house, 'financiamento', 0.18), (s.card, 'cartão', 0.42), (s.factory, 'empresas', 0.56))):
        x = 180 + 320 * i
        fn(x, 1010, 130, T('f2', fr))
        s.text(lab, x, 1108, T('f2', fr) + 0.3, 'SemiBold', 27)
        s.arrow((x + 105, 1060), (x + 105, 960), T('f2', fr) + 0.45, 0.25, color=ORANGE, w=4, head=16)
    s.hand('menos emprego', 540, 1215, T('f2', 0.84), 62)

    # 06 — O CÍRCULO
    s = S[6]
    CX, CY, R = 540, 720, 350
    pos = {k: (CX + R * math.cos(math.radians(a)), CY + R * math.sin(math.radians(a))) for k, a in (('GASTO', -90), ('DÍVIDA', 30), ('JUROS', 150))}
    s.label_box('JUROS', *pos['JUROS'], 240, 100, T('g1', 0.02))
    s.label_box('DÍVIDA', *pos['DÍVIDA'], 240, 100, T('g1', 0.62))
    s.label_box('GASTO', *pos['GASTO'], 240, 100, T('g2', 0.0))
    s.hand('círculo', CX, CY - 30, T('g2', 0.08), 84)
    s.hand('vicioso', CX, CY + 50, T('g2', 0.16), 84)
    s.arc(CX, CY, R, -66, 12, T('g2', 0.42), 0.5, color=ORANGE)
    s.arc(CX, CY, R, 50, 130, T('g2', 0.62), 0.5, color=ORANGE)
    s.arc(CX, CY, R, 168, 246, T('g2', 0.8), 0.5, color=ORANGE)

    # 07 — RESUMINDO
    s = S[7]
    pans = s.scale(540, 280, T('h1', 0.02), tilt=0.0, half=215, wl=0.8, wr=0.8)
    s.text('entra', pans[0][0], pans[0][1] + 36, T('h1', 0.6), 'SemiBold', 27)
    s.text('sai', pans[1][0], pans[1][1] + 36, T('h1', 0.65), 'SemiBold', 27)
    s.hand('a conta fecha', 540, 650, T('h1', 0.72), 62)
    for i, (lab, word, fr, dy) in enumerate((('DÍVIDA', 'para de crescer', 0.05, 0), ('INFLAÇÃO', 'cede', 0.42, 80), ('JUROS', 'caem', 0.68, 80))):
        x = 190 + 350 * i
        s.text(lab, x, 770, T('h2', fr), 'monoBold', 28, track=3)
        if dy: s.arrow((x, 815), (x, 815 + dy), T('h2', fr) + 0.2, 0.3, color=ORANGE, w=5)
        else: s.arrow((x - 50, 855), (x + 50, 855), T('h2', fr) + 0.2, 0.3, color=ORANGE, w=5)
        s.hand(word, x, 945, T('h2', fr) + 0.35, 46)
    s.person(200, 1140, 150, T('h3', 0.12))
    s.circle(200, 1140, 105, T('h3', 0.3), 0.5, color=ORANGE, w=4)
    for i, (w_, fr) in enumerate((('no preço', 0.45), ('no crédito', 0.62), ('nos seus investimentos', 0.78))):
        s.hand(w_, 370, 1085 + 58 * i, T('h3', fr), 50, anchor='lm')

    # 08 — SEU DINHEIRO
    s = S[8]
    s.rich([('E O SEU ', INK), ('DINHEIRO', ORANGE), ('?', INK)], 50, 310, T('j1', 0.0), 'DBold', 88)
    rows = [('j2', s.bank, 'JUROS ALTOS', 'Renda fixa pós-fixada', 'Tesouro Selic, CDBs, fundos DI'),
            ('j3', s.cart, 'INFLAÇÃO ALTA', 'Títulos atrelados ao IPCA', 'Tesouro IPCA+, debêntures'),
            ('j4', None, 'RISCO FISCAL', 'Dólar e exterior', 'parte da carteira em moeda forte')]
    for i, (fid, icon, lab, title, note) in enumerate(rows):
        y = 400 + 275 * i; t0 = T(fid, 0.0)
        s.rect(60, y, 900, 235, T('j1', 0.45) + 0.25 * i, 0.7, w=3.5)
        if icon == s.cart: icon(170, y + 128, 120, t0 + 0.1, items=3)
        elif icon: icon(170, y + 118, 120, t0 + 0.1)
        else:                                   # globo
            s.circle(170, y + 118, 58, t0 + 0.1, 0.4)
            s.circle(170, y + 118, 24, t0 + 0.4, 0.3, ry=57, w=3)
            s.line((112, y + 118), (228, y + 118), t0 + 0.6, 0.2, w=3)
        s.text(lab, 290, y + 58, t0 + 0.15, 'monoBold', 25, MUTED, 'lm', track=3)
        s.text(title, 290, y + 118, t0 + 0.35, 'DBold', 47, INK, 'lm')
        s.hand(note, 292, y + 180, T(fid, 0.5), 44, anchor='lm')
    s.hand('não é recomendação: depende do seu perfil', 510, 1262, T('j5', 0.25), 42, color=INK)

    # 09 — FIM (fundo escuro)
    s = S[9]; s.bg = DARK
    s.rich([('AJUSTE FISCAL', CREAM)], 70, 640, T('i1', 0.0), 'DBold', 102)
    s.rich([('NÃO É IDEOLOGIA.', CREAM)], 70, 750, T('i1', 0.2), 'DBold', 102)
    s.rich([('É ARITMÉTICA.', ORANGE)], 70, 860, T('i1', 0.62), 'DBold', 102)
    te = T('i1', 1.0)
    s.text(ASSINATURA_FIM, 70, 1000, te + 0.2, 'SemiBold', 34, CREAM, 'lm')
    s.hand('quer proteger os seus investimentos?', 70, 1150, T('i2', 0.05), 62, anchor='lm')
    s.hand('me chama no direct', 70, 1225, T('i2', 0.6), 62, color=CREAM, anchor='lm')
    for i, l in enumerate(('Fontes: Banco Central (estatísticas fiscais, set/2026;', 'Copom, nov/2026) · IBGE (IPCA, out/2026) · PLOA 2027.',
                           'Conteúdo educativo. Não é recomendação de investimento.')):
        s.text(l, 70, 1400 + 34 * i, te + 0.6, 'monoRegular', 21, (130, 118, 108), 'lm')
    return S

# ---------------- legendas ----------------
def parse_caption(txt):
    words = []; hl = False
    for i, seg in enumerate(txt.split('*')):
        for w in seg.split(): words.append((w, i % 2 == 1))
    return words
CAPF = ('Medium', 52)
def layout_caption(words):
    f = font(*CAPF); sp = f.getlength(' '); maxw = 900 * SS
    lines = [[]]; cur = 0
    for w, hl in words:
        wd = f.getlength(w)
        if lines[-1] and cur + sp + wd > maxw: lines.append([]); cur = 0
        cur += (sp if lines[-1] else 0) + wd; lines[-1].append((w, hl, wd))
    out = []; y0 = 1352 - (len(lines) - 1) * 34
    for li, ln in enumerate(lines):
        tw = sum(w[2] for w in ln) + sp * (len(ln) - 1); x = W * SS / 2 - tw / 2
        for w, hl, wd in ln: out.append((w, hl, x, (y0 + li * 68) * SS)); x += wd + sp
    return out
CAPTIONS = []
def build_captions():
    ids = [f[0] for f in FALAS]
    for i, (fid, cap, _, txt) in enumerate(FALAS):
        if not txt: continue
        t0, t1 = FT[fid]; lay = layout_caption(parse_caption(txt))
        nxt = FT[ids[i + 1]][0] if i + 1 < len(ids) and FALAS[i + 1][1] == cap else ch_end(cap)
        span = (t1 - t0) * 0.82
        CAPTIONS.append((t0 - 0.05, nxt - 0.05, [(w, hl, x, y, t0 + span * k / max(1, len(lay))) for k, (w, hl, x, y) in enumerate(lay)]))
def draw_caption(d, t):
    f = font(*CAPF)
    for a, b, ws in CAPTIONS:
        if a <= t < b:
            for w, hl, x, y, tw in ws:
                al = clamp((t - tw) / 0.22)
                if al <= 0: continue
                d.text((x, y), w, font=f, fill=mix(PAPER, ORANGE if hl else INK, al), anchor='lm')

# ---------------- moldura ----------------
def draw_chrome(d, c, t):
    tl = t - CH0[c]; a = ease(tl / 0.35)
    f = font('monoMedium', 27)
    num, name = CAPS[c]
    HY = 168 * SS
    d.line((50 * SS, HY, 72 * SS, HY), fill=mix(PAPER, ORANGE, a), width=3 * SS)
    d.text((80 * SS, HY), num, font=f, fill=mix(PAPER, ORANGE, a), anchor='lm')
    x = 150 * SS
    for ch in name:
        d.text((x, HY), ch, font=f, fill=mix(PAPER, INK, a), anchor='lm'); x += f.getlength(ch) + 4 * SS
    f2 = font('monoMedium', 22); fb = font('monoBold', 22)
    FY = 1472
    d.text((50 * SS, FY * SS), ASSINATURA, font=f2, fill=MUTED, anchor='lm')

# ---------------- render ----------------
_G = {}
def init():
    _G['S'] = build(); build_captions()
    r = np.random.default_rng(3)
    n = r.normal(0, 1, (H // 2, W // 2)).astype(np.float32)
    n = np.asarray(Image.fromarray(((n * 20) + 128).clip(0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) - 128
    fine = r.normal(0, 1.6, (H, W)).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    vig = 1 - 0.05 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    _G['tex'] = (n * 0.22 + fine)[..., None]; _G['vig'] = vig[..., None]

def frame(i):
    t = i / FPS; c = chapter(t); sc = _G['S'][c]
    im = Image.new('RGB', (W * SS, H * SS), sc.bg); d = ImageDraw.Draw(im)
    sc.draw(d, t)
    if c < NCH - 1:
        draw_chrome(d, c, t); draw_caption(d, t)
    arr = np.asarray(im.reduce(SS), np.float32)
    # transições: esmaece para o fundo no fim do capítulo; entra no escuro com fade
    out_a = clamp((ch_end(c) - t) / 0.22)
    nxt_bg = _G['S'][c + 1].bg if c + 1 < NCH else sc.bg
    if out_a < 1: arr = arr * out_a + np.array(sc.bg if nxt_bg == sc.bg else PAPER, np.float32) * (1 - out_a)
    if c == NCH - 1:
        a = ease_io((t - CH0[c]) / 0.5)
        if a < 1: arr = arr * a + np.array(PAPER, np.float32) * (1 - a)
        a2 = clamp((TOTAL - t) / 0.5)
        if a2 < 1: arr = arr * a2
    arr = (arr + _G['tex']) * _G['vig']
    return np.clip(arr, 0, 255).astype(np.uint8).tobytes()

if __name__ == '__main__':
    if '--frame' in sys.argv:
        k = sys.argv.index('--frame'); init()
        Image.frombytes('RGB', (W, H), frame(int(float(sys.argv[k + 1]) * FPS))).save(sys.argv[k + 2]); sys.exit()
    n = int(TOTAL * FPS)
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', os.path.join(OUT, 'video_mudo.mp4')], stdin=subprocess.PIPE)
    with Pool(os.cpu_count(), initializer=init) as p:
        for j, b in enumerate(p.imap(frame, range(n), chunksize=8)):
            ff.stdin.write(b)
            if j % 300 == 0: print(f'{j}/{n}', flush=True)
    ff.stdin.close(); ff.wait(); print('ok', n)
