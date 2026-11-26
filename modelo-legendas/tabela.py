"""Layout de tabela comparativa (estilo "POV: você investiu R$ X em ANO").

Uso: python3 tabela.py tabela.json video_entrada saida.mp4
tabela.json: {"titulo": ["POV:", "VOCÊ INVESTIU ..."], "colunas": [{"nome", "cor", "valores": [...], "total"}],
              "linhas": ["2016", ...], "nota": "...", "escurecer": 0.35}
Saída 1080x1920, sem áudio, texto fixo desde o início.
"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
BOLD = os.path.join(HERE, "fonts/Montserrat-ExtraBold.ttf")
SEMI = os.path.join(HERE, "fonts/Montserrat-SemiBold.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def fit(path, text, width, start):
    s = start
    while s > 10 and font(path, s).getlength(text) > width:
        s -= 1
    return font(path, s)


def stroked(d, xy, text, f, fill, stroke="white", sw=5, anchor="mm"):
    d.text(xy, text, font=f, fill=fill, stroke_width=sw, stroke_fill=stroke, anchor=anchor)


def main(spec_path, src, out):
    sp = json.load(open(spec_path, encoding="utf-8"))
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    # véu escuro leve para dar leitura sobre o vídeo
    a = int(255 * sp.get("escurecer", 0.35))
    img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, a)))

    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds, d = ImageDraw.Draw(sh), ImageDraw.Draw(img)

    # título
    y = sp.get("titulo_y", 120)
    for i, line in enumerate(sp["titulo"]):
        f = fit(BOLD, line, W - 60, 110 if i == 0 else 78)
        ds.text((W / 2 + 3, y + 4), line, font=f, fill=(0, 0, 0, 170), anchor="mt")
        d.text((W / 2, y), line, font=f, fill="white", anchor="mt")
        y += f.size * 1.2

    cols = sp["colunas"]
    xs = sp.get("colunas_x", [400, 655, 920])
    pill_w, pill_h = sp.get("pilula", [240, 100])
    hy = sp.get("cabecalho_y", 470)
    fh = font(BOLD, 44)
    for c, x in zip(cols, xs):
        fhc = fit(BOLD, c["nome"], pill_w - 30, 44)
        d.rounded_rectangle([x - pill_w / 2, hy - pill_h / 2, x + pill_w / 2, hy + pill_h / 2], 34, fill=c["cor"])
        d.text((x, hy), c["nome"], font=fhc, fill="white", anchor="mm")

    fy = font(BOLD, 50)
    fv = font(BOLD, 54)
    ry, pitch = sp.get("linhas_y", 600), sp.get("linhas_passo", 98)
    for i, ano in enumerate(sp["linhas"]):
        yy = ry + i * pitch
        stroked(d, (40, yy), ano + ":", fy, (35, 35, 35), sw=4, anchor="lm")
        for c, x in zip(cols, xs):
            stroked(d, (x, yy), c["valores"][i], fv, c["cor_texto"] if "cor_texto" in c else c["cor"])

    ty = ry + len(sp["linhas"]) * pitch + 20
    ft = font(BOLD, 56)
    for c, x in zip(cols, xs):
        d.rounded_rectangle([x - pill_w / 2, ty - pill_h / 2, x + pill_w / 2, ty + pill_h / 2], 34, fill=c["cor"])
        d.text((x, ty), c["total"], font=ft, fill="white", anchor="mm")

    if sp.get("nota"):
        fn = font(SEMI, 30)
        d.text((W / 2, ty + pill_h / 2 + 30), sp["nota"], font=fn, fill="white", anchor="mt",
               stroke_width=2, stroke_fill=(0, 0, 0, 160))

    final = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    final.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    final.alpha_composite(img)
    tmp = os.path.splitext(out)[0] + "_tabela.png"
    final.save(tmp)
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                         "-of", "csv=p=0", src]).decode())
    dur = min(dur, sp.get("duracao", dur))
    vf = (f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1[v];"
          f"[v][1:v]overlay=0:0,format=yuv420p")
    subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", src, "-i", tmp, "-filter_complex", vf,
                           "-an", "-t", f"{dur:.3f}", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                           "-movflags", "+faststart", out])
    os.remove(tmp)


if __name__ == "__main__":
    main(*sys.argv[1:4])
