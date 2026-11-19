"""Aplica o padrão de legendas (ver PADRAO.md) num vídeo vertical, sem áudio.

Uso: python3 render.py texto.json video_entrada saida.mp4
texto.json: {"titulo": [l1, l2], "caixas": [[l1, l2], ...], "rodape": "Leia a legenda",
             "rodape_em": 0.6, "titulo_y": 0.18}
"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
S = W / 576  # medidas do modelo foram tiradas em 576x1024
TITLE_FONT = os.path.join(HERE, "fonts/InstrumentSerif-Regular.ttf")
BOX_FONT = os.path.join(HERE, "fonts/SourceSerif4-Regular.ttf")


def fit(path, sample, width):
    lo, hi = 5, 300
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if ImageFont.truetype(path, mid).getlength(sample) <= width:
            lo = mid
        else:
            hi = mid - 1
    return ImageFont.truetype(path, lo)


f_title = fit(TITLE_FONT, "Como chegar em 1 MILHÃO", 357 * S)
f_box = fit(BOX_FONT, "Dos 40 aos 45 invista R$ 1.000 por mês,", 354 * S)
f_foot = fit(TITLE_FONT, "Leia a legenda", 125 * S)


def shadow_text(img, lines, font, y, pitch):
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    tx = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ds, dt = ImageDraw.Draw(sh), ImageDraw.Draw(tx)
    for i, line in enumerate(lines):
        cy = y + i * pitch
        ds.text((W / 2 + 2, cy + 3), line, font=font, fill=(0, 0, 0, 150), anchor="mt")
        dt.text((W / 2, cy), line, font=font, fill="white", anchor="mt")
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    img.alpha_composite(tx)


def main(spec_path, src, out):
    spec = json.load(open(spec_path, encoding="utf-8"))
    base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow_text(base, spec["titulo"], f_title, spec.get("titulo_y", 0.18) * H, 35 * S)

    d = ImageDraw.Draw(base)
    pitch, pad_x, pad_y, gap = 26 * S, 12 * S, 11 * S, 25 * S
    asc, desc = f_box.getmetrics()
    y = spec.get("caixas_y", 0.555) * H
    for lines in spec["caixas"]:
        tw = max(f_box.getlength(l) for l in lines)
        bh = pad_y * 2 + pitch * (len(lines) - 1) + asc + desc * 0.4
        d.rectangle([W / 2 - tw / 2 - pad_x, y, W / 2 + tw / 2 + pad_x, y + bh], fill="white")
        for i, l in enumerate(lines):
            d.text((W / 2, y + pad_y + i * pitch), l, font=f_box, fill=(20, 20, 20), anchor="mt")
        y += bh + gap

    foot = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow_text(foot, [spec.get("rodape", "Leia a legenda")], f_foot, spec.get("rodape_y", 0.852) * H, 0)

    tmp = os.path.splitext(out)[0]
    base.save(tmp + "_base.png"); foot.save(tmp + "_rodape.png")
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                         "-of", "csv=p=0", src]).decode())
    t = spec.get("rodape_em", 0.6) * dur
    vf = (f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1[v];"
          f"[v][1:v]overlay=0:0[a];[a][2:v]overlay=0:0:enable='gte(t,{t:.2f})',format=yuv420p")
    subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", src, "-i", tmp + "_base.png",
                           "-i", tmp + "_rodape.png", "-filter_complex", vf, "-an",
                           "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                           "-movflags", "+faststart", out])


if __name__ == "__main__":
    main(*sys.argv[1:4])
