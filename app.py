import streamlit as st
import pandas as pd
from math import ceil
from datetime import date
from io import BytesIO

# =========================
# BRAND & THEME (Pastel Cute)
# =========================
BRAND_NAME   = "Security Pitch"
TAGLINE      = "SCM Pricing Calculator"
# Pastel palette
PRIMARY      = "#7C83FD"   # lavender
ACCENT       = "#1F2937"   # near-black text
BG_GRAD_1    = "#FFF7FB"   # blush
BG_GRAD_2    = "#F3F7FF"   # baby-blue
CARD_BG      = "#FFFFFF"   # white card
SOFT_LINE    = "#E8ECF3"   # soft border
HOVER        = "#F0F2FF"   # hover
WARNING      = "#F43F5E"   # rose
LOGO_PATH    = "logo.png"
FAVICON      = "🎀"

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
# GLOBAL STYLES (Cute UI)
# =========================
st.markdown(
    f"""
    <style>
      /* Background gradient */
      .stApp {{
        background: linear-gradient(180deg, {BG_GRAD_1} 0%, {BG_GRAD_2} 100%);
      }}
      /* Import friendly rounded font */
      @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
      html, body, [class^="css"] {{ font-family: 'Plus Jakarta Sans', system-ui, -apple-system, Segoe UI, Roboto, sans-serif; color:{ACCENT} }}
      /* App header "glass" */
      .app-header {{
        display:flex; align-items:center; gap:16px; padding:18px 20px;
        border-radius:18px; background: rgba(255,255,255,0.7);
        border: 1px solid {SOFT_LINE};
        backdrop-filter: blur(6px);
        box-shadow: 0 8px 24px rgba(124,131,253,0.12);
        margin-bottom: 10px;
      }}
      .brand-title {{ font-weight:800; font-size:26px; color:{ACCENT}; margin:0; }}
      .brand-subtitle {{ font-size:13px; color:#6B7280; margin:3px 0 0 0; }}

      /* Cards / panels */
      .card {{
        background:{CARD_BG};
        border:1px solid {SOFT_LINE};
        border-radius:18px;
        box-shadow: 0 10px 30px rgba(31,41,55,0.06);
        padding:18px;
      }}

      /* Section titles */
      .section-title {{
        display:flex; align-items:center; gap:10px;
        font-weight:800; font-size:22px;
        color:{ACCENT};
        margin:6px 0 12px 0;
      }}
      .pill {{
        display:inline-block; background:{PRIMARY}20; color:{PRIMARY};
        padding:4px 10px; border-radius:999px; font-weight:700; font-size:12px;
      }}

      /* Inputs */
      .stSelectbox > div > div, .stNumberInput > div > div > input {{
        border-radius:12px !important;
      }}

      /* Buttons cute */
      .stButton > button {{
        background:{PRIMARY} !important;
        color:#ffffff !important;
        border:0 !important;
        border-radius:14px !important;
        padding:10px 16px !important;
        box-shadow: 0 8px 24px rgba(124,131,253,0.30) !important;
      }}
      .stButton > button:hover {{ filter: brightness(1.03); background:{PRIMARY} !important; }}

      /* Metrics */
      [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {{ color:{ACCENT} !important; }}
      .kpi .metric-value {{ font-size:26px !important; font-weight:800 !important; }}
      .kpi .metric-label {{ color:#6B7280 !important; font-size:12px !important; }}

      /* Tables */
      [data-testid="stDataFrame"] * {{ color:{ACCENT} !important; }}
      [data-testid="stDataFrame"] div[role="columnheader"] {{
        background:#F7F8FF !important; color:{ACCENT} !important;
      }}

      /* Sidebar cute */
      section[data-testid="stSidebar"] > div {{
        background: rgba(255,255,255,0.85);
        border-left: 1px solid {SOFT_LINE};
        backdrop-filter: blur(4px);
      }}
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# HEADER (logo + brand)
# =========================
c_logo, c_head = st.columns([1, 7])
with c_logo:
    if LOGO_PATH:
        try:
            st.image(LOGO_PATH, use_container_width=True)
        except Exception:
            st.markdown("<div class='pill'>SP</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='pill'>SP</div>", unsafe_allow_html=True)

with c_head:
    st.markdown(
        f"""
        <div class='app-header'>
          <div>
            <div class='brand-title'>✨ {BRAND_NAME}</div>
            <div class='brand-subtitle'>{TAGLINE}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# =========================
# PRICING CONSTANTS / LOGIC
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
MA_RATE          = 0.20   # info only

def tier_price(qty: int, tiers):
    if qty == 0: return 0
    for bound, price in tiers:
        if qty <= bound:
            return price
    return None

def calc(total, cust_type, t1, t2, include_storage, storage_tb):
    if t1 + t2 > total:
        return {"status": "ERROR", "message": "AI cameras exceed total cameras."}
    if total > 100 or t1 > 100 or t2 > 100:
        return {"status": "CONTACT_SALES", "reason": "Total cameras or an AI tier exceeds 100."}

    cam_unit = tier_price(total, CAMERA_TIERS)
    t1_unit  = tier_price(t1, T1_TIERS)
    t2_unit  = tier_price(t2, T2_TIERS)
    mu       = SI_MU if cust_type == "SI" else NONSI_MU

    base_sub     = BASE_LICENSE
    cams_sub     = total * (cam_unit or 0)
    ai_base_sub  = (1 if t1 + t2 > 0 else 0) * AI_BASE_LICENSE
    ai_t1_sub    = t1 * (t1_unit or 0)
    ai_t2_sub    = t2 * (t2_unit or 0)

    hw_units      = ceil((t1 / T1_CAP) + (t2 / T2_CAP)) if (t1 + t2) > 0 else 0
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
        ("Cameras", total, cam_unit or 0, cams_sub),
        ("AI Base License", (1 if t1 + t2 > 0 else 0), AI_BASE_LICENSE, ai_base_sub),
        ("AI Licenses — Tier 1", t1, t1_unit or 0, ai_t1_sub),
        ("AI Licenses — Tier 2", t2, t2_unit or 0, ai_t2_sub),
        ("AI Processing Equipment", hw_units, hw_unit_price, hw_sub),
        ("Storage (HDD)", 1 if include_storage else 0, storage_sub if include_storage else 0, storage_sub),
    ]
    return {"status": "OK", "lines": lines, "grand_total": grand, "discount": discount, "net_total": net, "ma_yearly": ma}

