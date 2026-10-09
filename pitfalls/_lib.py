"""Gemeinsame Helfer für die Stolperstein-Module.

Das Wichtigste hier:

- `para()`: einfacher Fließtext mit Zeilenumbruch (sauber extrahierbar).
- `RawFont`: bettet eine TrueType-Schrift als Type0/Identity-H-Font selbst ein.
  Damit haben wir die volle Kontrolle über die ToUnicode-CMap, also darüber,
  welcher Unicode-Text einem Extraktor für eine Glyphe genannt wird (oder ob
  überhaupt einer). Text wird als roher PDF-Operator in den Content-Stream
  geschrieben, die Font-Ressource im `postprocess` nachträglich installiert.
- `Type3Font`: baut eine Type-3-Schrift, deren Glyphen PDF-Zeichenbefehle sind.
- `glyph_path_ops()`: liefert die Umrisse eines Textes als PDF-Pfad (Text als Kurven).
"""

from __future__ import annotations

import io
import logging
from pathlib import Path
from typing import Callable

import pikepdf
from fontTools import subset
from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen.canvas import Canvas

logging.getLogger("fontTools.subset").setLevel(logging.ERROR)

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "fonts"
DEJAVU = FONT_DIR / "DejaVuSans.ttf"
DEJAVU_BOLD = FONT_DIR / "DejaVuSans-Bold.ttf"
DEJAVU_SERIF = FONT_DIR / "DejaVuSerif.ttf"

# Seiten, die römisch nummeriert werden (Deckblatt). Danach beginnt "1".
FRONT_MATTER_PAGES = 1

LEFT = 72
RIGHT = 595 - 72
TEXT_WIDTH = RIGHT - LEFT
BODY_FONT = "Helvetica"
BODY_SIZE = 11
LEADING = 15


