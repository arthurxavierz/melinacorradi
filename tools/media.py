"""
Prepara as mídias do site a partir dos originais do Instagram em _raw/media.

  python tools/media.py            (gera só o que falta)
  python tools/media.py --force    (refaz tudo)

Gera em dist/assets:
  video/hero.mp4 (+ .jpg)      montagem quadrada do hero, só trechos sem texto por cima
  video/p/{id}.mp4             prévia muda de 6 s (vitrine)
  video/full/{id}.mp4          vídeo completo com som (modal), até 60 s
  img/reels/{id}.jpg           capa de cada vídeo
  img/fotos/{nome}.jpg         fotos e recortes (equipe, casos, aparelhos)
"""
import pathlib
import subprocess
import sys

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = ROOT / "_raw" / "media"
OUT = ROOT / "dist" / "assets"
FF = str((ROOT.parent / "achilles-video" / "node_modules" / "ffmpeg-static" / "ffmpeg.exe").resolve())

# id: (início da prévia, segundo da capa)
REELS = {
    "Da5pksku9-i": (17, 19), "DaQxkYHPgCk": (0.3, 1.5), "DeznLfhzDHL": (1, 3), "DfYAXrGz4VZ": (0.3, 2),
    "DfXwjb7TOo5": (2, 4), "DfpK3YQz5Sw": (3, 6), "Db6jGPLPTpu": (0.5, 9), "DagDDjMzj0t": (1, 5),
    "DaYDmyMuWdY": (5, 8), "DaiCMiSTL7n": (0.5, 3), "Dax0mEfuKVJ": (18, 21), "DasonEkuOTm": (0.3, 1.5),
    "DbBME_muqbY": (0.5, 2), "Ddjnja_Tqda": (0.3, 2),
}

# montagem do hero: (id, início, x, y, lado) recorte quadrado no quadro 720x1280, fora dos textos do post
HERO = [
    ("DeznLfhzDHL", 1.5, 124, 448, 472),
    ("Db6jGPLPTpu", 1.0, 0, 330, 720),
    ("DfYAXrGz4VZ", 0.4, 80, 0, 560),
    ("DfpK3YQz5Sw", 6.0, 0, 460, 720),
    ("Da5pksku9-i", 22.0, 0, 360, 720),
    ("DfXwjb7TOo5", 2.5, 0, 520, 720),
    ("DaYDmyMuWdY", 7.0, 0, 300, 720),
    ("DagDDjMzj0t", 3.5, 0, 430, 720),
]
CLIP, FADE = 3.2, 0.7
# fundo do hero em tela cheia: (id, início, y) faixa 720x405 do quadro vertical, fora dos textos do post
HERO_WIDE = [
    ("Db6jGPLPTpu", 1.0, 400), ("DfXwjb7TOo5", 2.5, 600), ("DeznLfhzDHL", 1.5, 480), ("Da5pksku9-i", 22.0, 420),
    ("DfYAXrGz4VZ", 0.4, 60), ("DfpK3YQz5Sw", 6.0, 600), ("DagDDjMzj0t", 3.5, 520), ("DaYDmyMuWdY", 7.0, 400),
]

# nome: (arquivo original, recorte (x0, y0, x1, y1) ou None, largura máxima)
FOTOS = {
    "melina": ("DesZQ6Ntmlo-0", (0, 610, 655, 1687), 900),
    "franklin": ("DesZvG1t-kb-0", (0, 600, 675, 1687), 900),
    "lucas": ("Desa6KJt36i-0", (0, 625, 660, 1687), 900),
    "laysa": ("DesHhuOzMRG-0", (0, 660, 640, 1687), 900),
    "melina-azul": ("DY4x8dpgxVC-0", (68, 456, 742, 1350), 800),
    "coroa": ("DagiLBNv5rx-0", None, 1200),
    "restauracao-1": ("DZuqAsIjh-G-0", None, 1000),
    "restauracao-2": ("DZuqAsIjh-G-1", None, 1000),
    "implante-caso": ("DaQdZpBOV1R-0", None, 1080),
    "limpeza-caso": ("DaCEJtvtHuB-0", None, 1080),
    "limpeza-post": ("Db3Uc9hOnXV-0", None, 1080),
    "siso-caso": ("Dat6mFrjWvm-0", None, 1080),
    "clarea-day": ("Dal2h4dNhJr-0", None, 1080),
    "comunicado": ("Dah3i_ETRr5-0", None, 1080),
    "aparelho-autoligado": ("DejmmWwEWCv-1", (150, 40, 1000, 640), 1000),
    "aparelho-estetico": ("DejmmWwEWCv-2", (150, 40, 1000, 640), 1000),
    "aparelho-convencional": ("DejmmWwEWCv-3", (150, 40, 1000, 640), 1000),
    "alinhadores": ("DejmmWwEWCv-4", (150, 40, 1000, 640), 1000),
    "ortodontia": ("DejmmWwEWCv-0", None, 1080),
    "black-home": ("DgGjirEzqkP-0", None, 1080),
    "black-premium": ("DgGlF8zThOT-0", None, 1080),
}
# quadros parados tirados dos vídeos: nome: (id, segundo, recorte)
STILLS = {
    "melina-sorriso": ("DasonEkuOTm", 0.4, (0, 0, 720, 720)),
    # círculo do hero: gerado à mão com eq de brilho (crop=600:600:60:40 em 0.6 s)
    "recepcao": ("Da5pksku9-i", 25, (0, 330, 720, 1080)),
    "fachada": ("Da5pksku9-i", 13, (0, 300, 720, 1100)),
    "protese": ("DeznLfhzDHL", 3, (124, 448, 596, 920)),
    "instrumentos": ("Db6jGPLPTpu", 2, (0, 330, 720, 1050)),
    "clareamento": ("DfXwjb7TOo5", 4, (0, 520, 720, 1240)),
    "atendimento": ("DfYAXrGz4VZ", 0.4, (40, 0, 680, 560)),
    "sorriso": ("DagDDjMzj0t", 4, (0, 430, 720, 1150)),
    "equipe-sala": ("DaQxkYHPgCk", 0.4, (0, 120, 720, 900)),
}

