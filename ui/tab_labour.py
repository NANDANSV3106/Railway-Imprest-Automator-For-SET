"""
Tab 2 — Labour: worker attendance inputs for THAYAMMA and DEVAMMA,
wage computation, and the deterministic no-overlap leave-day preview.
"""
import streamlit as st

from config import DAILY_WAGE
from core.balance_store import _month_key
from core.state import init_default


def render_tab2(sel_month, sel_year, days_in_month):
    """
    Renders the Labour tab. Returns a dict with tha_worked, dev_worked,
    tha_total, dev_total, tha_leaves, dev_leaves for Tab 3.
    """
    _mk = _month_key(sel_month, sel_year)
    st.markdown('<p class="sec-title"><span class="sec-title-icon">👷</span>Worker Attendance</p>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:9px;padding:0.75rem 1rem;
                font-size:0.8rem;color:#1E40AF;margin-bottom:1.2rem;line-height:1.6">
        💡 <strong>Leave rule:</strong> Leave days are randomly assigned — no two workers share the same leave day.
        Daily wage: <strong>₹{DAILY_WAGE}</strong> per day.
    </div>
    """, unsafe_allow_html=True)

    col_w1, col_w2 = st.columns(2, gap="large")

    with col_w1:
        st.markdown("""
        <div class="worker-card-header">
            <div class="worker-avatar">👩</div>
            <div>
                <p class="worker-name">Smt. THAYAMMA</p>
                <p class="worker-sub">Cleaning Labour</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        _tha_key = f"tha_{_mk}"
        init_default(_tha_key, min(27, days_in_month))
        tha_worked = st.number_input("Days Worked", min_value=0,
                                     max_value=days_in_month, key=_tha_key)
        tha_total  = tha_worked * DAILY_WAGE
        tha_leaves = days_in_month - tha_worked
        st.markdown(f"""
        <div class="worker-stat-row">
            <div class="worker-stat">
                <p class="ws-label">Days Worked</p>
                <p class="ws-val">{tha_worked}</p>
            </div>
            <div class="worker-stat">
                <p class="ws-label">Days Leave</p>
                <p class="ws-val leave">{tha_leaves}</p>
            </div>
            <div class="worker-stat">
                <p class="ws-label">Total Wages</p>
                <p class="ws-val wage">₹{tha_total:,}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_w2:
        st.markdown("""
        <div class="worker-card-header">
            <div class="worker-avatar">👩</div>
            <div>
                <p class="worker-name">Smt. DEVAMMA</p>
                <p class="worker-sub">Cleaning Labour</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        _dev_key = f"dev_{_mk}"
        init_default(_dev_key, min(27, days_in_month))
        dev_worked = st.number_input("Days Worked", min_value=0,
                                     max_value=days_in_month, key=_dev_key)
        dev_total  = dev_worked * DAILY_WAGE
        dev_leaves = days_in_month - dev_worked
        st.markdown(f"""
        <div class="worker-stat-row">
            <div class="worker-stat">
                <p class="ws-label">Days Worked</p>
                <p class="ws-val">{dev_worked}</p>
            </div>
            <div class="worker-stat">
                <p class="ws-label">Days Leave</p>
                <p class="ws-val leave">{dev_leaves}</p>
            </div>
            <div class="worker-stat">
                <p class="ws-label">Total Wages</p>
                <p class="ws-val wage">₹{dev_total:,}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    combined_leaves = tha_leaves + dev_leaves
    tha_leave_set, dev_leave_set = set(), set()
    if combined_leaves > days_in_month:
        st.error(f"⚠️ Combined leave days ({combined_leaves}) exceed the total days in {sel_month} ({days_in_month}). "
                  "Both workers cannot share the same leave day — please reduce leave days.")
    else:
        tha_lv = days_in_month - tha_worked
        dev_lv = days_in_month - dev_worked
        tha_leave_set = set(range(days_in_month - tha_lv + 1, days_in_month + 1)) if tha_lv > 0 else set()
        dev_e = days_in_month - tha_lv
        dev_s = dev_e - dev_lv + 1
        dev_leave_set = set(range(dev_s, dev_e + 1)) if dev_lv > 0 else set()
        if tha_lv > 0 or dev_lv > 0:
            tha_days_str = ", ".join(map(str, sorted(tha_leave_set))) if tha_lv else "None"
            dev_days_str = ", ".join(map(str, sorted(dev_leave_set))) if dev_lv else "None"
          



    return {
        "tha_worked": tha_worked, "dev_worked": dev_worked,
        "tha_total": tha_total, "dev_total": dev_total,
        "tha_leaves": tha_leaves, "dev_leaves": dev_leaves,
        "tha_leave_set": tha_leave_set, "dev_leave_set": dev_leave_set,
    }
