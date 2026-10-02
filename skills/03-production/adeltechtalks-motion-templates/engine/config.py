"""Paths and per-video inputs for the motion templates.

Every script imports its paths from here — nothing is hardcoded to a machine.
Folders can be moved with environment variables:

    ATC_FONTS_DIR   fonts downloaded by engine/fetch_fonts.sh   (default: engine/fonts)
    ATC_INPUT_DIR   per-video inputs: photos, result frames, logos (default: ./input)
    ATC_WORK_DIR    test frames, silent renders, sfx and music   (default: ./work)
    ATC_OUT_DIR     final videos                                  (default: ./output)
    ATC_BRAND       brand file                                    (default: input/brand.json)

Brand: colours, fonts, logo, name and the ending text come from input/brand.json
(+ input/<logo>). Without one, the example brand in examples/adeltechtalks/ is used
and a notice is printed — run the brand setup in SKILL.md to make it yours.

INPUT/WORK/OUT are relative to the folder you run from.

Per-video inputs (all optional — a placeholder is drawn and the missing file is
reported when one isn't there):

    input/brand.json           your brand (colours, fonts, logo, name, ending text) — see brand.template.json
    input/logo.png             your logo, transparent PNG
    input/photo.jpg            portrait used for the avatar / collage photo
    input/result/*.png         frames of the result clip (shown inside the phone)
    input/cutout.png           subject cut-out for editorial_depth
    input/partner_1.png        partner logo 1 (liquid_glass, paper_collage), only for that promo
    input/partner_2.png        partner logo 2 (liquid_glass, paper_collage), only for that promo
    input/flag_1.jpg           flag / badge 1 (liquid_glass, paper_collage)
    input/flag_2.png           flag / badge 2 (liquid_glass, paper_collage)
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENGINE_DIR = ROOT / "engine"
FONTS_DIR = Path(os.environ.get("ATC_FONTS_DIR", ENGINE_DIR / "fonts")).resolve()
ASSETS_DIR = ROOT / "assets"
EXAMPLE_BRAND_DIR = ROOT / "examples" / "adeltechtalks"
INPUT_DIR = Path(os.environ.get("ATC_INPUT_DIR", "input")).resolve()
WORK_DIR = Path(os.environ.get("ATC_WORK_DIR", "work")).resolve()
OUT_DIR = Path(os.environ.get("ATC_OUT_DIR", "output")).resolve()

for _d in (WORK_DIR, OUT_DIR):
    _d.mkdir(parents=True, exist_ok=True)

MISSING = []


def work(name):
    """Path for an intermediate file (test frames, silent mp4, wav)."""
    return str(WORK_DIR / name)


def asset(name):
    """Path to a file that ships with the skill (assets/)."""
    return str(ASSETS_DIR / name)


def _note(name, what):
    if name not in MISSING:
        MISSING.append(name)
        print(f"[placeholder] {INPUT_DIR / name} not found — using a placeholder for {what}.")


def _placeholder(size, label, rgba=False):
    from PIL import Image, ImageDraw
    w, h = size
    im = Image.new("RGBA" if rgba else "RGB", (w, h), (220, 235, 255, 255) if rgba else (220, 235, 255))
    d = ImageDraw.Draw(im)
    step = max(12, min(w, h) // 8)
    for x in range(-h, w, step):
        d.line([(x, 0), (x + h, h)], fill=(200, 218, 245), width=max(2, step // 6))
    d.rectangle([0, 0, w - 1, h - 1], outline=(37, 99, 235), width=max(2, min(w, h) // 60))
    d.text((w // 2, h // 2), label, fill=(23, 70, 162), anchor="mm")
    return im


def input_image(name, size=(1600, 1600), what="photo", rgba=False):
    """Open input/<name>, or return a labelled placeholder of `size`."""
    from PIL import Image
    p = INPUT_DIR / name
    if p.exists():
        return Image.open(p)
    _note(name, what)
    return _placeholder(size, name, rgba)


def input_frames(folder="result", size=(540, 960), count=24, what="result clip frames"):
    """PNG frames from input/<folder>/, or `count` placeholder frames."""
    from PIL import Image
    d = INPUT_DIR / folder
    files = sorted(d.glob("*.png")) if d.is_dir() else []
    if files:
        return [Image.open(p).convert("RGBA") for p in files]
    _note(folder + "/*.png", what)
    return [_placeholder(size, f"{folder} {i + 1}/{count}", rgba=True) for i in range(count)]


# ---------- brand ----------
_BRAND = None


def _rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def brand():
    """Brand settings: input/brand.json (or $ATC_BRAND), else the example brand."""
    global _BRAND
    if _BRAND is None:
        import json
        p = Path(os.environ.get("ATC_BRAND", INPUT_DIR / "brand.json")).resolve()
        if not p.exists():
            print(f"[brand] {p} not found — using the example brand (examples/adeltechtalks). "
                  "Set up your own brand first (see SKILL.md, Step 0).")
            p = EXAMPLE_BRAND_DIR / "brand.json"
        with open(p, encoding="utf-8") as f:
            b = json.load(f)
        example = json.loads((EXAMPLE_BRAND_DIR / "brand.json").read_text(encoding="utf-8"))
        for key in ("colors", "fonts", "ending"):           # fill any missing keys from the example
            b[key] = {**example[key], **b.get(key, {})}
        for key in ("name", "tagline", "language", "logo"):
            b.setdefault(key, example[key])
        b["_dir"] = p.parent
        b["rgb"] = {k: _rgb(v) for k, v in b["colors"].items()}
        b["ending"] = {k: v.replace("{name}", b["name"]) for k, v in b["ending"].items()}
        _BRAND = b
    return _BRAND


def color(name):
    return brand()["rgb"][name]


def logo():
    """The brand logo as RGBA (a transparent PNG works best), or a lettered placeholder."""
    from PIL import Image, ImageDraw
    b = brand()
    p = Path(b["_dir"]) / b["logo"]
    if p.exists():
        return Image.open(p).convert("RGBA")
    _note(b["logo"], "the brand logo")
    im = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((112, 112, 912, 912), fill=(255, 255, 255, 255))
    d.ellipse((232, 232, 792, 792), fill=(0, 0, 0, 0))
    return im
