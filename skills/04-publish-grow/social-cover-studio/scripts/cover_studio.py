#!/usr/bin/env python3
"""Social Cover Studio — one photo -> branded covers/thumbnails in 4 templates x 3 sizes.

Templates:  depth | cinematic | studio | creator
  depth      big word BEHIND the product/person, product + keyword underneath (minimal)
  cinematic  full photo, dark film grade, pill label + 2-line headline at the bottom
  studio     subject cut out onto a brand-colour backdrop with glow, huge title under it
  creator    made for photos of a PERSON with the product: word behind the head,
             product name chip + tilted keyword sticker

Examples:
  python cover_studio.py --image p.jpg --word GLACIER --product "iPhone 18 Pro Max" \
     --keyword "لوني المفضل" --emoji 💙 --brand brand.json --template all --preview --out out/
  python cover_studio.py ... --template depth --sizes 9x16,4x5,16x9 --out out/
"""
import argparse, json, os, urllib.request
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

CACHE = os.path.expanduser("~/.cache/cover-studio"); os.makedirs(CACHE, exist_ok=True)
GF = "https://raw.githubusercontent.com/google/fonts/main/"
FONTS = {  # name -> (path in google/fonts, is_variable)
    "Montserrat": ("ofl/montserrat/Montserrat%5Bwght%5D.ttf", True),
    "Inter": ("ofl/inter/Inter%5Bopsz,wght%5D.ttf", True),
    "Poppins": ("ofl/poppins/Poppins-ExtraBold.ttf", False),
    "Bebas Neue": ("ofl/bebasneue/BebasNeue-Regular.ttf", False),
    "Anton": ("ofl/anton/Anton-Regular.ttf", False),
    "Cairo": ("ofl/cairo/Cairo%5Bslnt,wght%5D.ttf", True),
    "Tajawal": ("ofl/tajawal/Tajawal-ExtraBold.ttf", False),
    "Readex Pro": ("ofl/readexpro/ReadexPro%5BHEXP,wght%5D.ttf", True),
    "IBM Plex Sans Arabic": ("ofl/ibmplexsansarabic/IBMPlexSansArabic-Bold.ttf", False),
    "Alexandria": ("ofl/alexandria/Alexandria%5Bwght%5D.ttf", True),
}
DEFAULT_BRAND = {          # neutral starter look — every creator should replace it with their own
    "handle": "",
    "dark": "#111318",       # backgrounds / shadows
    "dark_2": "#1E1B2E",     # second background tone
    "primary": "#FF6A3D",    # glow, dots, studio backdrop
    "highlight": "#FFD23F",  # second headline line, chips
    "light": "#FFFFFF",      # main text
    "soft": "#F1F1F1",       # keyword text
    "font_latin": "Montserrat",
    "font_arabic": "Cairo",
    "background_darkness": 0.5,
    "clean": True,           # real photo colours + light background blur (set False for the dark cinematic look)
    "bg_blur": 7,
    "primary_deep": "#C2410C"
}
AR = dict(direction='rtl', language='ar')
def rgb(h): h = h.lstrip('#'); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
def rtl(s): return any('\u0590' <= c <= '\u08FF' for c in s)
def fetch(url, name):
    p = os.path.join(CACHE, name)
    if not os.path.exists(p) or os.path.getsize(p) < 1000: urllib.request.urlretrieve(url, p)
    return p
def fpath(name):
    path, _ = FONTS.get(name, FONTS["Montserrat"]); return fetch(GF + path, name.replace(' ', '_') + '.ttf')
def font(name, size, weight=800):
    f = ImageFont.truetype(fpath(name), size)
    try:
        f.set_variation_by_axes([weight if a['name'] in (b'Weight', 'Weight') else a['default'] for a in f.get_variation_axes()])
    except Exception: pass
    return f
def emoji_img(ch):
    if not ch: return None
    cps = '-'.join(f"{ord(c):x}" for c in ch if ord(c) != 0xFE0F)
    svg = fetch(f"https://raw.githubusercontent.com/jdecked/twemoji/main/assets/svg/{cps}.svg", f"e_{cps}.svg")
    import cairosvg; png = os.path.join(CACHE, f"e_{cps}.png")
    cairosvg.svg2png(url=svg, write_to=png, output_width=300, output_height=300)
    return Image.open(png).convert('RGBA')

