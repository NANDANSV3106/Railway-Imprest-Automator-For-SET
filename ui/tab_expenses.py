"""
Tab 1 — Consumables: voucher-mode selector and Bill 1 / Bill 2 inputs.
"""
import datetime
import streamlit as st

from core.balance_store import _month_key
from core.state import init_default


def render_tab1(sel_month, sel_year, month_idx, days_in_month):
    """
    Renders the Consumables tab. Returns a dict with everything Tab 3
    needs: v1_amt, v2_amt, v1_date, v2_date, v1_items, v2_items,
    num_bills, has_stationery, cash_total.
    """
    st.markdown('<p class="sec-title"><span class="sec-title-icon">⚙️</span>Voucher Mode</p>', unsafe_allow_html=True)

    num_bills = st.radio(
        "Voucher mode",
        options=[1, 2],
        format_func=lambda x: "3 Vouchers — 1 Consumable Bill" if x == 1 else "4 Vouchers — 2 Bills",
        label_visibility="collapsed",
        key=f"num_bills_{_month_key(sel_month, sel_year)}",
    )

    has_stationery = False
    if num_bills == 2:
        has_stationery = st.checkbox(
            "Bill 2 is a Stationery bill (otherwise it's a second Consumable bill)",
            key=f"has_stationery_{_month_key(sel_month, sel_year)}",
        )

    # Default dates for date pickers.
    # Consumable bills must be dated within the imprest month itself
    # (e.g. generating for July requires bill dates in July).
    _default_d1 = datetime.date(int(sel_year), month_idx, min(25, days_in_month))
    _default_d2 = datetime.date(int(sel_year), month_idx, min(26, days_in_month))
    _min_date   = datetime.date(int(sel_year), month_idx, 1)
    _max_date   = datetime.date(int(sel_year), month_idx, days_in_month)

    # Scope every widget key to the active month/year. Without this,
    # Streamlit keeps reusing the same session_state slot regardless of
    # which month is selected, so amounts typed for one month kept
    # showing up (unreset) when switching to another month.
    _mk = _month_key(sel_month, sel_year)

    # Explicit per-key defaults (belt-and-braces vs relying on number_input's
    # implicit `value=` handling, which some Streamlit versions/setups don't
    # reliably apply once a key has ever been touched elsewhere in the app).
    _v1a_key, _v1d_key, _v1i_key = f"v1a_{_mk}", f"v1d_{_mk}", f"v1i_{_mk}"
    _v2a_key, _v2d_key, _v2i_key = f"v2a_{_mk}", f"v2d_{_mk}", f"v2i_{_mk}"
    init_default(_v1a_key, 0); init_default(_v1d_key, _default_d1); init_default(_v1i_key, 0)
    init_default(_v2a_key, 0); init_default(_v2d_key, _default_d2); init_default(_v2i_key, 0)

    if num_bills == 1:
        # 3-Voucher: single bill, full width — Amount | Date picker | Items
        st.markdown('<p class="sec-title"><span class="sec-title-icon">📋</span>Bill 1 — Consumable</p>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3, gap="medium")
        with c1:
            v1_amt   = st.number_input("Amount (Rs.)", min_value=0, step=1, key=_v1a_key)
        with c2:
            v1_date_obj = st.date_input("Date", min_value=_min_date, max_value=_max_date, key=_v1d_key)
            v1_date = v1_date_obj.strftime("%d/%m/%Y")
        with c3:
            v1_items = st.number_input("Number of Items", min_value=0, step=1, key=_v1i_key)
        v1_total_disp = int(v1_amt)
        st.markdown(
            f'''<div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:9px;
            padding:0.65rem 1rem;margin-top:0.8rem;display:flex;align-items:center;gap:1rem">
            <span style="font-size:0.75rem;font-weight:700;color:#166534;text-transform:uppercase;letter-spacing:0.5px">Bill Total</span>
            <span style="font-size:1.4rem;font-weight:800;color:#059669">₹{v1_total_disp:,}</span>
            </div>''',
            unsafe_allow_html=True
        )
        v2_amt = 0; v2_date = ""; v2_items = 0

    else:
        # 4-Voucher: two bills side by side
        label2   = "Stationery" if has_stationery else "Consumable"
        col_b1, col_b2 = st.columns(2, gap="large")

        with col_b1:
            st.markdown('<p class="sec-title"><span class="sec-title-icon">📋</span>Bill 1 — Consumable</p>', unsafe_allow_html=True)
            v1_amt      = st.number_input("Amount (Rs.)", min_value=0, step=1, key=_v1a_key)
            v1_date_obj = st.date_input("Date", min_value=_min_date, max_value=_max_date, key=_v1d_key)
            v1_date     = v1_date_obj.strftime("%d/%m/%Y")
            v1_items    = st.number_input("Number of Items", min_value=0, step=1, key=_v1i_key)
            v1_disp = int(v1_amt)
            st.markdown(
                f'''<div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:9px;
                padding:0.55rem 1rem;margin-top:0.6rem;display:flex;align-items:center;gap:0.8rem">
                <span style="font-size:0.72rem;font-weight:700;color:#166534;text-transform:uppercase">Bill Total</span>
                <span style="font-size:1.2rem;font-weight:800;color:#059669">₹{v1_disp:,}</span>
                </div>''',
                unsafe_allow_html=True
            )

        with col_b2:
            st.markdown(f'''<p class="sec-title"><span class="sec-title-icon">📋</span>Bill 2 — {label2}</p>''', unsafe_allow_html=True)
            v2_amt      = st.number_input("Amount (Rs.)", min_value=0, step=1, key=_v2a_key)
            v2_date_obj = st.date_input("Date", min_value=_min_date, max_value=_max_date, key=_v2d_key)
            v2_date     = v2_date_obj.strftime("%d/%m/%Y")
            v2_items    = st.number_input("Number of Items", min_value=0, step=1, key=_v2i_key)
            v2_disp = int(v2_amt)
            st.markdown(
                f'''<div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:9px;
                padding:0.55rem 1rem;margin-top:0.6rem;display:flex;align-items:center;gap:0.8rem">
                <span style="font-size:0.72rem;font-weight:700;color:#166534;text-transform:uppercase">Bill Total</span>
                <span style="font-size:1.2rem;font-weight:800;color:#059669">₹{v2_disp:,}</span>
                </div>''',
                unsafe_allow_html=True
            )

    cash_total = int(v1_amt) + int(v2_amt)

    st.markdown(f"""
    <div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:9px;
    padding:0.7rem 1.1rem;margin-top:1rem;display:flex;align-items:center;justify-content:space-between">
        <span style="font-size:0.8rem;font-weight:700;color:#1B4DB0;text-transform:uppercase;letter-spacing:0.5px">Combined Bill Total (excl. labour)</span>
        <span style="font-size:1.3rem;font-weight:800;color:#1B4DB0">₹{cash_total:,}</span>
    </div>
    """, unsafe_allow_html=True)

    return {
        "v1_amt": v1_amt, "v2_amt": v2_amt,
        "v1_date": v1_date, "v2_date": v2_date,
        "v1_items": v1_items, "v2_items": v2_items,
        "num_bills": num_bills, "has_stationery": has_stationery,
        "cash_total": cash_total,
    }