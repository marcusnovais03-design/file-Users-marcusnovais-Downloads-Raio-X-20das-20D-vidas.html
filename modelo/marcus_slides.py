"""Gerador de slides no modelo oficial do Marcus Novais (referência: carrossel "Apocalipse empresarial").

Marcação de texto rico (títulos e corpo):
  [g]texto[/g]  -> destaque dourado
  [r]texto[/r]  -> destaque vermelho
  **texto**     -> negrito (corpo)
Use "\n" no corpo para separar parágrafos.
"""
import re
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1350
F = "/usr/share/fonts/opentype/inter/"
HERE = __file__.rsplit("/", 1)[0]
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"

# Paleta (amostrada dos slides de referência)
NAVY_BG = (7, 13, 36)
NAVY_GRID = (16, 23, 48)
LIGHT_BG = (242, 239, 232)
LIGHT_GRID = (226, 223, 217)
NAVY_TXT = (19, 32, 92)
BODY_LIGHT = (48, 58, 100)
GOLD_DARK = (227, 182, 90)    # dourado em fundo escuro
GOLD_LIGHT = (168, 116, 30)   # dourado em fundo claro
RED = (227, 20, 30)
WHITE = (255, 255, 255)
BODY_DARK = (220, 223, 232)
DIVIDER_DARK = (42, 47, 66)
DIVIDER_LIGHT = (205, 203, 200)
FOOTER = "Marcus Novais | Planejador Financeiro, CFP®"


def font(name, size):
    return ImageFont.truetype(F + name, size)


TITLE = lambda s: font("InterDisplay-Black.otf", s)
KICK = font("Inter-ExtraBold.otf", 30)
BODY = font("Inter-Regular.otf", 40)
BODY_B = font("Inter-Bold.otf", 40)
FOOT = font("Inter-Bold.otf", 25)
SWIPE = font("Inter-Bold.otf", 28)
COUNT = font("Inter-ExtraBold.otf", 27)


def spaced(d, xy, text, f, fill, tracking):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=f, fill=fill)
        x += f.getlength(ch) + tracking
    return x


def spaced_len(text, f, tracking):
    return sum(f.getlength(c) for c in text) + tracking * (len(text) - 1)


def parse(text, base, gold, red, bold_color=None):
    """-> list of (word, color, bold, trailing_space)"""
    toks = re.split(r"(\[g\]|\[/g\]|\[r\]|\[/r\]|\*\*)", text)
    color, bold, out = base, False, []
    for t in toks:
        if t == "[g]": color = gold
        elif t == "[r]": color = red
        elif t in ("[/g]", "[/r]"): color = base
        elif t == "**": bold = not bold
        elif t:
            parts = re.split(r"( )", t)
            for p in parts:
                if p == " ":
                    if out: out[-1][3] = True
                elif p:
                    c = color if (color != base or not bold or bold_color is None) else bold_color
                    out.append([p, c, bold, False])
    return out


def rich(d, text, x, y, maxw, f_reg, f_bold, lh, base, gold, red, bold_color=None, tracking=0, upper=False):
    if upper:
        text = re.sub(r"(\[/?[gr]\])|([^\[]+)", lambda m: m.group(1) or m.group(2).upper(), text)
    words = parse(text, base, gold, red, bold_color)
    gap = 8 if tracking < 0 else 0
    # group words glued without space (e.g. "dólar" + ".") into unbreakable units
    units, u = [], []
    for wd in words:
        u.append(wd)
        if wd[3]: units.append(u); u = []
    if u: units.append(u)
    lines, cur, w = [], [], 0
    for un in units:
        uw = sum(spaced_len(wd[0], f_bold if wd[2] else f_reg, tracking) for wd in un)
        last = un[-1]; lf = f_bold if last[2] else f_reg
        sp = lf.getlength(" ") + tracking + gap
        need = uw if not cur else w + uw
        if cur and need > maxw:
            lines.append(cur); cur, w = [], 0; need = uw
        cur.extend(un); w = need + (sp if last[3] else 0)
    if cur: lines.append(cur)
    for ln in lines:
        cx = x
        for wd in ln:
            f = f_bold if wd[2] else f_reg
            cx = spaced(d, (cx, y), wd[0], f, wd[1], tracking)
            if wd[3]: cx += f.getlength(" ") + tracking + gap
        y += lh
    return y


