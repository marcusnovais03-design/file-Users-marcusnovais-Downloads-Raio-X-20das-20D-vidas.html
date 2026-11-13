#!/usr/bin/env python3
"""Vídeo vertical 'Invista no seu filho' — estilo kinetic typography cinematográfico."""
import math, subprocess, sys, os
from functools import lru_cache
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
FD = '/usr/share/fonts/opentype/inter/'
CREAM = (238, 232, 220); INK = (20, 19, 21); RED = (222, 40, 54); GRAY = (178, 172, 164)

# ---------------- dados da simulação ----------------
IM = 1.10 ** (1 / 12) - 1
PMTS = [100, 500, 1000, 2500, 5000]
def series(p):
    b = [0.0]
    for _ in range(240):
        b.append(b[-1] * (1 + IM) + p)
    return np.array(b)
SER = [series(p) for p in PMTS]

def brl(x): return 'R$ ' + f'{x:,.0f}'.replace(',', '.')
def compact(v):
    if v >= 1e6:
        s = f'{v/1e6:.1f}'.replace('.', ',').replace(',0', '')
        return f'R$ {s} mi'
    if v >= 1e3: return f'R$ {v/1e3:.0f} mil'
    return f'R$ {v:.0f}'

# ---------------- roteiro / timeline ----------------
SCENES = [('s1', 3.6), ('s2', 3.2), ('s3', 4.0), ('s4', 4.4), ('s5', 3.2),
          ('c0', 6.4), ('c1', 6.4), ('c2', 6.4), ('c3', 6.4), ('c4', 6.4),
          ('s10', 5.6), ('s11', 5.0), ('s12', 5.5)]
STARTS = {}
_t = 0
for n, d in SCENES:
    STARTS[n] = _t; _t += d
TOTAL = _t
CREAM_SCENES = {'s4', 's10', 's12'}
# momentos de impacto (flash + boom)
HITS = [STARTS['s2'] + 0.45, STARTS['s3'] + 2.55, STARTS['s4'] + 2.75, STARTS['s10'] + 0.55,
        STARTS['s11'] + 3.6, STARTS['s12'] + 0.55] + [STARTS[f'c{k}'] + 4.6 for k in range(5)]

# ---------------- helpers ----------------
@lru_cache(None)
def F(weight, size): return ImageFont.truetype(f'{FD}InterDisplay-{weight}.otf', size)
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_io(x): x = clamp(x); return 0.5 - 0.5 * math.cos(math.pi * x)

@lru_cache(maxsize=256)
def rich(segs, size, weight='Bold', glow=0.5, glow_color=None):
    """segs: tuple de (texto, cor). Retorna RGBA com brilho."""
    f = F(weight, size)
    full = ''.join(s for s, _ in segs)
    asc, desc = f.getmetrics()
    tw = f.getlength(full)
    pad = int(size * 0.4) + 12
    w, h = int(tw) + 2 * pad, asc + desc + 2 * pad
    base_col = glow_color or segs[0][1]
    img = Image.new('RGBA', (w, h), base_col + (0,))
    d = ImageDraw.Draw(img)
    x = pad
    for s, c in segs:
        d.text((x, pad), s, font=f, fill=c + (255,))
        x += f.getlength(s)
    if glow > 0:
        a = img.getchannel('A').filter(ImageFilter.GaussianBlur(size * 0.16)).point(lambda v: int(v * glow))
        g = Image.new('RGBA', (w, h), base_col + (0,)); g.putalpha(a)
        g.alpha_composite(img); img = g
    return img

def T(txt, size, weight='Bold', color=CREAM, glow=0.5, glow_color=None):
    return rich(((txt, color),), size, weight, glow, glow_color)

def place(cv, img, cx, cy, tl, dur=0.45, mode='zoom', alpha=1.0, scale=1.0):
    if tl < 0 or alpha <= 0: return
    p = ease_out(tl / dur)
    s = scale; dy = 0; br = 0
    if mode == 'zoom':  s *= 1 + 0.30 * (1 - p); br = 14 * (1 - p)
    elif mode == 'rise': dy = 46 * (1 - p); br = 6 * (1 - p)
    elif mode == 'slam': s *= 1 + 1.2 * (1 - p) ** 2; br = 18 * (1 - p)
    a = alpha * clamp(tl / (dur * 0.55))
    im = img
    if abs(s - 1) > 0.004:
        im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR)
    if br > 0.7: im = im.filter(ImageFilter.GaussianBlur(br))
    if a < 0.995:
        im = im.copy(); im.putalpha(im.getchannel('A').point(lambda v: int(v * a)))
    x, y = int(cx - im.width / 2), int(cy - im.height / 2 + dy)
    cv.alpha_composite(im, (max(x, 0), max(y, 0)), (max(-x, 0), max(-y, 0)))

