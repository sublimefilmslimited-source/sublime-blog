"""Branded infographic generator for blog posts (original images rank best in Google Images).

Each image spec (from a post's front matter `images:` list):
  name:    keyword-rich file name, e.g. "social-media-manager-skills-checklist"
  type:    steps | checklist | table | chat
  title:   headline drawn on the image
  alt:     alt text (describe what the image shows, include the topic naturally)
  caption: visible caption under the image
  items:   steps/checklist -> list of "Label: optional detail" strings
           table           -> list of [left, right] pairs (first pair = header)
           chat            -> list of message strings (from the social media manager)
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

RED, INK, GREY, MIST, LINE, WHITE = "#d80707", "#0b0b0c", "#5d5f64", "#f5f5f6", "#e6e6e9", "#ffffff"
W = 1200
PAD = 80


def _font(src, weight, size):
    return ImageFont.truetype(str(Path(src) / f"Gilroy-{weight}.ttf"), size)


def _wrap(draw, text, font, width):
    words, lines, line = text.split(), [], ""
    for w in words:
        t = (line + " " + w).strip()
        if draw.textlength(t, font=font) <= width:
            line = t
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines


def _lh(font, k=1.3):
    a, d = font.getmetrics()
    return int((a + d) * k)


class _Canvas:
    """Two-pass drawing: measure height first, then paint."""

    def __init__(self, src, height=4000):
        self.src = src
        self.im = Image.new("RGB", (W, height), WHITE)
        self.d = ImageDraw.Draw(self.im)
        self.y = 0

    def f(self, weight, size):
        return _font(self.src, weight, size)


def _header(c, eyebrow, title):
    d = c.d
    d.rectangle([0, 0, W, 14], fill=RED)
    d.polygon([(W - 150, 14), (W, 14), (W, 164)], fill=INK)
    c.y = 78
    eb = c.f("Bold", 26)
    d.text((PAD, c.y), eyebrow.upper(), font=eb, fill=RED)
    c.y += 54
    size = 62
    while True:
        tf = c.f("Bold", size)
        lines = _wrap(d, title, tf, W - 2 * PAD - 60)
        if len(lines) <= 3 or size <= 44:
            break
        size -= 4
    for ln in lines:
        d.text((PAD, c.y), ln, font=tf, fill=INK)
        c.y += _lh(tf, 1.12)
    c.y += 36


def _footer(c):
    d = c.d
    c.y += 30
    d.line([(PAD, c.y), (W - PAD, c.y)], fill=LINE, width=2)
    c.y += 30
    # mini logo mark
    x, y = PAD, c.y
    d.polygon([(x + 8, y + 2), (x + 24, y), (x + 17, y + 9), (x + 14, y + 9), (x + 14, y + 14), (x + 8, y + 21), (x + 8, y + 8)], fill=INK)
    d.polygon([(x + 19, y + 29), (x + 3, y + 30), (x + 10, y + 21), (x + 13, y + 21), (x + 13, y + 17), (x + 19, y + 10), (x + 19, y + 23)], fill=RED)
    d.text((PAD + 40, c.y + 2), "Sublime Media Limited", font=c.f("Bold", 26), fill=INK)
    url = "sublimemedialimited.com/blog"
    uf = c.f("Bold", 26)
    d.text((W - PAD - d.textlength(url, font=uf), c.y + 2), url, font=uf, fill=RED)
    c.y += 70
    c.d.rectangle([0, c.y - 14, W, c.y], fill=RED)


def _split(item):
    if ":" in item:
        a, b = item.split(":", 1)
        return a.strip(), b.strip()
    return item.strip(), ""


def _steps(c, items, numbered=True):
    d = c.d
    lf, df, nf = c.f("Bold", 36), c.f("Medium", 28), c.f("Bold", 30)
    textx = PAD + 96
    width = W - textx - PAD
    for i, it in enumerate(items, 1):
        label, detail = _split(it)
        top = c.y
        if numbered:
            d.ellipse([PAD, top, PAD + 64, top + 64], fill=RED)
            n = str(i)
            d.text((PAD + 32 - d.textlength(n, font=nf) / 2, top + 14), n, font=nf, fill=WHITE)
        else:
            d.ellipse([PAD + 4, top + 4, PAD + 60, top + 60], fill=RED)
            d.line([(PAD + 18, top + 33), (PAD + 28, top + 43), (PAD + 46, top + 22)], fill=WHITE, width=6)
        y = top + 8
        for ln in _wrap(d, label, lf, width):
            d.text((textx, y), ln, font=lf, fill=INK)
            y += _lh(lf, 1.15)
        if detail:
            y += 4
            for ln in _wrap(d, detail, df, width):
                d.text((textx, y), ln, font=df, fill=GREY)
                y += _lh(df, 1.3)
        c.y = max(y, top + 64) + 34
        if i < len(items) and numbered:
            d.line([(PAD + 32, top + 70), (PAD + 32, c.y - 6)], fill=LINE, width=4)


def _table(c, rows):
    d = c.d
    hf, cf = c.f("Bold", 30), c.f("Medium", 28)
    x0, x1, x2 = PAD, PAD + 330, W - PAD
    for r, (a, b) in enumerate(rows):
        f = hf if r == 0 else cf
        la = _wrap(d, a, c.f("Bold", 28) if r else hf, x1 - x0 - 40)
        lb = _wrap(d, b, f, x2 - x1 - 40)
        h = max(len(la), len(lb)) * _lh(f, 1.3) + 40
        fill = INK if r == 0 else (MIST if r % 2 == 0 else WHITE)
        d.rectangle([x0, c.y, x2, c.y + h], fill=fill)
        ty = c.y + 20
        for ln in la:
            d.text((x0 + 24, ty), ln, font=c.f("Bold", 28) if r else hf, fill=WHITE if r == 0 else RED)
            ty += _lh(f, 1.3)
        ty = c.y + 20
        for ln in lb:
            d.text((x1 + 20, ty), ln, font=f, fill=WHITE if r == 0 else INK)
            ty += _lh(f, 1.3)
        c.y += h
    c.y += 10


def _chat(c, msgs):
    d = c.d
    # phone-like chat panel
    top = c.y
    c.y += 30
    mf = c.f("Medium", 30)
    for m in msgs:
        lines = []
        for para in m.split("\n"):
            lines += _wrap(d, para, mf, W - 2 * PAD - 160) or [""]
        h = len(lines) * _lh(mf, 1.35) + 44
        x1 = W - PAD - 30
        x0 = x1 - max(d.textlength(l, font=mf) for l in lines) - 56
        x0 = min(x0, PAD + 120)
        d.rounded_rectangle([x0, c.y, x1, c.y + h], radius=28, fill="#dcf8c6")
        ty = c.y + 22
        for ln in lines:
            d.text((x0 + 28, ty), ln, font=mf, fill=INK)
            ty += _lh(mf, 1.35)
        c.y += h + 22
    c.y += 10
    panel = Image.new("RGB", (W - 2 * PAD, c.y - top), "#efe7de")
    region = c.im.crop((PAD, top, W - PAD, c.y))
    # re-composite bubbles onto chat background
    mask = Image.eval(region.convert("L"), lambda v: 0 if v == 255 else 255)
    panel.paste(region, (0, 0), mask)
    rounded = Image.new("L", panel.size, 0)
    ImageDraw.Draw(rounded).rounded_rectangle([0, 0, panel.size[0] - 1, panel.size[1] - 1], radius=30, fill=255)
    c.im.paste(panel, (PAD, top), rounded)


_FONT_CHECK = None


def _clean(text, src):
    """Drop characters Gilroy can't draw (emoji etc.) so no empty boxes appear."""
    global _FONT_CHECK
    if _FONT_CHECK is None:
        from fontTools.ttLib import TTFont
        _FONT_CHECK = set(TTFont(str(Path(src) / "Gilroy-Medium.ttf")).getBestCmap())
    text = text.replace("₦", "NGN ")  # Gilroy has no naira glyph
    out = "".join(ch for ch in text if ord(ch) in _FONT_CHECK or ch in " \n")
    return " ".join(out.split(" ")).strip()


