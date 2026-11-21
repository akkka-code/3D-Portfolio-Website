#!/usr/bin/env python3
"""
Builds the complete, publication-grade Microsoft Word Project Report:
  docs/Web3D_Portfolio_Project_Report.docx

Covers all 6 engineering modules, WebGPU/TSL shaders, Blender 5.1 procedural avatar,
After Effects & FFmpeg editorial showreel, Hybrid RAG AI assistant (AHMAD.AI),
secured Resend contact API, performance/bundle engineering, automated verification,
and Vercel CI/CD production deployment.
"""

import os
import re
from docx import Document
from docx.shared import Inches, Pt, Mm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(ROOT, "docs", "report_assets")
OUT_DOCX = os.path.join(ROOT, "docs", "Web3D_Portfolio_Project_Report.docx")

# Design Tokens
HEX_NAVY = "0B132B"
HEX_NAVY_MID = "162447"
HEX_TEAL = "0284C7"
HEX_CYAN = "00E5FF"
HEX_LIME = "DDFB24"
HEX_INK = "1E293B"
HEX_MUTED = "64748B"
HEX_ZEBRA = "F8FAFC"
HEX_CALLOUT = "EFF6FF"
HEX_CODE_BG = "F1F5F9"
HEX_BORDER = "CBD5E1"
HEX_WHITE = "FFFFFF"

RGB_NAVY = RGBColor(0x0B, 0x13, 0x2B)
RGB_TEAL = RGBColor(0x02, 0x84, 0xC7)
RGB_CYAN = RGBColor(0x00, 0xE5, 0xFF)
RGB_LIME = RGBColor(0xDD, 0xFB, 0x24)
RGB_INK = RGBColor(0x1E, 0x29, 0x3B)
RGB_MUTED = RGBColor(0x64, 0x74, 0x8B)
RGB_WHITE = RGBColor(0xFF, 0xFF, 0xFF)
RGB_CODE = RGBColor(0x0F, 0x4C, 0x81)

CONTENT_WIDTH_IN = 6.65


# ---------------------------------------------------------------------------
# Low-level OOXML helpers
# ---------------------------------------------------------------------------
def set_cell_shading(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)


def set_cell_margins(cell, top=68, bottom=68, left=115, right=115):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement("w:tcMar")
    for m, val in [("top", top), ("bottom", bottom), ("left", left), ("right", right)]:
        node = OxmlElement(f"w:{m}")
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")
        tcMar.append(node)
    tcPr.append(tcMar)


def set_cell_borders(cell, top=None, bottom=None, left=None, right=None):
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement("w:tcBorders")
    for side, spec in [("top", top), ("bottom", bottom), ("left", left), ("right", right)]:
        if spec is None:
            continue
        el = OxmlElement(f"w:{side}")
        val, sz, color = spec
        el.set(qn("w:val"), val)
        el.set(qn("w:sz"), str(sz))
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), color)
        tcBorders.append(el)
    tcPr.append(tcBorders)


def set_table_borders(table, border_color=HEX_BORDER):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'  <w:top w:val="single" w:sz="6" w:space="0" w:color="{HEX_NAVY}"/>'
        f'  <w:bottom w:val="single" w:sz="6" w:space="0" w:color="{HEX_NAVY}"/>'
        f'  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="{border_color}"/>'
        f'  <w:left w:val="none"/>'
        f'  <w:right w:val="none"/>'
        f'  <w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)


def set_row_cant_split(row):
    trPr = row._tr.get_or_add_trPr()
    trPr.append(OxmlElement("w:cantSplit"))


def set_row_header(row):
    trPr = row._tr.get_or_add_trPr()
    trPr.append(OxmlElement("w:tblHeader"))


def add_paragraph_bottom_border(paragraph, color_hex=HEX_TEAL, size="12"):
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = parse_xml(
        f'<w:pBdr {nsdecls("w")}>'
        f'  <w:bottom w:val="single" w:sz="{size}" w:space="4" w:color="{color_hex}"/>'
        f'</w:pBdr>'
    )
    pPr.append(pBdr)


def add_run_shading(run, fill_hex=HEX_CODE_BG):
    rPr = run._r.get_or_add_rPr()
    rPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" w:fill="{fill_hex}"/>'))


def add_field(paragraph, field_text, font_size=8.5, color=RGB_MUTED):
    run = paragraph.add_run()
    run.font.name = "Segoe UI"
    run.font.size = Pt(font_size)
    run.font.color.rgb = color
    fldChar1 = OxmlElement("w:fldChar")
    fldChar1.set(qn("w:fldCharType"), "begin")
    instrText = OxmlElement("w:instrText")
    instrText.set(qn("xml:space"), "preserve")
    instrText.text = f" {field_text} "
    fldChar2 = OxmlElement("w:fldChar")
    fldChar2.set(qn("w:fldCharType"), "separate")
    fldChar3 = OxmlElement("w:fldChar")
    fldChar3.set(qn("w:fldCharType"), "end")
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(fldChar3)


def enable_update_fields_on_open(doc):
    settings = doc.settings.element
    update = OxmlElement("w:updateFields")
    update.set(qn("w:val"), "true")
    settings.append(update)


# ---------------------------------------------------------------------------
# High-level Typography & Layout Helpers (Nested bold + code safe)
# ---------------------------------------------------------------------------
BOLD_RE = re.compile(r"(\*\*[^*]+\*\*)")
CODE_ITAL_RE = re.compile(r"(`[^`]+`|\*[^*]+\*)")


def _emit_code_and_italic(p, text, font_size, color, bold):
    for part in CODE_ITAL_RE.split(text):
        if not part:
            continue
        if part.startswith("`") and part.endswith("`"):
            r = p.add_run(part[1:-1])
            r.font.name = "Consolas"
            r.font.size = Pt(max(font_size - 1.0, 8.0))
            r.font.bold = bold
            r.font.color.rgb = RGB_CODE
            add_run_shading(r, HEX_CODE_BG)
        elif part.startswith("*") and part.endswith("*"):
            r = p.add_run(part[1:-1])
            r.font.name = "Segoe UI"
            r.font.size = Pt(font_size)
            r.font.italic = True
            r.font.bold = bold
            r.font.color.rgb = color
        else:
            r = p.add_run(part)
            r.font.name = "Segoe UI"
            r.font.size = Pt(font_size)
            r.font.bold = bold
            r.font.color.rgb = RGB_NAVY if (bold and color == RGB_INK) else color


def add_rich_runs(p, text, font_size=9.8, color=RGB_INK, base_bold=False):
    for chunk in BOLD_RE.split(text):
        if not chunk:
            continue
        if chunk.startswith("**") and chunk.endswith("**"):
            _emit_code_and_italic(p, chunk[2:-2], font_size, color, bold=True)
        else:
            _emit_code_and_italic(p, chunk, font_size, color, bold=base_bold)


def add_body(doc, text, space_after=5.0, align=WD_ALIGN_PARAGRAPH.LEFT):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.16
    add_rich_runs(p, text, font_size=9.8, color=RGB_INK)
    return p


def add_bullet(doc, text, space_after=3.2):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.14
    add_rich_runs(p, text, font_size=9.6, color=RGB_INK)
    return p


def add_h1(doc, text, page_break=False):
    if page_break:
        doc.add_page_break()
    p = doc.add_paragraph(style="Heading 1")
    p.paragraph_format.space_before = Pt(12 if not page_break else 2)
    p.paragraph_format.space_after = Pt(5.5)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.font.name = "Segoe UI"
    r.font.size = Pt(14.0)
    r.font.bold = True
    r.font.color.rgb = RGB_NAVY
    add_paragraph_bottom_border(p, HEX_TEAL, size="12")
    return p


def add_h2(doc, text):
    p = doc.add_paragraph(style="Heading 2")
    p.paragraph_format.space_before = Pt(9)
    p.paragraph_format.space_after = Pt(3.5)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.font.name = "Segoe UI"
    r.font.size = Pt(11.2)
    r.font.bold = True
    r.font.color.rgb = RGB_TEAL
    return p


def add_callout(doc, title, body_text, accent_hex=HEX_TEAL, fill_hex=HEX_CALLOUT):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    cell = tbl.cell(0, 0)
    cell.width = Inches(CONTENT_WIDTH_IN)
    set_cell_shading(cell, fill_hex)
    set_cell_margins(cell, top=95, bottom=95, left=150, right=135)
    set_cell_borders(
        cell,
        top=("single", 4, HEX_BORDER),
        bottom=("single", 4, HEX_BORDER),
        right=("single", 4, HEX_BORDER),
        left=("single", 24, accent_hex),
    )
    set_row_cant_split(tbl.rows[0])

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2.5)
    rt = p.add_run(title)
    rt.font.name = "Segoe UI"
    rt.font.size = Pt(9.6)
    rt.font.bold = True
    rt.font.color.rgb = RGB_NAVY

    p2 = cell.add_paragraph()
    p2.paragraph_format.space_before = Pt(0)
    p2.paragraph_format.space_after = Pt(0)
    p2.paragraph_format.line_spacing = 1.14
    add_rich_runs(p2, body_text, font_size=9.2, color=RGB_INK)

    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(3.5)


def add_code_block(doc, title, code_text):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    cell = tbl.cell(0, 0)
    cell.width = Inches(CONTENT_WIDTH_IN)
    set_cell_shading(cell, HEX_ZEBRA)
    set_cell_margins(cell, top=80, bottom=80, left=135, right=120)
    set_cell_borders(
        cell,
        top=("single", 4, HEX_BORDER),
        bottom=("single", 4, HEX_BORDER),
        right=("single", 4, HEX_BORDER),
        left=("single", 18, HEX_NAVY),
    )
    set_row_cant_split(tbl.rows[0])

    p0 = cell.paragraphs[0]
    p0.paragraph_format.space_before = Pt(0)
    p0.paragraph_format.space_after = Pt(3.5)
    rt = p0.add_run(title)
    rt.font.name = "Segoe UI"
    rt.font.size = Pt(8.5)
    rt.font.bold = True
    rt.font.color.rgb = RGB_TEAL

    p1 = cell.add_paragraph()
    p1.paragraph_format.space_before = Pt(0)
    p1.paragraph_format.space_after = Pt(0)
    p1.paragraph_format.line_spacing = 1.12
    rc = p1.add_run(code_text.strip())
    rc.font.name = "Consolas"
    rc.font.size = Pt(7.9)
    rc.font.color.rgb = RGB_INK

    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(3.5)