def highlight(cv, txt, size, cx, cy, tl, box=RED, color=CREAM):
    """Caixa que 'varre' da esquerda + texto por cima (como o marca-texto da referência)."""
    if tl < 0: return
    f = F('ExtraBold', size)
    tw = f.getlength(txt); asc, desc = f.getmetrics()
    bw, bh = int(tw + size * 0.45), int(asc * 1.02 + size * 0.12)
    p = ease_out(tl / 0.32)
    b = Image.new('RGBA', (max(1, int(bw * p)), bh), box + (255,))
    cv.alpha_composite(b, (int(cx - bw / 2), int(cy - bh / 2 + size * 0.04)))
    place(cv, T(txt, size, 'ExtraBold', color, glow=0), cx, cy, tl - 0.12, 0.35, 'zoom')

# ---------------- texturas pré-calculadas ----------------
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
_r = np.sqrt(((xx - W / 2) / (W * 0.72)) ** 2 + ((yy - H / 2) / (H * 0.60)) ** 2)
VIG = np.clip(1 - 0.62 * _r ** 2.0, 0.18, 1)[..., None].astype(np.float32)
_sy, _sx = np.mgrid[0:2 * H:2, 0:2 * W:2].astype(np.float32)
_spot_half = np.exp(-(((_sx - W) / 520) ** 2 + ((_sy - H) / 640) ** 2))
SPOT = np.repeat(np.repeat(_spot_half, 2, 0), 2, 1).astype(np.float32)   # 2H x 2W, centrado em (W,H)
del _sx, _sy, _spot_half
rng = np.random.default_rng(7)
GRAIN = [np.repeat(np.repeat(rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32), 2, 0), 2, 1) for _ in range(6)]
PAPER = (1 - 0.035 * np.clip(np.repeat(np.repeat(rng.normal(0, 1, (H // 4, W // 4)), 4, 0), 4, 1), -2, 2)
         ).astype(np.float32)[..., None]
_beam = Image.new('L', (W, H), 0)
ImageDraw.Draw(_beam).polygon([(W * 0.62, -50), (W * 0.86, -50), (W * 0.35, H + 50), (-W * 0.25, H + 50)], fill=255)
BEAM = (np.asarray(_beam.filter(ImageFilter.GaussianBlur(90)), np.float32) / 255)[..., None]
PART = rng.random((55, 5))   # partículas de poeira: x, y, vx, vy, tamanho

def spot(cx, cy):
    cx, cy = int(clamp(cx, 0, W)), int(clamp(cy, 0, H))
    return SPOT[H - cy:2 * H - cy, W - cx:2 * W - cx][..., None]

def background(name, t, tl):
    if name in CREAM_SCENES:
        sp = spot(W * 0.5 + 120 * math.sin(t * 0.4), H * 0.38 + 80 * math.cos(t * 0.3))
        arr = np.array(CREAM, np.float32) * PAPER * (0.90 + 0.12 * sp)
        return arr
    sp = spot(W * (0.5 + 0.18 * math.sin(t * 0.35 + len(name))), H * (0.42 + 0.1 * math.cos(t * 0.27)))
    arr = np.full((H, W, 3), 9, np.float32) + sp * np.array([60, 57, 54], np.float32)
    if name in ('s1', 's3', 's11', 's5'):
        arr += BEAM * np.array([34, 32, 30], np.float32) * (0.75 + 0.25 * math.sin(t * 1.3))
    if name in ('s2', 's11'):   # brilho vermelho de fundo
        arr += spot(W * 0.5, H * 0.55) * np.array([38, 4, 6], np.float32)
    return arr

def particles(t):
    im = Image.new('L', (W // 2, H // 2), 0); d = ImageDraw.Draw(im)
    for x0, y0, vx, vy, s in PART:
        x = ((x0 + (vx - 0.5) * 0.02 * t) % 1) * W / 2
        y = ((y0 - (0.2 + vy) * 0.015 * t) % 1) * H / 2
        r = 0.6 + s * 2.2
        d.ellipse((x - r, y - r, x + r, y + r), fill=int(70 + 120 * s))
    im = im.filter(ImageFilter.GaussianBlur(1.2)).resize((W, H), Image.BILINEAR)
    return (np.asarray(im, np.float32) / 255)[..., None]

# ---------------- cenas ----------------
def scene_s1(cv, tl):
    place(cv, T('seu filho', 120, 'ExtraBold'), W / 2, 760, tl - 0.10)
    place(cv, T('pode completar', 78, 'Medium', glow=0.3), W / 2, 885, tl - 0.85, mode='rise')
    place(cv, T('20 anos', 210, 'Black'), W / 2, 1080, tl - 1.75, mode='slam')

def scene_s2(cv, tl):
    place(cv, T('com mais de', 72, 'Medium', glow=0.3), W / 2, 640, tl - 0.05, mode='rise')
    place(cv, T('R$ 3,5', 250, 'Black', RED, 0.9, RED), W / 2, 880, tl - 0.45, mode='slam')
    place(cv, T('MILHÕES', 160, 'Black'), W / 2, 1080, tl - 0.95)
    place(cv, T('no nome dele.', 66, 'Medium', glow=0.3), W / 2, 1270, tl - 1.75, mode='rise')

def clock(cv, tl):
    cx, cy, R = W / 2, 1000, 330
    a = clamp(tl / 0.6) * 0.55
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    col = CREAM + (int(255 * a),)
    d.ellipse((cx - R, cy - R, cx + R, cy + R), outline=col, width=3)
    for k in range(60):
        ang = k * math.pi / 30; l = 34 if k % 5 == 0 else 14
        d.line([(cx + (R - 14) * math.sin(ang), cy - (R - 14) * math.cos(ang)),
                (cx + (R - 14 - l) * math.sin(ang), cy - (R - 14 - l) * math.cos(ang))], fill=col, width=4 if k % 5 == 0 else 2)
    m = tl * 2.4; hh = tl * 0.2
    d.line([(cx, cy), (cx + 260 * math.sin(m), cy - 260 * math.cos(m))], fill=col, width=6)
    d.line([(cx, cy), (cx + 170 * math.sin(hh), cy - 170 * math.cos(hh))], fill=col, width=10)
    d.ellipse((cx - 12, cy - 12, cx + 12, cy + 12), fill=RED + (int(255 * a / 0.55),))
    cv.alpha_composite(im.filter(ImageFilter.GaussianBlur(1.0)))

def scene_s3(cv, tl):
    clock(cv, tl)
    place(cv, T('o segredo', 96, 'ExtraBold'), W / 2, 420, tl - 0.10)
    place(cv, T('não é dinheiro.', 80, 'Medium', glow=0.3), W / 2, 535, tl - 1.0, mode='rise')
    place(cv, T('é', 80, 'Medium', glow=0.3), W / 2, 1480, tl - 2.15, mode='rise')
    place(cv, T('TEMPO.', 230, 'Black', RED, 0.9, RED), W / 2, 1640, tl - 2.55, mode='slam')

def scene_s4(cv, tl):
    place(cv, T('quando você', 88, 'Medium', INK, 0), W / 2, 520, tl - 0.05, mode='rise')
    place(cv, T('começa cedo,', 118, 'ExtraBold', INK, 0), W / 2, 640, tl - 0.55)
    place(cv, T('quem trabalha pesado', 86, 'Bold', INK, 0), W / 2, 880, tl - 1.3, mode='rise')
    place(cv, T('são os', 62, 'Medium', INK, 0), W / 2, 1080, tl - 2.25, mode='rise')
    highlight(cv, 'JUROS', 200, W / 2, 1240, tl - 2.75)
    place(cv, T('COMPOSTOS', 138, 'Black', INK, 0), W / 2, 1440, tl - 3.15)

def scene_s5(cv, tl):
    place(cv, T('faz a conta comigo:', 70, 'Medium', glow=0.3), W / 2, 700, tl - 0.05, mode='rise')
    place(cv, T('20 anos', 200, 'Black'), W / 2, 900, tl - 0.75, mode='slam')
    place(cv, T('10% ao ano', 130, 'ExtraBold', RED, 0.8, RED), W / 2, 1100, tl - 1.45)
    place(cv, T('aportes todo mês', 54, 'Medium', GRAY, 0.2), W / 2, 1260, tl - 2.1, mode='rise')

# ---- gráfico ----
PX0, PX1, PY0, PY1 = 190, 1000, 640, 1300
BY0, BY1 = 600, 1340          # faixa supersampled
def nice_step(v):
    raw = v / 4; e = 10 ** math.floor(math.log10(raw))
    for m in (1, 2, 2.5, 5, 10):
        if m * e >= raw: return m * e

def draw_grid(cv, ymax, alpha):
    if alpha <= 0.01: return
    ov = Image.new('RGBA', cv.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov); st = nice_step(ymax / 1.12); f = F('Medium', 26)
    v = st
    while v < ymax * 0.97:
        y = PY1 - (PY1 - PY0) * v / ymax
        d.line([(PX0, y), (PX1, y)], fill=(255, 255, 255, int(48 * alpha)), width=2)
        lab = compact(v); d.text((PX0 - 16 - f.getlength(lab), y - 15), lab, font=f, fill=GRAY + (int(200 * alpha),))
        v += st
    cv.alpha_composite(ov)

def scene_chart(cv, tl, k):
    p = PMTS[k]; s = SER[k]; final = s[-1]
    prev_max = (SER[k - 1][-1] if k > 0 else final * 1.6) * 1.12
    tgt = final * 1.12
    q = ease_io(tl / 0.9)
    ymax = prev_max + (tgt - prev_max) * q
    # cabeçalho
    place(cv, T('SIMULAÇÃO  ·  20 ANOS  ·  10% a.a.', 30, 'SemiBold', GRAY, 0), W / 2, 215, tl, 0.3, 'rise', 0.8)
    place(cv, T(f'R$ {p:,}'.replace(',', '.'), 175, 'Black'), W / 2, 345, tl - 0.08, mode='slam')
    place(cv, T('por mês', 56, 'Medium', CREAM, 0.3), W / 2, 485, tl - 0.35, mode='rise')
    # grid (cross-fade entre escalas)
    draw_grid(cv, ymax, 1 - q if k > 0 else 0)
    draw_grid(cv, ymax, q if k > 0 else clamp(tl / 0.5))
    ov = Image.new('RGBA', cv.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    d.line([(PX0, PY1), (PX1, PY1)], fill=(255, 255, 255, 90), width=2)
    f = F('Medium', 28)
    for yr in (0, 5, 10, 15, 20):
        x = PX0 + (PX1 - PX0) * yr / 20; lab = str(yr)
        d.text((x - f.getlength(lab) / 2, PY1 + 16), lab, font=f, fill=GRAY + (220,))
    lab = 'idade do seu filho (anos)'; f2 = F('Medium', 26)
    d.text((W / 2 - f2.getlength(lab) / 2 + 40, PY1 + 58), lab, font=f2, fill=GRAY + (150,))
    cv.alpha_composite(ov)
    # camadas 2x
    S2 = 2
    lay = Image.new('RGBA', (W * S2, (BY1 - BY0) * S2), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
    line = Image.new('RGBA', lay.size, (0, 0, 0, 0)); dn = ImageDraw.Draw(line)
    def P(m, v): return (S2 * (PX0 + (PX1 - PX0) * m / 240), S2 * (PY1 - (PY1 - PY0) * v / ymax - BY0))
    for j in range(k):   # curvas anteriores "achatando"
        dl.line([P(m, SER[j][m]) for m in range(0, 241, 2)], fill=(150, 145, 138, 150), width=5, joint='curve')
    prog = ease_io((tl - 0.6) / 4.0)
    mm = 240 * prog
    if mm > 0.5:
        n = int(mm); fr = mm - n
        vend = s[n] + (s[min(n + 1, 240)] - s[n]) * fr
        ms = list(range(0, n + 1)) + [mm]
        curve = [P(m, s[m]) for m in range(n + 1)] + [P(mm, vend)]
        inv = [P(m, p * m) for m in ms]
        dl.polygon(curve + inv[::-1], fill=RED + (95,))
        dl.polygon(inv + [P(mm, 0), P(0, 0)], fill=(235, 228, 215, 34))
        dl.line(inv, fill=(200, 194, 184, 150), width=4)
        dn.line(curve, fill=CREAM + (255,), width=9, joint='curve')
        tx, ty = curve[-1]
        pulse = 0.5 + 0.5 * math.sin(tl * 7)
        rr = 22 + 10 * pulse
        dn.ellipse((tx - rr, ty - rr, tx + rr, ty + rr), outline=RED + (int(160 + 90 * pulse),), width=5)
        dn.ellipse((tx - 12, ty - 12, tx + 12, ty + 12), fill=CREAM + (255,))
    else:
        vend = 0
    lay = lay.reduce(2); line = line.reduce(2)
    glow = line.filter(ImageFilter.GaussianBlur(9))
    cv.alpha_composite(lay, (0, BY0)); cv.alpha_composite(glow, (0, BY0)); cv.alpha_composite(line, (0, BY0))
    # contador
    place(cv, T('seu filho terá', 42, 'Medium', GRAY, 0.2), W / 2, 1490, tl - 0.5, mode='rise')
    pop = 1 + 0.12 * math.exp(-max(tl - 4.6, 0) / 0.12) * (tl >= 4.6)
    place(cv, T(brl(vend), 132, 'Black', CREAM, 0.9, RED), W / 2, 1610, 10 if tl > 0.7 else tl - 0.2, scale=pop)
    juros = final - p * 240
    segs = (('investido ', GRAY), (brl(p * 240), CREAM), ('   ·   ', GRAY), ('juros ', GRAY), (brl(juros), RED))
    place(cv, rich(segs, 36, 'SemiBold', 0), W / 2, 1735, tl - 4.75, mode='rise')
    place(cv, T('Simulação hipotética · 10% a.a. · sem IR, taxas e inflação · não é garantia de rentabilidade',
                23, 'Medium', GRAY, 0), W / 2, 1845, tl, 0.3, 'rise', 0.8)

def scene_s10(cv, tl):
    place(cv, T('em todos os cenários', 66, 'Medium', INK, 0), W / 2, 430, tl - 0.05, mode='rise')
    place(cv, T('2/3', 400, 'Black', RED, 0), W / 2, 740, tl - 0.55, mode='slam')
    place(cv, T('do valor final', 84, 'Bold', INK, 0), W / 2, 1010, tl - 1.3, mode='rise')
    place(cv, T('veio dos juros.', 84, 'ExtraBold', INK, 0), W / 2, 1110, tl - 1.75, mode='rise')
    # barra
    if tl > 2.0:
        x0, x1, y, h = 110, 970, 1300, 76; wtot = x1 - x0
        q = ease_io((tl - 2.0) / 1.3)
        ov = Image.new('RGBA', cv.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        frac_inv = 24000 / SER[0][-1]
        d.rectangle((x0, y, x1, y + h), outline=INK + (90,), width=2)
        a = min(q / frac_inv, 1) * frac_inv
        d.rectangle((x0, y, x0 + wtot * a, y + h), fill=(110, 105, 100, 255))
        if q > frac_inv:
            d.rectangle((x0 + wtot * frac_inv, y, x0 + wtot * q, y + h), fill=RED + (255,))
        cv.alpha_composite(ov)
        place(cv, T(f'seu bolso {frac_inv*100:.0f}%', 38, 'SemiBold', INK, 0), x0 + wtot * frac_inv / 2, y + h + 50, tl - 2.6, mode='rise')
        place(cv, T(f'juros {(1-frac_inv)*100:.0f}%', 38, 'Bold', RED, 0), x0 + wtot * (frac_inv + 1) / 2, y + h + 50, tl - 3.2, mode='rise')
    highlight(cv, 'não do seu bolso.', 82, W / 2, 1590, tl - 4.1, box=INK, color=CREAM)

def scene_s11(cv, tl):
    place(cv, T('o melhor dia pra começar', 72, 'Medium', glow=0.3), W / 2, 600, tl - 0.05, mode='rise')
    place(cv, T('foi quando ele nasceu.', 84, 'ExtraBold'), W / 2, 715, tl - 1.0)
    place(cv, T('o segundo melhor?', 72, 'Medium', glow=0.3), W / 2, 1040, tl - 2.5, mode='rise')
    place(cv, T('HOJE.', 280, 'Black', RED, 0.9, RED), W / 2, 1250, tl - 3.6, mode='slam')

def scene_s12(cv, tl):
    place(cv, T('comenta', 104, 'ExtraBold', INK, 0), W / 2, 640, tl - 0.05)
    highlight(cv, 'FILHO', 210, W / 2, 830, tl - 0.55)
    place(cv, T('que eu te mando', 80, 'Medium', INK, 0), W / 2, 1040, tl - 1.3, mode='rise')
    place(cv, T('a simulação', 100, 'ExtraBold', INK, 0), W / 2, 1145, tl - 1.75, mode='rise')
    place(cv, T('do seu caso.', 100, 'ExtraBold', INK, 0), W / 2, 1255, tl - 2.15, mode='rise')
    place(cv, T('Marcus Novais', 52, 'SemiBold', INK, 0), W / 2, 1420, tl - 2.7, mode='rise')
    place(cv, T('@mnovais', 92, 'Black', RED, 0), W / 2, 1510, tl - 2.95, mode='zoom')
    for i, ln in enumerate(['Simulação hipotética: aportes mensais por 240 meses à taxa de 10% a.a.',
                            '(≈0,797% a.m.), sem considerar IR, taxas e inflação. Não representa',
                            'promessa ou garantia de rentabilidade futura.']):
        place(cv, T(ln, 25, 'Medium', (90, 86, 82), 0), W / 2, 1640 + i * 36, tl - 0.4, 0.4, 'rise')

DRAW = {'s1': scene_s1, 's2': scene_s2, 's3': scene_s3, 's4': scene_s4, 's5': scene_s5,
        's10': scene_s10, 's11': scene_s11, 's12': scene_s12}
for _k in range(5):
    DRAW[f'c{_k}'] = (lambda kk: (lambda cv, tl: scene_chart(cv, tl, kk)))(_k)

# ---------------- frame ----------------
def frame(fi):
    t = fi / FPS
    for name, dur in SCENES:
        if STARTS[name] <= t < STARTS[name] + dur or name == 's12': break
    tl = t - STARTS[name]
    cream = name in CREAM_SCENES
    bg = background(name, t, tl)
    if not cream:
        bg += particles(t) * 70
    cv = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).convert('RGBA')
    DRAW[name](cv, tl)
    if name != 's12':   # assinatura fixa em todo o vídeo
        c1 = INK if cream else CREAM
        segs = (('Marcus Novais', c1), ('  ·  ', RED), ('@mnovais', c1))
        place(cv, rich(segs, 36, 'SemiBold', 0 if cream else 0.35), W / 2, 140, 10, alpha=0.9)
    img = cv.convert('RGB')
    # câmera: zoom lento
    z = 1.0 + 0.05 * ease_io(tl / dur)
    if z > 1.001:
        cw, chh = W / z, H / z
        img = img.resize((W, H), Image.BILINEAR, box=((W - cw) / 2, (H - chh) / 2, (W + cw) / 2, (H + chh) / 2))
    # transição: smear horizontal + flash
    kin = clamp(1 - tl / 0.24) ** 2 if name != 's1' else 0
    kout = clamp(1 - (dur - tl) / 0.12) ** 2 if name != 's12' else 0
    k = max(kin, kout)
    if k > 0.01:
        sw = max(8, int(W / (1 + 40 * k)))
        img = img.resize((sw, H), Image.BILINEAR).resize((W, H), Image.BILINEAR)
    arr = np.asarray(img, np.float32).copy()
    sh = int(round(3 + 18 * k))
    arr[..., 0] = np.roll(arr[..., 0], sh, axis=1)
    arr[..., 2] = np.roll(arr[..., 2], -sh, axis=1)
    fl = sum(math.exp(-(t - h) / 0.14) for h in HITS if 0 <= t - h < 1)
    arr += (70 * kin + 55 * fl) * (0.4 if cream else 1)
    arr *= (VIG * (0.55 if cream else 1) + (0.45 if cream else 0))
    arr *= 1 + 0.018 * math.sin(t * 41) * math.sin(t * 13)
    arr += GRAIN[fi % 6][..., None] * (7 if cream else 10)
    if t < 0.35: arr *= t / 0.35
    if t > TOTAL - 0.4: arr *= max(0, (TOTAL - t) / 0.4)
    return np.clip(arr, 0, 255).astype(np.uint8).tobytes()

if __name__ == '__main__':
    out = sys.argv[1]
    only = sys.argv[2:]   # frames de teste
    if only:
        for s in only:
            fi = int(float(s) * FPS)
            Image.frombytes('RGB', (W, H), frame(fi)).save(f'{out}_{s}.png')
        sys.exit()
    n = int(TOTAL * FPS)
    ff = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                           '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
                           '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    with Pool(4) as pool:
        for i, b in enumerate(pool.imap(frame, range(n), chunksize=4)):
            ff.stdin.write(b)
            if i % 150 == 0: print(i, '/', n, flush=True)
    ff.stdin.close(); ff.wait()
    print('done', TOTAL)