def emoji(img, ch, x, y, size):
    try:
        ef = ImageFont.truetype(EMOJI, 109)
        e = Image.new("RGBA", (140, 140), (0, 0, 0, 0))
        ImageDraw.Draw(e).text((0, 0), ch, font=ef, embedded_color=True)
        e = e.crop(e.getbbox()).resize((size, size), Image.LANCZOS)
        img.alpha_composite(e, (int(x), int(y)))
    except Exception:
        pass


def background(dark):
    img = Image.new("RGBA", (W, H), NAVY_BG if dark else LIGHT_BG)
    d = ImageDraw.Draw(img)
    g = NAVY_GRID if dark else LIGHT_GRID
    for x in range(0, W, 54): d.line([(x, 0), (x, H)], fill=g, width=1)
    for y in range(0, H, 54): d.line([(0, y), (W, y)], fill=g, width=1)
    return img


def photo_bg(photo, fade_from, fade_to):
    img = Image.new("RGBA", (W, H), (10, 16, 40))
    p = Image.open(photo).convert("RGBA")
    img.alpha_composite(p, (0, 0))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for y in range(H):
        if y < fade_from: a = 0
        elif y < fade_to: a = int(255 * ((y - fade_from) / (fade_to - fade_from)) ** 1.2)
        else: a = 255
        t = y / H
        d.line([(0, y), (W, y)], fill=(int(14 - 6 * t), int(22 - 8 * t), int(52 - 14 * t), a))
    img.alpha_composite(ov)
    return img


def chrome(img, n, total, dark, swipe=True):
    d = ImageDraw.Draw(img)
    c = WHITE if dark else NAVY_TXT
    lab = f"{n:02d}/{total:02d}"
    spaced(d, (990 - spaced_len(lab, COUNT, 2), 60), lab, COUNT, c, 2)
    d.text((90, 1257), FOOTER, font=FOOT, fill=c)
    if swipe:
        sw = "deslize"; tw = SWIPE.getlength(sw)
        d.text((934 - tw, 1254), sw, font=SWIPE, fill=c)
        d.line([(952, 1272), (986, 1272)], fill=c, width=4)
        d.line([(972, 1259), (986, 1272), (972, 1285)], fill=c, width=4, joint="curve")


def kicker(d, text, x, y, color):
    spaced(d, (x, y), text.upper(), KICK, color, 6)
    return y + 52


def cover(path, n, total, kick, title, sub=None, sub_emoji="👉", photo=None, title_size=92):
    img = photo_bg(photo or HERE + "/fotos/marcus-capa.png", 380, 598)
    d = ImageDraw.Draw(img)
    # layout bottom-up: measure title lines first
    tmp = Image.new("RGBA", (W, H)); td = ImageDraw.Draw(tmp)
    lh = int(title_size * 0.98)
    th = rich(td, title, 90, 0, 900, TITLE(title_size), TITLE(title_size), lh, WHITE, GOLD_DARK, RED, tracking=-3, upper=True)
    y0 = 1100 - th - (60 if sub else 0)
    kicker(d, kick, 92, y0 - 62, RED)
    y = rich(d, title, 90, y0, 900, TITLE(title_size), TITLE(title_size), lh, WHITE, GOLD_DARK, RED, tracking=-3, upper=True)
    if sub:
        sf = font("Inter-Light.otf", 42)
        d.text((92, y + 30), sub, font=sf, fill=(225, 228, 238))
        if sub_emoji: emoji(img, sub_emoji, 92 + sf.getlength(sub) + 14, y + 32, 46)
    chrome(img, n, total, True)
    img.convert("RGB").save(path, quality=95)