# ------------------------------------------------------------------ segmentation
def segment(img):
    import cv2
    from rembg import remove, new_session
    from pymatting import estimate_foreground_ml
    hard = remove(img, session=new_session('isnet-general-use'), only_mask=True)
    loose = remove(img, session=new_session('u2net'), only_mask=True)
    h = np.asarray(hard); full = np.maximum(h, np.asarray(loose))
    ycc = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2YCrCb)          # add the holding hand
    sk = cv2.inRange(ycc, (40, 135, 85), (255, 180, 135))
    sk = cv2.morphologyEx(sk, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
    sk = cv2.morphologyEx(sk, cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
    near = cv2.dilate((h > 128).astype(np.uint8), np.ones((81, 81), np.uint8))
    hy = np.where((h > 128).any(1))[0]
    below = np.zeros_like(sk); below[int(hy.min() + 0.15 * (hy.max() - hy.min())):, :] = 1   # hands hold from the sides/below, not above the product
    full = np.maximum(full, ((sk > 0) & (near > 0) & (below > 0)).astype(np.uint8) * 255)   # skin right next to the product only
    # keep only the blobs that actually touch the subject (drop stray desk / light pieces)
    fb = (full > 110).astype(np.uint8); n, lab, st, _ = cv2.connectedComponentsWithStats(fb)
    keep = np.zeros_like(fb)
    for k in range(1, n):
        c = lab == k
        if (c & (h > 128)).any(): keep[c] = 1
    full = (full.astype(np.float32) * cv2.dilate(keep, np.ones((5, 5), np.uint8))).astype(np.uint8)
    full[:max(0, int(hy.min()) - 6), :] = 0   # nothing above the product's top edge belongs to the subject
    full = np.maximum(full, h)
    fgc = estimate_foreground_ml(np.asarray(img) / 255.0, np.maximum(h, full) / 255.0)
    fg = Image.fromarray((np.clip(fgc, 0, 1) * 255).astype(np.uint8))
    tight = lambda m: m.point(lambda v: int(255 * min(1, max(0, (v / 255 - 0.15) / 0.7))))
    return dict(hard=tight(hard), full=tight(Image.fromarray(full).filter(ImageFilter.GaussianBlur(1.5))),
                soft=Image.fromarray(full).filter(ImageFilter.GaussianBlur(25)), fg=fg)

def subject_box(mask):
    hb = np.asarray(mask) > 128; ys, xs = np.where(hb); w = hb.sum(1)
    rows = np.where(w >= 0.45 * w.max())[0]; top, bot = ys.min(), rows.max()
    x2 = np.where(hb[top:bot + 1].any(0))[0]
    return top, bot, (x2.min() + x2.max()) / 2, x2.min(), x2.max()

# ------------------------------------------------------------------ drawing helpers
class Canvas:
    def __init__(s, W, H, B): s.W, s.H, s.B = W, H, B; s.im = Image.new('RGBA', (W, H), rgb(B['dark']) + (255,)); s.Y, s.X = np.mgrid[0:H, 0:W]
    def over(s, layer): s.im = Image.alpha_composite(s.im, layer)
    def paste_photo(s, img, sc, ox, oy, feather=True, mask=None):
        pw, ph = int(img.width * sc), int(img.height * sc); r = img.resize((pw, ph), Image.LANCZOS).convert('RGBA')
        if mask is None:
            yy, xx = np.mgrid[0:ph, 0:pw]; e = min(pw, ph) * 0.1; fm = np.ones((ph, pw), np.float32)
            if feather:
                if ox > 0: fm *= np.clip(xx / e, 0, 1)
                if ox + pw < s.W: fm *= np.clip((pw - xx) / e, 0, 1)
                if oy > 0: fm *= np.clip(yy / e, 0, 1)
                if oy + ph < s.H: fm *= np.clip((ph - yy) / e, 0, 1)
            m = Image.fromarray((fm * 255).astype(np.uint8))
        else: m = mask.resize((pw, ph), Image.LANCZOS)
        layer = Image.new('RGBA', (s.W, s.H), (0, 0, 0, 0)); lm = Image.new('L', (s.W, s.H), 0)
        layer.paste(r, (ox, oy)); lm.paste(m, (ox, oy)); s.im = Image.composite(layer, s.im, lm)
    def fill_blur(s, dark):
        cs = max(s.W / dark.width, s.H / dark.height); f = dark.resize((int(dark.width * cs) + 2, int(dark.height * cs) + 2)).filter(ImageFilter.GaussianBlur(45))
        s.im = f.crop(((f.width - s.W) // 2, (f.height - s.H) // 2, (f.width - s.W) // 2 + s.W, (f.height - s.H) // 2 + s.H)).convert('RGBA')
    def glow(s, cx, cy, rx, ry, color, alpha):
        g = np.exp(-(((s.X - cx) / rx) ** 2 + ((s.Y - cy) / ry) ** 2)); a = np.zeros((s.H, s.W, 4), np.uint8); a[..., :3] = color; a[..., 3] = (g * alpha).astype(np.uint8); s.over(Image.fromarray(a, 'RGBA'))
    def shade(s, alpha_map, color):
        a = np.zeros((s.H, s.W, 4), np.uint8); a[..., :3] = color; a[..., 3] = np.clip(alpha_map, 0, 255).astype(np.uint8); s.over(Image.fromarray(a, 'RGBA'))
    def fit_font(s, text, fam, width, maxsize, weight=800):
        d = ImageDraw.Draw(s.im); kw = AR if rtl(text) else {}
        b = d.textbbox((0, 0), text, font=font(fam, 300, weight), **kw); size = min(maxsize, int(300 * width / max(1, b[2] - b[0])))
        return font(fam, size, weight)
    def text(s, xy, t, f, fill, anchor='l', shadow=True):
        d = ImageDraw.Draw(s.im); kw = AR if rtl(t) else {}; b = d.textbbox((0, 0), t, font=f, **kw)
        x = xy[0] - b[0] if anchor == 'l' else (s.W - (b[2] - b[0])) // 2 - b[0] if anchor == 'c' else xy[0] - b[2]
        y = xy[1] - b[1]
        if shadow:
            sh = Image.new('RGBA', (s.W, s.H), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((x + 3, y + 5), t, font=f, fill=(0, 0, 0, 150), **kw); s.over(sh.filter(ImageFilter.GaussianBlur(8)))
        ImageDraw.Draw(s.im).text((x, y), t, font=f, fill=fill, **kw)
        return (x + b[0], xy[1], x + b[2], xy[1] + b[3] - b[1])
    def gradient_text(s, xy, t, f, c1, c2, glowc=None):
        kw = AR if rtl(t) else {}; d = ImageDraw.Draw(s.im); b = d.textbbox((0, 0), t, font=f, **kw)
        x = (s.W - (b[2] - b[0])) // 2 - b[0] if xy[0] is None else xy[0] - b[0]; y = xy[1] - b[1]
        if glowc:
            g = Image.new('RGBA', (s.W, s.H), (0, 0, 0, 0)); ImageDraw.Draw(g).text((x, y), t, font=f, fill=glowc + (190,), **kw); s.over(g.filter(ImageFilter.GaussianBlur(max(12, s.H // 70))))
        m = Image.new('L', (s.W, s.H), 0); ImageDraw.Draw(m).text((x, y), t, font=f, fill=255, **kw)
        tt = np.clip((s.Y - xy[1]) / max(1, b[3] - b[1]), 0, 1)[..., None]; g = np.zeros((s.H, s.W, 4), np.uint8)
        g[..., :3] = (np.array(c1) * (1 - tt) + np.array(c2) * tt).astype(np.uint8); g[..., 3] = 255
        s.im = Image.composite(Image.fromarray(g, 'RGBA'), s.im, m); return m, (x + b[0], xy[1], x + b[2], xy[1] + b[3] - b[1])
    def keyword(s, x, y, kw_text, emo, size, color, center=False, fam_ar='Cairo', fam_lat='Montserrat'):
        if not kw_text and not emo: return
        f = font(fam_ar, int(size * 1.43), 900) if rtl(kw_text) else font(fam_lat, int(size * 1.1), 800)
        d = ImageDraw.Draw(s.im); kwa = AR if rtl(kw_text) else {}; b = d.textbbox((0, 0), kw_text, font=f, **kwa) if kw_text else (0, 0, 0, 0)
        es = int(size * 1.3) if emo else 0; gap = int(size * 0.28) if emo and kw_text else 0; w = b[2] - b[0] + gap + es
        x0 = (s.W - w) // 2 if center else x; mid = y + (b[3] + b[1]) // 2 if kw_text else y + es // 2
        if rtl(kw_text):
            if emo: s.im.alpha_composite(emo.resize((es, es), Image.LANCZOS), (x0, mid - es // 2))
            if kw_text: ImageDraw.Draw(s.im).text((x0 + es + gap - b[0], y), kw_text, font=f, fill=color, **kwa)
        else:
            if kw_text: ImageDraw.Draw(s.im).text((x0 - b[0], y), kw_text, font=f, fill=color)
            if emo: s.im.alpha_composite(emo.resize((es, es), Image.LANCZOS), (x0 + b[2] - b[0] + gap, mid - es // 2))
    def handle(s, x, y, B):
        if not B.get('handle'): return
        ws = max(26, int(min(s.W, s.H) * 0.04)); f = font(B['font_latin'], ws, 700); d = ImageDraw.Draw(s.im)
        if B.get('clean'):   # readable on any photo without darkening it
            tb = d.textbbox((0, 0), B['handle'], font=f); pad = int(ws * 0.45)
            d.rounded_rectangle((x - pad, y - pad * 0.6, x + ws * 0.8 + tb[2] + pad, y + tb[3] + pad * 0.8), radius=int(ws), fill=(255, 255, 255))
            d.ellipse((x, y + ws * 0.25, x + ws * 0.5, y + ws * 0.75), fill=rgb(B['primary'])); d.text((x + ws * 0.8, y), B['handle'], font=f, fill=rgb(B['dark'])); return
        d.ellipse((x, y + ws * 0.25, x + ws * 0.5, y + ws * 0.75), fill=rgb(B['primary'])); d.text((x + ws * 0.8, y), B['handle'], font=f, fill=(255, 255, 255, 230))
    def chip(s, x, y, t, f, bg, fg, pad=(34, 18), radius=None, rotate=0, outline=False, center=False):
        kw = AR if rtl(t) else {}; d = ImageDraw.Draw(s.im); b = d.textbbox((0, 0), t, font=f, **kw)
        w, h = b[2] - b[0] + 2 * pad[0], b[3] - b[1] + 2 * pad[1]; r = radius if radius is not None else h // 2
        c = Image.new('RGBA', (w + 4, h + 4), (0, 0, 0, 0)); cd = ImageDraw.Draw(c)
        if outline: cd.rounded_rectangle((2, 2, w, h), radius=r, outline=bg, width=4)
        else: cd.rounded_rectangle((2, 2, w, h), radius=r, fill=bg)
        cd.text((2 + pad[0] - b[0], 2 + pad[1] - b[1]), t, font=f, fill=fg, **kw)
        if rotate: c = c.rotate(rotate, expand=True, resample=Image.BICUBIC)
        if center: x = (s.W - c.width) // 2
        s.im.alpha_composite(c, (int(x), int(y))); return (x, y, x + c.width, y + c.height)

def darkened(img, B, k=None):
    if B.get('clean'):   # clean mode: real colours, only a light blur to separate the product from the background
        return img.filter(ImageFilter.GaussianBlur(B.get('bg_blur', 7) * img.width / 1450))
    k = B['background_darkness'] if k is None else k
    t = np.array(rgb(B['dark']), np.float32) * 0.5 + np.array(rgb(B['dark_2']), np.float32) * 0.5
    return Image.fromarray(np.clip(np.asarray(img).astype(np.float32) * (1 - k) + t * k, 0, 255).astype(np.uint8))

def place(img, box, W, H, top_y, bottom_y, cx_target, cover_w=True, cover_h=True):
    top, bot, cx = box[0], box[1], box[2]
    sc = (bottom_y - top_y) / (bot - top)
    if cover_w: sc = max(sc, W / img.width)
    if cover_h: sc = max(sc, (H - top_y) / (img.height - top))   # photo always reaches the bottom edge
    ox = int(cx_target - cx * sc); pw = img.width * sc
    if pw >= W: ox = int(min(0, max(W - pw, ox)))
    return sc, ox, int(top_y - top * sc)

def chip_block(c, B, a, E, y, center=True, x=110, psize=52):
    """Product name + keyword as solid chips: readable on any photo without darkening it."""
    fp = font(B['font_latin'], psize, 800)
    r = c.chip(x, y, a.product, fp, rgb(B['dark']), (255, 255, 255), center=center, pad=(36, 18))
    if a.keyword:
        fk = font(B['font_arabic'], int(psize * 1.15), 900) if rtl(a.keyword) else font(B['font_latin'], psize, 800)
        k = c.chip(x, r[3] + 16, a.keyword, fk, rgb(B['primary']), (255, 255, 255), center=center, pad=(36, 14))
        if E: c.im.alpha_composite(E.resize((72, 72), Image.LANCZOS), (int(k[2]) - 20, int((k[1] + k[3]) / 2) - 36))
        return k[3]
    return r[3]

# ------------------------------------------------------------------ templates (9:16 base, 1080x1920)
SAFE_TOP, SAFE_BOT = 240, 1680      # IG/TikTok grid shows only the centre 3:4

def t_depth(img, S, B, a, E):
    W, H = 1080, 1920; c = Canvas(W, H, B); dark = darkened(img, B); c.fill_blur(dark)
    box = subject_box(S['hard']); fw = c.fit_font(a.word, B['font_arabic'] if rtl(a.word) else B['font_latin'], W - 130, 330)
    wb = ImageDraw.Draw(c.im).textbbox((0, 0), a.word, font=fw, **(AR if rtl(a.word) else {})); cap = wb[3] - wb[1]
    clean = B.get('clean', False)
    wy = 420; ps = 58; text_max = 1590 - (230 if clean else int(ps * 1.3 + ps * 1.43 * 1.25))   # everything stays inside the 4:5 zone (y 265-1615)
    sc, ox, oy = place(img, box, W, H, wy + cap * 0.62, text_max + 30, W / 2)
    c.paste_photo(dark, sc, ox, oy)
    if not clean: c.glow(ox + box[2] * sc, oy + (box[0] + box[1]) / 2 * sc, (box[4] - box[3]) * sc * 0.75, (box[1] - box[0]) * sc * 0.65, rgb(B['primary']), 35)
    if clean: tm, _ = c.gradient_text((None, wy), a.word, fw, rgb(B['primary']), rgb(B.get('primary_deep', '#1746A2')))
    else: tm, _ = c.gradient_text((None, wy), a.word, fw, rgb(B['light']), rgb(B['soft']) if B.get('word_bottom') is None else rgb(B['word_bottom']), rgb(B['primary']))
    if not clean:
        sm = S['soft'].resize((int(img.width * sc), int(img.height * sc))); lay = Image.new('L', (W, H), 0); lay.paste(sm, (ox, oy))
        tmd = np.asarray(tm.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(6))) / 255.0
        spot = Image.fromarray((np.asarray(lay).astype(np.float32) * (1 - tmd)).astype(np.uint8))
        L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); L.paste(img.resize((int(img.width * sc), int(img.height * sc))).convert('RGBA'), (ox, oy)); c.im = Image.composite(L, c.im, spot)
    ty = int(min(text_max, oy + box[1] * sc + 20))
    if not clean: c.shade(np.clip((c.Y - (ty - H * 0.1)) / (H * 0.25), 0, 1) ** 1.3 * 200, rgb(B['dark']))   # shade the background only
    c.paste_photo(S['fg'], sc, ox, oy, mask=S['full'] if clean else S['hard'])   # product (and the hand holding it) sharp on top, true colours
    if clean:
        chip_block(c, B, a, E, ty)
    else:
        c.text((0, ty), a.product, font(B['font_latin'], ps, 700), rgb(B['light']), 'c')
        c.keyword(0, ty + int(ps * 1.3), a.keyword, E, ps, rgb(B['soft']), center=True, fam_ar=B['font_arabic'], fam_lat=B['font_latin'])
    c.handle(int(W * 0.075), 300, B); return c.im.convert('RGB')

def t_cinematic(img, S, B, a, E):
    W, H = 1080, 1920; c = Canvas(W, H, B); dark = darkened(img, B, 0.35); c.fill_blur(dark)
    box = subject_box(S['hard'])
    sc, ox, oy = place(img, box, W, H, SAFE_TOP + 170, 1180, W / 2)
    c.paste_photo(dark, sc, ox, oy)
    c.shade(np.clip((c.Y - 900) / 700, 0, 1) ** 1.1 * 245, rgb(B['dark']))
    c.shade(np.clip((420 - c.Y) / 300, 0, 1) * 150, rgb(B['dark']))
    y = 1215
    if a.keyword or E:
        f = font(B['font_arabic'] if rtl(a.keyword) else B['font_latin'], 46, 600)
        r = c.chip(95, y, (a.keyword + ' ' if a.keyword else ''), f, rgb(B['light']), rgb(B['light']), outline=True, pad=(34, 16))
        if E: c.im.alpha_composite(E.resize((52, 52), Image.LANCZOS), (int(r[2]) + 14, int((r[1] + r[3]) / 2) - 26))
        y = int(r[3]) + 28
    f1 = c.fit_font(a.product, B['font_latin'], W - 190, 120, 800); r1 = c.text((95, y), a.product, f1, rgb(B['light']))
    f2 = c.fit_font(a.word, B['font_arabic'] if rtl(a.word) else B['font_latin'], W - 190, 190, 900)
    c.text((95, r1[3] + 14), a.word, f2, rgb(B['highlight']))
    c.handle(95, 300, B); return c.im.convert('RGB')

def t_studio(img, S, B, a, E):
    W, H = 1080, 1920; c = Canvas(W, H, B)
    c.shade(np.clip(c.Y / H, 0, 1) * 255, rgb(B['dark_2']))
    box = subject_box(S['full']); arm = (np.asarray(S['full'])[-1] > 128).any()
    sc, ox, oy = place(img, box, W, H, SAFE_TOP + 120, 1160, W / 2, cover_w=False, cover_h=False)
    if arm and oy + img.height * sc < H: sc2 = (H - oy) / img.height; sc = max(sc, sc2); ox = int(W / 2 - box[2] * sc)
    c.glow(W / 2, oy + (box[0] + box[1]) / 2 * sc, W * 0.55, H * 0.28, rgb(B['primary']), 200)
    c.glow(W / 2, oy + (box[0] + box[1]) / 2 * sc, W * 0.25, H * 0.12, rgb(B['highlight']), 60)
    # soft ground shadow
    c.paste_photo(S['fg'], sc, ox, oy, mask=S['full'])
    c.shade(np.clip((c.Y - 1150) / 420, 0, 1) ** 1.2 * 235, rgb(B['dark']))
    fw = c.fit_font(a.word, B['font_arabic'] if rtl(a.word) else B['font_latin'], W - 150, 260, 900)
    _, r = c.gradient_text((None, 1255), a.word, fw, rgb(B['light']), rgb(B['highlight']))
    c.text((0, r[3] + 26), a.product, font(B['font_latin'], 56, 700), rgb(B['light']), 'c')
    c.keyword(0, r[3] + 26 + 80, a.keyword, E, 50, rgb(B['soft']), center=True, fam_ar=B['font_arabic'], fam_lat=B['font_latin'])
    c.handle(int(W * 0.075), 300, B); return c.im.convert('RGB')

def t_creator(img, S, B, a, E):
    W, H = 1080, 1920; c = Canvas(W, H, B); dark = darkened(img, B, 0.4); c.fill_blur(dark)
    box = subject_box(S['full'])
    fw = c.fit_font(a.word, B['font_arabic'] if rtl(a.word) else B['font_latin'], W - 80, 420, 900)
    wb = ImageDraw.Draw(c.im).textbbox((0, 0), a.word, font=fw); cap = wb[3] - wb[1]
    wy = 380
    sc, ox, oy = place(img, box, W, H, wy + cap * 0.45, 1420, W / 2)
    c.paste_photo(dark, sc, ox, oy)
    tm, _ = c.gradient_text((None, wy), a.word, fw, rgb(B['highlight']), rgb(B['primary']), rgb(B['primary']))
    if not B.get('clean'): c.shade(np.clip((c.Y - 1250) / 450, 0, 1) ** 1.2 * 230, rgb(B['dark']))   # background only
    c.paste_photo(S['fg'], sc, ox, oy, mask=S['full'])   # subject keeps its real colours
    f = font(B['font_latin'], 50, 800)
    r = c.chip(0, 1400, a.product, f, rgb(B['light']) if not B.get('clean') else rgb(B['dark']), rgb(B['dark']) if not B.get('clean') else (255, 255, 255), center=True, pad=(40, 20))
    if a.keyword or E:
        fk = font(B['font_arabic'] if rtl(a.keyword) else B['font_latin'], 54, 800)
        k = c.chip(0, r[3] + 26, a.keyword or ' ', fk, rgb(B['highlight']), rgb(B['dark']), rotate=-4, radius=22, center=True, pad=(38, 18))
        if E: c.im.alpha_composite(E.resize((84, 84), Image.LANCZOS), (int(k[2]) - 18, int((k[1] + k[3]) / 2) - 42))
    c.handle(int(W * 0.075), 300, B); return c.im.convert('RGB')

# ------------------------------------------------------------------ 16:9 (shared wide layout, styled per template)
def wide(img, S, B, a, E, tpl):
    W, H = 1920, 1080; c = Canvas(W, H, B)
    use_full = tpl in ('studio', 'creator') or B.get('clean'); mask = S['full'] if use_full else S['hard']; box = subject_box(S['full'] if tpl in ('studio', 'creator') else S['hard'])
    sc = 0.78 * H / (box[1] - box[0]); ox = int(W * 0.73 - box[2] * sc); oy = int(H * 0.09 - box[0] * sc)
    if tpl == 'studio':
        c.shade(np.clip(c.X / W, 0, 1) * 255, rgb(B['dark_2'])); c.glow(W * 0.72, H * 0.5, W * 0.3, H * 0.6, rgb(B['primary']), 200)
        if ox + img.width * sc < W: pass
    else:
        dark = darkened(img, B, 0.35 if tpl == 'cinematic' else 0.5); c.fill_blur(dark)
        if ox + img.width * sc < W: ox = int(W - img.width * sc)
        c.paste_photo(dark, sc, ox, oy)
        if not B.get('clean'):
            c.shade(np.clip(((W * 0.55) - c.X) / (W * 0.4), 0, 1) * (170 if tpl == 'cinematic' else 120), rgb(B['dark']))
            if tpl == 'depth': c.glow(ox + box[2] * sc, H / 2, W * 0.2, H * 0.5, rgb(B['primary']), 85)
    left = ox + box[3] * sc
    fam_w = B['font_arabic'] if rtl(a.word) else B['font_latin']
    if tpl in ('depth', 'creator'):
        fw = c.fit_font(a.word, fam_w, max(700, min(1250, left + 0.03 * W - 95)), 330, 900)
        if B.get('clean'): c1, c2 = (rgb(B['primary']), rgb(B.get('primary_deep', '#1746A2'))) if tpl == 'depth' else (rgb(B['highlight']), rgb(B['primary']))
        else: c1, c2 = (rgb(B['light']), rgb(B.get('word_bottom', B['soft']))) if tpl == 'depth' else (rgb(B['highlight']), rgb(B['primary']))
        c.gradient_text((95, 210), a.word, fw, c1, c2, None if B.get('clean') else rgb(B['primary']))
        c.paste_photo(S['fg'], sc, ox, oy, mask=mask)
        if B.get('clean'): chip_block(c, B, a, E, 600, center=False, x=110, psize=64)
        else:
            c.text((110, 600), a.product, font(B['font_latin'], 72, 700), rgb(B['light']))
            c.keyword(110, 694, a.keyword, E, 72, rgb(B['soft']), fam_ar=B['font_arabic'], fam_lat=B['font_latin'])
    else:
        c.paste_photo(S['fg'], sc, ox, oy, mask=mask)
        f1 = c.fit_font(a.product, B['font_latin'], min(900, left - 170), 96, 800); r1 = c.text((110, 360), a.product, f1, rgb(B['light']))
        f2 = c.fit_font(a.word, fam_w, min(900, left - 170), 200, 900)
        if tpl == 'studio': _, r2 = c.gradient_text((110, r1[3] + 20), a.word, f2, rgb(B['light']), rgb(B['highlight']))
        else: r2 = c.text((110, r1[3] + 20), a.word, f2, rgb(B['highlight']))
        c.keyword(110, r2[3] + 40, a.keyword, E, 60, rgb(B['soft']), fam_ar=B['font_arabic'], fam_lat=B['font_latin'])
    c.handle(110, 80, B); return c.im.convert('RGB')

def _badge(c, x_right, y, text, B, size=26):
    if not text: return
    ar = rtl(text); kw = dict(direction='rtl', language='ar') if ar else {}
    d = ImageDraw.Draw(c.im); bf = font(B['font_arabic'] if ar else B['font_latin'], size, 800)
    b = d.textbbox((0, 0), text, font=bf, **kw); bw = b[2] - b[0] + 64
    d.rounded_rectangle((x_right - bw, y, x_right, y + 50), radius=25, fill=rgb(B['dark']))
    d.ellipse((x_right - bw + 18, y + 18, x_right - bw + 32, y + 32), fill=rgb(B['primary']))
    d.text((x_right - bw + 42 - b[0], y + 25 - (b[1] + b[3]) / 2), text, font=bf, fill=(255, 255, 255), **kw)

def _crop_to(img, box_xy, W, H, fill_ratio=0.9):
    """Crop the photo so the subject fills `fill_ratio` of the frame width (or height), centered."""
    top, bot, cx, x0, x1 = box_xy
    sw, sh = x1 - x0, bot - top
    s = min(W * fill_ratio / sw, H * 0.88 / sh)
    s = max(s, W / img.width, H / img.height)
    cy = (top + bot) / 2
    L = int(min(max(cx * s - W / 2, 0), img.width * s - W)); T = int(min(max(cy * s - H / 2, 0), img.height * s - H))
    return img.resize((int(img.width * s), int(img.height * s)), Image.LANCZOS).crop((L, T, L + W, T + H))

def t_editorial(img, S, B, a, E):
    """Light, photography-first: natural photo + clean Warm White text panel on top."""
    W, H = 1080, 1920; PANEL = 640
    c = Canvas(W, H, B); c.im = Image.new('RGBA', (W, H), rgb(B.get('surface', '#FAFAF8')) + (255,))
    box = subject_box(S['hard'])
    c.im.paste(_crop_to(img, box, W, H - PANEL, 0.86).convert('RGBA'), (0, PANEL))
    d = ImageDraw.Draw(c.im); ink = rgb(B['dark'])
    if B.get('handle'):
        f = font(B['font_latin'], 38, 700); d.ellipse((80, 300, 100, 320), fill=rgb(B['primary'])); d.text((114, 288), B['handle'], font=f, fill=ink)
    _badge(c, W - 80, 284, getattr(a, 'badge', ''), B)
    hf = c.fit_font(a.product, B['font_latin'], W - 160, 128, 800); c.text((0, 372), a.product, hf, ink, 'c', shadow=False)
    kw = (a.keyword or a.word)
    af = font(B['font_arabic'], 84, 900) if rtl(kw) else font(B['font_latin'], 76, 800)
    d = ImageDraw.Draw(c.im); kk = AR if rtl(kw) else {}; b2 = d.textbbox((0, 0), kw, font=af, **kk)
    es = 80 if E else 0; gap = 20 if E else 0; w2 = b2[2] - b2[0] + gap + es; x2 = (W - w2) // 2
    if E: c.im.alpha_composite(E.resize((es, es), Image.LANCZOS), (x2, 520 + (b2[3] - b2[1]) // 2 - es // 2 + 6))
    ImageDraw.Draw(c.im).text((x2 + es + gap - b2[0], 520 - b2[1]), kw, font=af, fill=rgb(B['primary']), **kk)
    return c.im.convert('RGB')

def wide_editorial(img, S, B, a, E):
    W, H = 1920, 1080; PANEL = 820
    c = Canvas(W, H, B); c.im = Image.new('RGBA', (W, H), rgb(B.get('surface', '#FAFAF8')) + (255,))
    c.im.paste(_crop_to(img, subject_box(S['hard']), W - PANEL, H, 0.78).convert('RGBA'), (PANEL, 0))
    d = ImageDraw.Draw(c.im); ink = rgb(B['dark'])
    if B.get('handle'):
        f = font(B['font_latin'], 36, 700); d.ellipse((90, 100, 108, 118), fill=rgb(B['primary'])); d.text((122, 88), B['handle'], font=f, fill=ink)
    hf = c.fit_font(a.product, B['font_latin'], PANEL - 170, 130, 800); r = c.text((90, 380), a.product, hf, ink, shadow=False)
    kw = (a.keyword or a.word); af = font(B['font_arabic'], 80, 900) if rtl(kw) else font(B['font_latin'], 72, 800)
    kk = AR if rtl(kw) else {}; ImageDraw.Draw(c.im).text((90, r[3] + 40), kw, font=af, fill=rgb(B['primary']), **kk)
    if getattr(a, 'badge', ''):
        _badge(c, 90 + 380, 250, a.badge, B)
    return c.im.convert('RGB')

def to_4x5(v):
    """Facebook 4:5 from a finished 9:16 cover without cutting text: keep the whole
    safe band (y 240-1690), scale it to 1350 high, and fill the side gaps with a
    blurred copy of the same band so nothing is cropped or stretched."""
    band = v.crop((0, 240, 1080, 1690))
    s = 1350 / band.height; bw = int(1080 * s)
    back = band.resize((1080, 1350), Image.LANCZOS).filter(ImageFilter.GaussianBlur(30))
    fg = band.resize((bw, 1350), Image.LANCZOS)
    m = Image.new('L', (bw, 1350), 255); md = np.asarray(m).astype(np.float32)
    e = 40; ramp = np.clip(np.arange(bw) / e, 0, 1) * np.clip((bw - 1 - np.arange(bw)) / e, 0, 1)
    m = Image.fromarray((np.tile(ramp, (1350, 1)) * 255).astype(np.uint8))
    back.paste(fg, ((1080 - bw) // 2, 0), m)
    return back

TEMPLATES = {'editorial': t_editorial,'depth': t_depth, 'cinematic': t_cinematic, 'studio': t_studio, 'creator': t_creator}
LABELS = {'editorial': '0 · Editorial', 'depth': '1 · Depth', 'cinematic': '2 · Cinematic', 'studio': '3 · Studio', 'creator': '4 · Creator'}

def main():
    ap = argparse.ArgumentParser()
    for k in ('image', 'word', 'product'): ap.add_argument('--' + k, required=True)
    ap.add_argument('--keyword', default=''); ap.add_argument('--badge', default=''); ap.add_argument('--emoji', default=''); ap.add_argument('--brand', default='')
    ap.add_argument('--template', default='all'); ap.add_argument('--sizes', default='9x16,4x5,16x9')
    ap.add_argument('--preview', action='store_true', help='only a side-by-side sheet of the templates (9:16)')
    ap.add_argument('--out', default='./covers'); ap.add_argument('--name', default='cover')
    a = ap.parse_args(); B = dict(DEFAULT_BRAND)
    if a.brand: B.update(json.load(open(a.brand)))
    os.makedirs(a.out, exist_ok=True)
    img = ImageOps.exif_transpose(Image.open(a.image)).convert('RGB')
    if max(img.size) > 2600: img.thumbnail((2600, 2600), Image.LANCZOS)
    S = segment(img); E = emoji_img(a.emoji)
    tpls = list(TEMPLATES) if a.template == 'all' else a.template.split(',')
    if a.preview:
        tiles = []
        for t in tpls:
            im = TEMPLATES[t](img, S, B, a, E).resize((432, 768), Image.LANCZOS)
            lab = Image.new('RGB', (432, 60), (255, 255, 255)); ImageDraw.Draw(lab).text((16, 12), LABELS[t], font=font('Montserrat', 30, 700), fill=(20, 20, 20))
            t_ = Image.new('RGB', (432, 828), 'white'); t_.paste(lab, (0, 0)); t_.paste(im, (0, 60)); tiles.append(t_)
        sheet = Image.new('RGB', (len(tiles) * 452 - 20, 828), 'white')
        for i, t_ in enumerate(tiles): sheet.paste(t_, (i * 452, 0))
        p = os.path.join(a.out, f'{a.name}_templates_preview.jpg'); sheet.save(p, quality=90); print(p); return
    for t in tpls:
        sizes = a.sizes.split(',')
        if '9x16' in sizes or '4x5' in sizes:
            v = TEMPLATES[t](img, S, B, a, E)
            if '9x16' in sizes: p = os.path.join(a.out, f'{a.name}_{t}_instagram-tiktok_1080x1920.jpg'); v.save(p, quality=92); print(p)
            if '4x5' in sizes: p = os.path.join(a.out, f'{a.name}_{t}_facebook_1080x1350.jpg'); to_4x5(v).save(p, quality=92); print(p)
        if '16x9' in sizes:
            p = os.path.join(a.out, f'{a.name}_{t}_youtube_1920x1080.jpg'); (wide_editorial(img, S, B, a, E) if t == 'editorial' else wide(img, S, B, a, E, t)).save(p, quality=92); print(p)

if __name__ == '__main__':
    main()
