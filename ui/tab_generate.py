"""
Tab 3 — Generate & Download: opening balance (auto-filled from the
previous month), financial summary, stale-document invalidation,
template validation, document generation, and download cards.
"""
import streamlit as st

from config import SANCTIONED_AMOUNT, DAILY_WAGE, TEMPLATES
from core.balance_store import (
    _month_key, _prev_month_year, _next_month_year,
    get_prev_month_closing_balance, save_month_closing_balance,
)
from core.num_to_words import amount_in_words
from core.validation import ANNEX1_ANCHORS, LABOUR_ANCHORS, validate_template
from docx_engine.annexure1 import generate_annexure_1
from docx_engine.labour import generate_labour_annexure


def render_tab3(sel_month, sel_year, days_in_month, tab1, tab2):
    """
    Renders the Generate & Download tab.
    tab1 / tab2 are the dicts returned by render_tab1() / render_tab2().
    """
    # Unpack what came from the other two tabs
    v1_amt, v2_amt   = tab1["v1_amt"], tab1["v2_amt"]
    v1_date, v2_date = tab1["v1_date"], tab1["v2_date"]
    v1_items, v2_items = tab1["v1_items"], tab1["v2_items"]
    num_bills, has_stationery = tab1["num_bills"], tab1["has_stationery"]
    cash_total = tab1["cash_total"]

    tha_worked, dev_worked = tab2["tha_worked"], tab2["dev_worked"]
    tha_total, dev_total   = tab2["tha_total"], tab2["dev_total"]
    tha_leaves, dev_leaves = tab2["tha_leaves"], tab2["dev_leaves"]
    tha_leave_set = tab2.get("tha_leave_set", set())
    dev_leave_set = tab2.get("dev_leave_set", set())

    total_expended = int(cash_total) + int(dev_total) + int(tha_total)

    st.markdown('<p class="sec-title"><span class="sec-title-icon">💳</span>Opening Balance</p>', unsafe_allow_html=True)

    _prev_closing = get_prev_month_closing_balance(sel_month, sel_year)
    _prev_month_name, _prev_year_name = _prev_month_year(sel_month, sel_year)
    _ob_key = f"opening_balance_{_month_key(sel_month, sel_year)}"
    if _ob_key not in st.session_state:
        st.session_state[_ob_key] = _prev_closing if _prev_closing is not None else 0

    opening_balance = st.number_input(
        "Opening Balance carried forward from last month (Rs.)",
        min_value=0,
        key=_ob_key,
        label_visibility="collapsed"
    )
    if _prev_closing is not None:
        st.markdown(f"""
        <p style="font-size:0.76rem;color:#94A3B8;margin:-6px 0 1rem 0">
            ✅ Auto-filled from {_prev_month_name.title()} {_prev_year_name}'s closing balance (₹{_prev_closing:,}). Edit if needed.
        </p>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <p style="font-size:0.76rem;color:#94A3B8;margin:-6px 0 1rem 0">
            ⚠️ No stored closing balance found for {_prev_month_name.title()} {_prev_year_name} — enter it manually.
            Generating {sel_month.title()} {sel_year} will save its closing balance for next month.
        </p>
        """, unsafe_allow_html=True)

    atm_recoupment  = SANCTIONED_AMOUNT - int(opening_balance)
    closing_balance = SANCTIONED_AMOUNT - total_expended
    is_negative     = closing_balance < 0

    st.markdown('<p class="sec-title"><span class="sec-title-icon">📊</span>Financial Summary</p>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="fin-grid">
        <div class="fin-card blue">
            <span class="fin-icon">🏦</span>
            <p class="fin-label">Opening Balance</p>
            <p class="fin-value">₹{int(opening_balance):,}</p>
            <p class="fin-sub">From last month</p>
        </div>
        <div class="fin-card amber">
            <span class="fin-icon">🏧</span>
            <p class="fin-label">ATM Recoupment</p>
            <p class="fin-value">₹{atm_recoupment:,}</p>
            <p class="fin-sub">Required this month</p>
        </div>
        <div class="fin-card violet">
            <span class="fin-icon">💸</span>
            <p class="fin-label">Total Expended</p>
            <p class="fin-value">₹{total_expended:,}</p>
            <p class="fin-sub">{amount_in_words(total_expended)[:28]}…</p>
        </div>
        <div class="fin-card {'red' if is_negative else 'green'}">
            <span class="fin-icon">{'⚠️' if is_negative else '✅'}</span>
            <p class="fin-label">Closing Balance</p>
            <p class="fin-value" style="color:{'#DC2626' if is_negative else '#059669'}">₹{closing_balance:,}</p>
            <p class="fin-sub">{'Overspent!' if is_negative else 'Carry forward'}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="sec-title"><span class="sec-title-icon">📂</span>Expenditure Breakdown</p>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="breakdown-row">
        <div class="breakdown-item">
            <p class="bd-label">🛒 Consumables</p>
            <p class="bd-value">₹{int(cash_total):,}</p>
            <p class="bd-sub">Voucher 1{" + 2" if num_bills == 2 else ""}</p>
        </div>
        <div class="breakdown-item">
            <p class="bd-label">👩 THAYAMMA Wages</p>
            <p class="bd-value">₹{int(tha_total):,}</p>
            <p class="bd-sub">{tha_worked} days × ₹{DAILY_WAGE}</p>
        </div>
        <div class="breakdown-item">
            <p class="bd-label">👩 DEVAMMA Wages</p>
            <p class="bd-value">₹{int(dev_total):,}</p>
            <p class="bd-sub">{dev_worked} days × ₹{DAILY_WAGE}</p>
        </div>
        <div class="breakdown-item" style="border-color:#1B4DB0">
            <p class="bd-label">📋 Grand Total</p>
            <p class="bd-value" style="color:#1B4DB0">₹{total_expended:,}</p>
            <p class="bd-sub">of ₹{SANCTIONED_AMOUNT:,} sanctioned</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if is_negative:
        st.error(f"⚠️ Closing balance is negative (₹{closing_balance:,}). "
                  f"You have overspent the sanctioned amount by ₹{abs(closing_balance):,}. "
                  "Please review your entries before generating.")

    _current_signature = (
        sel_month, sel_year, num_bills, has_stationery,
        int(opening_balance), int(v1_amt), int(v2_amt), v1_date, v2_date,
        int(v1_items), int(v2_items),
        int(tha_worked), int(dev_worked),
        int(SANCTIONED_AMOUNT), int(DAILY_WAGE),
    )
    if st.session_state.get("generated_signature") not in (None, _current_signature):
        for _k in ("annex_1_bytes", "labour_bytes", "annex_1_name", "labour_name"):
            st.session_state.pop(_k, None)
        st.session_state.pop("generated_signature", None)
        st.info("ℹ️ Inputs changed since the last generation — previous downloads were cleared. Click Generate again for the updated documents.")

    st.markdown('<p class="sec-title"><span class="sec-title-icon">⚡</span>Generate Documents</p>', unsafe_allow_html=True)

    leave_overlap = (tha_leaves + dev_leaves) > days_in_month
    block_generate = is_negative or leave_overlap

    gen_col, _ = st.columns([2, 1])
    with gen_col:
        generate_clicked = st.button(
            "🚀  Generate All Documents",
            type="primary",
            disabled=block_generate
        )

    if is_negative:
        st.caption("⛔ Fix the negative closing balance before generating documents.")
    if leave_overlap:
        st.caption("⛔ Fix the overlapping leave days on the Labour tab before generating documents.")

    if generate_clicked and not block_generate:
        if num_bills == 1:
            annex_1_template = TEMPLATES["annex1_3v"]
        elif has_stationery:
            annex_1_template = TEMPLATES["annex1_4v_stationery"]
        else:
            annex_1_template = TEMPLATES["annex1_4v_no_stationery"]
        labour_template = (TEMPLATES["labour_3v"] if num_bills == 1
                           else TEMPLATES["labour_4v"])

        try:
            with st.spinner("⏳ Checking templates…"):
                validate_template(annex_1_template, ANNEX1_ANCHORS, min_tables=5)
                validate_template(labour_template, LABOUR_ANCHORS, min_tables=1)
        except RuntimeError as e:
            st.warning(f"⚠️ Template check couldn't confirm the structure: {e}\n\nAttempting generation anyway — if it fails, that will show a specific error below.")
        except Exception as e:
            st.error(f"❌ Could not read a template file. Check the **templates/** folder exists and is readable.")
            st.caption(f"Details: {e}")
            st.stop()

        annex_1_file = None
        try:
            with st.spinner("⏳ Generating Annexure 1…"):
                annex_1_file = generate_annexure_1(
                    annex_1_template, sel_month, sel_year,
                    int(opening_balance), atm_recoupment, int(cash_total),
                    int(dev_total), int(tha_total), total_expended, int(closing_balance),
                    SANCTIONED_AMOUNT, int(v1_amt), int(v2_amt), v1_date, v2_date,
                    v1_items=int(v1_items), v2_items=int(v2_items),
                    num_vouchers=(3 if num_bills == 1 else 4),
                    has_stationery=has_stationery
                )
        except Exception as e:
            st.error("❌ Annexure I generation failed — the template layout may not match what the app expects.")
            st.caption(f"Details: {e}")
            st.stop()

        labour_file = None
        try:
            with st.spinner("⏳ Generating Labour Annexure…"):
                labour_file = generate_labour_annexure(
                    labour_template, sel_month, sel_year,
                    int(tha_worked), int(dev_worked), DAILY_WAGE
                )
        except Exception as e:
            st.error("❌ Labour Annexure generation failed — the template layout may not match what the app expects.")
            st.caption(f"Details: {e}")
            st.stop()

        st.session_state["annex_1_bytes"] = annex_1_file.read()
        st.session_state["labour_bytes"]  = labour_file.read()
        st.session_state["annex_1_name"]  = f"ANNEXURE_1_{sel_month}_{sel_year}.docx"
        st.session_state["labour_name"]   = f"LABOUR_{sel_month}_{sel_year}.docx"
        st.session_state["generated_signature"] = _current_signature
        save_month_closing_balance(sel_month, sel_year, int(closing_balance))
        _next_m, _next_y = _next_month_year(sel_month, sel_year)
        st.success("✅ Both documents generated successfully — download them below.")
        st.caption(f"💾 Closing balance ₹{int(closing_balance):,} saved — it will auto-fill {_next_m.title()} {_next_y}'s opening balance.")

    if "annex_1_bytes" in st.session_state and "labour_bytes" in st.session_state:
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        st.markdown('<p class="sec-title"><span class="sec-title-icon">⬇️</span>Download Documents</p>', unsafe_allow_html=True)
        dl1, dl2 = st.columns(2, gap="large")

        with dl1:
            st.markdown(f"""
            <div class="dl-card">
                <div class="dl-card-header">
                    <div class="dl-file-icon">📄</div>
                    <div>
                        <p class="dl-file-title">Annexure I — Master Bill</p>
                        <p class="dl-file-sub">Balance sheet, summary, ledger &amp; certification</p>
                    </div>
                </div>
                <div class="dl-filename">{st.session_state['annex_1_name']}</div>
            </div>
            """, unsafe_allow_html=True)
            st.download_button(
                "⬇️  Download Annexure I",
                data=st.session_state["annex_1_bytes"],
                file_name=st.session_state["annex_1_name"],
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key="dl_annex1",
                use_container_width=True
            )

        with dl2:
            st.markdown(f"""
            <div class="dl-card">
                <div class="dl-card-header">
                    <div class="dl-file-icon">👷</div>
                    <div>
                        <p class="dl-file-title">Annexure II — Labour</p>
                        <p class="dl-file-sub">Attendance register &amp; wage disbursement</p>
                    </div>
                </div>
                <div class="dl-filename">{st.session_state['labour_name']}</div>
            </div>
            """, unsafe_allow_html=True)
            st.download_button(
                "⬇️  Download Labour Annexure",
                data=st.session_state["labour_bytes"],
                file_name=st.session_state["labour_name"],
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key="dl_labour",
                use_container_width=True
            )