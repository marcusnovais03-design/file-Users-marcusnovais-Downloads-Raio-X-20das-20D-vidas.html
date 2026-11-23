import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../modelo"))
from marcus_slides import *

OUT = os.path.dirname(os.path.abspath(__file__)) + "/"
SW, SH = 1080, 1920
FOTO = "/tmp/claude-0/-home-user-file-Users-marcusnovais-Downloads-Raio-X-20das-20D-vidas-html/ccc5c897-030e-52c5-8b6f-200b11dcfafa/images/1.jpg"

img = Image.new("RGBA", (SW, SH), NAVY_BG); d = ImageDraw.Draw(img)
for x in range(0, SW, 54): d.line([(x, 0), (x, SH)], fill=NAVY_GRID)
for y in range(0, SH, 54): d.line([(0, y), (SW, y)], fill=NAVY_GRID)

# foto na parte de baixo, inteira e com transparência mínima (só a borda de cima se funde ao fundo)
p = Image.open(FOTO).convert("RGB"); p = p.resize((SW, int(p.height * SW / p.width)), Image.LANCZOS)
PY = 1060
crop = p.crop((0, 40, SW, 40 + SH - PY)).convert("RGBA")
mask = Image.new("L", crop.size, 255); md = ImageDraw.Draw(mask)
for yy in range(160):
    md.line([(0, yy), (SW, yy)], fill=int(255 * (yy / 160) ** 1.3))
img.paste(crop, (0, PY), mask)
d = ImageDraw.Draw(img)

layer = Image.new("RGBA", (SW, SH), (0, 0, 0, 0)); t = ImageDraw.Draw(layer)
y = kicker_pill(t, "Economia", 92, 250)
y = rich(t, "Crescer pouco com [r]inflação alta[/r]", 90, y + 4, 900, TITLE(84), TITLE(84), 82,
         WHITE, GOLD_DARK, RED_DARK, tracking=-3, upper=True)

ty = y + 26; tw = 433; th = 230
lab = font("Inter-Bold.otf", 30); big = font("InterDisplay-Black.otf", 96); sub = font("Inter-SemiBold.otf", 27)
for i, (title, val, note, col, arrow) in enumerate([
        ("PIB 2026", "1,8%", "antes: 2,0%", GOLD_DARK, "down"),
        ("Inflação 2026", "5,2%", "acima da meta", RED_DARK, "up")]):
    x0 = 92 + i * (tw + 30)
    t.rounded_rectangle((x0, ty, x0 + tw, ty + th), radius=26, fill=(16, 24, 52, 255), outline=(42, 50, 80, 255), width=2)
    t.text((x0 + 30, ty + 24), title, font=lab, fill=WHITE)
    t.text((x0 + 28, ty + 68), val, font=big, fill=col)
    ax, ay = x0 + tw - 46, ty + 44
    if arrow == "down": t.polygon([(ax - 22, ay - 10), (ax + 22, ay - 10), (ax, ay + 24)], fill=col)
    else: t.polygon([(ax - 22, ay + 12), (ax + 22, ay + 12), (ax, ay - 22)], fill=col)
    t.text((x0 + 30, ty + 182), note, font=sub, fill=(170, 176, 198))

y = ty + th + 34
y = rich(t, "Na prática: seu patrimônio cresce pouco e o custo de vida sobe. É o [g]pior dos mundos para quem não se protege[/g].",
         92, y, 896, font("Inter-Regular.otf", 38), font("Inter-Bold.otf", 38), 50, BODY_DARK, GOLD_DARK, RED_DARK, bold_color=WHITE)

hint = font("Inter-ExtraBold.otf", 40); q = "Seu patrimônio acompanhou a inflação?"
t.text((92, y + 34), q, font=hint, fill=WHITE)
emoji(layer, "👇", 92 + hint.getlength(q) + 12, y + 36, 46)
ff = font("Inter-Bold.otf", 28); nm = "Marcus Novais | Planejador Financeiro, CFP®"
t.rounded_rectangle((76, 1676, 108 + ff.getlength(nm), 1730), radius=27, fill=(7, 13, 36, 200))
t.text((92, 1688), nm, font=ff, fill=WHITE)
print("texto termina em", y)
sh = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
sh.putalpha(layer.split()[3].filter(ImageFilter.GaussianBlur(10)).point(lambda a: int(a * 0.8)))
img.alpha_composite(sh); img.alpha_composite(layer)
img.convert("RGB").save(OUT + "story.png", quality=95)