def render(spec, src, out_dir, eyebrow):
    if spec["type"] == "illustration":
        return _save(Image.open(Path(src).parent / spec["src"]).convert("RGB"), spec, out_dir)
    spec = dict(spec)
    spec["title"] = _clean(spec["title"], src)
    spec["items"] = ([[_clean(a, src), _clean(b, src)] for a, b in spec["items"]] if spec["type"] == "table"
                     else [_clean(x, src) for x in spec["items"]])
    c = _Canvas(src)
    _header(c, eyebrow, spec["title"])
    t = spec["type"]
    if t == "steps":
        _steps(c, spec["items"], numbered=True)
    elif t == "checklist":
        _steps(c, spec["items"], numbered=False)
    elif t == "table":
        _table(c, spec["items"])
    elif t == "chat":
        _chat(c, spec["items"])
    else:
        raise ValueError(f"unknown image type {t}")
    _footer(c)
    return _save(c.im.crop((0, 0, W, c.y)), spec, out_dir)


def _save(im, spec, out_dir):
    out_dir = Path(out_dir)
    exif = Image.Exif()
    exif[0x013B] = "Zelia Kafene, Sublime Media Limited"      # Artist
    exif[0x8298] = "© Sublime Media Limited"                   # Copyright
    exif[0x010E] = spec.get("alt") or spec.get("title", "")              # ImageDescription
    jpg = out_dir / f"{spec['name']}.jpg"
    webp = out_dir / f"{spec['name']}.webp"
    im.save(jpg, "JPEG", quality=88, optimize=True, progressive=True, exif=exif)
    im.save(webp, "WEBP", quality=84, method=6, exif=exif)
    return im.size
