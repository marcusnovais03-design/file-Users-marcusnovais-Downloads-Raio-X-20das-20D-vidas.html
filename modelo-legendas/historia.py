"""Layout de história em texto corrido (alinhado à esquerda, sobre vídeo escurecido).

Uso: python3 historia.py historia.json video_entrada saida.mp4
historia.json: {"linhas": ["Texto com *destaque amarelo*", "", ...], "y": 0.08, "tamanho": 52,
                "passo": 1.32, "escurecer": 0.4}
Linha vazia = espaço entre parágrafos. Trechos entre *asteriscos* ficam amarelos.
A primeira linha usa "tamanho_titulo". Saída 1080x1920, sem áudio, texto fixo desde o início.
"""
import json, os, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import split_emoji, emoji_img  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
BOLD = os.path.join(HERE, "fonts/Montserrat-Bold.ttf")
XBOLD = os.path.join(HERE, "fonts/Montserrat-ExtraBold.ttf")
YELLOW = "#FFD21F"


def main(spec_path, src, out):
    sp = json.load(open(spec_path, encoding="utf-8"))
    img = Image.new("RGBA", (W, H), (0, 0, 0, int(255 * sp.get("escurecer", 0.4))))
    txt = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dt, ds = ImageDraw.Draw(txt), ImageDraw.Draw(sh)

    x0 = sp.get("x", 70)
    y = sp.get("y", 0.08) * H
    size = sp.get("tamanho", 50)
    for i, line in enumerate(sp["linhas"]):
        s = sp.get("tamanho_titulo", round(size * 1.25)) if i == 0 else size
        f = ImageFont.truetype(XBOLD if i == 0 else BOLD, s)
        if not line:
            y += s * sp.get("paragrafo", 0.7)
            continue
        line, emo = split_emoji(line)
        x = x0
        for j, part in enumerate(re.split(r"\*", line)):
            if not part:
                continue
            color = YELLOW if j % 2 else "white"
            ds.text((x + 2, y + 3), part, font=f, fill=(0, 0, 0, 200))
            dt.text((x, y), part, font=f, fill=color)
            x += f.getlength(part)
        if emo:
            em = emoji_img(emo, s * 0.95)
            txt.alpha_composite(em, (round(x + s * 0.25), round(y + s * 0.6 - em.height / 2)))
        y += s * sp.get("passo", 1.3)

    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5)))
    img.alpha_composite(txt)
    tmp = os.path.splitext(out)[0] + "_historia.png"
    img.save(tmp)
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