def text_slide(path, n, total, kick, title, body, dark=False, title_size=74, extra=None):
    img = background(dark); d = ImageDraw.Draw(img)
    gold = GOLD_DARK if dark else GOLD_LIGHT
    base_t = WHITE if dark else NAVY_TXT
    base_b = BODY_DARK if dark else BODY_LIGHT
    bold_c = WHITE if dark else NAVY_TXT
    # measure
    tmp = ImageDraw.Draw(Image.new("RGBA", (W, H)))
    def draw(dd, y):
        y = kicker(dd, kick, 92, y, gold)
        y = rich(dd, title, 90, y, 920, TITLE(title_size), TITLE(title_size), int(title_size * 0.98), base_t, gold, RED, tracking=-3, upper=True)
        y += 22
        for para in body.split("\n"):
            y = rich(dd, para.strip(), 90, y, 900, BODY, BODY_B, 52, base_b, gold, RED, bold_color=bold_c)
            y += 26
        return y
    hgt = draw(tmp, 0) + (extra[1] if extra else 0)
    y = draw(d, max(260, (H - hgt) // 2 - 40))
    if extra: extra[0](img, d, y)
    chrome(img, n, total, dark)
    img.convert("RGB").save(path, quality=95)


def bullets_slide(path, n, total, kick, title, items, dark=True, title_size=74):
    img = background(dark); d = ImageDraw.Draw(img)
    gold = GOLD_DARK if dark else GOLD_LIGHT
    base_t = WHITE if dark else NAVY_TXT
    base_b = BODY_DARK if dark else BODY_LIGHT
    bold_c = WHITE if dark else NAVY_TXT
    div = DIVIDER_DARK if dark else DIVIDER_LIGHT
    BF, BFB = font("Inter-Regular.otf", 37), font("Inter-Bold.otf", 37)
    def draw(dd, y):
        y = kicker(dd, kick, 92, y, gold)
        y = rich(dd, title, 90, y, 920, TITLE(title_size), TITLE(title_size), int(title_size * 0.98), base_t, gold, RED, tracking=-3, upper=True)
        y += 34
        for it in items:
            if dd is not tmp: dd.ellipse((90, y + 12, 116, y + 38), fill=gold)
            y = rich(dd, it, 147, y, 845, BF, BFB, 46, base_b, gold, RED, bold_color=bold_c) + 18
            if dd is not tmp: dd.line([(90, y), (990, y)], fill=div, width=2)
            y += 26
        return y
    tmp = ImageDraw.Draw(Image.new("RGBA", (W, H)))
    hgt = draw(tmp, 0)
    draw(d, max(260, (H - hgt) // 2 - 40))
    chrome(img, n, total, dark)
    img.convert("RGB").save(path, quality=95)


def cta(path, n, total, title, button="Acesse o link na BIO e me chame", photo=None, title_size=80):
    img = photo_bg(photo or HERE + "/fotos/marcus-cta.png", 480, 780)
    d = ImageDraw.Draw(img)
    tmp = ImageDraw.Draw(Image.new("RGBA", (W, H)))
    lh = int(title_size * 0.98)
    th = rich(tmp, title, 90, 0, 900, TITLE(title_size), TITLE(title_size), lh, WHITE, GOLD_DARK, RED, tracking=-3, upper=True)
    y = rich(d, title, 90, 1080 - th, 900, TITLE(title_size), TITLE(title_size), lh, WHITE, GOLD_DARK, RED, tracking=-3, upper=True)
    bf = font("Inter-ExtraBold.otf", 34)
    bw = bf.getlength(button) + 66
    d.rounded_rectangle((90, y + 28, 90 + bw, y + 112), radius=18, fill=GOLD_DARK)
    d.text((123, y + 49), button, font=bf, fill=(20, 22, 30))
    chrome(img, n, total, True, swipe=False)
    img.convert("RGB").save(path, quality=95)
