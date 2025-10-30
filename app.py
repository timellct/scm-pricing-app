# app.py — no more CONTACT_SALES; uses override pricing instead
import streamlit as st
import pandas as pd
from math import ceil
from datetime import date
from io import BytesIO

st.set_page_config(
    page_title="Security Pitch — SCM Pricing Calculator",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- minimal readable style ---
st.markdown(
    """
    <style>
      section[data-testid="stSidebar"] {display:none !important;}
      .stApp {background: linear-gradient(180deg,#FFF7FB 0%,#F3F7FF 100%);}
      div[data-baseweb="input"]>div, div[data-baseweb="select"]>div{
        background:#fff!important;color:#111827!important;border:1px solid #E5E7EB!important;border-radius:12px!important;
      }
      div[role="listbox"]{background:#fff!important;}
      .stButton>button{background:#7C83FD!important;color:#fff!important;border:0!important;border-radius:14px!important;padding:10px 16px!important;}
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("## ✨ Security Pitch\nSCM Pricing Calculator")

# ---------- constants ----------
CAMERA_TIERS = [(10, 1800), (30, 1600), (50, 1500), (100, 1300)]
T1_TIERS     = [(50, 11000), (100, 8000)]
T2_TIERS     = [(50, 5600), (100, 4500)]

STORAGE_BASE = {1:1670, 2:2030, 4:2930, 6:4990, 8:6890, 10:10990}

BASE_LICENSE    = 45000
AI_BASE_LICENSE = 15000
T1_CAP, T2_CAP  = 10, 14
HW_BASE         = 65000

PARTNER_MU    = 0.20
NONPARTNER_MU = 0.30
MA_RATE       = 0.20

def thb(n):
    try: return f"{int(round(n)):,}"
    except: return "-"

def tier_price(qty, tiers):
    if qty == 0: return 0
    for bound, price in tiers:
        if qty <= bound:
            return price
    return None  # caller will override

def choose_storage_combo(required_tb: int):
    if required_tb <= 0: return {}
    sizes = sorted(STORAGE_BASE.keys())
    combo, remain = {}, required_tb
    while remain > 0:
        pick = sizes[-1] if remain > sizes[-1] else next(s for s in sizes if s >= remain)
        combo[pick] = combo.get(pick, 0) + 1
        remain -= pick
    return combo

# ---------- core calc (no CONTACT_SALES) ----------
def calc(total, cust_type, t1, t2, include_storage, storage_tb_total):
    if t1 + t2 > total:
        return {"status":"ERROR","message":"AI cameras exceed total cameras."}

    # camera unit price (override if >100)
    cam_unit = 1200 if total > 100 else (tier_price(total, CAMERA_TIERS) or 1200)
    t1_unit  = 6000 if t1    > 100 else (tier_price(t1, T1_TIERS)     or 6000)
    t2_unit  = 3500 if t2    > 100 else (tier_price(t2, T2_TIERS)     or 3500)

    is_partner = (cust_type == "Partner")
    mu = PARTNER_MU if is_partner else NONPARTNER_MU

    base_sub    = BASE_LICENSE
    cams_sub    = total * cam_unit
    ai_base_sub = (1 if t1 + t2 > 0 else 0) * AI_BASE_LICENSE
    ai_t1_sub   = t1 * t1_unit
    ai_t2_sub   = t2 * t2_unit

    hw_units      = ceil((t1 / T1_CAP) + (t2 / T2_CAP)) if (t1 + t2) > 0 else 0
    hw_unit_price = (HW_BASE * (1 + mu)) if hw_units > 0 else 0
    hw_sub        = hw_units * hw_unit_price

    storage_lines, storage_sub = [], 0
    if include_storage:
        if not storage_tb_total or storage_tb_total <= 0:
            return {"status":"ERROR","message":"Please enter required Storage TB (>0)."}
        combo = choose_storage_combo(int(storage_tb_total))
        for size_tb, qty in sorted(combo.items(), reverse=True):
            unit_after_markup = STORAGE_BASE[size_tb] * (1 + mu)
            sub = qty * unit_after_markup
            storage_sub += sub
            storage_lines.append((f"HDD {size_tb} TB", qty, unit_after_markup, sub))

    # Partner discount −20% applies only to SW/licensing (not HW/Storage)
    discountable = base_sub + cams_sub + ai_base_sub + ai_t1_sub + ai_t2_sub
    partner_discount = (-0.20 * discountable) if is_partner else 0

    grand_before_disc = base_sub + cams_sub + ai_base_sub + ai_t1_sub + ai_t2_sub + hw_sub + storage_sub
    net_total = grand_before_disc + partner_discount
    ma_yearly = MA_RATE * net_total

    lines = [
        ("Base License", 1, BASE_LICENSE, base_sub),
        ("Cameras", total, cam_unit, cams_sub),
        ("AI Base License", (1 if t1 + t2 > 0 else 0), AI_BASE_LICENSE, ai_base_sub),
        ("AI Licenses — Tier 1", t1, t1_unit, ai_t1_sub),
        ("AI Licenses — Tier 2", t2, t2_unit, ai_t2_sub),
        ("AI Processing Equipment", hw_units, hw_unit_price, hw_sub),
    ]
    lines.extend(storage_lines)

    return {
        "status":"OK",
        "lines":lines,
        "grand_total":grand_before_disc,
        "discount":partner_discount,
        "net_total":net_total,
        "ma_yearly":ma_yearly,
    }

# ---------- UI ----------
st.markdown("### 🚀 Project Inputs")
with st.form("inputs", border=False):
    c1, c2 = st.columns(2)
    total      = c1.number_input("Total Cameras", min_value=0, value=22, step=1)
    cust_type  = c2.selectbox("Customer Type", ["Partner", "Non-Partner"])
    t1         = c1.number_input("AI Tier 1 Cameras", min_value=0, value=5, step=1)
    t2         = c2.number_input("AI Tier 2 Cameras", min_value=0, value=7, step=1)
    include_st = c1.selectbox("Include Storage?", ["No", "Yes"]) == "Yes"
    storage_tb = c2.number_input("Storage Required (TB)", min_value=1, value=8, step=1) if include_st else None
    submit     = st.form_submit_button("Calculate ✨", use_container_width=True)

if submit:
    r = calc(total, cust_type, t1, t2, include_st, storage_tb)
    if r["status"] == "ERROR":
        st.error(r["message"])
    else:
        st.markdown("### 🧁 Summary")
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Grand Total (THB)", thb(r["grand_total"]))
        k2.metric("Partner Discount (THB)", thb(r["discount"]))
        k3.metric("Net Total (THB)", thb(r["net_total"]))
        k4.metric("MA 20%/yr (THB)", thb(r["ma_yearly"]))

        st.markdown("### 🧾 Quote Table")
        rows = [
            {"Item": n, "Qty": q, "Unit Price (THB)": thb(u) if u else "-", "Subtotal (THB)": thb(s) if s else "-"}
            for (n, q, u, s) in r["lines"] if not (q == 0 and s == 0)
        ]
        rows += [
            {"Item":"","Qty":"","Unit Price (THB)":"", "Subtotal (THB)":""},
            {"Item":"Grand Total (THB)"     ,"Qty":"","Unit Price (THB)":"", "Subtotal (THB)": thb(r["grand_total"])},
            {"Item":"Partner Discount (THB)","Qty":"","Unit Price (THB)":"", "Subtotal (THB)": thb(r["discount"])},
            {"Item":"Net Total (THB)"       ,"Qty":"","Unit Price (THB)":"", "Subtotal (THB)": thb(r["net_total"])},
            {"Item":"MA 20%/yr (info)"      ,"Qty":"","Unit Price (THB)":"", "Subtotal (THB)": thb(r["ma_yearly"])},
        ]
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)

        def to_excel(df: pd.DataFrame) -> bytes:
            buf = BytesIO()
            with pd.ExcelWriter(buf, engine="xlsxwriter") as w:
                df.to_excel(w, sheet_name="Quote", index=False)
                ws = w.sheets["Quote"]
                for i, col in enumerate(df.columns):
                    width = max(14, int(df[col].astype(str).map(len).max()) + 2)
                    ws.set_column(i, i, width)
            return buf.getvalue()

        st.download_button(
            "📥 Download Quote",
            data=to_excel(df),
            file_name=f"SCM_Quote_{date.today().isoformat()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

st.markdown(
    "<div style='text-align:center;color:#6B7280;font-size:12px;margin-top:10px;'>"
    "Made with 💜 • For custom scopes, contact Solutions Team.</div>",
    unsafe_allow_html=True
)