def add_styled_table(doc, caption, headers, rows, col_widths, pad_v=62, font_sz=8.5):
    if caption:
        pc = doc.add_paragraph()
        pc.paragraph_format.space_before = Pt(5)
        pc.paragraph_format.space_after = Pt(2.5)
        pc.paragraph_format.keep_with_next = True
        r = pc.add_run(caption)
        r.font.name = "Segoe UI"
        r.font.size = Pt(9.0)
        r.font.bold = True
        r.font.color.rgb = RGB_NAVY

    tbl = doc.add_table(rows=1 + len(rows), cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    set_table_borders(tbl)

    # Header row
    hdr_row = tbl.rows[0]
    set_row_header(hdr_row)
    set_row_cant_split(hdr_row)
    for j, htext in enumerate(headers):
        cell = hdr_row.cells[j]
        cell.width = Inches(col_widths[j])
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        set_cell_shading(cell, HEX_NAVY)
        set_cell_margins(cell, top=pad_v + 16, bottom=pad_v + 16, left=105, right=105)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(htext)
        r.font.name = "Segoe UI"
        r.font.size = Pt(font_sz + 0.2)
        r.font.bold = True
        r.font.color.rgb = RGB_WHITE

    # Body rows
    for i, rdata in enumerate(rows):
        row = tbl.rows[i + 1]
        set_row_cant_split(row)
        bg = HEX_ZEBRA if i % 2 == 1 else HEX_WHITE
        for j, val in enumerate(rdata):
            cell = row.cells[j]
            cell.width = Inches(col_widths[j])
            cell.vertical_alignment = WD_ALIGN_VERTICAL.TOP
            set_cell_shading(cell, bg)
            set_cell_margins(cell, top=pad_v, bottom=pad_v, left=105, right=105)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.12
            add_rich_runs(p, str(val), font_size=font_sz, color=RGB_INK, base_bold=(j == 0))

    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(3.5)
    return tbl


def add_figure(doc, img_path, caption, width_in=6.40, space_after=6.5):
    if not os.path.exists(img_path):
        print(f"WARNING: Missing figure {img_path}")
        return
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(4)
    p_img.paragraph_format.space_after = Pt(2.5)
    p_img.paragraph_format.keep_with_next = True
    run = p_img.add_run()
    run.add_picture(img_path, width=Inches(width_in))

    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(0)
    p_cap.paragraph_format.space_after = Pt(space_after)
    r = p_cap.add_run(caption)
    r.font.name = "Segoe UI"
    r.font.size = Pt(8.6)
    r.font.italic = True
    r.font.color.rgb = RGB_MUTED


def add_kpi_strip(doc, kpis):
    tbl = doc.add_table(rows=1, cols=len(kpis))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    set_row_cant_split(tbl.rows[0])
    w = CONTENT_WIDTH_IN / len(kpis)
    for idx, (val, lbl, sub) in enumerate(kpis):
        cell = tbl.cell(0, idx)
        cell.width = Inches(w)
        set_cell_shading(cell, HEX_ZEBRA)
        set_cell_margins(cell, top=95, bottom=95, left=85, right=85)
        set_cell_borders(
            cell,
            top=("single", 18, HEX_TEAL if idx % 2 == 0 else HEX_NAVY),
            bottom=("single", 4, HEX_BORDER),
            left=("single", 4, HEX_BORDER),
            right=("single", 4, HEX_BORDER),
        )
        p1 = cell.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p1.paragraph_format.space_after = Pt(1.5)
        r1 = p1.add_run(val)
        r1.font.name = "Segoe UI"
        r1.font.size = Pt(13.0)
        r1.font.bold = True
        r1.font.color.rgb = RGB_NAVY

        p2 = cell.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p2.paragraph_format.space_after = Pt(1.5)
        r2 = p2.add_run(lbl)
        r2.font.name = "Segoe UI"
        r2.font.size = Pt(7.8)
        r2.font.bold = True
        r2.font.color.rgb = RGB_TEAL

        p3 = cell.add_paragraph()
        p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p3.paragraph_format.space_after = Pt(0)
        r3 = p3.add_run(sub)
        r3.font.name = "Segoe UI"
        r3.font.size = Pt(7.4)
        r3.font.color.rgb = RGB_MUTED

    sp = doc.add_paragraph()
    sp.paragraph_format.space_after = Pt(4)


def configure_toc_styles(doc):
    """Make Word's native TOC 1 / TOC 2 styles crisp and compact so TOC fits on 1 page."""
    for style_name, sz, bold, space_after in [
        ("TOC 1", 9.0, True, 2.5),
        ("TOC 2", 8.5, False, 1.5),
    ]:
        try:
            st = doc.styles[style_name]
            st.font.name = "Segoe UI"
            st.font.size = Pt(sz)
            st.font.bold = bold
            st.font.color.rgb = RGB_NAVY if bold else RGB_INK
            st.paragraph_format.space_before = Pt(0)
            st.paragraph_format.space_after = Pt(space_after)
            st.paragraph_format.line_spacing = 1.08
        except KeyError:
            pass


# ---------------------------------------------------------------------------
# Document Assembly
# ---------------------------------------------------------------------------
def build_report():
    doc = Document()
    enable_update_fields_on_open(doc)
    configure_toc_styles(doc)

    # Configure A4 page & balanced margins
    section = doc.sections[0]
    section.page_width = Mm(210)
    section.page_height = Mm(297)
    section.left_margin = Inches(0.80)
    section.right_margin = Inches(0.80)
    section.top_margin = Inches(0.76)
    section.bottom_margin = Inches(0.76)
    section.different_first_page_header_footer = True

    normal = doc.styles["Normal"]
    normal.font.name = "Segoe UI"
    normal.font.size = Pt(9.8)
    normal.font.color.rgb = RGB_INK

    # Running Header (Pages 2+) with explicit flush-right tab stop at 6.65 in
    hdr = section.header
    hp = hdr.paragraphs[0]
    hp.paragraph_format.space_after = Pt(4)
    hp.paragraph_format.tab_stops.add_tab_stop(Inches(CONTENT_WIDTH_IN), WD_TAB_ALIGNMENT.RIGHT)
    add_paragraph_bottom_border(hp, HEX_BORDER, size="6")
    hr1 = hp.add_run("INTERACTIVE 3D WEBGPU PORTFOLIO  |  TECHNICAL PROJECT REPORT")
    hr1.font.name = "Segoe UI"
    hr1.font.size = Pt(8.0)
    hr1.font.bold = True
    hr1.font.color.rgb = RGB_MUTED
    hr2 = hp.add_run("\tSYED MUHAMMAD AHMAD (AKKA)")
    hr2.font.name = "Segoe UI"
    hr2.font.size = Pt(8.0)
    hr2.font.bold = True
    hr2.font.color.rgb = RGB_TEAL

    # Running Footer (Pages 2+) with explicit flush-right tab stop + dynamic PAGE of NUMPAGES
    ftr = section.footer
    fp = ftr.paragraphs[0]
    fp.paragraph_format.space_before = Pt(4)
    fp.paragraph_format.tab_stops.add_tab_stop(Inches(CONTENT_WIDTH_IN), WD_TAB_ALIGNMENT.RIGHT)
    pPr = fp._p.get_or_add_pPr()
    pPr.append(parse_xml(
        f'<w:pBdr {nsdecls("w")}><w:top w:val="single" w:sz="6" w:space="4" w:color="{HEX_BORDER}"/></w:pBdr>'
    ))
    fr1 = fp.add_run("NED University of Engineering & Technology — BS CS & IT (Gaming & Animation)\tPage ")
    fr1.font.name = "Segoe UI"
    fr1.font.size = Pt(8.0)
    fr1.font.color.rgb = RGB_MUTED
    add_field(fp, "PAGE", font_size=8.0, color=RGB_NAVY)
    fr2 = fp.add_run(" of ")
    fr2.font.name = "Segoe UI"
    fr2.font.size = Pt(8.0)
    fr2.font.color.rgb = RGB_MUTED
    add_field(fp, "NUMPAGES", font_size=8.0, color=RGB_NAVY)

    # =========================================================================
    # PAGE 1: COVER PAGE (Engineered to fit 100% cleanly on Page 1)
    # =========================================================================
    cover_tbl = doc.add_table(rows=1, cols=1)
    cover_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cover_tbl.autofit = False
    ccell = cover_tbl.cell(0, 0)
    ccell.width = Inches(CONTENT_WIDTH_IN)
    set_cell_shading(ccell, HEX_NAVY)
    set_cell_margins(ccell, top=185, bottom=170, left=220, right=220)
    set_cell_borders(
        ccell,
        top=("single", 36, HEX_CYAN),
        bottom=("single", 24, HEX_LIME),
        left=("single", 6, HEX_NAVY_MID),
        right=("single", 6, HEX_NAVY_MID),
    )

    cp0 = ccell.paragraphs[0]
    cp0.paragraph_format.space_after = Pt(6)
    cr0 = cp0.add_run("FINAL PROJECT REPORT  //  WEB3D INTERACTIVE PORTFOLIO")
    cr0.font.name = "Consolas"
    cr0.font.size = Pt(9.2)
    cr0.font.bold = True
    cr0.font.color.rgb = RGB_LIME

    cp1 = ccell.add_paragraph()
    cp1.paragraph_format.space_after = Pt(8)
    cp1.paragraph_format.line_spacing = 1.12
    cr1 = cp1.add_run("Design, Engineering, and Deployment of an\nInteractive 3D WebGPU Portfolio")
    cr1.font.name = "Segoe UI"
    cr1.font.size = Pt(20.5)
    cr1.font.bold = True
    cr1.font.color.rgb = RGB_WHITE

    cp2 = ccell.add_paragraph()
    cp2.paragraph_format.space_after = Pt(0)
    cp2.paragraph_format.line_spacing = 1.20
    cr2 = cp2.add_run(
        "Real-Time Three.js TSL Cyberpunk Environment, Custom Rigged Blender 5.1 Avatar, "
        "Editorial Motion Showreel, Hybrid RAG AI Assistant (AHMAD.AI), and Serverless Communication Architecture"
    )
    cr2.font.name = "Segoe UI"
    cr2.font.size = Pt(10.0)
    cr2.font.color.rgb = RGBColor(0xCB, 0xD5, 0xE1)

    sp = doc.add_paragraph()
    sp.paragraph_format.space_after = Pt(3)

    add_figure(
        doc,
        os.path.join(ROOT, "public", "video", "promo-poster.jpg"),
        "Cover Figure: 2026 Game & XR Developer Showreel editorial cover framing four live gameplay viewports inside the samsy.ninja-inspired layout.",
        width_in=5.65,
        space_after=5.0,
    )

    meta_rows = [
        ["Author / Developer", "Syed Muhammad Ahmad (Handle: AKKA)"],
        ["Academic Program", "BS Computer Science & Information Technology — Specialisation in Gaming & Animation"],
        ["Institution", "NED University of Engineering & Technology, Karachi, Pakistan (Batch 2023–2027)"],
        ["Industry Role", "Game Development Intern, Aerox ERP (Oct 2026 – Present)"],
        ["Live Production URL", "https://syed-muhammad-ahmad-portfolio.vercel.app"],
        ["Source Repository", "https://github.com/akkka-code/3D-Portfolio-Website"],
        ["Direct Contact", "ahmedakka765@gmail.com  |  linkedin.com/in/syed-muhammad-ahmad-55b240284"],
        ["Core Architecture", "Three.js r185 (WebGPU + TSL) · Vite 6 · Blender 5.1 · After Effects · Gemini RAG · Vercel"],
        ["Document Release", "Final Technical Report v2.0 — November 2026"],
    ]
    add_styled_table(
        doc,
        None,
        ["Project Metadata Field", "Details"],
        meta_rows,
        [1.90, 4.75],
        pad_v=46,
        font_sz=8.4,
    )

    # =========================================================================
    # PAGE 2: EXECUTIVE SUMMARY & TABLE OF CONTENTS
    # =========================================================================
    add_h1(doc, "Executive Summary", page_break=True)
    add_body(
        doc,
        "This technical report presents the end-to-end architecture, shader engineering, 3D character production, "
        "motion design, artificial intelligence integration, security hardening, and cloud deployment of the "
        "**Interactive 3D WebGPU Portfolio** created for **Syed Muhammad Ahmad (AKKA)**. Rather than presenting "
        "game development, XR, and graphics engineering work through static thumbnails, the platform unifies a "
        "**real-time WebGPU cyberpunk alley** authored exclusively in **Three.js Shading Language (TSL)** with an "
        "ultra-clean, high-contrast minimalist editorial interface modeled on modern creative-technologist portfolios "
        "(`samsy.ninja`)."
    )
    add_body(
        doc,
        "The platform is engineered around a strict **Single Source of Truth** (`content/profile.json`) that feeds "
        "every downstream surface simultaneously: the curated 9-project interactive index, the 8 in-world holographic "
        "video kiosks lining the rainy 3D alley, the pre-built vector knowledge index powering the **AHMAD.AI** "
        "Retrieval-Augmented Generation (RAG) assistant, and the 9-act 1080p editorial showreel. All six system "
        "modules are verified via automated retrieval, validation, and build test suites and deployed continuously "
        "to **Vercel** from GitHub."
    )

    add_kpi_strip(doc, [
        ("9 Projects", "CURATED PORTFOLIO", "Unity · UE5 · XR · C++ · WebGPU"),
        ("5,000 Drops", "GPU COLLISION RAIN", "512² Height RT · Zero CPU Raycast"),
        ("20-Bone Rig", "BLENDER 5.1 AVATAR", "6 NLA Clips · 3 Morphs · 3rd-POV"),
        ("44 Chunks", "HYBRID RAG AI", "768-d Dense + BM25 · Citations"),
    ])

    add_callout(
        doc,
        "Key Architectural Highlights & Zero-GLSL WebGPU Mandate",
        "All real-time rendering passes import strictly from `three/webgpu` and `three/tsl` with zero legacy custom "
        "GLSL shaders under `src/`. Expensive screen-space reflections (SSR) were replaced with a manual oblique "
        "mirror camera rendering into a half-resolution `HalfFloat` planar render target perturbed by procedural "
        "TSL concentric rain ripples, eliminating WebGPU attachment hazards while sustaining 60 FPS desktop and "
        "adaptive-DPR mobile performance."
    )

    # Page 3: Native Word Table of Contents + List of Figures
    add_h1(doc, "Table of Contents", page_break=True)
    p_toc = doc.add_paragraph()
    p_toc.paragraph_format.space_after = Pt(8)
    add_field(p_toc, 'TOC \\o "1-2" \\h \\z \\u', font_size=9.0, color=RGB_NAVY)

    lof_rows = [
        ["Cover Figure", "2026 Game & XR Developer Showreel Editorial Cover (2×2 Gameplay Matrix)"],
        ["Figure 1", "End-to-End Full-Stack System Architecture (Content, WebGPU Client & Vercel APIs)"],
        ["Figure 2", "Per-Frame WebGPU Execution Sequence & TSL RenderPipeline Post-Processing Graph"],
        ["Figure 3", "Selected Flagship Game & XR Projects Showcased in the Portfolio and 3D Alley Kiosks"],
        ["Figure 4", "Side-by-Side Comparison: Procedural Blender 5.1 Avatar Render vs. Reference Styling"],
        ["Figure 5", "Composited Showreel Frames: Act 4 Dual Engine Comparison & Act 6 Triple XR Suite"],
        ["Figure 6", "Hybrid RAG AI Assistant Pipeline (Offline Ingestion + Online Dense/BM25 Fusion)"],
        ["Figure 7", "Production Vite 6 Gzipped Bundle Breakdown & 3D Static Asset Budget Analysis"],
    ]
    add_styled_table(
        doc,
        "List of Figures",
        ["Figure", "Caption / Technical Subject"],
        lof_rows,
        [1.15, 5.50],
        pad_v=44,
        font_sz=8.2,
    )

    # =========================================================================
    # SECTION 1: INTRODUCTION, PROBLEM STATEMENT & OBJECTIVES
    # =========================================================================
    add_h1(doc, "1. Introduction, Problem Statement & Project Objectives", page_break=True)

    add_h2(doc, "1.1 Project Background & Motivation")
    add_body(
        doc,
        "Technical recruiters, game studios, and creative-technology directors evaluate game developers and 3D "
        "engineers not merely by bulleted resumes, but by verifiable real-time execution. Traditional HTML/CSS "
        "portfolios fail to convey real-time shader mastery, spatial navigation engineering, 3D rigging workflows, "
        "or interactive AI engineering. Conversely, many experimental WebGL demos sacrifice usability, load speed, "
        "mobile stability, and recruiter scannability in favor of opaque 3D navigation."
    )
    add_body(
        doc,
        "This Web3D project resolves that tension through a **dual-mode architecture**: visitors immediately land in "
        "an ultra-legible, Swiss-grid minimalist creative-technologist portfolio (`samsy.ninja` editorial layout) "
        "floated over a live 60 FPS WebGPU cyberpunk alley whose camera smoothly tracks scroll depth across five "
        "cinematic waypoints. At any moment, visitors can click **Explore 3D World** to dismiss the editorial layer "
        "and walk directly down the rain-drenched alley in **third-person or first-person perspective** alongside a "
        "custom-rigged 3D avatar of the developer, inspecting eight illuminated gameplay video kiosks and conversing "
        "with an AI assistant grounded strictly in verified portfolio documents."
    )

    add_h2(doc, "1.2 Problem Statement")
    add_bullet(doc, "**Static Presentation Gap:** Conventional web portfolios cannot demonstrate live GPU compute shaders, PBR lighting, spatial audio, or 3D character animation directly inside the browser.")
    add_bullet(doc, "**WebGPU Rendering & Performance Bottlenecks:** Naive Screen-Space Reflections (SSR) and CPU-driven particle rain break under WebGPU `PassNode` attachment constraints and saturate mobile GPUs.")
    add_bullet(doc, "**Content Fragmentation:** Maintaining project descriptions separately across website HTML, chatbot prompts, and promotional videos causes drift and inconsistent metadata.")
    add_bullet(doc, "**LLM Hallucination Risk:** Unconstrained AI portfolio chatbots frequently fabricate dates, GPAs, employment history, or contact details when visitors ask out-of-scope questions.")
    add_bullet(doc, "**Production Security & Media Stutter:** Public contact forms attract automated spam bots, while simultaneous 3D video textures and 1080p showreel players cause frame drops and audio overlap without explicit lifecycle orchestration.")

    add_h2(doc, "1.3 Six-Module Project Objectives")
    mod_rows = [
        ["Module 1", "Interactive 3D WebGPU Portfolio", "Render a rainy cyberpunk alley with GPU collision rain, planar wet-ground reflections, 8 gameplay video kiosks, BVH walk controls, and a responsive editorial UI."],
        ["Module 2", "Custom Procedural 3D Avatar", "Model, shade, rig (20 bones), animate (6 NLA tracks), and morph-rig (3 shape keys) a stylized likeness in Blender 5.1 via reproducible Python scripting."],
        ["Module 3", "Editorial Promotional Showreel", "Author a 46.8-second 1080p@30fps 9-act developer trailer in Adobe After Effects + FFmpeg aligned with the editorial design system and custom cyber-groove soundtrack."],
        ["Module 4", "Hybrid RAG AI Assistant", "Build `AHMAD.AI` using offline Gemini 768-d embeddings + BM25 hybrid retrieval, strict anti-hallucination prompting, clickable citations, 9-language support, and voice I/O."],
        ["Module 5", "Secured Email & Contact API", "Deliver an isomorphic client/server contact pipeline with honeypot, timing check, per-IP rate limiting, XSS sanitization, and Resend REST email delivery."],
        ["Module 6", "Optimization, QA & Cloud CI/CD", "Implement adaptive DPR, vendor chunk splitting, automated RAG/API test suites, security/cache headers, and zero-config GitHub-to-Vercel production deployment."],
    ]
    add_styled_table(
        doc,
        "Table 1: Core Engineering Modules & Deliverable Objectives",
        ["Module", "Domain", "Primary Engineering Objective"],
        mod_rows,
        [0.95, 1.95, 3.75],
    )

    add_h2(doc, "1.4 Technology Stack Matrix")
    stack_rows = [
        ["3D Graphics & Shaders", "`three` `^0.185.1` (`three/webgpu`, `three/tsl`), `three-mesh-bvh` `^0.9.13`", "WebGPU-first renderer, TSL node materials, GPU compute rain, BVH spatial raycasting"],
        ["Frontend & Motion", "Vanilla ES2022 Modules, CSS Custom Properties, `gsap` `^3.15.0`, Vite `^6.3.5`", "Zero-framework overhead, inertial UI reveals, 5-waypoint camera choreography, fast builds"],
        ["3D Asset & Rigging", "Blender 5.1 Python API (`bpy`, `bmesh`), Draco & KTX2/Basis Transcoders, glTF 2.0", "Reproducible procedural avatar, compressed city/car/plane GLBs, PBR workflows"],
        ["Motion & Video Pipeline", "Adobe After Effects ExtendScript (`.jsx`), Python Pillow 12.3, `ffmpeg-static` 6.1", "9-act editorial showreel, kinetic typography, H.264 `+faststart` streaming optimization"],
        ["AI & RAG Pipeline", "Google Gemini REST API (`gemini-embedding-001`, `gemini-3.7-flash`), `unpdf` `^1.0.0`", "768-d dense vectors, BM25 lexical fusion, PDF CV extraction, Web Speech STT/TTS"],
        ["Backend & Security", "Vercel Serverless Node.js (`>=20`), Resend REST API, shared validation module", "Origin check, sliding-window rate limiter, honeypot, HTML escaping, graceful fallback"],
        ["Deployment & Analytics", "Vercel CLI `^56.2.0`, `@vercel/analytics` `^1.5.0`, `@vitejs/plugin-basic-ssl`", "HTTPS local WebGPU dev, immutable CDN asset caching, automated GitHub production CI/CD"],
    ]
    add_styled_table(
        doc,
        "Table 2: Verified Production Technology Stack (from package.json & Pipeline Scripts)",
        ["Layer", "Technologies & Versions", "Engineering Role"],
        stack_rows,
        [1.45, 2.55, 2.65],
    )

    # =========================================================================
    # SECTION 2: SYSTEM ARCHITECTURE & ENGINEERING DESIGN
    # =========================================================================
    add_h1(doc, "2. System Architecture & Engineering Design", page_break=True)

    add_body(
        doc,
        "The repository follows a modular, factory-based composition architecture rooted in `src/main.js` rather than "
        "a monolithic game-engine inheritance hierarchy. Each subsystem (`world`, `pipeline`, `cameraDirector`, "
        "`renderLoop`, `appShell`, `portfolioUI`, `inspectorSession`, and `adaptiveDpr`) is constructed as a plain "
        "object returning clean closure-scoped APIs. Optional subsystems return `null` when toggled off in "
        "`src/world/features.js`, and every call site uses optional chaining (`?.`) so features can be cleanly "
        "isolated or stripped according to `STRIP_ORDER`."
    )

    add_figure(
        doc,
        os.path.join(ASSETS_DIR, "diag_architecture.png"),
        "Figure 1: End-to-End Full-Stack System Architecture illustrating Single-Source-of-Truth content authoring, WebGPU browser client subsystems, and Vercel serverless RAG & Contact APIs.",
        width_in=6.55,
    )

    add_h2(doc, "2.1 Single Source of Truth Data Flow")
    add_body(
        doc,
        "A core design invariant is that personal identity, project metadata, skills, education, experience, and "
        "media URLs are maintained once in `content/profile.json`. This eliminates synchronization bugs across four "
        "independent consumers:"
    )
    add_bullet(doc, "**Editorial Portfolio UI (`src/portfolio/createPortfolioUI.js`):** Directly imports `content/profile.json` at build time to populate hero metrics, the 9-project filterable index, case study modals, capability matrices, timeline cards, and direct contact links.")
    add_bullet(doc, "**In-World 3D Project Kiosks (`src/world/arcade/createProjectScreens.js`):** Reads the first 8 project objects to procedurally generate `1024×220` neon HUD header `CanvasTexture` headers and bind crisp gameplay `VideoTexture` loops to alley screens.")
    add_bullet(doc, "**RAG Vector Index (`scripts/ingest.mjs` → `data/vector-index.json`):** Converts `content/profile.json`, `knowledge/SyedMuhammadAhmad_CV.pdf`, and `knowledge/portfolio-details.md` into 28 structured documents and 44 overlapping chunks with 768-dimensional embeddings.")
    add_bullet(doc, "**Promotional Showreel (`video/make_hud_overlays.py` & `video/build_promo.jsx`):** Synchronizes project titles, categories, years, and engine tags across the 9-act 1080p trailer.")

    add_h2(doc, "2.2 Repository Structure & Module Routing")
    dir_rows = [
        ["`src/main.js`", "Application bootstrapper: applies device budgets, initializes WebGPU, loads world/post/UI/audio, runs shader warmup, and starts the render loop."],
        ["`src/bootstrap/`", "`createRenderer.js` (WebGPU context + shadow updater) and `createCamera.js` (perspective FOV + responsive layout sync)."],
        ["`src/world/`", "`createWorld.js`, `features.js`, `bvh.js`, `city/`, `car/`, `avatar/`, `arcade/`, `ground/`, `weather/`, `billboards/`, `effects/`."],
        ["`src/tsl/`", "Reusable pure-TSL shader nodes: `rainRipples.js`, `surfaceRain.js`, `edgeChromaticAberration.js`, `boxBlur.js`, `rainGlass.js`."],
        ["`src/post/`", "`postprocessing.js` (`RenderPipeline` MRT, GTAO, Bloom, Lensflare, SMAA) and `look/cyberpunkLook.js` (6 cinematic color grading presets)."],
        ["`src/controls/` & `src/runtime/`", "`createWalkControls.js` (BVH collision + WASD/touch walk), `createCameraDirector.js`, `createRenderLoop.js`, `warmup.js`."],
        ["`src/portfolio/` & `src/ui/`", "`createPortfolioUI.js` + `portfolio.css` (`samsy.ninja` editorial UI, AI chat drawer, modals) and `ui/chrome/` (`createAudioButton.js`, settings)."],
        ["`src/platform/`", "`performanceProfile.js` (device budgets), `adaptiveDpr.js` (sustained FPS downgrade controller), `deviceLayout.js`, `userPreferences.js`."],
        ["`blender/` & `video/`", "Reproducible Blender 5.1 Python avatar builder (`build_avatar.py`, `avatar.blend`) and After Effects/FFmpeg showreel scripts (`build_promo.jsx`, `make_hud_overlays.py`)."],
        ["`api/` & `shared/`", "Vercel serverless endpoints (`api/chat.js`, `api/contact.js`), RAG retriever (`api/_lib/retriever.js`), Gemini REST client (`api/_lib/gemini.js`), shared validator (`shared/validation.js`)."],
        ["`scripts/` & `data/`", "Offline automation (`ingest.mjs`, `render-promo-video.mjs`, `test-rag.mjs`, `test-api.mjs`) and pre-built `data/vector-index.json`."],
    ]
    add_styled_table(
        doc,
        "Table 3: Workspace Directory & Architectural Module Routing",
        ["Directory / Entry Point", "Responsibility & Key Files"],
        dir_rows,
        [1.95, 4.70],
    )

    # =========================================================================
    # SECTION 3: MODULE 1 — INTERACTIVE 3D WEBGPU & TSL ENVIRONMENT
    # =========================================================================
    add_h1(doc, "3. Module 1 — Interactive 3D WebGPU & TSL Environment", page_break=True)

    add_h2(doc, "3.1 WebGPU-First Renderer & Three Shading Language (TSL)")
    add_body(
        doc,
        "All graphics modules import strictly from `three/webgpu` and `three/tsl`, targeting modern WebGPU compute "
        "and node-based rendering pipelines (with Three.js automatic WebGL2 backend fallback when a browser lacks "
        "WebGPU support). Zero raw GLSL shader strings exist under `src/`. Every procedural effect—from raindrop "
        "physics and puddle ripples to wet car droplets and edge chromatic aberration—is composed declaratively "
        "using TSL `Fn`, `uniform`, `instancedArray`, `MeshStandardNodeMaterial`, and `RenderPipeline`."
    )
    add_body(
        doc,
        "During our cross-platform codebase audit, a Windows Chromium warning (`The powerPreference option is "
        "currently ignored when calling requestAdapter() on Windows`) was eliminated in `src/bootstrap/createRenderer.js` "
        "by omitting redundant `powerPreference` hints on Windows user agents while preserving high-performance adapter "
        "selection on macOS and Linux."
    )

    add_h2(doc, "3.2 GPU Height-Map Collision Rain & Splash Simulation")
    add_body(
        doc,
        "To prevent rain particles from unrealistically falling through building overhangs, awnings, and the parked "
        "Quadra vehicle without executing prohibitive per-drop CPU raycasts, the scene implements a two-pass GPU "
        "height-map collision system (`src/world/weather/createCollisionHeight.js` and `createCollisionRain.js`):"
    )
    add_bullet(doc, "**Top-Down Orthographic Height Pass:** A downward-looking `OrthographicCamera` spanning a `100 × 100 × 80` world-unit volume tracks the active camera XZ coordinates at `y = 50`. An override `MeshBasicNodeMaterial` outputs `vec4(positionWorld, 1)` per texel into a `512 × 512` `HalfFloatType` render target configured with `NearestFilter` and `generateMipmaps = false` to prevent edge-bleeding height interpolation artifacts.")
    add_bullet(doc, "**Strict Occlusion Hide List (`collisionHideObjects.js`):** Immediately before capturing the height texture, the loop hides `rain.group`, `sky.mesh`, `planes.group`, `avatar.root`, `projectScreens.group`, and all `smoke.emitters` so transparent particles and floating UI never block rain from reaching roofs and pavement.")
    add_bullet(doc, "**WebGPU Compute Integration (`5,000` Instances):** Storage buffers (`instancedArray`) store raindrop positions, velocities, splash positions, and splash animation cycles. Each frame, a TSL compute kernel integrates vertical fall velocity, computes height-map UVs via `collisionHeight.getUV(worldPos)`, samples `floorY = texture(heightMap, uv).y`, and triggers a TSL `If` branch upon impact to spawn a 5-frame sprite-sheet water splash (`water-splash.webp`) and recycle the streak overhead.")
    add_bullet(doc, "**Unified Scene Pass Integration:** Collision rain runs with `useDedicatedPass: false`, compositing directly inside the main scene pass rather than incurring an extra full-screen render target overhead, with optional frame-skipping (`collisionRainFrameSkip`) on the height RT alone.")

    add_h2(doc, "3.3 Wet Ground Planar Reflections & Procedural Ripples (SSR Replacement)")
    add_body(
        doc,
        "Historically, Screen-Space Reflections (SSR) proved both prohibitively expensive and incompatible with "
        "reliable roughness masking on WebGPU, while Three.js's built-in `reflector()` node triggered WebGPU "
        "`TextureBinding | RenderAttachment` validation hazards inside `PassNode` graphs. The ground shader "
        "(`src/world/ground/createGround.js` + `src/tsl/rainRipples.js`) resolves this cleanly:"
    )
    add_bullet(doc, "**Manual Oblique Mirror Camera:** A dedicated `PerspectiveCamera` mirrors the active camera across the pavement plane (`y = -5.4`) and renders the reflected cyberpunk skyline and neon signage into a half-resolution (`0.5×`) `HalfFloat` render target (`GroundPlanarReflection`), gated by `groundReflectionFrameSkip`.")
    add_bullet(doc, "**Procedural World-Space Rain Ripples (`rainRipples.js`):** Evaluates a 3×3 Voronoi-hashed neighborhood (`hash12`, `hash22`) in world XZ space (`positionWorld.xz * 4.83`), computing finite-difference radial sine wave derivatives (`h = 0.001`) attenuated quadratically by droplet lifetime `(1 - t)²` to output perturbed tangent normals.")
    add_bullet(doc, "**Roughness-Modulated Composition:** Both tiled PBR puddle maps (`wet-puddles-albedo/normal/roughness.jpg`, `uvRepeat = 14.9`) and procedural ripple derivatives warp `screenUV.flipX()`, mixing planar neon reflections into the pavement via emissive energy modulated by `(1 - roughness)`.")

    add_h2(doc, "3.4 Procedural Wet Car Paint (surfaceRain.js)")
    add_body(
        doc,
        "Wet droplets sliding across the parked cyberpunk Quadra sports car (`src/world/car/applyCarSurfaceRain.js` "
        "and `src/tsl/surfaceRain.js`) are decoupled completely from ground ripples. A zero-simulation-texture TSL "
        "drop graph (`MovingDropLayer`) evaluates staggered vertical drop cells with sinusoidal horizontal wiggle, "
        "sawtooth gravity fall curves, trailing micro-droplets, and finite-difference surface normals on a dedicated "
        "**UV1 channel** (leaving UV0 untouched for vehicle PBR maps). To conserve fragment ALU cycles when the "
        "visitor walks away, `carSurfaceRain.syncProximity()` automatically fades and disables droplet updates "
        "between `20` and `32` world units (`carSurfaceRainFadeStart/End`)."
    )

    add_h2(doc, "3.5 Per-Frame Render Loop & TSL Post-Processing Stack")
    add_body(
        doc,
        "Frame execution follows a deterministic pipeline in `src/runtime/createRenderLoop.js` feeding into "
        "`src/post/postprocessing.js` and `src/post/look/cyberpunkLook.js`:"
    )

    add_figure(
        doc,
        os.path.join(ASSETS_DIR, "diag_render_pipeline.png"),
        "Figure 2: Per-Frame WebGPU Execution Sequence (Stage A: Auxiliary Passes & GPU Compute) and Three.js TSL RenderPipeline Post-Processing Graph (Stage B).",
        width_in=6.55,
    )

    tsl_rows = [
        ["Collision Height RT", "`createCollisionHeight.js`", "`512×512` HalfFloat Nearest", "Captures `positionWorld` from top-down ortho camera (`100×100×80m`)"],
        ["GPU Compute Rain", "`createCollisionRain.js`", "`5,000` instanced streaks", "WebGPU compute kernel + 5-frame sprite splashes on roof/floor impact"],
        ["Wet Ground Reflection", "`createGround.js` + `rainRipples.js`", "Half-res (`0.5×`) mirror RT", "Oblique planar reflection warped by PBR normals + 3×3 Voronoi ripples"],
        ["Car Surface Droplets", "`applyCarSurfaceRain.js` + `surfaceRain.js`", "UV1 procedural (fade 20–32m)", "Animated sliding drops + trails driving roughness & normal perturbation"],
        ["GTAO Pre-Pass", "`postprocessing.js` (`GTAONode`)", "Half-res (`0.5×`), 6 samples", "Depth + packed view-space normals excluding rain & smoke layers"],
        ["Scene MRT + Emissive Bloom", "`postprocessing.js` (`BloomNode`, `LensflareNode`)", "Half-res (`0.5×`), blur `r=4`", "Separate `output` & `emissive` attachments drive selective neon glow & ghost flares"],
        ["Cyberpunk Look Grading", "`cyberpunkLook.js` + `edgeChromaticAberration.js`", "6 presets (default `neonNoir`)", "Distance/sky fog, tint, green suppression, contrast, edge CA, vignette, film grain"],
        ["Anti-Aliasing", "`postprocessing.js` (`SMAANode`)", "Full-res post-grade pass", "Subpixel Morphological Anti-Aliasing crisp on neon edges and thin cables"],
    ]
    add_styled_table(
        doc,
        "Table 4: Summary of WebGPU TSL Shaders & Post-Processing Subsystems",
        ["Subsystem", "Source Modules", "Resolution / Budget", "Technical Function"],
        tsl_rows,
        [1.40, 1.75, 1.35, 2.15],
    )

    add_h2(doc, "3.6 BVH Walk Controls, 3rd-Person Avatar & 8-Screen Project Kiosk Arcade")
    add_body(
        doc,
        "Walking exploration (`src/controls/createWalkControls.js` + `src/world/bvh.js`) uses `three-mesh-bvh` "
        "Bounding Volume Hierarchies built on city geometry, boundary colliders, and the Quadra car hull. Three "
        "lateral cylinder probes (`WALL_LATERAL_OFFSETS = [0, -0.85, 0.85]` × `playerRadius = 0.55m`) prevent wall "
        "clipping while vertical ground probes enforce smooth curb stepping (`maxStepUp = 0.4m`, `maxStepDown = 1.75m`). "
        "Movement supports exponential acceleration/deceleration (`WASD` / arrow keys, `Shift` `1.8×` sprint with dynamic "
        "`+8°` FOV boost, `C` `0.55×` crouch, and a touch virtual joystick on mobile devices)."
    )
    add_body(
        doc,
        "In **Third-Person Perspective** (default enabled; toggleable anytime via the `V` key or the 3D exploration "
        "HUD bar), `loadAvatar.js` smoothly interpolates the rigged Blender avatar `2.15m` ahead of the camera along "
        "the horizontal look vector, orients the root yaw toward velocity, blends into the `Walk` NLA clip scaled by "
        "horizontal speed (`0.75×–1.85×`), and applies procedural stride reinforcement so locomotion looks crisp "
        "without blocking the visitor's sightline. Lining both sides of the alley, `createProjectScreens.js` installs "
        "**8 custom neon holographic kiosks** plus overhead alley archways. Each kiosk pairs a `1024×220` sci-fi "
        "header `CanvasTexture` with a crystal-clear unlit TSL `VideoTexture` material so scene shadows never darken "
        "gameplay videos. Crucially, `projectScreens.setPaused(true)` suspends all background 3D video decoders "
        "whenever the user plays the 1080p Showreel or opens a Project Case Study Modal, eliminating GPU decode contention."
    )

    add_h2(doc, "3.7 Layered Audio Architecture & Overlap Prevention")
    add_body(
        doc,
        "Audio (`src/ui/chrome/createAudioButton.js` and `src/audio/`) layers the user's custom 1:58 dark-cyberpunk "
        "electro-bass track (`public/funky-cyber-groove.mp3`, gain `1.0`) with ambient rainfall (`public/light-rain.mp3`, "
        "gain `0.28`), supplemented in 3D walk mode by spatial car engine rumble, overhead flying craft audio, and "
        "6 randomized wet footstep samples (`wet_footstep-step-01..06.mp3`). Playing `#sn-promo-video` automatically "
        "pauses background music and restores it upon pause/end, while `createAudioButton.js` guards both "
        "`startOnFirstInteraction` and `window.focus` against restarting music while a video player is active."
    )

    # =========================================================================
    # SECTION 4: EDITORIAL UI/UX ARCHITECTURE & 9-PROJECT SHOWCASE
    # =========================================================================
    add_h1(doc, "4. Editorial UI/UX Architecture & 9-Project Showcase", page_break=True)

    add_h2(doc, "4.1 samsy.ninja Minimalist Creative-Technologist Design System")
    add_body(
        doc,
        "The portfolio overlay (`src/portfolio/createPortfolioUI.js` and `src/portfolio/portfolio.css`) adopts a "
        "disciplined Swiss architectural aesthetic inspired by `samsy.ninja`: high-contrast obsidian surfaces "
        "(`#07070A` void, `#0D0D12` elevated panels, `#F4F4F6` off-white ink), `1px` crisp structural hairlines "
        "(`rgba(244, 244, 246, 0.16)`), bold uppercase kinetic typography (`Syne` / `Space Grotesk` with hollow "
        "outline display strokes paired with `JetBrains Mono` indices), and surgical acid-lime (`#DDFB24`) interactive "
        "accents—plus a complete high-contrast **Light Mode** toggle."
    )
    add_bullet(doc, "**Fixed Architectural Topbar (`.sn-topbar`):** Houses brand mark (`SYED MUHAMMAD AHMAD` / `AKKA®`), green availability pulse dot, section jump anchors (`Works (09)`, `Showreel`, `Capabilities`, `Contact`), `◈ AHMAD.AI`, `Explore 3D World ↗`, `Sound: ON/OFF`, and `Light/Dark` mode.")
    add_bullet(doc, "**5-Waypoint WebGPU Scroll Choreography:** Native browser scrolling smoothly interpolates the background 3D WebGPU camera across 5 curated alley poses (Hero over the wet Quadra car → Alley Kiosk Corridor → 3D Avatar Stage → Wide Architectural Perspective → Neon Skyline) without wheel-event hijacking.")
    add_bullet(doc, "**Curated Interactive Project Index (`(01)`):** Supports instant category filtering (`All`, `Game`, `XR`, `Web`), real-time keyword search across engines/tags, `[Index List]` vs `[Media Grid]` layout switching, a right-anchored 60 FPS floating wave-distortion video preview canvas (`.sn-hover-preview`), and a single-view **Project Case Study Modal** with `ArrowLeft`/`ArrowRight` keyboard pagination.")
    add_bullet(doc, "**Unobstructed Full-Screen 3D World Mode (`.sn-mode-3d`):** Clicking `Explore 3D World ↗` hides the editorial DOM cleanly and docks a minimal floating control bar at top-center containing `Exit 3D World`, `View: 3RD PERSON (V)`, and live 3D avatar gesture buttons (`Wave`, `Victory`, `Point`, `Talk`) so character animations are 100% unobstructed.")

    add_h2(doc, "4.2 Complete Catalog of Showcased Projects")
    proj_rows = [
        ["001", "Chrono Rebellion", "2026", "Game", "Unity, C#, HDRP", "1st/3rd-person sci-fi shooter with time-manipulation mechanics, custom HUD, and HDRP combat."],
        ["002", "Behind the Smile", "2026", "Game", "Unity, C#, GGJ 2026", "Narrative-driven 3D game shipped in 48 hours at Global Game Jam 2026 on theme 'Masks'."],
        ["003", "Paper Plane Dash", "2025", "Game", "Unreal Engine 5, Blueprints", "3rd-person endless runner featuring procedural level generation, lane switching, and obstacle physics."],
        ["004", "Solar System Exploration", "2025", "XR (VR)", "Unity, OpenXR, XR Toolkit", "Immersive VR astronomy simulation with teleport locomotion and interactive world-space UI."],
        ["005", "Voxelcraft 3D", "2025", "Game", "3D, Voxel, Sandbox", "Block-building procedural 3D sandbox featuring terrain biomes, inventory, and live block editing."],
        ["006", "Pac-Man (C++ / SFML)", "2024", "Game", "C++, SFML, QuadTrees", "2D arcade engine applying Graph pathfinding AI and QuadTree spatial collision partitioning."],
        ["007", "AR Memory Card Game", "2025", "XR (AR)", "Unity, Vuforia, C#", "Marker-based augmented reality memory game with image-target tracking and match scoring."],
        ["008", "AR Face Filter App", "2025", "XR (CV)", "Python, OpenCV, MediaPipe", "Real-time webcam facial landmark tracker applying neon glasses, frames, and eye-glow filters."],
        ["009", "Interactive 3D Portfolio", "2026", "Web3D", "Three.js WebGPU, Blender, RAG", "This flagship WebGPU cyberpunk alley, custom 3D avatar, AE showreel, and Gemini RAG platform."],
    ]
    add_styled_table(
        doc,
        "Table 5: Complete 9-Project Portfolio Index Mapped from content/profile.json",
        ["#", "Project Title", "Year", "Type", "Core Stack", "Technical Highlights"],
        proj_rows,
        [0.42, 1.35, 0.48, 0.65, 1.45, 2.30],
        pad_v=52,
    )

    add_figure(
        doc,
        os.path.join(ASSETS_DIR, "fig_projects_grid.jpg"),
        "Figure 3: Direct engine captures from four flagship portfolio projects featured in both the Editorial Index and the in-world 3D Alley Holographic Kiosks.",
        width_in=6.45,
    )

    # =========================================================================
    # SECTION 5: MODULE 2 — CUSTOM 3D AVATAR (BLENDER 5.1)
    # =========================================================================
    add_h1(doc, "5. Module 2 — Custom Procedural 3D Avatar in Blender 5.1", page_break=True)

    add_h2(doc, "5.1 Reproducible Python Asset Pipeline")
    add_body(
        doc,
        "Rather than relying on generic third-party character packs, a custom stylized 3D avatar modeled after "
        "Syed Muhammad Ahmad was built programmatically via a 754-line Blender 5.1 Python script "
        "(`blender/build_avatar.py`). Running Blender headlessly (`blender.exe -b --factory-startup --python "
        "blender\\build_avatar.py`) deterministically constructs all meshes, materials, armature bones, vertex "
        "weights, facial morph targets, and NLA animation tracks, outputting three synchronized artifacts: "
        "`blender/avatar.blend` (native source project), `public/models/avatar.glb` (`2.53 MB` web-ready glTF 2.0 "
        "binary with Y-up convention, skins, morphs, and NLA tracks), and `blender/avatar_preview.png` (`1024×1024` "
        "Eevee studio render with 3-point key + cyan/magenta rim lights)."
    )

    add_h2(doc, "5.2 Character Modeling, Likeness & PBR Materials")
    add_body(
        doc,
        "The character incorporates 15 glTF-compliant **Principled BSDF** materials (`Skin`, `Stubble`, `Hair`, "
        "`EyeWhite`, `Iris`, `Pupil`, `EyeHighlight`, `Lips`, `BikerJacket`, `BlackShirt`, `DarkJeans`, `Sneakers`, "
        "`SneakerSole`, `GlassesFrame`, `NeonCyan`, and `NeonMagenta`). Smoothly rounded capsule limb geometry "
        "prevents hard crease artifacts during animation, while facial styling captures reference-photo details: "
        "swept-up voluminous sculpted hair locks (8 layered hair-sweep primitives over a trimmed cranial cap), "
        "dark metallic-rimmed glasses with ear temples, neat moustache, jawline stubble, and an olive-charcoal "
        "biker jacket accented with emissive cyan (`#00E5FF`, strength `3.5`) zipper piping and magenta (`#FF2BD6`, "
        "strength `3.0`) cuff/heel trim that naturally triggers selective WebGPU bloom."
    )

    add_h2(doc, "5.3 20-Bone Armature, 6 NLA Clips & Facial Morph Targets")
    add_body(
        doc,
        "The skeleton (`AvatarRig`) defines **20 hierarchical bones**: a 6-bone central chain (`Root` → `Hips` → "
        "`Spine` → `Chest` → `Neck` → `Head`) plus mirrored 7-bone limb chains on Left/Right (`Shoulder.L/R`, "
        "`UpperArm.L/R`, `LowerArm.L/R`, `Hand.L/R`, `UpperLeg.L/R`, `LowerLeg.L/R`, `Foot.L/R`). All 6 authored "
        "animation clips are pushed to Non-Linear Animation (NLA) tracks for independent glTF export, complemented "
        "by 3 blendshape morph targets on `HeadMesh`."
    )

    anim_rows = [
        ["`Idle`", "120 frames (4.0 s)", "Loop", "Subtle chest breathing, hip weight shift, natural head glance; default standby state."],
        ["`Walk`", "33 frames (1.1 s)", "Loop (Speed-Scaled)", "Full bipedal stride (hip bob, counter-rotating torso, leg & arm swing) for 3rd-person alley walk."],
        ["`Wave`", "75 frames (2.5 s)", "Once → Idle", "Friendly right-hand greeting wave; triggered by HUD gesture button or proximity arrival."],
        ["`Talk`", "90 frames (3.0 s)", "Loop (While Speaking)", "Conversational dual-hand gesturing and head nods synchronized with `AHMAD.AI` voice playback."],
        ["`Point`", "60 frames (2.0 s)", "Once → Idle", "Left-arm presenting gesture directing visitor attention toward featured project kiosks."],
        ["`Victory`", "60 frames (2.0 s)", "Once → Idle", "Celebratory double fist-pump + hop triggered from the 3D World gesture bar."],
        ["`Blink` / `Smile` / `MouthOpen`", "Real-time Shape Keys", "Procedural (0.0–1.0)", "Automatic periodic blinking, wave smile boost, and dynamic sinusoidal lip-sync during TTS audio."],
    ]
    add_styled_table(
        doc,
        "Table 6: Blender 5.1 Avatar NLA Animation Tracks & Facial Morph Target Specifications",
        ["Clip / Shape Key", "Duration / Type", "Playback Mode", "Interactive Runtime Trigger (loadAvatar.js)"],
        anim_rows,
        [1.40, 1.25, 1.25, 2.75],
        pad_v=48,
    )

    add_h2(doc, "5.4 Real-Time WebGPU Runtime Integration")
    add_body(
        doc,
        "At load time (`src/world/avatar/loadAvatar.js`), every mesh material on `avatar.glb` is converted into a "
        "native `MeshStandardNodeMaterial` for full WebGPU TSL lighting and shadow compatibility. A spinning emissive "
        "cyan holographic ring (`AvatarHoloRing`) plus dedicated cyan key (`2.4`) and magenta rim (`2.0`) point lights "
        "keep the silhouette legible in the dark alley. Per frame, the avatar tracks the user's cursor with its `Head` "
        "bone, blinks procedurally, synchronizes `Talk` + `MouthOpen` morph weights with Web Speech TTS narration, "
        "and transitions smoothly via cross-faded `AnimationMixer` actions (`0.16–0.22s`)."
    )

    add_figure(
        doc,
        os.path.join(ASSETS_DIR, "fig_avatar_comparison.jpg"),
        "Figure 4: Side-by-side comparison of the procedural Blender 5.1 Eevee avatar render (left) and the developer reference styling photograph (right).",
        width_in=6.20,
    )

    # =========================================================================
    # SECTION 6: MODULE 3 — EDITORIAL PROMOTIONAL SHOWREEL
    # =========================================================================
    add_h1(doc, "6. Module 3 — Editorial Promotional Showreel", page_break=True)

    add_h2(doc, "6.1 Visual Alignment & Hybrid After Effects / FFmpeg Pipeline")
    add_body(
        doc,
        "To eliminate generic visual effects and unify the video trailer with the portfolio website, the 46.8-second "
        "1080p@30fps showreel was rebuilt from the ground up using the exact `samsy.ninja` design tokens extracted "
        "from `src/portfolio/portfolio.css`: `#07070A` Obsidian Void, `#0D0D12` elevated frames, `#F4F4F6` off-white "
        "type, `#DDFB24` surgical acid-lime accents, and `1px` Swiss grid hairlines. The automated production pipeline "
        "combines three reproducible scripts:"
    )
    add_bullet(doc, "**Adobe After Effects ExtendScript (`video/build_promo.jsx`):** Programmatically constructs `video/promo.aep` with high-influence cubic-bezier kinetic typography (`KeyframeEase(0, 85)` / `(0, 35)`), rectangular shutter mask wipes, animated `1px` rules, and 9 composited scenes.")
    add_bullet(doc, "**Editorial Overlay Renderer (`video/make_hud_overlays.py`):** Uses Python Pillow (`12.3`) to generate 9 crisp `1920×1080` transparent RGBA architectural overlay plates (`hud_scene1_intro.png` through `hud_scene9_outro.png`), including the redesigned 2×2 gameplay matrix cover frame with outer-corner quadrant tags and zero portrait clutter.")
    add_bullet(doc, "**Streaming-Optimized FFmpeg Compositor (`scripts/render-promo-video.mjs`):** Composites 1080p game footage with smooth cubic ease-out HUD slide-ups (`42*pow(1-t/0.44,3)`), muxes the user's custom 1:58 cyberpunk electro-bass soundtrack (`video/music/funky-cyber-groove.wav`) with smooth `0.6s` fade-in and `2.0s` fade-out (`160 kbps` AAC), and encodes `public/video/promo.mp4` (`10.81 MB`, H.264 High Profile, `CRF 24`, `maxrate 1800k`, `bufsize 3600k`, `-g 60`, `-movflags +faststart`) plus `public/video/promo-poster.jpg` (`298.5 kB`).")

    add_h2(doc, "6.2 Nine-Act Editorial Storyboard")
    acts_rows = [
        ["Act 1", "0.0 – 4.8 s", "2×2 Gameplay Cover & Title Lockup", "Four live game quadrants (`Chrono Rebellion`, `Paper Plane Dash`, `Behind the Smile`, `Voxelcraft`) framed around centered editorial title lockup."],
        ["Act 2", "4.8 – 10.2 s", "`001` Chrono Rebellion", "Full-screen 1080p Unity HDRP combat capture with sinusoidal eased camera pan and lower-left Swiss case study card."],
        ["Act 3", "10.2 – 15.6 s", "`002` Behind the Smile", "Global Game Jam 2026 narrative 3D showcase with cubic ease-out HUD reveal and hairline engine badges."],
        ["Act 4", "15.6 – 21.0 s", "`003 × 006` Dual Engine Split", "Side-by-side split-screen comparing *Paper Plane Dash* (Unreal Engine 5 Blueprints) and *Pac-Man* (C++ / SFML / QuadTrees)."],
        ["Act 5", "21.0 – 26.2 s", "`005` Voxelcraft 3D", "Full-screen procedural voxel sandbox showcase demonstrating real-time world exploration and block editing."],
        ["Act 6", "26.2 – 31.8 s", "`004 × 007 × 008` Triple XR Suite", "Asymmetric 3-viewport layout uniting *Solar System VR* (`1080×1080`), *AR Memory Card* (`840×540`), and *AR Face Filter* (`840×540`)."],
        ["Act 7", "31.8 – 37.0 s", "`(02)` Blender 5.1 Avatar & Stack", "Showcases the custom rigged 20-bone 3D avatar alongside the 4-row technical capabilities matrix."],
        ["Act 8", "37.0 – 41.6 s", "`(01)` 09 Works Quad Matrix", "High-tempo 4-up simultaneous gameplay montage centered beneath the `09 SELECTED WORKS (2024–2026)` plaque."],
        ["Act 9", "41.6 – 46.8 s", "`(04)` Direct Transmission Outro", "Clean Swiss contact table (Vercel live URL, email, LinkedIn, NED University—phone number omitted for privacy) flanked by avatar & portrait frames."],
    ]
    add_styled_table(
        doc,
        "Table 7: Nine-Act Editorial Showreel Storyboard (46.8 s · 1920×1080 @ 30 fps · 10.81 MB)",
        ["Act", "Timestamp", "Title", "Visual & Editorial Architecture"],
        acts_rows,
        [0.58, 0.92, 1.75, 3.40],
        pad_v=46,
    )

    add_figure(
        doc,
        os.path.join(ASSETS_DIR, "fig_showreel_scenes.jpg"),
        "Figure 5: Selected composited frames from public/video/promo.mp4 — Act 4 Dual Engine Comparison (left) and Act 6 Triple Extended Reality Viewport (right).",
        width_in=6.45,
    )

    add_callout(
        doc,
        "Playback Smoothness & Browser Cache Busting",
        "In `src/portfolio/createPortfolioUI.js`, `#sn-promo-video` is configured with `preload=\"none\"` and versioned "
        "query parameters (`?v=20261120d`) on both `poster` and `source`. This guarantees zero initial video bandwidth "
        "on page load, prevents stale browser poster caching, and coordinates seamlessly with `projectScreens.setPaused(true)` "
        "and `appShell.audioButton.pause()` whenever the visitor presses Play."
    )

    # =========================================================================
    # SECTION 7: MODULE 4 — HYBRID RAG AI ASSISTANT (AHMAD.AI)
    # =========================================================================
    add_h1(doc, "7. Module 4 — Hybrid RAG AI Assistant (AHMAD.AI)", page_break=True)

    add_body(
        doc,
        "To let visitors and recruiters interrogate Syed Muhammad Ahmad's portfolio conversationally without risking "
        "LLM hallucinations, Module 4 implements a zero-database serverless **Hybrid Retrieval-Augmented Generation "
        "(RAG)** architecture across `scripts/ingest.mjs`, `api/_lib/retriever.js`, `api/_lib/gemini.js`, and `api/chat.js`."
    )

    add_figure(
        doc,
        os.path.join(ASSETS_DIR, "diag_rag_pipeline.png"),
        "Figure 6: End-to-End Hybrid RAG Pipeline — Phase 1 Offline Ingestion & Embedding (scripts/ingest.mjs) and Phase 2 Online Hybrid Retrieval, Grounding & Voice Response (api/chat.js).",
        width_in=6.55,
    )

    add_h2(doc, "7.1 Offline Document Ingestion & Structure-Aware Chunking")
    add_body(
        doc,
        "Executing `npm run ingest` parses three authoritative sources: `content/profile.json` (programmatically "
        "mapped into typed overview, skill-group, project, achievement, education, experience, and contact documents), "
        "`knowledge/SyedMuhammadAhmad_CV.pdf` (extracted cleanly via `unpdf`), and `knowledge/portfolio-details.md` "
        "(parsed with YAML frontmatter). The heading- and sentence-boundary chunker (`CHUNK_SIZE = 700` characters, "
        "`CHUNK_OVERLAP = 120` characters) splits **28 structured documents into 44 overlapping chunks**, prepending "
        "section headings so no chunk loses contextual provenance. Each chunk is embedded in batches of 50 via "
        "Google's `gemini-embedding-001` (`768` dimensions, `RETRIEVAL_DOCUMENT` task type), L2-normalized so cosine "
        "similarity reduces to a fast dot product, and serialized to `data/vector-index.json`."
    )

    add_h2(doc, "7.2 Hybrid Dense Vector + BM25 Fusion Retrieval")
    add_body(
        doc,
        "Pure dense embeddings occasionally miss exact acronyms or library names (`HDRP`, `SFML`, `QuadTrees`, `CEGA`, "
        "`Aerox ERP`), while pure lexical search misses paraphrased semantic queries. At runtime (`api/_lib/retriever.js`), "
        "`data/vector-index.json` is cached in serverless RAM alongside an in-memory BM25 inverted index (`k1 = 1.4`, "
        "`b = 0.75`, title tokens boosted `2×`). For every query (expanded with the previous user turn when shorter "
        "than 6 words to handle follow-ups like *\"tell me more about the second one\"*), hybrid relevance combines "
        "semantic and lexical evidence:"
    )

    add_code_block(
        doc,
        "Hybrid Fusion Scoring & Diversity Capping (api/_lib/retriever.js)",
        "dense      = dot(queryEmbedding, chunk.embedding)            // L2-normalized cosine sim\n"
        "sparseNorm = bm25Score(chunk, queryTokens) / maxBm25Score    // Normalized [0, 1]\n"
        "score      = 0.75 * dense + 0.25 * sparseNorm * Math.max(dense, 0.30)\n"
        "// Enforce per-source diversity: max 2 chunks per sourceId -> top k = 6 chunks"
    )

    add_h2(doc, "7.3 Grounded Generation, Anti-Hallucination & Resilience")
    add_bullet(doc, "**Strict System Prompt Grounding:** The top-6 chunks are injected inside `<sources>...</sources>` numbered `[1]`..`[6]`. The system prompt forbids inventing unverified personal facts, mandates inline bracketed citations (`[1]`, `[2]`), enforces prompt-injection resistance, and directs unknown personal questions to the contact form.")
    add_bullet(doc, "**Clickable Deep-Link Citations:** The backend extracts only citation indices actually referenced in the generated response (`answer.matchAll(/\\[(\\d+)\\]/g)`) and maps them to section metadata (`section`, `itemId`, `score`). Clicking a citation chip in the chat drawer scrolls smoothly to that exact portfolio section or opens the corresponding Project Case Study Modal.")
    add_bullet(doc, "**Multi-Model Resilience & Extractive Fallback:** `api/_lib/gemini.js` queries `gemini-3.7-flash` first with a 12-second timeout and automatically cascades through four fallback models (`gemini-3.6-flash`, `gemini-3.5-flash`, `gemini-3.8-flash`, `gemma-4-31b-it`). If the Gemini API is unreachable or unconfigured, `api/chat.js` falls back gracefully to an extractive BM25 responder guarded by `hasTopicMatch(query, results)`—preventing false-positive matches on unrelated topics (e.g., *\"favorite pizza topping\"*).")
    add_bullet(doc, "**Multilingual & Voice Interface:** Supports 9 selectable languages (`en`, `ur`, `ar`, `hi`, `fr`, `es`, `de`, `zh`, `tr`) plus automatic language detection (including Roman Urdu), Web Speech API voice dictation (`SpeechRecognition`), spoken readout (`speechSynthesis`), and real-time 3D avatar `Talk` + `MouthOpen` lip-sync.")

    # =========================================================================
    # SECTION 8: MODULE 5 — SECURED EMAIL & CONTACT SYSTEM
    # =========================================================================
    add_h1(doc, "8. Module 5 — Secured Email & Contact Communication System", page_break=True)

    add_body(
        doc,
        "Direct visitor communication is powered by an isomorphic validation architecture (`shared/validation.js`), "
        "HTTP security utilities (`api/_lib/http.js`), and the Vercel serverless endpoint (`api/contact.js`). Importing "
        "the exact same `validateContact()` and `escapeHtml()` functions on both browser and server guarantees zero "
        "drift between UI feedback and backend enforcement."
    )

    sec_rows = [
        ["Field Schema & Length Guards", "`shared/validation.js`", "Enforces `name` (2–80 chars, no `<` `>` or control chars), RFC 5322 `email` (≤254 chars), `subject` (3–120 chars), `message` (10–4000 chars, max 3 URLs)."],
        ["Silent Honeypot Trap", "`api/contact.js` (line 93)", "Hidden `website` field invisible to humans; if populated by a bot, the server logs the block and returns a silent HTTP `200` so bots do not adapt."],
        ["Minimum Fill-Time Guard", "`CONTACT_LIMITS.minFillTimeMs`", "Embedded `startedAt` timestamp verifies at least `3,000 ms` elapsed between form render and submission; instantaneous scripted posts are sinkholed."],
        ["Per-IP Sliding Rate Limiter", "`api/_lib/http.js`", "Caps submissions at `5` requests per `10 minutes` per client IP (`HTTP 429`), paired with `20/min` on `/api/chat`."],
        ["CORS Origin & XSS Escaping", "`isOriginAllowed()` + `escapeHtml()`", "Restricts cross-origin POST abuse and escapes all HTML entities (`&`, `<`, `>`, `\"`, `'`) before interpolating into email markup."],
        ["Resend Delivery & Relay Fallback", "`sendWithResend()` (`api/contact.js`)", "Delivers dark-styled HTML + plain-text emails with `reply_to` set to the visitor via Resend REST API; gracefully logs verified transmissions if `RESEND_API_KEY` is unconfigured."],
        ["Privacy Hardening", "`createPortfolioUI.js` & `video/`", "Personal phone number was removed across the Contact section, After Effects ExtendScript, and rendered showreel outro, retaining email, LinkedIn, Canva, and PDF CV."],
    ]
    add_styled_table(
        doc,
        "Table 8: Contact Communication Security Controls & Implementation Details",
        ["Security / Functional Layer", "Module", "Enforcement Behavior"],
        sec_rows,
        [1.65, 1.55, 3.45],
    )

    # =========================================================================
    # SECTION 9: PERFORMANCE ENGINEERING & OPTIMIZATION
    # =========================================================================
    add_h1(doc, "9. Performance Engineering & Cross-Device Optimization", page_break=True)

    add_body(
        doc,
        "Delivering a multi-pass WebGPU cyberpunk alley alongside high-resolution video media on both desktop "
        "workstations and constrained mobile GPUs requires strict frame-budget governance. Performance controls are "
        "centralized in `src/platform/performanceProfile.js`, `src/platform/adaptiveDpr.js`, `src/runtime/warmup.js`, "
        "and `vite.config.js`."
    )

    add_figure(
        doc,
        os.path.join(ASSETS_DIR, "diag_perf_bundle.png"),
        "Figure 7: Production Vite 6 Gzipped Transfer Footprint (left) and Static 3D Model, Audio & Faststart Showreel Disk Budgets (right).",
        width_in=6.55,
    )

    add_h2(doc, "9.1 Runtime GPU Budgets & Adaptive DPR Governor")
    add_bullet(doc, "**Half-Resolution Expensive Passes (`0.5×`):** Planar ground reflection, GTAO (`6` samples), emissive Bloom, and Lens Flare all execute at half screen resolution (`0.5×`), cutting fragment fill-rate by `75%` with virtually indistinguishable visual softness on wet reflections and glow.")
    add_bullet(doc, "**Adaptive DPR Controller (`adaptiveDpr.js`):** Starts capped at `1.5×` pixel ratio on desktop (`1.25×` on Apple mobile). Once the scene settles past boot (`adaptiveSampleGate.allow = true`), if sustained FPS falls below `50 FPS` across `2` consecutive measurement windows, DPR steps down cleanly to `0.85×` and fires `onForcedLow()`—shedding DoF, Lens Flare, and city video billboard decoding permanently for the session without oscillation.")
    add_bullet(doc, "**Safari & Mobile GPU Protections (`applyDevicePerformanceDefaults`):** Automatically disables lensflare, video billboards, and GTAO on phones/tablets, disables adaptive dynamic resize on Safari WebGPU, and enforces upfront shader compilation (`shouldCompileBeforeRenderLoop()`) on Safari to avoid concurrent pipeline-compile freezes.")
    add_bullet(doc, "**Zero-Hitch Startup Warmup (`src/runtime/warmup.js`):** Pre-compiles deferred WebGPU shader pipelines and executes initial shadow map baking before unlocking smooth interactive scrolling.")

    add_h2(doc, "9.2 Production Bundle Metrics & CDN Asset Strategy")
    perf_rows = [
        ["Main Application Entry (`index.js`)", "187.93 kB raw", "62.14 kB gzip", "Core app bootstrap, editorial UI, portfolio data, audio & walk controls"],
        ["Stylesheet (`index.css`)", "120.81 kB raw", "22.79 kB gzip", "Complete `samsy.ninja` dark/light editorial CSS + HUD & modal rules"],
        ["Three.js Engine (`vendor-three`)", "1,302.45 kB raw", "382.45 kB gzip", "Isolated long-term cacheable chunk (`three/webgpu` + `three/tsl` addons)"],
        ["Animation Engine (`vendor-gsap`)", "70.90 kB raw", "27.95 kB gzip", "GSAP 3.15 motion choreography split into its own browser cache chunk"],
        ["BVH Spatial Collision (`vendor-bvh`)", "49.00 kB raw", "16.18 kB gzip", "Accelerated mesh raycasting split from core application updates"],
        ["Draco & Basis WASM Decoders", "1,005.50 kB raw", "399.72 kB gzip", "On-demand geometry & KTX2 texture transcoding (`public/libs/`)"],
        ["3D Scene Models (`public/models/`)", "12.21 MB total", "CDN Immutable", "`cyberpunk_compressed` (4.64 MB), `quadra` (2.61 MB), `avatar` (2.53 MB), `plane` (2.42 MB)"],
        ["Showreel (`public/video/promo.mp4`)", "10.81 MB total", "`preload=\"none\"`", "1080p@30fps H.264 `+faststart`, zero download until user clicks Play"],
    ]
    add_styled_table(
        doc,
        "Table 9: Verified Vite 6 Production Build & Static Asset Footprint (npm run build)",
        ["Artifact / Chunk", "Uncompressed", "Transfer / Cache", "Optimization Strategy"],
        perf_rows,
        [1.80, 1.05, 1.15, 2.65],
        pad_v=52,
    )

    # =========================================================================
    # SECTION 10: TESTING, VERIFICATION & AUDIT
    # =========================================================================
    add_h1(doc, "10. Testing, Verification & Quality Assurance", page_break=True)

    add_body(
        doc,
        "Every major subsystem is backed by repeatable command-line verification scripts and production build gates. "
        "Below are the verified results executed directly against the final codebase (`November 21, 2026`)."
    )

    add_h2(doc, "10.1 Automated RAG Retrieval & Media Integrity Suite (npm run test:rag)")
    add_code_block(
        doc,
        "Verified Execution Log — node scripts/test-rag.mjs (Exit Code 0)",
        "=== 1. Verifying RAG Vector Index ===\n"
        "Owner: Syed Muhammad Ahmad | Chunks: 44 | Has Embeddings: true\n"
        "✓ \"Chrono Rebellion Unity HDRP\"           -> [Project — Chrono Rebellion] (score: 1.000)\n"
        "✓ \"Behind the Smile Global Game Jam 2026\" -> [Project — Behind the Smile] (score: 1.000)\n"
        "✓ \"Paper Plane Dash Unreal Engine 5\"      -> [Project — Paper Plane Dash] (score: 1.000)\n"
        "✓ \"Pac-Man C++ SFML QuadTrees\"            -> [Project — Pac-Man] (score: 1.000)\n"
        "✓ \"NED University Gaming and Animation\"   -> [Education — BS CS & IT ...] (score: 1.000)\n"
        "✓ \"Aerox ERP Game Development Intern\"     -> [Experience — Game Dev Intern] (score: 1.000)\n\n"
        "=== 2. Verifying Public Media Assets Referenced in profile.json ===\n"
        "✓ Verified all 29 public 3D models, videos, posters, audio tracks, and CV assets exist on disk."
    )

    add_h2(doc, "10.2 Serverless RAG & Contact Security Verification (npm run test:api)")
    add_code_block(
        doc,
        "Verified Execution Log — node scripts/test-api.mjs (Exit Code 0)",
        "=== 1. Grounded Question (POST /api/chat) ===\n"
        "Status: 200 | Citations: [1] Profile overview, [2] Detailed Portfolio KB, [3] Skills — Game Engines\n\n"
        "=== 2. Anti-Hallucination Guard (\"favorite pizza topping and passport number?\") ===\n"
        "Answer: \"I don't have that information in Syed Muhammad Ahmad's portfolio documents...\"\n\n"
        "=== 3. Invalid Contact Payload Rejection (POST /api/contact) ===\n"
        "Status: 422 | Errors returned for name (<2), email (invalid), subject (<3), message (<10)\n\n"
        "=== 4. Valid Contact Submission ===\n"
        "Status: 200 | { ok: true, id: \"relay_...\", mode: \"logged\" } -> All RAG & Contact API tests passed!"
    )

    add_h2(doc, "10.3 Comprehensive Codebase Audit & Resolved Engineering Issues")
    audit_rows = [
        ["Windows WebGPU Adapter Warning", "`createRenderer.js`", "Omitted ignored `powerPreference` on Windows Chromium to eliminate startup console warnings."],
        ["Promo & Background Audio Overlap", "`createPortfolioUI.js`, `createAudioButton.js`", "Auto-paused background music when `#sn-promo-video` plays and guarded `pointerdown`/`focus` auto-resume."],
        ["Video Lag During Showreel Playback", "`createProjectScreens.js`, `promo.mp4`", "Added `setPaused(true)` to pause 8 background 3D video decoders and re-encoded `promo.mp4` (`10.8 MB`, `+faststart`)."],
        ["Unobstructed 3D Avatar Gestures", "`createPortfolioUI.js`, `portfolio.css`", "Moved 3D avatar gesture & 1st/3rd-POV buttons into a dedicated floating bar inside Full-Screen 3D World mode."],
        ["Scroll & Hover Navigation Glitch", "`createPortfolioUI.js`", "Removed custom wheel `e.preventDefault()` hijacking and background white-out hover flashes for native smooth scrolling."],
        ["Extractive RAG False Positives", "`api/chat.js`", "Added `hasTopicMatch(query, results)` filtering owner-name tokens so out-of-scope queries cleanly refuse in fallback mode."],
        ["Stale Browser Video Cover Cache", "`createPortfolioUI.js`, `make_hud_overlays.py`", "Redesigned 2×2 editorial showreel cover, switched `<video>` to `preload=\"none\"`, and added `?v=20261120d` cache busting."],
        ["Privacy Cleanup (Phone Removal)", "`createPortfolioUI.js`, `make_hud_overlays.py`, `build_promo.jsx`", "Removed personal phone number across web Contact UI, After Effects script, and rendered showreel outro."],
    ]
    add_styled_table(
        doc,
        "Table 10: Comprehensive Codebase Audit Findings & Verified Resolutions",
        ["Issue Identified", "Affected Modules", "Verified Resolution"],
        audit_rows,
        [1.75, 1.75, 3.15],
        pad_v=48,
    )

    # =========================================================================
    # SECTION 11: CLOUD DEPLOYMENT, CI/CD & PRODUCTION INFRASTRUCTURE
    # =========================================================================
    add_h1(doc, "11. Cloud Deployment, CI/CD & Production Infrastructure", page_break=True)

    add_body(
        doc,
        "The portfolio is deployed in production on **Vercel** at "
        "**`https://syed-muhammad-ahmad-portfolio.vercel.app`** (Project ID: `prj_s2ZtnC5JouxsRuXvrXJpFjFTU1da`) "
        "and linked directly to the GitHub repository **`akkka-code/3D-Portfolio-Website`**. Every `git push` to "
        "the primary branch automatically triggers a Vite 6 production build, serverless function packaging, and "
        "atomic edge rollout with zero downtime."
    )

    add_h2(doc, "11.1 Serverless & CDN Configuration (vercel.json)")
    add_bullet(doc, "**Serverless Bundling:** `api/chat.js` runs with a `30s` execution budget and explicitly declares `\"includeFiles\": \"data/vector-index.json\"` so the 44-chunk vector index is co-located inside the Lambda bundle with sub-millisecond disk reads and zero external vector database cost.")
    add_bullet(doc, "**Contact Function:** `api/contact.js` executes with a `15s` ceiling and automatic JSON body parsing.")
    add_bullet(doc, "**Edge Cache Headers:** Immutable 1-year caching (`public, max-age=31536000, immutable`) is enforced for `/models/*`, `/fonts/*`, and `/textures/*`, while `/video/*` uses `max-age=604800, stale-while-revalidate=86400` so updated showreel assets propagate cleanly.")
    add_bullet(doc, "**HTTP Security Headers:** Global response headers enforce `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, and `Referrer-Policy: strict-origin-when-cross-origin`.")
    add_bullet(doc, "**Telemetry:** `@vercel/analytics` (`inject()`) tracks visitor page views safely without blocking rendering.")

    env_rows = [
        ["`GEMINI_API_KEY`", "Optional (Recommended)", "Enables live 768-d query embeddings and Gemini Flash generation in `/api/chat`; absent → BM25 fallback."],
        ["`GEMINI_CHAT_MODEL`", "Configured (`gemini-3.7-flash`)", "Primary Gemini LLM model identifier; cascades automatically across 4 fallback models on demand spikes."],
        ["`GEMINI_EMBED_MODEL`", "Default (`gemini-embedding-001`)", "768-dimensional embedding model used during both `npm run ingest` and query embedding."],
        ["`CONTACT_TO_EMAIL`", "Configured (`ahmedakka765@gmail.com`)", "Destination inbox receiving formatted contact form submissions from `/api/contact`."],
        ["`RESEND_API_KEY`", "Optional (Production Email)", "Resend REST API token (`re_...`) for live email delivery; absent → verified server-side relay logging."],
        ["`CONTACT_FROM_EMAIL`", "Default (`onboarding@resend.dev`)", "Verified sender identity displayed on outbound portfolio contact emails."],
    ]
    add_styled_table(
        doc,
        "Table 11: Production Environment Variables & Cloud Configuration",
        ["Variable Name", "Production Status", "Purpose & Fallback Behavior"],
        env_rows,
        [1.75, 1.85, 3.05],
    )

    # =========================================================================
    # SECTION 12: CHALLENGES, FUTURE WORK & CONCLUSION
    # =========================================================================
    add_h1(doc, "12. Challenges Faced, Future Work & Conclusion", page_break=True)

    add_h2(doc, "12.1 Key Engineering Challenges & Technical Resolutions")
    add_bullet(doc, "**WebGPU Attachment Conflicts in Reflective Shaders:** Using Three.js's high-level TSL `reflector()` inside a multi-pass `RenderPipeline` caused `TextureBinding | RenderAttachment` validation errors under WebGPU. Replacing it with a manual oblique mirror camera writing to an independent half-resolution `HalfFloat` render target eliminated the conflict and improved GPU frame pacing.")
    add_bullet(doc, "**Balancing 3D Immersion with Recruiter Usability:** Early iterations hid portfolio projects behind 3D walk triggers or obscured the 3D avatar behind modal drawers. Restructuring the frontend into two cleanly separated modes—a high-contrast `samsy.ninja` Editorial Index Mode with scroll-choreographed WebGPU backdrops and a dedicated Full-Screen 3D World Exploration Mode with unobstructed avatar controls—satisfied both casual recruiters and technical graphics evaluators.")
    add_bullet(doc, "**Simultaneous Multi-Stream Video & Audio Contention:** Decoding 8 in-world gameplay kiosk textures while playing a 1080p showreel caused frame drops and music overlap. Implementing centralized `projectScreens.setPaused()` coordination, `preload=\"none\"` faststart MP4 encoding, and bidirectional audio-button ducking resolved both issues cleanly.")
    add_bullet(doc, "**Zero-Cost Grounded AI Without External Vector Databases:** Hosting external vector databases adds latency, cold starts, and ongoing fees. Pre-computing L2-normalized 768-d embeddings into a compact `data/vector-index.json` file bundled directly into `/api/chat` achieved sub-10ms hybrid retrieval with 100% top-1 accuracy across test benchmarks.")

    add_h2(doc, "12.2 Future Enhancements Roadmap")
    add_bullet(doc, "**WebAudio FFT-Reactive TSL Shaders:** Bind real-time frequency spectrum bands from `funky-cyber-groove.mp3` to TSL uniforms modulating neon signage emissive pulse and puddle reflection intensity.")
    add_bullet(doc, "**Interactive In-Alley Kiosk Raycast Selection:** Enable clicking any of the 8 illuminated 3D alley kiosks while in Third-Person Walk Mode to open its Case Study Modal directly from the 3D viewport.")
    add_bullet(doc, "**Dynamic Weather State Machine:** Add TSL uniform blending between Heavy Storm, Neon Drizzle, and Clear Midnight states with synchronized cloud density and raindrop compute counts.")
    add_bullet(doc, "**Automated Visual Regression CI:** Integrate headless Chromium WebGPU Playwright snapshots into GitHub Actions to verify both Editorial and 3D render outputs on every pull request.")

    add_h2(doc, "12.3 Conclusion")
    add_body(
        doc,
        "The **Interactive 3D WebGPU Portfolio** successfully demonstrates the convergence of modern real-time "
        "computer graphics, procedural 3D character art, editorial motion design, retrieval-augmented artificial "
        "intelligence, and hardened cloud deployment. By pairing pure Three.js TSL WebGPU shaders (GPU collision "
        "rain, half-res planar wet reflections, UV1 vehicle droplets, GTAO/Bloom/SMAA post-processing) with a "
        "reproducible 20-bone Blender 5.1 avatar, a cohesive 9-act 1080p editorial showreel, and a grounded hybrid "
        "RAG assistant (`AHMAD.AI`), the platform serves both as a production-deployed professional portfolio for "
        "**Syed Muhammad Ahmad (AKKA)** and as a complete reference engineering implementation for next-generation "
        "Web3D applications."
    )

    # =========================================================================
    # APPENDIX A: DEVELOPER COMMAND & RUNTIME REFERENCE
    # =========================================================================
    add_h1(doc, "Appendix A — Developer Command & Runtime Reference", page_break=True)

    cmd_rows = [
        ["`npm run dev` / `npm run dev:https`", "Starts Vite 6 development server with local `/api/chat` and `/api/contact` middleware (`dev:https` enables WebGPU secure context on LAN)."],
        ["`npm run build` / `npm run preview`", "Compiles ES2022 production bundle with vendor chunk splitting (`dist/`) and launches local production preview."],
        ["`npm run ingest`", "Parses `content/profile.json` + `knowledge/` into 44 chunks, computes 768-d Gemini embeddings, and writes `data/vector-index.json`."],
        ["`npm run test:rag`", "Verifies all 44 vector index chunks, 6 benchmark queries (score `1.000`), and presence of all 29 public media assets on disk."],
        ["`npm run test:api`", "Executes end-to-end tests against `/api/chat` (grounded + anti-hallucination) and `/api/contact` (422 validation + 200 delivery)."],
        ["`npm run deploy`", "Deploys production build and serverless API functions to Vercel (`https://syed-muhammad-ahmad-portfolio.vercel.app`)."],
        ["`blender.exe -b --factory-startup --python blender\\build_avatar.py`", "Deterministically rebuilds `blender/avatar.blend`, `public/models/avatar.glb`, and `blender/avatar_preview.png`."],
        ["`node scripts/render-promo-video.mjs`", "Regenerates 9 editorial overlays (`make_hud_overlays.py`), composites all 9 acts with soundtrack, and outputs `promo.mp4` + `promo-poster.jpg`."],
        ["`window.__app.perf.printHelp()`", "In-browser DevTools API allowing live A/B toggling of GTAO, Bloom, Lensflare, SMAA, Planar Reflection, and Adaptive DPR."],
    ]
    add_styled_table(
        doc,
        "Table 12: Complete Build, Asset Pipeline, Verification & DevTools Command Reference",
        ["Command / Runtime API", "Description & Output"],
        cmd_rows,
        [2.70, 3.95],
    )

    os.makedirs(os.path.dirname(OUT_DOCX), exist_ok=True)
    doc.save(OUT_DOCX)
    print(f"Successfully generated Word report: {OUT_DOCX} ({os.path.getsize(OUT_DOCX) / 1024:.1f} KB)")


if __name__ == "__main__":
    build_report()