def roman(n: int) -> str:
    vals = [(10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i")]
    out = ""
    for v, s in vals:
        while n >= v:
            out += s
            n -= v
    return out


def page_label(physical_page: int) -> str:
    """Gedruckte Seitenzahl zu einer physischen Seite (1-basiert)."""
    if physical_page <= FRONT_MATTER_PAGES:
        return roman(physical_page)
    return str(physical_page - FRONT_MATTER_PAGES)


def para(
    c: Canvas,
    x: float,
    y: float,
    text: str,
    width: float = TEXT_WIDTH,
    font: str = BODY_FONT,
    size: float = BODY_SIZE,
    leading: float = LEADING,
) -> float:
    """Zeichnet einen umbrochenen Absatz und gibt die y-Position darunter zurück."""
    c.setFont(font, size)
    for line in simpleSplit(text, font, size, width):
        c.drawString(x, y, line)
        y -= leading
    return y - leading * 0.5


def label(c: Canvas, x: float, y: float, text: str) -> float:
    """Kleine graue Zwischenüberschrift, z. B. "Variante A"."""
    c.setFillGray(0.35)
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(x, y, text)
    c.setFillGray(0)
    return y - 14


# ---------------------------------------------------------------------------
# Glyphen-Umrisse
# ---------------------------------------------------------------------------


class _PdfPathPen(BasePen):
    """fontTools-Pen, der PDF-Pfadoperatoren erzeugt."""

    def __init__(self, glyph_set, dx: float = 0.0):
        super().__init__(glyph_set)
        self.ops: list[str] = []
        self.dx = dx

    def _pt(self, p) -> str:
        return f"{p[0] + self.dx:.1f} {p[1]:.1f}"

    def _moveTo(self, p):
        self.ops.append(f"{self._pt(p)} m")

    def _lineTo(self, p):
        self.ops.append(f"{self._pt(p)} l")

    def _curveToOne(self, p1, p2, p3):
        self.ops.append(f"{self._pt(p1)} {self._pt(p2)} {self._pt(p3)} c")

    def _closePath(self):
        self.ops.append("h")


_tt_cache: dict[Path, TTFont] = {}


def _tt(path: Path) -> TTFont:
    if path not in _tt_cache:
        _tt_cache[path] = TTFont(path)
    return _tt_cache[path]


def glyph_path_ops(text: str, font_path: Path = DEJAVU) -> tuple[str, float, int]:
    """Umrisse eines Textes in Font-Einheiten. Gibt (ops, advance, unitsPerEm) zurück."""
    tt = _tt(font_path)
    cmap = tt.getBestCmap()
    gs = tt.getGlyphSet()
    x = 0.0
    ops: list[str] = []
    for ch in text:
        name = cmap[ord(ch)]
        pen = _PdfPathPen(gs, dx=x)
        gs[name].draw(pen)
        ops.extend(pen.ops)
        x += tt["hmtx"][name][0]
    return " ".join(ops), x, tt["head"].unitsPerEm


def draw_text_as_paths(c: Canvas, x: float, y: float, size: float, text: str, font_path: Path = DEJAVU) -> None:
    """Text als gefüllte Pfade, ohne Textobjekt. Für Extraktoren unsichtbar."""
    ops, _, upm = glyph_path_ops(text, font_path)
    s = size / upm
    c._code.append(f"q {s:.6f} 0 0 {s:.6f} {x} {y} cm {ops} f Q")


# ---------------------------------------------------------------------------
# Selbst eingebettete Schriften
# ---------------------------------------------------------------------------

# Bekommt (Glyph-ID, "eigentlicher" Unicode-Text) und liefert, was in der
# ToUnicode-CMap stehen soll. None = kein Eintrag für diese Glyphe.
ToUnicodePolicy = Callable[[int, str], "str | None"]


def correct_tounicode(gid: int, text: str) -> str | None:
    return text


class RawFont:
    """Type0/Identity-H-Schrift mit frei wählbarer ToUnicode-CMap.

    Verwendung im `draw()`:
        font = RawFont("F_lig")
        font.show(c, x, y, 12, "Text")
    und im `postprocess()`:
        font.install(pdf, page)

    `tounicode=None` lässt die CMap komplett weg (dann sehen Extraktoren nur
    Glyph-IDs), sonst entscheidet die Policy pro Glyphe. `strip_cmap=True`
    entfernt zusätzlich die cmap-Tabelle und die Glyphnamen aus der
    eingebetteten Schrift, damit auch schlaue Extraktoren nichts rekonstruieren.
    """

    def __init__(
        self,
        name: str,
        font_path: Path = DEJAVU,
        tounicode: ToUnicodePolicy | None = correct_tounicode,
        strip_cmap: bool = False,
    ):
        self.name = name
        self.strip_cmap = strip_cmap
        self.font_path = font_path
        self.tt = _tt(font_path)
        self.cmap = self.tt.getBestCmap()
        self.upm = self.tt["head"].unitsPerEm
        self.tounicode = tounicode
        self.used: dict[int, str] = {}  # gid -> Unicode-Text, den die Glyphe darstellt

    def _gid(self, ch: str) -> int:
        gid = self.tt.getGlyphID(self.cmap[ord(ch)])
        self.used.setdefault(gid, ch)
        return gid

    def glyph(self, ch: str, meaning: str) -> int:
        """Registriert eine Glyphe (z. B. Ligatur 'ﬁ') mit ihrer Bedeutung ('fi')."""
        gid = self.tt.getGlyphID(self.cmap[ord(ch)])
        self.used[gid] = meaning
        return gid

    def encode(self, text: str) -> str:
        return "".join(f"{self._gid(ch):04X}" for ch in text)

    def width(self, text: str, size: float) -> float:
        hmtx = self.tt["hmtx"]
        return sum(hmtx[self.cmap[ord(ch)]][0] for ch in text) * size / self.upm

    def show(self, c: Canvas, x: float, y: float, size: float, text: str) -> None:
        c._code.append(f"BT /{self.name} {size} Tf {x} {y} Td <{self.encode(text)}> Tj ET")

    def show_tj(self, c: Canvas, x: float, y: float, size: float, parts: list[str | float]) -> None:
        """TJ-Array: Strings und Verschiebungen (in 1/1000 em, negativ = nach rechts)."""
        items = " ".join(f"<{self.encode(p)}>" if isinstance(p, str) else f"{p:g}" for p in parts)
        c._code.append(f"BT /{self.name} {size} Tf {x} {y} Td [{items}] TJ ET")

    def _subset_font(self) -> bytes:
        tt = TTFont(self.font_path)
        opts = subset.Options()
        opts.retain_gids = True
        opts.notdef_outline = True
        opts.name_IDs = ["*"]
        sub = subset.Subsetter(opts)
        order = tt.getGlyphOrder()
        sub.populate(glyphs=[order[g] for g in self.used])
        sub.subset(tt)
        if self.strip_cmap:
            del tt["cmap"]
            tt["post"].formatType = 3.0
        buf = io.BytesIO()
        tt.save(buf)
        return buf.getvalue()

    def _cmap_stream(self) -> bytes:
        entries = []
        for gid, text in sorted(self.used.items()):
            mapped = self.tounicode(gid, text)
            if mapped is None:
                continue
            utf16 = mapped.encode("utf-16-be").hex().upper()
            entries.append(f"<{gid:04X}> <{utf16}>")
        body = "\n".join(
            f"{len(chunk)} beginbfchar\n" + "\n".join(chunk) + "\nendbfchar"
            for chunk in (entries[i : i + 100] for i in range(0, len(entries), 100))
        )
        return (
            "/CIDInit /ProcSet findresource begin\n12 dict begin\nbegincmap\n"
            "/CIDSystemInfo << /Registry (Adobe) /Ordering (UCS) /Supplement 0 >> def\n"
            "/CMapName /Adobe-Identity-UCS def\n/CMapType 2 def\n"
            "1 begincodespacerange\n<0000> <FFFF>\nendcodespacerange\n"
            f"{body}\nendcmap\nCMapName currentdict /CMap defineresource pop\nend\nend\n"
        ).encode()

    def install(self, pdf: pikepdf.Pdf, page: pikepdf.Page) -> None:
        tt = self.tt
        scale = 1000 / self.upm
        hmtx = tt["hmtx"]
        order = tt.getGlyphOrder()
        widths: list = []
        for gid in sorted(self.used):
            widths += [gid, pikepdf.Array([round(hmtx[order[gid]][0] * scale)])]
        head, hhea = tt["head"], tt["hhea"]
        base = pikepdf.Name("/XYZABC+" + tt["name"].getDebugName(6))
        descriptor = pikepdf.Dictionary(
            Type=pikepdf.Name.FontDescriptor,
            FontName=base,
            Flags=32,
            FontBBox=[round(v * scale) for v in (head.xMin, head.yMin, head.xMax, head.yMax)],
            ItalicAngle=0,
            Ascent=round(hhea.ascent * scale),
            Descent=round(hhea.descent * scale),
            CapHeight=round(hhea.ascent * scale * 0.7),
            StemV=80,
            FontFile2=pdf.make_stream(self._subset_font()),
        )
        cidfont = pikepdf.Dictionary(
            Type=pikepdf.Name.Font,
            Subtype=pikepdf.Name.CIDFontType2,
            BaseFont=base,
            CIDSystemInfo=pikepdf.Dictionary(Registry="Adobe", Ordering="Identity", Supplement=0),
            FontDescriptor=pdf.make_indirect(descriptor),
            W=pikepdf.Array(widths),
            CIDToGIDMap=pikepdf.Name.Identity,
        )
        font = pikepdf.Dictionary(
            Type=pikepdf.Name.Font,
            Subtype=pikepdf.Name.Type0,
            BaseFont=base,
            Encoding=pikepdf.Name("/Identity-H"),
            DescendantFonts=[pdf.make_indirect(cidfont)],
        )
        if self.tounicode is not None:
            font.ToUnicode = pdf.make_stream(self._cmap_stream())
        add_font_resource(page, self.name, pdf.make_indirect(font))


class Type3Font:
    """Type-3-Schrift aus DejaVu-Umrissen, Glyphnamen ohne Bedeutung, keine ToUnicode.

    So sehen z. B. Bitmap-Fonts aus alten dvips/LaTeX-Workflows aus.
    """

    def __init__(self, name: str, font_path: Path = DEJAVU):
        self.name = name
        self.font_path = font_path
        self.codes: dict[str, int] = {}

    def encode(self, text: str) -> str:
        for ch in text:
            if ch not in self.codes:
                self.codes[ch] = len(self.codes) + 1
        return "".join(f"{self.codes[ch]:02X}" for ch in text)

    def show(self, c: Canvas, x: float, y: float, size: float, text: str) -> None:
        c._code.append(f"BT /{self.name} {size} Tf {x} {y} Td <{self.encode(text)}> Tj ET")

    def install(self, pdf: pikepdf.Pdf, page: pikepdf.Page) -> None:
        tt = _tt(self.font_path)
        upm = tt["head"].unitsPerEm
        procs = pikepdf.Dictionary()
        widths = []
        differences: list = [1]
        for ch, code in sorted(self.codes.items(), key=lambda kv: kv[1]):
            ops, adv, _ = glyph_path_ops(ch, self.font_path)
            gname = f"/g{code}"
            procs[gname] = pdf.make_stream(f"{adv:.0f} 0 d0 {ops} f".encode())
            differences.append(pikepdf.Name(gname))
            widths.append(round(adv))
        head = tt["head"]
        font = pikepdf.Dictionary(
            Type=pikepdf.Name.Font,
            Subtype=pikepdf.Name.Type3,
            FontBBox=[head.xMin, head.yMin, head.xMax, head.yMax],
            FontMatrix=[1 / upm, 0, 0, 1 / upm, 0, 0],
            CharProcs=procs,
            Encoding=pikepdf.Dictionary(Type=pikepdf.Name.Encoding, Differences=differences),
            FirstChar=1,
            LastChar=len(self.codes),
            Widths=widths,
            Resources=pikepdf.Dictionary(),
        )
        add_font_resource(page, self.name, pdf.make_indirect(font))


def add_font_resource(page: pikepdf.Page, name: str, font: pikepdf.Object) -> None:
    res = page.obj.get("/Resources")
    if res is None:
        page.obj.Resources = res = pikepdf.Dictionary()
    if "/Font" not in res:
        res.Font = pikepdf.Dictionary()
    res.Font[pikepdf.Name("/" + name)] = font


_registered: set[str] = set()


def dejavu(bold: bool = False, serif: bool = False) -> str:
    """Registriert DejaVu bei reportlab (mit korrekter ToUnicode) und gibt den Namen zurück."""
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont as RLTTFont

    path = DEJAVU_SERIF if serif else DEJAVU_BOLD if bold else DEJAVU
    name = path.stem
    if name not in _registered:
        pdfmetrics.registerFont(RLTTFont(name, str(path)))
        _registered.add(name)
    return name


def text_image(
    lines: list[str],
    width_pt: float,
    height_pt: float,
    *,
    size_pt: float = 12,
    leading_pt: float = 20,
    margin_pt: float = 12,
    scale: float = 2.5,
    rotate: float = 0.0,
    noise: int = 0,
    font_path: Path = DEJAVU_SERIF,
    seed: int = 42,
):
    """Rendert Textzeilen in ein Graustufenbild (für Scans und Screenshots).

    Zeile i hat ihre Grundlinie bei margin_pt + size_pt + i * leading_pt von oben.
    """
    import random

    from PIL import Image, ImageDraw, ImageFilter, ImageFont

    w, h = int(width_pt * scale), int(height_pt * scale)
    img = Image.new("L", (w, h), 255)
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(str(font_path), int(size_pt * scale))
    for i, line in enumerate(lines):
        baseline = (margin_pt + size_pt + i * leading_pt) * scale
        d.text((margin_pt * scale, baseline), line, font=font, fill=20, anchor="ls")
    if rotate:
        img = img.rotate(rotate, resample=Image.BICUBIC, fillcolor=255)
    if noise:
        rnd = random.Random(seed)
        px = img.load()
        for _ in range(w * h // 40):
            x, y = rnd.randrange(w), rnd.randrange(h)
            px[x, y] = max(0, min(255, px[x, y] + rnd.randint(-noise, noise)))
        img = img.filter(ImageFilter.GaussianBlur(0.6))
    return img


def draw_pil_image(c: Canvas, img, x: float, y: float, width: float, height: float, quality: int = 35) -> None:
    from reportlab.lib.utils import ImageReader

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality)
    buf.seek(0)
    c.drawImage(ImageReader(buf), x, y, width, height)


SOURCES = ROOT / "quellen" / "out"


class ExternalPage:
    """Seite aus einem fremd erzeugten PDF (LaTeX, Browser, …) übernehmen.

    mode="replace" (Standard): Unsere Seite wird durch die Originalseite ersetzt,
        Content-Stream, Schriften und Seitengröße bleiben exakt wie vom Erzeuger.
        Eigener Titel, Kopf- und Fußzeile entfallen dann auf dieser Seite.
    mode="overlay": Die fremde Seite wird als Form-XObject in ein Rechteck gesetzt.
        Achtung: Das ist selbst ein Stolperstein (siehe text_in_xobject), z. B.
        verliert pdfminer darin Leerzeichen.

    Verwendung: in draw() bei overlay `place(x, y, w, h)` aufrufen,
    in postprocess() `install(pdf, page)`.
    """

    def __init__(self, filename: str, page: int = 0, mode: str = "replace"):
        self.path = SOURCES / filename
        self.page = page
        self.mode = mode
        self.rect: tuple[float, float, float, float] | None = None
        self._src: pikepdf.Pdf | None = None

    @property
    def exists(self) -> bool:
        return self.path.exists()

    def place(self, x: float, y: float, width: float, height: float) -> None:
        self.rect = (x, y, x + width, y + height)

    def install(self, pdf: pikepdf.Pdf, page: pikepdf.Page) -> None:
        self._src = pikepdf.open(self.path)  # muss bis zum Speichern offen bleiben
        src_page = self._src.pages[self.page]
        if self.mode == "replace":
            idx = next(i for i, p in enumerate(pdf.pages) if p.obj.objgen == page.obj.objgen)
            pdf.pages[idx] = src_page
            return
        assert self.rect is not None, "place() wurde nicht aufgerufen"
        form = pdf.copy_foreign(src_page.as_form_xobject())
        page.add_overlay(form, pikepdf.Rectangle(*self.rect), expand=True)