def thb(n):
    try: return f"{int(round(n)):,}"
    except Exception: return "-"

# =========================
# SIDEBAR (Mini Manual)
# =========================
st.sidebar.header("Manual 💡")
st.sidebar.write(
    """
**Inputs:**  
• Total Cameras, Customer Type (SI / Non-SI)  
• Include Storage (Yes/No), AI Tier 1, AI Tier 2  
• Storage TB (1, 2, 4, 6, 8, 10)

**Rules:**  
• SI auto-discount 20%  
• Non-SI markup +30% (SI +20%) for hardware & storage  
• If any count > 100 → Contact Sales (hide totals)

**Outputs:** Grand Total, Discount, Net Total, MA 20%/yr (info)
"""
)
st.sidebar.caption(f"© {date.today().year} {BRAND_NAME}")

# =========================
# INPUT CARD
# =========================
st.markdown("<div class='section-title'>🧁 Project Inputs</div>", unsafe_allow_html=True)
with st.container():
    with st.form("inputs", border=False):
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        total = c1.number_input("Total Cameras", min_value=0, value=22, step=1)
        cust_type = c2.selectbox("Customer Type", ["SI", "Non-SI"])
        t1 = c1.number_input("AI Tier 1 Cameras", min_value=0, value=5, step=1)
        t2 = c2.number_input("AI Tier 2 Cameras", min_value=0, value=7, step=1)
        include_storage = c1.selectbox("Include Storage?", ["No", "Yes"]) == "Yes"
        storage_tb = c2.selectbox("Storage TB", [1, 2, 4, 6, 8, 10], index=4) if include_storage else None
        st.markdown("</div>", unsafe_allow_html=True)

        submitted = st.form_submit_button("Calculate ✨", use_container_width=True)

