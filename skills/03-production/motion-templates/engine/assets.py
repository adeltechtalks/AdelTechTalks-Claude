"""Find free, licence-safe images for a video when the user has none.

    python engine/assets.py search "astronaut helmet" [--source all] [--n 12] [--portrait]
    python engine/assets.py get 3 --as photo.jpg [--cutout [--one]] [--bw]
    python engine/assets.py credits

search   looks in Openverse (CC0 / CC BY / CC BY-SA, commercial use allowed),
         Wikimedia Commons, NASA Images (public domain) and — when you set a free
         key — Pexels (PEXELS_API_KEY), Pixabay (PIXABAY_API_KEY), Unsplash
         (UNSPLASH_ACCESS_KEY). Writes work/assets/<query>/sheet.jpg (numbered
         thumbnails to pick from) and results.json.
get      downloads result N of the last search into input/<name>, optionally cuts
         out the subject (--cutout → transparent PNG, needs `pip install rembg[cpu]`;
         --one keeps only the biggest subject)
         and/or makes it black & white (--bw). Logs source + licence + author in
         input/credits.json.
credits  prints the credit lines to paste into the caption.

Never use images of real people, film stills, brand logos or anything the
licence doesn't allow — only what this tool returns, and keep the credits.
"""
import argparse
import io
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # skill root, so the engine package is importable
from engine import config

import requests
from PIL import Image, ImageDraw, ImageOps

UA = {"User-Agent": "motion-templates/1.3 (https://github.com/adeltechtalks/AdelTechTalks-Claude)"}
LAST = Path(config.work("assets")) / "last.json"


def _get(url, **kw):
    r = requests.get(url, headers={**UA, **kw.pop("headers", {})}, timeout=25, **kw)
    r.raise_for_status()
    return r


def openverse(q, n, portrait):
    p = {"q": q, "page_size": n, "license_type": "commercial,modification", "mature": "false"}
    if portrait:
        p["aspect_ratio"] = "tall"
    out = []
    for it in _get("https://api.openverse.org/v1/images/", params=p).json().get("results", []):
        out.append({"source": "Openverse/" + (it.get("source") or ""), "title": it.get("title") or "",
                    "thumb": it.get("thumbnail") or it["url"], "url": it["url"],
                    "license": f"CC {it['license'].upper()} {it.get('license_version') or ''}".replace("CC CC0", "CC0").replace("CC PDM", "Public Domain").strip(),
                    "author": it.get("creator") or "", "page": it.get("foreign_landing_url") or ""})
    return out


def commons(q, n, portrait):
    p = {"action": "query", "format": "json", "generator": "search", "gsrsearch": f"{q} filetype:bitmap",
         "gsrnamespace": 6, "gsrlimit": n, "prop": "imageinfo", "iiprop": "url|extmetadata|size", "iiurlwidth": 400}
    pages = _get("https://commons.wikimedia.org/w/api.php", params=p).json().get("query", {}).get("pages", {})
    out = []
    for pg in sorted(pages.values(), key=lambda x: x.get("index", 0)):
        ii = pg["imageinfo"][0]; md = ii.get("extmetadata", {})
        lic = md.get("LicenseShortName", {}).get("value", "")
        if not re.search(r"CC0|Public domain|CC BY", lic, re.I) or re.search(r"NC|ND", lic):
            continue
        if portrait and ii.get("height", 0) < ii.get("width", 1):
            continue
        out.append({"source": "Wikimedia Commons", "title": pg["title"].removeprefix("File:"), "thumb": ii["thumburl"],
                    "url": ii["url"], "license": lic,
                    "author": re.sub(r"<[^>]+>", "", md.get("Artist", {}).get("value", "")).strip(),
                    "page": ii.get("descriptionurl", "")})
    return out


def nasa(q, n, portrait):
    items = _get("https://images-api.nasa.gov/search", params={"q": q, "media_type": "image", "page_size": n}).json()["collection"]["items"]
    out = []
    for it in items[:n]:
        d = it["data"][0]; thumb = it["links"][0]["href"]
        out.append({"source": "NASA", "title": d.get("title", ""), "thumb": thumb,
                    "url": thumb.replace("~thumb", "~orig"), "alt": thumb.replace("~thumb", "~large"),
                    "license": "Public Domain (NASA)", "author": d.get("photographer") or d.get("center", "NASA"),
                    "page": f"https://images.nasa.gov/details/{d['nasa_id']}"})
    return out


def pexels(q, n, portrait):
    key = os.environ.get("PEXELS_API_KEY")
    if not key:
        return []
    p = {"query": q, "per_page": n, **({"orientation": "portrait"} if portrait else {})}
    return [{"source": "Pexels", "title": it.get("alt", ""), "thumb": it["src"]["medium"], "url": it["src"]["large2x"],
             "license": "Pexels License", "author": it["photographer"], "page": it["url"]}
            for it in _get("https://api.pexels.com/v1/search", params=p, headers={"Authorization": key}).json()["photos"]]


def pixabay(q, n, portrait):
    key = os.environ.get("PIXABAY_API_KEY")
    if not key:
        return []
    p = {"key": key, "q": q, "per_page": max(3, n), "safesearch": "true", **({"orientation": "vertical"} if portrait else {})}
    return [{"source": "Pixabay", "title": it.get("tags", ""), "thumb": it["webformatURL"], "url": it["largeImageURL"],
             "license": "Pixabay Content License", "author": it["user"], "page": it["pageURL"]}
            for it in _get("https://pixabay.com/api/", params=p).json()["hits"]]


