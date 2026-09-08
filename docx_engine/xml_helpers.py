"""
Low-level OOXML helpers for writing precisely-formatted Word runs/cells.
python-docx's high-level API cannot control every formatting detail
the reference documents need (exact spacing, run-level bold/size on
existing cell content, etc.) so these build/edit XML elements directly.

Private (_-prefixed) functions are the low-level primitives. Public
functions below are the ones docx_engine/annexure1.py and labour.py
actually call (via `xh.something(...)`).

Font sizes below are in half-points (Word's <w:sz> unit) — size=24
means 12pt, size=22 means 11pt, size=20 means 10pt, etc.
"""
import docx
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


def _make_run(text, bold=False, size=None, underline=False,
              font_ascii="Calibri", color=None):
    """Build a <w:r> element with optional formatting."""
    r = OxmlElement('w:r')
    rpr = OxmlElement('w:rPr')
    if bold:
        rpr.append(OxmlElement('w:b'))
        rpr.append(OxmlElement('w:bCs'))
    if font_ascii:
        rf = OxmlElement('w:rFonts')
        rf.set(qn('w:ascii'), font_ascii)
        rf.set(qn('w:hAnsi'), font_ascii)
        rf.set(qn('w:cs'), font_ascii)
        rpr.append(rf)
    if color:
        c = OxmlElement('w:color')
        c.set(qn('w:val'), color)
        rpr.append(c)
    if size:
        sz = OxmlElement('w:sz')
        sz.set(qn('w:val'), str(size))
        rpr.append(sz)
        szcs = OxmlElement('w:szCs')
        szcs.set(qn('w:val'), str(size))
        rpr.append(szcs)
    if underline:
        u = OxmlElement('w:u')
        u.set(qn('w:val'), 'single')
        rpr.append(u)
    r.append(rpr)
    t = OxmlElement('w:t')
    t.text = text
    if text and (text[0] == ' ' or text[-1] == ' '):
        t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    r.append(t)
    return r


def _clear_para_runs(para):
    """Remove all <w:r> children from a paragraph."""
    for r_elem in para._p.findall(qn('w:r')):
        para._p.remove(r_elem)


def _set_para_spacing(para, after="0", line="240", line_rule="auto"):
    """Add/replace <w:spacing> inside <w:pPr>."""
    ppr = para._p.find(qn('w:pPr'))
    if ppr is None:
        ppr = OxmlElement('w:pPr')
        para._p.insert(0, ppr)
    sp = ppr.find(qn('w:spacing'))
    if sp is None:
        sp = OxmlElement('w:spacing')
        ppr.append(sp)
    sp.set(qn('w:after'), after)
    sp.set(qn('w:line'), line)
    sp.set(qn('w:lineRule'), line_rule)


def _set_cell_run(cell, text, bold=False, size=None, spacing_after="0",
                  spacing_line="240", font_ascii="Calibri", color="000000"):
    """
    Replace cell content with a single run.
    Applies spacing and font size to both pPr and the run itself
    (matching the exact XML pattern of the correct template).
    """
    para = cell.paragraphs[0]
    _clear_para_runs(para)
    _set_para_spacing(para, after=spacing_after, line=spacing_line)

    # Also write rPr into pPr (paragraph-mark formatting) so spacing is correct
    ppr = para._p.find(qn('w:pPr'))
    ppr_rpr = ppr.find(qn('w:rPr'))
    if ppr_rpr is None:
        ppr_rpr = OxmlElement('w:rPr')
        ppr.append(ppr_rpr)
    # Clear and rebuild pPr rPr
    for child in list(ppr_rpr):
        ppr_rpr.remove(child)
    if font_ascii:
        rf = OxmlElement('w:rFonts')
        rf.set(qn('w:ascii'), font_ascii)
        rf.set(qn('w:eastAsia'), 'Times New Roman')
        rf.set(qn('w:hAnsi'), font_ascii)
        rf.set(qn('w:cs'), font_ascii)
        ppr_rpr.append(rf)
    if color:
        c = OxmlElement('w:color'); c.set(qn('w:val'), color); ppr_rpr.append(c)
    if size:
        sz = OxmlElement('w:sz'); sz.set(qn('w:val'), str(size)); ppr_rpr.append(sz)
        szcs = OxmlElement('w:szCs'); szcs.set(qn('w:val'), str(size)); ppr_rpr.append(szcs)

    run = _make_run(text, bold=bold, size=size,
                    font_ascii=font_ascii, color=color)
    para._p.append(run)


