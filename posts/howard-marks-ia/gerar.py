import sys, os, subprocess, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../modelo"))
from marcus_slides import *

OUT = os.path.dirname(os.path.abspath(__file__)) + "/"
T = 10
FOTO = HERE + "/fotos/marcus-polo-sala.png"


def capa(path):
    img = photo_light(FOTO, 640, 980, 215)
    def txt(layer, d):
        y = kicker_pill(d, "IA e investimentos", 92, 790)
        y = rich(d, "As [g]11 perguntas[/g] de Howard Marks sobre IA", 90, y, 920, TITLE(84), TITLE(84), 82,
                 WHITE, GOLD_DARK, RED_DARK, tracking=-3, upper=True)
        sf = font("Inter-Medium.otf", 42); s = "Estas mexem no seu dinheiro"
        d.text((92, y + 22), s, font=sf, fill=WHITE)
        emoji(layer, "👉", 92 + sf.getlength(s) + 14, y + 24, 46)
    shadowed(img, txt)
    chrome(img, 1, T, True)
    img.convert("RGB").save(path, quality=95)


def cta(path):
    img = photo_light(FOTO, 640, 980, 215)
    def txt(layer, d):
        y = rich(d, "Quanto do seu patrimônio [g]depende da IA[/g]?", 90, 830, 920,
                 TITLE(80), TITLE(80), 78, WHITE, GOLD_DARK, RED_DARK, tracking=-3, upper=True)
        bf = font("Inter-ExtraBold.otf", 34); b = "Acesse o link na BIO e me chame"
        bw = bf.getlength(b) + 66
        d.rounded_rectangle((90, y + 28, 90 + bw, y + 112), radius=18, fill=GOLD_DARK)
        d.text((123, y + 49), b, font=bf, fill=(20, 22, 30))
    shadowed(img, txt)
    chrome(img, T, T, True, swipe=False)
    img.convert("RGB").save(path, quality=95)


BARS = [("Dívida ligada à IA no mundo", 600, GOLD_DARK), ("Só nos EUA, em grau de investimento", 400, RED_DARK)]


def barras(img, d, y, p=1.0):
    lab = font("Inter-Bold.otf", 32); val = font("InterDisplay-ExtraBold.otf", 50)
    note = font("Inter-SemiBold.otf", 24)
    y += 20
    for i, (nome, v, cor) in enumerate(BARS):
        q = max(0.0, min(1.0, p * 1.5 - i * 0.35))
        d.text((92, y), nome, font=lab, fill=WHITE)
        t = f"US$ {v * q:.0f} bi"
        d.text((92, y + 48), t, font=val, fill=cor)
        d.rounded_rectangle((92, y + 118, 990, y + 148), radius=15, fill=(30, 36, 60))
        if q > 0:
            d.rounded_rectangle((92, y + 118, 92 + max(30, 898 * v / 600 * q), y + 148), radius=15, fill=cor)
        y += 190
    d.text((92, y), "Emissões em 2026, segundo dados do Goldman Sachs citados no memo.", font=note, fill=(150, 156, 178))


def dado(path, p=1.0):
    text_slide(path, 5, T, "Pergunta 3",
               "E quem está [r]pagando a conta[/r]?",
               "A corrida da IA não é feita só com caixa: as gigantes estão **tomando dívida** para construir data centers.",
               dark=True, extra=(lambda img, d, y: barras(img, d, y, p), 420))


capa(OUT + "01.png")
text_slide(OUT + "02.png", 2, T, "Quem é ele",
           "O investidor que [g]Buffett lê primeiro[/g]",
           "Howard Marks é cofundador da **Oaktree**, uma das maiores gestoras de crédito do mundo. Warren Buffett já disse que os memos dele são **a primeira coisa que abre** na correspondência.\n"
           "No novo memo, \"Um leigo pensa sobre IA\", ele organiza o tema em [g]11 perguntas[/g]. Separei as que mais importam para quem investe.")
text_slide(OUT + "03.png", 3, T, "Pergunta 1",
           "A IA traz eficiência. Mas [r]traz lucro[/r]?",
           "Nas palavras dele: \"sabemos que a IA vai aumentar a eficiência, mas vai aumentar a **lucratividade**?\"\n"
           "Eficiência pode virar **preço menor para o cliente**, e não margem maior para a empresa. [g]Nem toda revolução enche o bolso do acionista.[/g]",
           dark=True)
text_slide(OUT + "04.png", 4, T, "Pergunta 2",
           "Quem vai [g]ficar com o lucro[/g]?",
           "Marks lembra a lição de Buffett: tecnologias que mudaram o mundo, como a aviação e a internet, **nem sempre enriqueceram quem investiu nelas**.\n"
           "Se os modelos de IA virarem algo parecido entre si, a **concorrência por preço** pode transferir o ganho para os usuários.")
dado(OUT + "05.png")
bullets_slide(OUT + "06.png", 6, T, "Pergunta 4",
              "É uma [r]bolha[/r]?",
              ["A **tecnologia** está sendo superestimada?",
               "O **gasto** é exagerado perto do retorno esperado?",
               "Os investidores estão **pagando caro** e correndo risco demais?",
               "Para ele, saber se o retorno vai compensar é, em grande parte, **\"uma questão de fé\"**"],
              dark=False)
text_slide(OUT + "07.png", 7, T, "Pergunta 5",
           "Então [g]espero a poeira baixar[/g]?",
           "Marks diz que não: o futuro **nunca fica claro**, e quem espera a certeza paga caro, porque o mercado cobra um preço alto pelo **consenso otimista**.\n"
           "A resposta dele não é fugir nem apostar tudo. É [g]investir sabendo o risco que está correndo[/g].",
           dark=True)
text_slide(OUT + "08.png", 8, T, "Trazendo para o Brasil",
           "Você já tem IA [r]sem saber[/r]",
           "Fundo global, ETF de bolsa americana, BDR, previdência com parcela no exterior: boa parte desse dinheiro está em **poucas gigantes de tecnologia**.\n"
           "Na semana passada, a troca de CEO de **uma única empresa** derrubou e levantou a bolsa americana. [g]Concentração escondida só aparece na queda.[/g]")
bullets_slide(OUT + "09.png", 9, T, "O que eu faria",
              "Como investir [g]sem depender de fé[/g]",
              ["Descobrir **quanto da carteira** já está exposto a IA e tecnologia",
               "Definir um **limite por tema** e respeitar",
               "Entrar **aos poucos**, e não na euforia",
               "Nunca usar a **reserva de emergência** nem dívida para isso"], dark=True)
cta(OUT + "10.png")

with tempfile.TemporaryDirectory() as tmp:
    n = 30 * 6
    for i in range(n):
        p = min(1.0, i / (30 * 3.0)); p = 1 - (1 - p) ** 3
        dado(f"{tmp}/f{i:04d}.png", p)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "30", "-i", f"{tmp}/f%04d.png",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", OUT + "05.mp4"], check=True)
print("ok")