def unsplash(q, n, portrait):
    key = os.environ.get("UNSPLASH_ACCESS_KEY")
    if not key:
        return []
    p = {"query": q, "per_page": n, **({"orientation": "portrait"} if portrait else {})}
    return [{"source": "Unsplash", "title": it.get("alt_description") or "", "thumb": it["urls"]["small"], "url": it["urls"]["full"],
             "license": "Unsplash License", "author": it["user"]["name"], "page": it["links"]["html"]}
            for it in _get("https://api.unsplash.com/search/photos", params=p, headers={"Authorization": f"Client-ID {key}"}).json()["results"]]


SOURCES = {"openverse": openverse, "commons": commons, "nasa": nasa, "pexels": pexels, "pixabay": pixabay, "unsplash": unsplash}


def search(a):
    names = list(SOURCES) if a.source == "all" else a.source.split(",")
    res = []
    for s in names:
        try:
            got = SOURCES[s](a.query, a.n, a.portrait)
            res += got
            print(f"  {s:<9} {len(got)}")
        except Exception as e:  # one source down shouldn't stop the search
            print(f"  {s:<9} skipped ({e.__class__.__name__})")
    if not res:
        sys.exit("nothing found — try other words (English works best) or another --source")
    out = Path(config.work("assets")) / re.sub(r"\W+", "_", a.query).strip("_")
    out.mkdir(parents=True, exist_ok=True)
    tw, th, cols = 240, 300, 6
    thumbs = []
    for i, r in enumerate(res):
        try:
            im = Image.open(io.BytesIO(_get(r["thumb"]).content)).convert("RGB")
            thumbs.append((i, ImageOps.fit(im, (tw, th))))
        except Exception:
            pass
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * (th + 26)), "white")
    d = ImageDraw.Draw(sheet)
    for k, (i, im) in enumerate(thumbs):
        x, y = (k % cols) * tw, (k // cols) * (th + 26)
        sheet.paste(im, (x, y + 26))
        d.text((x + 6, y + 6), f"#{i}  {res[i]['source'][:22]}", fill=(0, 0, 0))
    sheet.save(out / "sheet.jpg", quality=85)
    (out / "results.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))
    LAST.write_text(json.dumps({"query": a.query, "results": str(out / "results.json")}))
    print(f"{len(res)} results · pick one from {out / 'sheet.jpg'}")


def get(a):
    last = json.loads(LAST.read_text())
    r = json.loads(Path(last["results"]).read_text())[a.index]
    try:
        raw = _get(r["url"]).content
    except Exception:
        raw = _get(r.get("alt", r["thumb"])).content
    im = Image.open(io.BytesIO(raw))
    im = ImageOps.exif_transpose(im).convert("RGB")
    if max(im.size) > 2400:
        im.thumbnail((2400, 2400), Image.LANCZOS)
    if a.bw:
        im = ImageOps.grayscale(im).convert("RGB")
    dest = Path(config.INPUT_DIR) / a.as_
    dest.parent.mkdir(parents=True, exist_ok=True)
    if a.cutout:
        try:
            from rembg import new_session, remove
        except ImportError:
            sys.exit("--cutout needs: pip install 'rembg[cpu]'")
        # isnet-general-use: ~170 MB, downloaded once to ~/.rembg; MT_CUTOUT_MODEL=u2netp for a 5 MB quick one
        im = remove(im, session=new_session(os.environ.get("MT_CUTOUT_MODEL", "isnet-general-use")))
        if a.one:  # keep only the biggest subject
            import numpy as np
            from scipy import ndimage
            al = np.asarray(im.split()[3]) > 40
            lab, n = ndimage.label(al)
            if n > 1:
                keep = lab == (np.argmax(ndimage.sum(al, lab, range(1, n + 1))) + 1)
                im.putalpha(Image.fromarray((np.asarray(im.split()[3]) * keep).astype("uint8")))
        im = im.crop(im.getbbox())
        dest = dest.with_suffix(".png")
    im.save(dest)
    cred = Path(config.INPUT_DIR) / "credits.json"
    log = json.loads(cred.read_text()) if cred.exists() else []
    log = [c for c in log if c["file"] != dest.name] + [{"file": dest.name, **{k: r[k] for k in ("title", "author", "license", "source", "page")}}]
    cred.write_text(json.dumps(log, indent=1, ensure_ascii=False))
    print(f"saved {dest} ({im.size[0]}×{im.size[1]}) · {r['license']} · {r['author'] or r['source']}")


def credits(_):
    cred = Path(config.INPUT_DIR) / "credits.json"
    for c in json.loads(cred.read_text()) if cred.exists() else []:
        print(f"{c['file']}: “{c['title'][:60]}” by {c['author'] or c['source']} · {c['license']} · {c['page']}")


def main():
    ap = argparse.ArgumentParser(description="Find free, licence-safe images.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search"); s.add_argument("query"); s.add_argument("--source", default="all")
    s.add_argument("--n", type=int, default=12); s.add_argument("--portrait", action="store_true")
    g = sub.add_parser("get"); g.add_argument("index", type=int); g.add_argument("--as", dest="as_", required=True)
    g.add_argument("--cutout", action="store_true"); g.add_argument("--one", action="store_true"); g.add_argument("--bw", action="store_true")
    sub.add_parser("credits")
    a = ap.parse_args()
    {"search": search, "get": get, "credits": credits}[a.cmd](a)


if __name__ == "__main__":
    main()