def _set_alloc_amount_cell(cell, text, size=22):
    """
    Set allocation-table amount cell, right-aligned.
    size=22 -> 11pt (was 18 -> 9pt).
    """
    para = cell.paragraphs[0]
    _clear_para_runs(para)
    # Set right alignment
    ppr = para._p.find(qn('w:pPr'))
    if ppr is None:
        ppr = OxmlElement('w:pPr')
        para._p.insert(0, ppr)
    jc = ppr.find(qn('w:jc'))
    if jc is None:
        jc = OxmlElement('w:jc')
        ppr.append(jc)
    jc.set(qn('w:val'), 'right')
    # Plain run with given size
    run = _make_run(text, size=size, font_ascii=None)
    para._p.append(run)


def _right_align_cell(cell):
    """Add right-alignment to every paragraph of a cell."""
    for para in cell.paragraphs:
        ppr = para._p.find(qn('w:pPr'))
        if ppr is None:
            ppr = OxmlElement('w:pPr')
            para._p.insert(0, ppr)
        jc = ppr.find(qn('w:jc'))
        if jc is None:
            jc = OxmlElement('w:jc')
            ppr.append(jc)
        jc.set(qn('w:val'), 'right')


# ─────────────────────────────────────────────────────────────
# PUBLIC API — these are what docx_engine/annexure1.py and
# docx_engine/labour.py actually call via `xh.something(...)`.
# ─────────────────────────────────────────────────────────────

def clear_para_runs(para):
    """Public alias — remove all runs from a paragraph."""
    _clear_para_runs(para)


def append_run(para, text, bold=False, size=None, font_ascii="Calibri", color=None):
    """Append a new formatted run to a paragraph (does not clear existing runs)."""
    run = _make_run(text, bold=bold, size=size, font_ascii=font_ascii, color=color)
    para._p.append(run)


def set_para_spacing(para, after="0", line="240", line_rule="auto"):
    """Public alias — set paragraph spacing."""
    _set_para_spacing(para, after=after, line=line, line_rule=line_rule)


def set_cell_run(cell, text, bold=False, size=None, spacing_after="0",
                 spacing_line="240", font_ascii="Calibri", color="000000"):
    """Public alias — replace cell content with a single formatted run."""
    _set_cell_run(cell, text, bold=bold, size=size, spacing_after=spacing_after,
                 spacing_line=spacing_line, font_ascii=font_ascii, color=color)


def set_alloc_amount_cell(cell, text, size=22):
    """Public alias — nested allocation-table Amount cell (11pt, right-aligned)."""
    _set_alloc_amount_cell(cell, text, size=size)


def set_alloc_text_cell(cell, text, size=22, bold=False):
    """Nested allocation-table Sl.No / Allocation text cell — no alignment
    change (keeps whatever the template already had), just font size."""
    para = cell.paragraphs[0]
    _clear_para_runs(para)
    run = _make_run(text, bold=bold, size=size)
    para._p.append(run)


def right_align_cell(cell):
    """Public alias — right-align every paragraph in a cell."""
    _right_align_cell(cell)


def set_bold_right_cell(cell, text, size=20):
    """Replace cell content with a single bold, right-aligned run.
    Used for balance-matrix amounts (Opening/Closing Balance, Sanctioned Amount)."""
    para = cell.paragraphs[0]
    _clear_para_runs(para)
    run = _make_run(text, bold=True, size=size)
    para._p.append(run)
    _right_align_cell(cell)


def set_summary_table_cell(cell, text, bold=False, size=20):
    """Replace cell content in the 7-column voucher summary table
    (date / items count / amount columns), right-aligned."""
    para = cell.paragraphs[0]
    _clear_para_runs(para)
    run = _make_run(text, bold=bold, size=size)
    para._p.append(run)
    _right_align_cell(cell)


def set_ledger_date_cell(cell, text, size=24):
    """G.I. Ledger table (page 2) date column — 12pt, not bold,
    alignment left as the template default."""
    para = cell.paragraphs[0]
    _clear_para_runs(para)
    run = _make_run(text, bold=False, size=size)
    para._p.append(run)


def set_ledger_amount_cell(cell, text, size=24):
    """G.I. Ledger table (page 2) amount column — 12pt, bold, right-aligned."""
    para = cell.paragraphs[0]
    _clear_para_runs(para)
    run = _make_run(text, bold=True, size=size)
    para._p.append(run)
    _right_align_cell(cell)


def fmt_items(items):
    """Format an item count as a two-digit string ('5' -> '05'),
    matching the voucher-number formatting style used elsewhere in the form."""
    try:
        n = int(items)
    except (TypeError, ValueError):
        return str(items)
    return f"{n:02d}"


def format_total_row_cells(row, pt_size=12, sz_val=None):
    """Bold every cell in a TOTAL row and set its font size (in points)."""
    for cell in row.cells:
        for para in cell.paragraphs:
            if not para.runs and para.text:
                para.add_run(para.text)
            for run in para.runs:
                run.font.bold = True
                run.font.size = docx.shared.Pt(pt_size)