"""
Annexure-1 (master imprest bill) generation engine.

Populates the ANNEXURE_TEMPLATE.docx by locating specific anchor text
in its paragraphs/tables and replacing/appending runs — see
core/validation.py for the anchor list this template must contain.

Station-specific static text (station name, division, officer name,
phone numbers, ATM card number) is left untouched — it's already
correct in the template itself, so this engine only fills in the
month-to-month variable data (dates, amounts, voucher details).
"""
import docx

from core.dates import get_days_in_month
from core.num_to_words import amount_in_words
from docx_engine import xml_helpers as xh
from io import BytesIO


def generate_annexure_1(template_path, month, year,
                        op_bal, atm_recoup, cash_total,
                        dev_total, tha_total, tot_exp, cl_bal,
                        sanc_amt, v1_amt, v2_amt, v1_date, v2_date,
                        v1_items=0, v2_items=0, num_vouchers=3,
                        has_stationery=False):

    doc = docx.Document(template_path)
    days, m_idx = get_days_in_month(month, year)
    s_date   = f"01/{m_idx:02d}/{year}"
    e_date   = f"{days}/{m_idx:02d}/{year}"
    next_m   = 1 if m_idx == 12 else m_idx + 1
    next_y   = int(year) + 1 if m_idx == 12 else year
    next_date = f"01/{next_m:02d}/{next_y}"
    l_total  = dev_total + tha_total

    # ── 1. PARAGRAPH REPLACEMENTS ────────────────────────────
    for p in doc.paragraphs:
        txt = p.text

        if "Date:" in txt and "THROUGH" not in txt and "Dated:" not in txt:
            p.text = ("\t\t\t\t\t\t\t\t\t\t\t  Date:" + e_date)

        elif "Sub : Recoupment" in txt or ("Sub:" in txt and "Recoupment" in txt):
            p.text = f"\t\tSub: Recoupment of imprest bill for the period {s_date} to {e_date}"

        # ── Item 14: Vr. No. line ──
        elif ("14. Vr. No." in txt) or ("Vr. No.01" in txt) or \
             ("14." in txt and "Vr. No." in txt and "Date" in txt):
            xh.clear_para_runs(p)
            xh.append_run(p, "14. ",    bold=False, size=16)
            xh.append_run(p, "Vr. No.", bold=False, size=20)
            xh.append_run(p, "01",      bold=True,  size=20)
            xh.append_run(p, " ",       bold=True,  size=20)
            xh.append_run(p, "Date ",   bold=False, size=20)
            xh.append_run(p, v1_date,   bold=True,  size=20)
            xh.append_run(p, ",",       bold=True,  size=20)
            xh.append_run(p, "Vr. No.", bold=False, size=20)
            xh.append_run(p, "02",      bold=True,  size=20)
            xh.append_run(p, " ",       bold=True,  size=20)
            xh.append_run(p, "Date",    bold=False, size=20)
            xh.append_run(p, f" {v2_date if (v2_amt and v2_date) else e_date}", bold=True, size=20)
            xh.append_run(p, " ,Vr.No ", bold=False, size=20)
            xh.append_run(p, "03",      bold=True,  size=20)
            xh.append_run(p, " Date ",  bold=False, size=20)
            xh.append_run(p, e_date,    bold=True,  size=20)
            if num_vouchers == 4:
                xh.append_run(p, " ,Vr.No ", bold=False, size=20)
                xh.append_run(p, "04",       bold=True,  size=20)
                xh.append_run(p, " Date ",   bold=False, size=20)
                xh.append_run(p, e_date,     bold=True,  size=20)

        # ── "Accepted for Rs. /-(...)" paragraph ──
        elif "Accepted for Rs." in txt and "14." not in txt:
            xh.clear_para_runs(p)
            words = amount_in_words(tot_exp)
            xh.append_run(p, "Accepted for Rs. ", bold=False, size=20)
            xh.append_run(p, f"{tot_exp}/-",      bold=True,  size=20)
            xh.append_run(p, words,               bold=True,  size=20)

        elif "For the month of" in txt:
            p.text = f"For the month of  {month}  {year}"

    # ── 2. TABLE ENGINE ──────────────────────────────────────
    for t_idx, table in enumerate(doc.tables):
        for r_idx, row in enumerate(table.rows):
            texts    = [c.text.strip() for c in row.cells]
            full_txt = " ".join(texts)

            # TABLE 0: Balance matrix
            if "Opening Balance" in full_txt and "Now recoupment" in full_txt \
                    and len(row.cells) >= 4:
                row.cells[0].text = f"Opening Balance as on {s_date}"
                xh.set_bold_right_cell(row.cells[1], str(op_bal))
                row.cells[2].text = f"Now recoupment Bill No. NIL,\nDated: {e_date}"
                xh.set_bold_right_cell(row.cells[3], str(tot_exp))

            elif "Last recoupment" in full_txt and "Closing" not in full_txt \
                    and len(row.cells) >= 2:
                row.cells[0].text = f"Last recoupment Bill No.NIL Dated {month} {year}"
                xh.set_bold_right_cell(row.cells[1], str(atm_recoup))

            elif "Closing Balance" in full_txt and len(row.cells) >= 4:
                row.cells[2].text = f"Closing Balance as on {e_date}"
                xh.set_bold_right_cell(row.cells[3], str(cl_bal))

            elif "Sanctioned Amount" in full_txt and len(row.cells) >= 4:
                xh.set_bold_right_cell(row.cells[1], str(sanc_amt))
                xh.set_bold_right_cell(row.cells[3], str(sanc_amt))

            # TABLE 2: 7-column summary — match by Sl.No (works for 3V & 4V)
            # Date of payment (cells[1]) is now bold per request.
            elif "09.295" in full_txt and len(row.cells) == 7:
                sl = texts[0]

                if sl in ("01", "1"):
                    xh.set_summary_table_cell(row.cells[1], v1_date, bold=True)
                    xh.set_summary_table_cell(row.cells[5], xh.fmt_items(v1_items), bold=True)
                    xh.set_summary_table_cell(row.cells[6], str(v1_amt), bold=True)

                elif sl in ("02", "2"):
                    if num_vouchers == 3:
                        xh.set_summary_table_cell(row.cells[1], e_date, bold=True)
                        xh.set_summary_table_cell(row.cells[6], str(dev_total), bold=True)
                    else:
                        xh.set_summary_table_cell(row.cells[1], v2_date, bold=True)
                        xh.set_summary_table_cell(row.cells[5], xh.fmt_items(v2_items), bold=True)
                        xh.set_summary_table_cell(row.cells[6], str(v2_amt), bold=True)

                elif sl in ("03", "3"):
                    if num_vouchers == 3:
                        xh.set_summary_table_cell(row.cells[1], e_date, bold=True)
                        xh.set_summary_table_cell(row.cells[6], str(tha_total), bold=True)
                    else:
                        xh.set_summary_table_cell(row.cells[1], e_date, bold=True)
                        xh.set_summary_table_cell(row.cells[6], str(dev_total), bold=True)

                elif sl in ("04", "4"):
                    xh.set_summary_table_cell(row.cells[1], e_date, bold=True)
                    xh.set_summary_table_cell(row.cells[6], str(tha_total), bold=True)

                # Set 10pt on all non-date/non-amount cells in this data row
                for ci, cell in enumerate(row.cells):
                    if ci not in (1, 5, 6):
                        for para in cell.paragraphs:
                            for run in para.runs:
                                run.font.size = docx.shared.Pt(10)

            elif texts[0] == "TOTAL" and len(row.cells) == 7:
                row.cells[6].text = str(tot_exp)
                xh.format_total_row_cells(row, pt_size=12, sz_val='20')
                xh.right_align_cell(row.cells[6])

            # TABLE 3: G.I. Ledger (page 2) — dates 12pt, amounts 12pt bold
            elif "OPENING BALANCE" in full_txt and len(row.cells) >= 6:
                xh.set_ledger_date_cell(row.cells[0], s_date)
                xh.set_ledger_amount_cell(row.cells[3], str(op_bal))

            elif "Amount received through ATM" in full_txt and len(row.cells) >= 4:
                xh.set_ledger_amount_cell(row.cells[3], str(atm_recoup))

            elif "Consumable Items" in full_txt and len(row.cells) >= 6:
                vno = texts[1]
                if vno in ("1", "01"):
                    xh.set_ledger_date_cell(row.cells[0], v1_date)
                    xh.set_ledger_amount_cell(row.cells[5], str(v1_amt))
                elif vno in ("2", "02") and num_vouchers == 4:
                    xh.set_ledger_date_cell(row.cells[0], v2_date)
                    xh.set_ledger_amount_cell(row.cells[5], str(v2_amt))

            # TABLE 3 Labour rows — 3V: vouchers 2&3; 4V: vouchers 3&4
            elif "Amount paid to cleaning labour" in full_txt and len(row.cells) >= 6:
                vno = texts[1]
                if num_vouchers == 3:
                    if vno in ("2", "02"):
                        xh.set_ledger_date_cell(row.cells[0], e_date)
                        xh.set_ledger_amount_cell(row.cells[5], str(dev_total))
                    elif vno in ("3", "03"):
                        xh.set_ledger_date_cell(row.cells[0], e_date)
                        xh.set_ledger_amount_cell(row.cells[5], str(tha_total))
                else:
                    if vno in ("3", "03"):
                        xh.set_ledger_date_cell(row.cells[0], e_date)
                        xh.set_ledger_amount_cell(row.cells[5], str(dev_total))
                    elif vno in ("4", "04"):
                        xh.set_ledger_date_cell(row.cells[0], e_date)
                        xh.set_ledger_amount_cell(row.cells[5], str(tha_total))

            elif "TOTAL" in full_txt and "OPENING" not in full_txt \
                    and len(row.cells) == 8:
                row.cells[3].text = str(sanc_amt)
                row.cells[5].text = str(tot_exp)
                xh.format_total_row_cells(row, pt_size=14, sz_val='22')
                xh.right_align_cell(row.cells[3])
                xh.right_align_cell(row.cells[5])

            # TABLE 4: Certified section
            elif "BALANCE AMOUNT ON HAND" in full_txt:
                xh.set_cell_run(
                    row.cells[0],
                    f"BALANCE AMOUNT ON HAND AS ON {e_date} IS RS. {cl_bal}/-",
                    size=28, spacing_after="0", spacing_line="240"
                )

            elif "2. Certified that the amount paid" in full_txt:
                cell = row.cells[0]
                para = cell.paragraphs[0]
                xh.clear_para_runs(para)
                xh.set_para_spacing(para, after="0", line="240")
                xh.append_run(para, "2. Certified that the amount paid and voucher accepted for Rs. ",
                            bold=False, size=28)
                xh.append_run(para, f"{tot_exp}/-", bold=True, size=28)

            elif "3. Certified that the amount on hand" in full_txt:
                cell = row.cells[0]
                para = cell.paragraphs[0]
                xh.clear_para_runs(para)
                xh.set_para_spacing(para, after="0", line="240")
                xh.append_run(para, f"3. Certified that the amount on hand as on {next_date} is Rs. ",
                            bold=False, size=28)
                xh.append_run(para, f"{cl_bal}/-", bold=True, size=28)

    # ── TABLE 4 — words rows (rows 3 and 5) ─────────────────
    if len(doc.tables) >= 5:
        t4 = doc.tables[4]
        if len(t4.rows) > 5:
            xh.set_cell_run(
                t4.rows[3].cells[0],
                amount_in_words(tot_exp),
                size=28, bold=True, spacing_after="0", spacing_line="240"
            )
            xh.set_cell_run(
                t4.rows[5].cells[0],
                amount_in_words(cl_bal),
                size=28, bold=True, spacing_after="0", spacing_line="240"
            )

    # ── 3. NESTED ALLOCATION TABLE — Sl.No / Allocation / Amount now 11pt ──
    if len(doc.tables) > 1:
        alloc_wrapper = doc.tables[1]
        if alloc_wrapper.rows and alloc_wrapper.rows[0].cells:
            cell = alloc_wrapper.rows[0].cells[0]
            if cell.tables:
                nested = cell.tables[0]
                for row in nested.rows:
                    texts    = [c.text.strip() for c in row.cells]
                    full_txt = " ".join(texts)
                    if texts[0] in ("01", "1") and "09.295" in full_txt:
                        xh.set_alloc_text_cell(row.cells[0], texts[0], size=22)
                        xh.set_alloc_amount_cell(row.cells[2], str(cash_total), size=22)
                        if has_stationery:
                            xh.set_alloc_text_cell(row.cells[4], "Consumable items bills & Stationery item bills", size=22)
                        else:
                            xh.set_alloc_text_cell(row.cells[4], "Consumable items bills", size=22)
                    elif texts[0] in ("02", "2") and "09.295" in full_txt:
                        xh.set_alloc_text_cell(row.cells[0], texts[0], size=22)
                        xh.set_alloc_amount_cell(row.cells[2], str(l_total), size=22)
                        xh.set_alloc_text_cell(row.cells[4], "Cleaning labour bills", size=22)

    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio


# ─────────────────────────────────────────────────────────────
# ANNEXURE 2  ENGINE
# ─────────────────────────────────────────────────────────────