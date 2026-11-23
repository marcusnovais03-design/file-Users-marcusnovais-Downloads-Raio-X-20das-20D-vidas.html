import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../modelo"))
import marcus_slides as M
from marcus_slides import *

OUT = os.path.dirname(os.path.abspath(__file__)) + "/"
SW, SH = 1080, 1920

img = Image.new("RGBA", (SW, SH), NAVY_BG); d = ImageDraw.Draw(img)
for x in range(0, SW, 54): d.line([(x, 0), (x, SH)], fill=NAVY_GRID)
for y in range(0, SH, 54): d.line([(0, y), (SW, y)], fill=NAVY_GRID)

y = kicker_pill(d, "Economia", 92, 300)
y = rich(d, "Crescer pouco com [r]inflação alta[/r]", 90, y + 6, 900, TITLE(96), TITLE(96), 94,
         WHITE, GOLD_DARK, RED_DARK, tracking=-3, upper=True)
y = rich(d, "O Banco Central cortou a projeção do PIB e vê a inflação em **5,2%** no fim de 2026.", 92, y + 24, 896,
         font("Inter-Regular.otf", 42), font("Inter-Bold.otf", 42), 56, BODY_DARK, GOLD_DARK, RED_DARK, bold_color=WHITE)

# two stat tiles
ty = y + 50; tw = 433; th = 300
lab = font("Inter-Bold.otf", 34); big = font("InterDisplay-Black.otf", 108); sub = font("Inter-SemiBold.otf", 30)
for i, (title, val, note, col, arrow) in enumerate([
        ("PIB 2026", "1,8%", "antes: 2,0%", GOLD_DARK, "down"),
        ("Inflação 2026", "5,2%", "acima da meta", RED_DARK, "up")]):
    x0 = 92 + i * (tw + 30)
    d.rounded_rectangle((x0, ty, x0 + tw, ty + th), radius=28, fill=(16, 24, 52), outline=(42, 50, 80), width=2)
    d.text((x0 + 34, ty + 32), title, font=lab, fill=WHITE)
    d.text((x0 + 30, ty + 84), val, font=big, fill=col)
    ax, ay = x0 + tw - 48, ty + 52
    if arrow == "down":
        d.polygon([(ax - 26, ay - 10), (ax + 26, ay - 10), (ax, ay + 30)], fill=col)
    else:
        d.polygon([(ax - 26, ay + 10), (ax + 26, ay + 10), (ax, ay - 30)], fill=col)
    d.text((x0 + 34, ty + 232), note, font=sub, fill=(170, 176, 198))

y = ty + th + 56
y = rich(d, "Na prática: o salário cresce pouco e o custo de vida sobe. É o [g]pior dos mundos para a sua renda[/g].",
         92, y, 896, font("Inter-Regular.otf", 42), font("Inter-Bold.otf", 42), 56, BODY_DARK, GOLD_DARK, RED_DARK, bold_color=WHITE)

# poll hint (leave space below for the Instagram poll sticker)
hint = font("Inter-ExtraBold.otf", 38)
d.text((92, y + 50), "Seu salário acompanhou a inflação?", font=hint, fill=WHITE)
emoji(img, "👇", 92 + hint.getlength("Seu salário acompanhou a inflação? "), y + 52, 44)
print("hint y", y + 50)

foot = font("Inter-Bold.otf", 28)
d.text((92, 1690), "Marcus Novais | Planejador Financeiro, CFP®", font=foot, fill=WHITE)
img.convert("RGB").save(OUT + "story.png", quality=95)
