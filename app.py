import streamlit as st
import pandas as pd
from math import ceil
from datetime import date

# =========================
# BRAND SETTINGS (edit here)
# =========================
BRAND_NAME   = "Security Pitch"
TAGLINE      = "SCM Pricing Calculator"
PRIMARY      = "#0D47A1"   # deep blue
ACCENT       = "#111827"   # near-black text
HIGHLIGHT_BG = "#F9FAFB"   # extra-light gray for panels
SUCCESS      = "#047857"   # green
WARNING      = "#B91C1C"   # red
LOGO_PATH    = "logo.png"  # file next to app.py; set to None if no logo
FAVICON      = "🧮"

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title=f"{BRAND_NAME} — {TAGLINE}",
    page_icon=FAVICON,
    layout="centered",
    initial_sidebar_state="expanded",
)

# =========================
# LIGHT STYLES
# =========================
st.markdown(
    f"""
    <style>
      .stApp {{ background-color: #FFFFFF; }}
      .app-header {{
        display:flex; align-items:center; gap:16px; padding:14px 18px;
        border-radius:14px; background: linear-gradient(90deg, {PRIMARY}14, {PRIMARY}08);
        border:1px solid #E5E7EB; margin-bottom:8px;
      }}
      .brand-title {{ font-weight:800; font-size:24px; color:{ACCENT}; margin:0; }}
      .brand-subtitle {{ font-size:13px; color:#4B5563; margin:2px 0 0 0; }}
      .panel {{ background:{HIGHLIGHT_BG}; padding:16px; border-radius:12px; border:1px solid #E5E7EB; }}
      .kpi .metric-label {{ color:#6B7280 !important; font-size:12px !important; }}
      .kpi .metric-value {{ font-size:22px !important; font-weight:800 !important; color:{ACCENT} !important; }}
      .footer-note {{ color:#6B7280; font-size:12px; text-align:center; margin-top:8px; }}
      .contact-sales {{ color:{WARNING}; font-weight:800; font-size:18px; }}
      .badge {{ display:inline-block; background:{PRIMARY}14; color:{PRIMARY}; padding:4px 10px; border-radius:999px; font-size:12px; font-weight:700; }}
      .table-note {{ color:#6B7280; font-size:12px; margin-top:6px; }}
      /* Improve label readability */
      label, .stMarkdown p {{ color:{ACCENT} !important; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# HEADER (logo + brand)
# =========================
cols = st.columns([1, 8])
with cols[0]:
    if LOGO_PATH:
        try:
            st.image(LOGO_PATH, use_container_width=True)
        except Exception:
            st.markdown(f"<div class='badge'>{BRAND_NAME[0:2].upper()}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='badge'>{BRAND_NAME[0:2].upper()}</div>", unsafe_allow_html=True)

with cols[1]:
    st.markdown(
        f"""
        <div class='app-header'>
          <div>
            <div class='brand-title'>{BRAND_NAME}</div>
            <div class='brand-subtitle'>{TAGLINE}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# =========================
# CONSTANTS (pricing logic)
# =========================
CAMERA_TIERS = [(10, 1800), (30, 1600), (50, 1500), (100, 1300)]
T1_TIERS     = [(50, 11000), (100, 8000)]
T2_TIERS     = [(50, 5600), (100, 4500)]
STORAGE_BASE = {1: 1670, 2: 2030, 4: 2930, 6: 4990, 8: 6890, 10: 10990}
BASE_LICENSE     = 45000
AI_BASE_LICENSE  = 15000
T1_CAP, T2_CAP   = 10, 14
HW_BASE          = 65000
SI_MU, NONSI_MU  = 0.20, 0.30
MA_RATE          = 0.20   # informational

def tier_price(qty: int, tiers):
    for bound, price in tiers:
        if qty <= bound:
            return price
    return None  # triggers contact sales upstream

def calc(total, cust_type, t1, t2, include_storage, storage_tb):
    # Validation
    if t1 + t2 > total:
        return {"status": "ERROR", "message": "AI cameras exceed total cameras."}

    # Contact Sales gate
    if total > 100 or t1 > 100 or t2 > 100:
        return {"status": "CONTACT_SALES", "reason": "Total cameras or an AI tier exceeds 100."}

    cam_unit = tier_price(total, CAMERA_TIERS)
    t1_unit  = tier_price(t1, T1_TIERS) if t1 > 0 else 0
    t2_unit  = tier_price(t2, T2_TIERS) if t2 > 0 else 0
    mu       = SI_MU if cust_type == "SI" else NONSI_MU

    base_sub     = BASE_LICENSE
    cams_sub     = total * cam_unit
    ai_base_sub  = (1 if t1 + t2 > 0 else 0) * AI_BASE_LICENSE
    ai_t1_sub    = t1 * (t1_unit or 0)
    ai_t2_sub    = t2 * (t2_unit or 0)

    hw_units      = ceil(t1 / T1_CAP + t2 / T2_CAP) if (t1 + t2) > 0 else 0
    hw_unit_price = (HW_BASE * (1 + mu)) if hw_units > 0 else 0
    hw_sub        = hw_units * hw_unit_price

    storage_sub = 0
    if include_storage:
        base = STORAGE_BASE.get(storage_tb)
        if base is None:
            return {"status": "ERROR", "message": "Invalid storage TB."}
        storage_sub = base * (1 + mu)

    grand    = base_sub + cams_sub + ai_base_sub + ai_t1_sub + ai_t2_sub + hw_sub + storage_sub
    discount = -0.20 * grand if cust_type == "SI" else 0
    net      = grand + discount
    ma       = MA_RATE * net

    lines = [
        ("Base License", 1, BASE_LICENSE, base_sub),
        ("Cameras", total, cam_unit, cams_sub),
        ("AI Base License", (1 if t1 + t2 > 0 else 0), AI_BASE_LICENSE, ai_base_sub),
        ("AI Licenses — Tier 1", t1, t1_unit, ai_t1_sub),
        ("AI Licenses — Tier 2", t2, t2_unit, ai_t2_sub),
        ("AI Processing Equipment", hw_units, hw_unit_price, hw_sub),
        ("Storage (HDD)", 1 if include_storage else 0, storage_sub if include_storage else 0, storage_sub),
    ]
    return {
        "status": "OK",
        "lines": lines,
        "grand_total": grand,
        "discount": discount,
        "net_total": net,
        "ma_yearly": ma,
    }

def thb(n):
    try:
        return f"{int(round(n)):,}"
    except Exception:
        return "-"

# =========================
# SIDEBAR — MINI MANUAL
# =========================
st.sidebar.header("Manual")
st.sidebar.write(
    """
**Inputs (yellow fields):**  
• Total Cameras • Customer Type (SI / Non-SI)  
• Include Storage (Yes/No) • AI Tier 1 • AI Tier 2  
• Storage TB (1, 2, 4, 6, 8, 10)

**Rules:**  
• SI auto-discount 20%  
• Non-SI markup +30% on hardware & storage (SI +20%)  
• Contact Sales if any count > 100 (totals hidden)

**Outputs:**  
• Grand Total (before discount)  
• Net Total (after discount)  
• MA 20%/yr (info only)
"""
)
st.sidebar.divider()
st.sidebar.caption(f"© {date.today().year} {BRAND_NAME}. All rights reserved.")

# =========================
# INPUT PANEL
# =========================
st.markdown("#### Project Inputs")
with st.form("inputs"):
    c1, c2 = st.columns(2)
    total = c1.number_input("Total Cameras", min_value=0, value=22, step=1, help="Total number of cameras in the project.")
    cust_type = c2.selectbox("Customer Type", ["SI", "Non-SI"], help="Applies discount/markup rules.")
    t1 = c1.number_input("AI Tier 1 Cameras", min_value=0, value=5, step=1)
    t2 = c2.number_input("AI Tier 2 Cameras", min_value=0, value=7, step=1)
    include_storage = c1.selectbox("Include Storage?", ["No", "Yes"]) == "Yes"
    storage_tb = c2.selectbox("Storage TB", [1, 2, 4, 6, 8, 10], index=4) if include_storage else None

    submitted = st.form_submit_button("Calculate", use_container_width=True)

# =========================
# RESULTS
# =========================
if submitted:
    r = calc(total, cust_type, t1, t2, include_storage, storage_tb)

    if r["status"] == "ERROR":
        st.error(r["message"])

    elif r["status"] == "CONTACT_SALES":
        st.markdown(
            f"<div class='panel'><span class='contact-sales'>CONTACT SALES</span>"
            f"<div class='table-note'>Totals are hidden for projects with more than 100 cameras or any AI tier above 100.</div></div>",
            unsafe_allow_html=True,
        )
        st.subheader("Grand Total")
        st.write("CONTACT SALES")

    else:
        # KPI metrics
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown("<div class='kpi'>", unsafe_allow_html=True)
            st.metric("Grand Total (THB)", thb(r["grand_total"]))
            st.markdown("</div>", unsafe_allow_html=True)
        with k2:
            st.markdown("<div class='kpi'>", unsafe_allow_html=True)
            st.metric("Partner Discount", thb(r["discount"]))
            st.markdown("</div>", unsafe_allow_html=True)
        with k3:
            st.markdown("<div class='kpi'>", unsafe_allow_html=True)
            st.metric("Net Total (THB)", thb(r["net_total"]))
            st.markdown("</div>", unsafe_allow_html=True)
        with k4:
            st.markdown("<div class='kpi'>", unsafe_allow_html=True)
            st.metric("MA 20%/yr (THB)", thb(r["ma_yearly"]))
            st.markdown("</div>", unsafe_allow_html=True)

        # Line items table
        df = pd.DataFrame(
            [
                {
                    "Item": name,
                    "Qty": qty,
                    "Unit Price (THB)": (thb(unit) if unit else "-"),
                    "Subtotal (THB)": (thb(sub) if sub else "-"),
                }
                for name, qty, unit, sub in r["lines"]
                if not (qty == 0 and sub == 0)
            ]
        )
        st.markdown("#### Line Items")
        st.dataframe(df, use_container_width=True)
        st.markdown("<div class='table-note'>MA is informational and not included in Net Total.</div>", unsafe_allow_html=True)

        # Exports
        colA, colB = st.columns(2)
        with colA:
            st.download_button(
                "Download Line Items (CSV)",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name=f"SCM_Line_Items_{date.today().isoformat()}.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with colB:
            totals_df = pd.DataFrame(
                {
                    "Grand Total (THB)": [thb(r["grand_total"])],
                    "Partner Discount (THB)": [thb(r["discount"])],
                    "Net Total (THB)": [thb(r["net_total"])],
                    "MA 20%/yr (THB)": [thb(r["ma_yearly"])],
                }
            )
            st.download_button(
                "Download Totals (CSV)",
                data=totals_df.to_csv(index=False).encode("utf-8"),
                file_name=f"SCM_Totals_{date.today().isoformat()}.csv",
                mime="text/csv",
                use_container_width=True,
            )

# =========================
# FOOTER
# =========================
st.markdown(
    "<div class='footer-note'>This tool follows the official pricing logic and Contact-Sales rules. For non-standard scopes, consult the Solutions Team.</div>",
    unsafe_allow_html=True,
)

