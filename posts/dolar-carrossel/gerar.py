import sys, os, subprocess, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../modelo"))
from marcus_slides import *

OUT = os.path.dirname(os.path.abspath(__file__)) + "/"
T = 7

# Dólar PTAX (Banco Central, série SGS 1) de 23/10 a 18/11; último ponto = fechamento informado (R$ 5,94)
DATA = [5.0377, 5.5007, 5.3346, 5.3420, 5.3744, 5.4212, 5.4935, 5.4778, 5.4621, 5.5013, 5.5146,
        5.5840, 5.5606, 5.6143, 5.6518, 5.7324, 5.7851, 5.8102, 5.94]


def chart(img, d, y, p=1.0):
    x0, x1, y0, y1 = 92, 930, y + 40, y + 430
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
        d.ellipse((e[0] - 14, e[1] - 14, e[0] + 14, e[1] + 14), fill=RED)
        lab = "R$ 5,94"; tw = big.getlength(lab)
        d.text((e[0] - tw + 6, e[1] - 70), lab, font=big, fill=RED)
    d.text((x0, y1 + 16), "23/10 · antes do 2º turno", font=small, fill=(150, 156, 178))
    lab = "último fechamento"; d.text((x1 - small.getlength(lab), y1 + 16), lab, font=small, fill=(150, 156, 178))


def chart_slide(path, p=1.0):
    text_slide(path, 2, T, "O dólar desde o 2º turno",
               "De R$ 5,04 para [r]R$ 5,94[/r]",
               "Alta de **18% em menos de um mês**. E essa conta chega ao seu prato, ao seu tanque e à sua parcela.",
               dark=True, extra=(lambda img, d, y: chart(img, d, y, p), 470))


cover(OUT + "01.png", 1, T, "Câmbio",
      "“Pobre não come dólar”? [g]Come sim,[/g] todo dia.",
      sub="Veja por quê")
chart_slide(OUT + "02.png")
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
cta(OUT + "07.png", 7, T, "Quer proteger o seu patrimônio [g]contra o dólar[/g]?")

# Versão animada do slide 2 (linha sendo desenhada), como os slides de dados do modelo
with tempfile.TemporaryDirectory() as tmp:
    frames = 30 * 6
    for i in range(frames):
        p = min(1.0, i / (30 * 3.5))
        p = 1 - (1 - p) ** 3
        chart_slide(f"{tmp}/f{i:04d}.png", p)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "30", "-i", f"{tmp}/f%04d.png",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", OUT + "02.mp4"], check=True)
print("ok")
