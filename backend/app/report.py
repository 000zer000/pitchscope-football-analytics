from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

import reportlab
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.db import ROOT

_fonts = Path(reportlab.__file__).parent / "fonts"
pdfmetrics.registerFont(TTFont("PitchSans", str(_fonts / "Vera.ttf")))
pdfmetrics.registerFont(TTFont("PitchSansBold", str(_fonts / "VeraBd.ttf")))

NAVY = colors.HexColor("#142c2a")
GREEN = colors.HexColor("#24715c")
BLUE = colors.HexColor("#537fba")


def fmt(value):
    if value is None:
        return "N/A"
    return f"{value:.2f}" if isinstance(value, float) else str(value)


def render_report(data, coverage):
    output = BytesIO()
    doc = SimpleDocTemplate(
        output,
        pagesize=(210 * mm, 297 * mm),
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="PitchScope - statistical comparison",
        author="PitchScope",
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="SmallPS", fontName="PitchSans", fontSize=8, leading=12, textColor=NAVY))
    styles["Title"].fontName = "PitchSansBold"
    styles["Heading2"].fontName = "PitchSansBold"
    styles["Title"].textColor = NAVY
    styles["Title"].alignment = 0

    def p(text):
        return Paragraph(escape(text), styles["SmallPS"])

    a, b = data["players"]
    pop = data["population"]
    story = [
        Paragraph("PitchScope", styles["Title"]),
        p("PLAYER COMPARISON REPORT | FIFA World Cup 2022"),
        Spacer(1, 5 * mm),
        Paragraph(escape(a["name"]) + "<br/>vs " + escape(b["name"]), styles["Heading2"]),
        p(
            f"Coverage: {coverage['imported_matches']}/{coverage['expected_matches']} matches. "
            f"Reference: {pop['role']}, minimum {pop['min_minutes']} min, {pop['count']} players."
        ),
        Spacer(1, 5 * mm),
    ]
    rows = [[p("Metric / unit"), p(a["name"]), p(b["name"])]]
    for m in data["metrics"]:
        rows.append([p(m["label"] + " (" + m["unit"] + ")"), fmt(a[m["key"]]), fmt(b[m["key"]])])
    table = Table(rows, colWidths=[82 * mm, 46 * mm, 46 * mm], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e7f0eb")),
                ("FONTNAME", (0, 0), (-1, -1), "PitchSans"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("TEXTCOLOR", (0, 0), (-1, -1), NAVY),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("LINEBELOW", (0, 0), (-1, -1), 0.3, colors.HexColor("#dce4de")),
            ]
        )
    )
    story += [table, Spacer(1, 5 * mm), p("SHOT VOLUME PER 90 RELIABLE MINUTES")]
    drawing = Drawing(490, 56)
    maximum = max(a["shots_p90"] or 0, b["shots_p90"] or 0, 1)
    for i, player in enumerate([a, b]):
        value = player["shots_p90"]
        y = 32 - i * 24
        drawing.add(
            Rect(0, y, 400 * (value or 0) / maximum, 14, fillColor=[GREEN, BLUE][i], strokeColor=None)
        )
        drawing.add(String(410, y + 3, fmt(value), fontName="PitchSans", fontSize=10, fillColor=NAVY))
    story += [
        drawing,
        p(f"Green: {a['name']}. Blue: {b['name']}. Volume does not measure talent."),
        Spacer(1, 3 * mm),
    ]
    for warning in data["warnings"]:
        story.append(p("Note: " + warning))
    story += [
        p(
            "Method: elapsed time in periods 1-4, including stoppage time and excluding breaks. Temporary absences deducted. "
            "Initial lineup role retained for each appearance. Per-90 rates use reliable appearances only. "
            "In-match penalties included; shootouts excluded; own goals not credited to a shooter. "
            "xG supplied by StatsBomb; no model trained. No tactical or potential claims."
        ),
        Spacer(1, 3 * mm),
        p("Source: StatsBomb Open Data / hudl/open-data. Commit : " + data["source_commit"]),
        p(
            "Transformations : "
            + ", ".join(sorted({r["transform_version"] for r in coverage["imports"]}))
            + ". File hashes and import dates: see the application Methodology page."
        ),
        p("https://github.com/hudl/open-data - data subject to the StatsBomb Public Data User Agreement."),
        Spacer(1, 3 * mm),
    ]
    logo = ROOT / "assets/statsbomb.png"
    if logo.exists():
        from PIL import Image as PILImage

        w, h = PILImage.open(logo).size
        story.append(Image(str(logo), width=40 * mm, height=40 * mm * h / w, hAlign="LEFT"))

    def footer(canvas, doc):
        canvas.setFont("PitchSans", 8)
        canvas.setFillColor(NAVY)
        canvas.drawString(18 * mm, 10 * mm, "PitchScope | Descriptive analysis, historical sample")
        canvas.drawRightString(192 * mm, 10 * mm, str(doc.page))

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return output.getvalue()
