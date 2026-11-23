import sys, os, subprocess, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../modelo"))
from marcus_slides import *

OUT = os.path.dirname(os.path.abspath(__file__)) + "/"
T = 7

# Dólar PTAX (Banco Central, série SGS 1) de 23/10 a 18/11; último ponto = fechamento informado (R$ 5,94)
DATA = [5.0377, 5.5007, 5.3346, 5.3420, 5.3744, 5.4212, 5.4935, 5.4778, 5.4621, 5.5013, 5.5146,
        5.5840, 5.5606, 5.6143, 5.6518, 5.7324, 5.7851, 5.8102, 5.94]


def chart(img, d, y, p=1.0):
    x0, x1, y0, y1 = 92, 930, y + 90, y + 470
    lo, hi = 4.9, 6.05
    small = font("Inter-SemiBold.otf", 24)
    def py(v): return y1 - (v - lo) / (hi - lo) * (y1 - y0)
    def px(i): return x0 + i * (x1 - x0) / (len(DATA) - 1)
    for g in (5.0, 5.5, 6.0):
        d.line([(x0, py(g)), (x1, py(g))], fill=DIVIDER_DARK, width=2)
        d.text((x1 + 14, py(g) - 14), f"{g:.2f}".replace(".", ","), font=small, fill=(150, 156, 178))
    k = max(2, int(round(p * (len(DATA) - 1))) + 1)
    pts = [(px(i), py(v)) for i, v in enumerate(DATA[:k])]
    d.line(pts, fill=GOLD_DARK, width=7, joint="curve")
    r = 11
    d.ellipse((pts[0][0] - r, pts[0][1] - r, pts[0][0] + r, pts[0][1] + r), fill=GOLD_DARK)
    big = font("Inter-ExtraBold.otf", 40)
    d.text((pts[0][0] + 26, pts[0][1] - 26), "R$ 5,04", font=big, fill=WHITE)
    if k == len(DATA):
        e = pts[-1]
        d.ellipse((e[0] - 14, e[1] - 14, e[0] + 14, e[1] + 14), fill=RED_DARK)
        lab = "R$ 5,94"; tw = big.getlength(lab)
        d.text((e[0] - tw + 6, e[1] - 70), lab, font=big, fill=RED_DARK)
    d.text((x0, y1 + 16), "23/10 · antes do 2º turno", font=small, fill=(150, 156, 178))
    lab = "último fechamento"; d.text((x1 - small.getlength(lab), y1 + 16), lab, font=small, fill=(150, 156, 178))


def chart_cover(path, p=1.0):
    img = background(True); d = ImageDraw.Draw(img)
    y = kicker_pill(d, "Câmbio", 92, 150)
    y = rich(d, "“Pobre não come dólar”? [g]Come sim,[/g] todo dia.", 90, y, 920, TITLE(84), TITLE(84), 82,
             WHITE, GOLD_DARK, RED_DARK, tracking=-3, upper=True)
    y = rich(d, "Dólar desde o 2º turno: **+18% em menos de um mês**.", 90, y + 18, 900, BODY, BODY_B, 52,
             BODY_DARK, GOLD_DARK, RED_DARK, bold_color=WHITE)
    chart(img, d, y + 10, p)
    chrome(img, 1, T, True)
    img.convert("RGB").save(path, quality=95)


def photo_slide(path):
    img = photo_light(HERE + "/fotos/marcus-estudio.png", 760, 1100, 135)
    def txt(layer, d):
        y = kicker_pill(d, "“Só os ricos vão sofrer”?", 92, 890)
        y = rich(d, "Calma. Vamos aos [g]fatos[/g].", 90, y, 900, TITLE(88), TITLE(88), 86, WHITE, GOLD_DARK, RED_DARK,
                 tracking=-3, upper=True)
        sf = font("Inter-Medium.otf", 42)
        d.text((92, y + 26), "O dólar chega no seu prato", font=sf, fill=WHITE)
        emoji(layer, "👉", 92 + sf.getlength("O dólar chega no seu prato") + 14, y + 28, 46)
    shadowed(img, txt)
    chrome(img, 2, T, True)
    img.convert("RGB").save(path, quality=95)


def cta_slide(path):
    img = photo_light(HERE + "/fotos/marcus-estudio.png", 760, 1100, 135)
    def txt(layer, d):
        y = rich(d, "Quer proteger o seu patrimônio [g]contra o dólar[/g]?", 90, 880, 900, TITLE(80), TITLE(80), 78,
                 WHITE, GOLD_DARK, RED_DARK, tracking=-3, upper=True)
        bf = font("Inter-ExtraBold.otf", 34); button = "Acesse o link na BIO e me chame"
        bw = bf.getlength(button) + 66
        d.rounded_rectangle((90, y + 28, 90 + bw, y + 112), radius=18, fill=GOLD_DARK)
        d.text((123, y + 49), button, font=bf, fill=(20, 22, 30))
    shadowed(img, txt)
    chrome(img, 7, T, True, swipe=False)
    img.convert("RGB").save(path, quality=95)


chart_cover(OUT + "01.png")
photo_slide(OUT + "02.png")
text_slide(OUT + "03.png", 3, T, "No café da manhã",
           "O pão tem [r]dólar[/r]",
           "O Brasil importa cerca de **metade do trigo** que consome, e o preço segue a cotação internacional.\n"
           "Pão, massa e biscoito [g]sobem junto com o dólar[/g].")
text_slide(OUT + "04.png", 4, T, "No prato",
           "Arroz, feijão e carne [r]também[/r]",
           "O Brasil importa cerca de **85% dos fertilizantes** que usa, segundo a Embrapa.\n"
           "Adubo mais caro é [g]comida mais cara[/g], mesmo a que nunca sai do país.")
bullets_slide(OUT + "05.png", 5, T, "A reação em cadeia",
              "Dólar alto vira [g]juros altos[/g]",
              ["Petróleo é cotado em dólar: **diesel e frete mais caros**",
               "Frete mais caro: **preço sobe no supermercado**",
               "Preços em alta: **Selic segue em 13,75%**",
               "Selic alta: **crediário, cartão e financiamento mais caros**"])
text_slide(OUT + "06.png", 6, T, "Na minha leitura",
           "Quem mais sofre não é quem [g]tem dólar[/g]",
           "É quem gasta quase toda a renda com **comida, transporte e dívida**.\n"
           "Quem tem patrimônio diversificado, [g]inclusive no exterior[/g], se protege.")
cta_slide(OUT + "07.png")

# Versão animada do slide 1 (linha do dólar sendo desenhada), como os slides de dados do modelo
with tempfile.TemporaryDirectory() as tmp:
    frames = 30 * 6
    for i in range(frames):
        p = min(1.0, i / (30 * 3.5))
        p = 1 - (1 - p) ** 3
        chart_cover(f"{tmp}/f{i:04d}.png", p)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "30", "-i", f"{tmp}/f%04d.png",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", OUT + "01.mp4"], check=True)
print("ok")