# =========================
# RESULTS
# =========================
if submitted:
    r = calc(total, cust_type, t1, t2, include_storage, storage_tb)

    if r["status"] == "ERROR":
        st.error(r["message"])

    elif r["status"] == "CONTACT_SALES":
        st.markdown(
            f"<div class='card'><div class='section-title'>📞 Contact Sales</div>"
            f"<div>Totals are hidden for projects with more than 100 cameras or any AI tier above 100.</div></div>",
            unsafe_allow_html=True,
        )
        st.subheader("Grand Total")
        st.write("CONTACT SALES")

    else:
        st.balloons()  # cute celebration

        # KPI cute cards
        st.markdown("<div class='section-title'>🍬 Summary</div>", unsafe_allow_html=True)
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown("<div class='card kpi'>", unsafe_allow_html=True)
            st.metric("Grand Total (THB)", thb(r["grand_total"]))
            st.markdown("</div>", unsafe_allow_html=True)
        with k2:
            st.markdown("<div class='card kpi'>", unsafe_allow_html=True)
            st.metric("Partner Discount", thb(r["discount"]))
            st.markdown("</div>", unsafe_allow_html=True)
        with k3:
            st.markdown("<div class='card kpi'>", unsafe_allow_html=True)
            st.metric("Net Total (THB)", thb(r["net_total"]))
            st.markdown("</div>", unsafe_allow_html=True)
        with k4:
            st.markdown("<div class='card kpi'>", unsafe_allow_html=True)
            st.metric("MA 20%/yr (THB)", thb(r["ma_yearly"]))
            st.markdown("</div>", unsafe_allow_html=True)

        # Line items table
        st.markdown("<div class='section-title'>🧾 Line Items</div>", unsafe_allow_html=True)
        df = pd.DataFrame(
            [
                {"Item": name, "Qty": qty,
                 "Unit Price (THB)": (thb(unit) if unit else "-"),
                 "Subtotal (THB)": (thb(sub) if sub else "-")}
                for name, qty, unit, sub in r["lines"]
                if not (qty == 0 and sub == 0)
            ]
        )
        st.dataframe(df, use_container_width=True)
        st.markdown("<div style='color:#6B7280;font-size:12px;margin-top:6px;'>MA is informational and not included in Net Total.</div>", unsafe_allow_html=True)

        # Excel download (1 button, 2 sheets)
        def build_excel(line_items_df: pd.DataFrame) -> bytes:
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                # Sheet 1: Line Items
                li = line_items_df.copy()
                li.to_excel(writer, sheet_name="Line Items", index=False)
                ws1 = writer.sheets["Line Items"]
                for i, col in enumerate(li.columns):
                    width = max(12, int(li[col].astype(str).map(len).max()) + 2)
                    ws1.set_column(i, i, width)

                # Sheet 2: Totals
                totals_df = pd.DataFrame(
                    {
                        "Field": ["Grand Total (THB)", "Partner Discount (THB)", "Net Total (THB)", "MA 20%/yr (THB)"],
                        "Value": [thb(r["grand_total"]), thb(r["discount"]), thb(r["net_total"]), thb(r["ma_yearly"])],
                    }
                )
                totals_df.to_excel(writer, sheet_name="Totals", index=False)
                ws2 = writer.sheets["Totals"]
                ws2.set_column(0, 0, 26)
                ws2.set_column(1, 1, 20)
            return buffer.getvalue()

        xlsx_bytes = build_excel(df)
        st.download_button(
            "📥 Download Quote (Excel)",
            data=xlsx_bytes,
            file_name=f"SCM_Quote_{date.today().isoformat()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

# =========================
# FOOTER
# =========================
st.markdown(
    "<div style='text-align:center;color:#6B7280;font-size:12px;margin-top:10px;'>Made with 💜 for easy quoting • For custom scopes, contact Solutions Team.</div>",
    unsafe_allow_html=True,
)
