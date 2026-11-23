import sys, os, subprocess, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../modelo"))
from marcus_slides import *

OUT = os.path.dirname(os.path.abspath(__file__)) + "/"
T = 8
FOTO = HERE + "/fotos/marcus-camisa-branca.png"


def capa(path):
    img = photo_light(FOTO, 680, 1020, 215)
    def txt(layer, d):
        y = kicker(d, "Herança", 92, 790, RED)
        y = rich(d, "O imóvel da família ainda está [g]no nome do avô[/g]?", 90, y, 920, TITLE(84), TITLE(84), 82,
                 WHITE, GOLD_DARK, RED, tracking=-3, upper=True)
        sf = font("Inter-Medium.otf", 42)
        d.text((92, y + 22), "Isso é uma bomba-relógio", font=sf, fill=WHITE)
        emoji(layer, "👉", 92 + sf.getlength("Isso é uma bomba-relógio") + 14, y + 24, 46)
    shadowed(img, txt)
    chrome(img, 1, T, True)
    img.convert("RGB").save(path, quality=95)


def cta(path):
    img = photo_light(FOTO, 680, 1020, 215)
    def txt(layer, d):
        y = rich(d, "Quer organizar o patrimônio da sua família [g]antes que vire problema[/g]?", 90, 820, 920,
                 TITLE(76), TITLE(76), 74, WHITE, GOLD_DARK, RED, tracking=-3, upper=True)
        bf = font("Inter-ExtraBold.otf", 34); b = "Acesse o link na BIO e me chame"
        bw = bf.getlength(b) + 66
        d.rounded_rectangle((90, y + 28, 90 + bw, y + 112), radius=18, fill=GOLD_DARK)
        d.text((123, y + 49), b, font=bf, fill=(20, 22, 30))
    shadowed(img, txt)
    chrome(img, T, T, True, swipe=False)
    img.convert("RGB").save(path, quality=95)


BARS = [("Até 60 dias", 0, (150, 156, 178)), ("Depois de 60 dias", 10, GOLD_DARK), ("Depois de 180 dias", 20, RED)]


def barras(img, d, y, p=1.0):
    lab = font("Inter-Bold.otf", 34); val = font("InterDisplay-ExtraBold.otf", 46)
    note = font("Inter-SemiBold.otf", 24)
    y += 20
    for i, (nome, v, cor) in enumerate(BARS):
        q = max(0.0, min(1.0, p * 1.6 - i * 0.3))
        d.text((92, y), nome, font=lab, fill=WHITE)
        txt = f"{v * q:.0f}% de multa" if v else "sem multa"
        tw = val.getlength(txt)
        d.text((990 - tw, y - 8), txt, font=val, fill=cor if v else (200, 204, 216))
        d.rounded_rectangle((92, y + 56, 990, y + 84), radius=14, fill=(30, 36, 60))
        if v and q > 0:
            d.rounded_rectangle((92, y + 56, 92 + (898 * v / 20) * q, y + 84), radius=14, fill=cor)
        y += 128
    d.text((92, y), "Exemplo: regra do ITCMD em São Paulo. Cada estado tem a sua.", font=note, fill=(150, 156, 178))


def dado(path, p=1.0):
    text_slide(path, 4, T, "O relógio está correndo",
               "Quanto mais demora, [r]mais caro[/r]",
               "A lei prevê abrir o inventário em até **2 meses** após o falecimento. Depois disso, o imposto sobre herança (ITCMD) pode vir com **multa**.",
               dark=True, extra=(lambda img, d, y: barras(img, d, y, p), 440))


capa(OUT + "01.png")
text_slide(OUT + "02.png", 2, T, "O problema",
           "No papel, o imóvel [r]não é seu[/r]",
           "Enquanto o inventário não é feito, o imóvel continua no nome de quem faleceu.\n"
           "A família **mora, usa e paga as contas**, mas [g]não é dona no registro[/g].", dark=True)
bullets_slide(OUT + "03.png", 3, T, "O que você não consegue fazer",
              "Um imóvel [r]travado[/r]",
              ["**Vender** ou doar com segurança",
               "**Financiar** ou dar o imóvel como garantia",
               "**Alugar** com um contrato bem amarrado",
               "**Dividir** entre os herdeiros sem conflito"], dark=False)
dado(OUT + "04.png")
text_slide(OUT + "05.png", 5, T, "E piora com o tempo",
           "Cada geração [r]multiplica[/r] o problema",
           "Se um herdeiro também falece, abre-se **um inventário dentro do outro**.\n"
           "Mais herdeiros, mais assinaturas, mais custos e [g]mais chance de briga[/g].")
text_slide(OUT + "06.png", 6, T, "Na minha leitura",
           "Imóvel irregular é [g]patrimônio pela metade[/g]",
           "Ele vale no papel, mas **não vira dinheiro** quando a família precisa.\n"
           "Regularizar não é burocracia: é [g]transformar o imóvel em patrimônio de verdade[/g].", dark=True)
bullets_slide(OUT + "07.png", 7, T, "O que eu faria",
              "Como [g]desarmar[/g] a bomba",
              ["Puxar a **matrícula atualizada** do imóvel no cartório",
               "Reunir os herdeiros e buscar **consenso**",
               "Avaliar o **inventário em cartório**, mais rápido quando há acordo",
               "Planejar o **ITCMD e os custos** antes de começar, com advogado"], dark=False)
cta(OUT + "08.png")

with tempfile.TemporaryDirectory() as tmp:
    n = 30 * 6
    for i in range(n):
        p = min(1.0, i / (30 * 3.0)); p = 1 - (1 - p) ** 3
        dado(f"{tmp}/f{i:04d}.png", p)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "30", "-i", f"{tmp}/f%04d.png",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", OUT + "04.mp4"], check=True)
print("ok")