V916 = "scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1"


def run(args):
    r = subprocess.run([FF, "-loglevel", "error", "-y", *args])
    if r.returncode:
        sys.exit("ffmpeg falhou: " + " ".join(args))


def need(p):
    p.parent.mkdir(parents=True, exist_ok=True)
    return not p.exists() or "--force" in sys.argv


def hero():
    p = OUT / "video" / "hero.mp4"
    if not need(p):
        return
    ins, parts = [], []
    for k, (rid, ss, x, y, s) in enumerate(HERO):
        ins += ["-ss", str(ss), "-t", str(CLIP), "-i", str(RAW / f"{rid}.mp4")]
        parts.append(f"[{k}:v]crop={s}:{s}:{x}:{y},scale=720:720,setsar=1,fps=30,format=yuv420p,trim=duration={CLIP},setpts=PTS-STARTPTS[v{k}]")
    chain, prev, off = [], "v0", 0.0
    for k in range(1, len(HERO)):
        off += CLIP - FADE
        out = f"x{k}"
        chain.append(f"[{prev}][v{k}]xfade=transition=fade:duration={FADE}:offset={off:.2f}[{out}]")
        prev = out
    flt = ";".join(parts + chain)
    run([*ins, "-filter_complex", flt, "-map", f"[{prev}]", "-an", "-c:v", "libx264", "-crf", "27", "-preset", "slow",
         "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(p)])
    run(["-ss", "0.3", "-i", str(p), "-frames:v", "1", "-q:v", "3", str(p.with_suffix(".jpg"))])
    print("ok hero")


def hero_wide():
    p = OUT / "video" / "hero-bg.mp4"
    if not need(p):
        return
    ins, parts = [], []
    for k, (rid, ss, y) in enumerate(HERO_WIDE):
        ins += ["-ss", str(ss), "-t", str(CLIP), "-i", str(RAW / f"{rid}.mp4")]
        parts.append(f"[{k}:v]crop=720:405:0:{y},scale=1280:720:flags=lanczos,unsharp=5:5:0.6,setsar=1,fps=30,format=yuv420p,trim=duration={CLIP},setpts=PTS-STARTPTS[v{k}]")
    chain, prev, off = [], "v0", 0.0
    for k in range(1, len(HERO_WIDE)):
        off += CLIP - FADE
        chain.append(f"[{prev}][v{k}]xfade=transition=fade:duration={FADE}:offset={off:.2f}[x{k}]")
        prev = f"x{k}"
    run([*ins, "-filter_complex", ";".join(parts + chain), "-map", f"[{prev}]", "-an", "-c:v", "libx264", "-crf", "28", "-preset", "slow",
         "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(p)])
    run(["-ss", "0.3", "-i", str(p), "-frames:v", "1", "-q:v", "3", str(p.with_suffix(".jpg"))])
    print("ok hero-bg")


def main():
    hero()
    hero_wide()
    for rid, (ss, cover) in REELS.items():
        src = str(RAW / f"{rid}.mp4")
        prev = OUT / "video" / "p" / f"{rid}.mp4"
        if need(prev):
            run(["-ss", str(ss), "-t", "6", "-i", src, "-an", "-vf", V916.format(w=360, h=640) + ",fps=30",
                 "-c:v", "libx264", "-crf", "29", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(prev)])
        full = OUT / "video" / "full" / f"{rid}.mp4"
        if need(full):
            run(["-i", src, "-t", "60", "-vf", V916.format(w=540, h=960), "-c:v", "libx264", "-crf", "28", "-preset", "slow",
                 "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", str(full)])
        jpg = OUT / "img" / "reels" / f"{rid}.jpg"
        if need(jpg):
            run(["-ss", str(cover), "-i", src, "-frames:v", "1", "-vf", V916.format(w=720, h=1280), "-q:v", "4", str(jpg)])
        print("ok", rid)

    for name, (rid, t, (x0, y0, x1, y1)) in STILLS.items():
        jpg = OUT / "img" / "fotos" / f"{name}.jpg"
        if need(jpg):
            run(["-ss", str(t), "-i", str(RAW / f"{rid}.mp4"), "-frames:v", "1",
                 "-vf", f"crop={x1 - x0}:{y1 - y0}:{x0}:{y0}", "-q:v", "3", str(jpg)])
        print("ok", name)

    for name, (fid, box, maxw) in FOTOS.items():
        jpg = OUT / "img" / "fotos" / f"{name}.jpg"
        if need(jpg):
            im = Image.open(RAW / f"{fid}.jpg").convert("RGB")
            if box:
                im = im.crop(box)
            if im.width > maxw:
                im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
            im.save(jpg, quality=84, optimize=True, progressive=True)
        print("ok", name)


if __name__ == "__main__":
    main()
