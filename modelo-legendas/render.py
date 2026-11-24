"""Aplica o padrão de legendas (ver PADRAO.md) num vídeo vertical, sem áudio.

Uso: python3 render.py texto.json video_entrada saida.mp4
texto.json: {"titulo": [l1, l2], "caixas": [[l1, l2], ...], "rodape": "Leia a legenda",
             "rodape_em": 0.6, "titulo_y": 0.18}
"""
import json, os, subprocess, sys
from PIL import Image, ImageColor, ImageDraw, ImageFont, ImageFilter

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


EMOJI_FONT = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"


def split_emoji(line):
    """Separa emoji no fim da linha (ex.: 'Veja por que 👇')."""
    if line and ord(line[-1]) >= 0x1F000:
        return line[:-1].rstrip(), line[-1]
    return line, None


def emoji_img(ch, height):
    f = ImageFont.truetype(EMOJI_FONT, 109)
    im = Image.new("RGBA", (136, 128), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((0, 0), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox())
    return im.resize((round(im.width * height / im.height), round(height)), Image.LANCZOS)


def shadow_text(img, lines, font, y, pitch, highlight=None, hl_color="#F5C400", colors=None):
    """highlight: índice da linha que vai dentro de uma caixa colorida (texto preto).
    colors: lista por linha com a cor do fundo (None = texto branco sem fundo)."""
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    tx = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ds, dt = ImageDraw.Draw(sh), ImageDraw.Draw(tx)
    for i, line in enumerate(lines):
        cy = y + i * pitch
        bg = colors[i] if colors else (hl_color if highlight == "all" or i == highlight else None)
        if bg:
            line, emo = split_emoji(line)
            l, _, r, _ = font.getbbox(line, anchor="lt")
            _, t, _, b = font.getbbox("ÁÓÉgjpç", anchor="lt")  # altura igual em todas as linhas
            em = emoji_img(emo, (b - t) * 1.1) if emo else None
            gap = font.size * 0.25 if em else 0
            tw = r + (gap + em.width if em else 0)
            x0 = W / 2 - tw / 2
            px, py = 12 * S, 6 * S
            dt.rectangle([x0 - px, cy + t - py, x0 + tw + px, cy + b + py], fill=bg)
            r_, g_, b_ = ImageColor.getrgb(bg)[:3]
            dark = 0.299 * r_ + 0.587 * g_ + 0.114 * b_ < 150
            dt.text((x0, cy), line, font=font, fill="white" if dark else (15, 15, 15), anchor="lt")
            if em:
                tx.alpha_composite(em, (round(x0 + r + gap), round(cy + (t + b) / 2 - em.height / 2)))
            continue
        ds.text((W / 2 + 2, cy + 3), line, font=font, fill=(0, 0, 0, 150), anchor="mt")
        dt.text((W / 2, cy), line, font=font, fill="white", anchor="mt")
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    img.alpha_composite(tx)


def main(spec_path, src, out):
    spec = json.load(open(spec_path, encoding="utf-8"))
    base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ft = ImageFont.truetype(TITLE_FONT, round(f_title.size * spec.get("titulo_escala", 1.0)))
    if "titulo_escalas" in spec:  # tamanho diferente por linha do título
        ty = spec.get("titulo_y", 0.18) * H
        cores = spec.get("titulo_cores") or [None] * len(spec["titulo"])
        for line, esc, cor in zip(spec["titulo"], spec["titulo_escalas"], cores):
            fl = ImageFont.truetype(TITLE_FONT, round(ft.size * esc))
            shadow_text(base, [line], fl, ty, 0, None, colors=[cor])
            ty += fl.size * (1.62 if cor else 1.2)
    else:
        shadow_text(base, spec["titulo"], ft, spec.get("titulo_y", 0.18) * H,
                    spec.get("titulo_pitch", 35) * S, spec.get("titulo_destaque"),
                    spec.get("cor_destaque", "#F5C400"), spec.get("titulo_cores"))

    d = ImageDraw.Draw(base)
    k = spec.get("caixa_escala", 1.0)
    f_box = ImageFont.truetype(BOX_FONT, round(globals()["f_box"].size * k))
    pitch, pad_x, pad_y, gap = 26 * S * k, 12 * S, 11 * S, spec.get("caixa_gap", 25) * S
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
    rod = spec.get("rodape", "Leia a legenda")
    rod = [rod] if isinstance(rod, str) else rod
    ff = ImageFont.truetype(TITLE_FONT, round(f_foot.size * spec.get("rodape_escala", 1.0)))
    shadow_text(foot, rod, ff, spec.get("rodape_y", 0.852) * H, ff.size * spec.get("rodape_pitch", 1.6),
                "all" if spec.get("rodape_destaque") else None, spec.get("cor_destaque", "#F5C400"))

    tmp = os.path.splitext(out)[0]
    base.save(tmp + "_base.png"); foot.save(tmp + "_rodape.png")
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                         "-of", "csv=p=0", src]).decode())
    dur = min(dur, spec.get("duracao", dur))
    t = spec.get("rodape_em", 0.6) * dur
    vf = (f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1[v];"
          f"[v][1:v]overlay=0:0[a];[a][2:v]overlay=0:0:enable='gte(t,{t:.2f})',format=yuv420p")
    subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", src, "-i", tmp + "_base.png",
                           "-i", tmp + "_rodape.png", "-filter_complex", vf, "-an", "-t", f"{dur:.3f}",
                           "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                           "-movflags", "+faststart", out])


if __name__ == "__main__":
    main(*sys.argv[1:4])
