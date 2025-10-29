import streamlit as st
import pandas as pd
from math import ceil
from datetime import date
from io import BytesIO

# =========================
# CUTE BRAND (Pastel, readable)
# =========================
BRAND_NAME = "Security Pitch"
TAGLINE    = "SCM Pricing Calculator"

# Pastel palette + dark readable text
PRIMARY    = "#7C83FD"   # lavender
ACCENT     = "#111827"   # near-black readable text
BG1        = "#FFF7FB"   # blush
BG2        = "#F3F7FF"   # baby-blue
CARD_BG    = "#FFFFFF"
SOFT_LINE  = "#E8ECF3"
WARNING    = "#F43F5E"
LOGO_PATH  = "logo.png"
FAVICON    = "🎀"

st.set_page_config(
    page_title=f"{BRAND_NAME} — {TAGLINE}",
    page_icon=FAVICON,
    layout="centered",
    initial_sidebar_state="collapsed",  # hide sidebar
)

# =========================
# GLOBAL STYLES
# =========================
st.markdown(
    f"""
    <style>
      /* Hide sidebar completely */
      section[data-testid="stSidebar"] {{ display:none !important; }}
      div[data-testid="collapsedControl"] {{ display:none !important; }}

      /* Background gradient */
      .stApp {{
        background: linear-gradient(180deg, {BG1} 0%, {BG2} 100%);
      }}

      /* Friendly font */
      @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
      html, body, [class^="css"], [class*="css"] {{
        font-family: 'Plus Jakarta Sans', system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
        color: {ACCENT} !important;
      }}

      /* Header card (glass) */
      .app-header {{
        display:flex; align-items:center; gap:16px; padding:18px 20px;
        border-radius:18px; background: rgba(255,255,255,0.85);
        border:1px solid {SOFT_LINE}; backdrop-filter: blur(6px);
        box-shadow: 0 8px 24px rgba(124,131,253,0.12); margin-bottom: 6px;
      }}
      .brand-title   {{ font-weight:800; font-size:26px; color:{ACCENT}; margin:0; }}
      .brand-subtitle{{ font-size:13px;  color:#6B7280; margin:3px 0 0 0; }}

      /* Card container */
      .card {{
        background:{CARD_BG}; border:1px solid {SOFT_LINE}; border-radius:18px;
        box-shadow: 0 10px 30px rgba(31,41,55,0.06); padding:18px;
      }}

      /* Section title */
      .section-title {{
        display:flex; align-items:center; gap:10px; font-weight:800; font-size:22px;
        color:{ACCENT}; margin:6px 0 12px 0;
      }}

      /* Force all headings/labels to dark text */
      label, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
      .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {{ color:{ACCENT} !important; }}

      /* ===== Inputs: white background + dark text + soft border ===== */
      div[data-baseweb="input"] > div,
      div[data-baseweb="select"] > div {{
        background:#FFFFFF !important;
        color:{ACCENT} !important;
        border:1px solid #E5E7EB !important;
        border-radius:12px !important;
        box-shadow:none !important;
      }}

      div[data-baseweb="input"] input,
      div[data-baseweb="select"] input {{
        color:{ACCENT} !important;
        background:#FFFFFF !important;
      }}

      .stNumberInput > div > div {{
        background:#FFFFFF !important;
        border:1px solid #E5E7EB !important;
        border-radius:12px !important;
      }}
      .stNumberInput input {{
        color:{ACCENT} !important; background:#FFFFFF !important;
      }}

      .stSelectbox > div {{
        background:#FFFFFF !important; border:1px solid #E5E7EB !important; border-radius:12px !important;
      }}
      div[role="listbox"] * {{ color:{ACCENT} !important; }}
      div[role="listbox"] {{ background:#FFFFFF !important; }}

      /* Buttons */
      .stButton > button {{
        background:{PRIMARY} !important; color:#FFFFFF !important; border:0 !important;
        border-radius:14px !important; padding:10px 16px !important;
        box-shadow:0 8px 24px rgba(124,131,253,0.30) !important;
      }}
      .stButton > button:hover {{ filter:brightness(1.03); }}

      /* Metrics & table text */
      [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {{ color:{ACCENT} !important; }}
      [data-testid="stDataFrame"] * {{ color:{ACCENT} !important; }}
      [data-testid="stDataFrame"] div[role="columnheader"] {{ background:#F7F8FF !important; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# HEADER
# =========================
c_logo, c_head = st.columns([1, 7])
with c_logo:
    try:
        if LOGO_PATH:
            st.image(LOGO_PATH, use_container_width=True)
        else:
            st.markdown("<div style='display:inline-block;background:#EDEBFE;color:#5B5CEB;padding:4px 10px;border-radius:999px;font-weight:700;'>SP</div>", unsafe_allow_html=True)
    except Exception:
        st.markdown("<div style='display:inline-block;background:#EDEBFE;color:#5B5CEB;padding:4px 10px;border-radius:999px;font-weight:700;'>SP</div>", unsafe_allow_html=True)

with c_head:
    st.markdown(
        f"""
        <div class='app-header'>
          <div>
            <div class='brand-title'>✨ {BRAND_NAME}</div>
            <div class='brand-subtitle'>{TAGLINE}</div>
          </div>
        </div>
        """, unsafe_allow_html=True,
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
MA_RATE          = 0.20  # info only

def tier_price(qty: int, tiers):
    if qty == 0: return 0
    for bound, price in tiers:
        if qty <= bound:
            return price
    return None  # exceeds max -> trigger contact sales

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
    return {"status":"OK","lines":lines,"grand_total":grand,"discount":discount,"net_total":net,"ma_yearly":ma}

def thb(n):
    try: return f"{int(round(n)):,}"
    except Exception: return "-"

# =========================
# INPUT CARD
# =========================
st.markdown("<div class='section-title'>🧁 Project Inputs</div>", unsafe_allow_html=True)
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
        st.balloons()

        # KPI summary
        st.markdown("<div class='section-title'>🍬 Summary</div>", unsafe_allow_html=True)
        k1, k2, k3, k4 = st.columns(4)
        for col, label, value in [
            (k1, "Grand Total (THB)", thb(r["grand_total"])),
            (k2, "Partner Discount", thb(r["discount"])),
            (k3, "Net Total (THB)", thb(r["net_total"])),
            (k4, "MA 20%/yr (THB)", thb(r["ma_yearly"])),
        ]:
            with col:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.metric(label, value)
                st.markdown("</div>", unsafe_allow_html=True)

        # Single table ready for client: Line Items + Totals rows
        st.markdown("<div class='section-title'>🧾 Quote Table</div>", unsafe_allow_html=True)
        line_rows = [
            {"Item": n, "Qty": q, "Unit Price (THB)": (thb(u) if u else "-"), "Subtotal (THB)": (thb(s) if s else "-")}
            for (n, q, u, s) in r["lines"] if not (q == 0 and s == 0)
        ]
        totals_rows = [
            {"Item":"", "Qty":"", "Unit Price (THB)":"", "Subtotal (THB)":""},
            {"Item":"Grand Total (THB)",        "Qty":"", "Unit Price (THB)":"", "Subtotal (THB)": thb(r["grand_total"])},
            {"Item":"Partner Discount (THB)",   "Qty":"", "Unit Price (THB)":"", "Subtotal (THB)": thb(r["discount"])},
            {"Item":"Net Total (THB)",          "Qty":"", "Unit Price (THB)":"", "Subtotal (THB)": thb(r["net_total"])},
            {"Item":"MA 20%/yr (info)",         "Qty":"", "Unit Price (THB)":"", "Subtotal (THB)": thb(r["ma_yearly"])},
        ]
        quote_df = pd.DataFrame(line_rows + totals_rows)
        st.dataframe(quote_df, use_container_width=True)

        # Excel (ONE sheet named "Quote")
        def build_excel(df: pd.DataFrame) -> bytes:
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                df.to_excel(writer, sheet_name="Quote", index=False)
                ws = writer.sheets["Quote"]
                # Autofit-ish
                for i, col in enumerate(df.columns):
                    width = max(14, int(df[col].astype(str).map(len).max()) + 2)
                    ws.set_column(i, i, width)
            return buffer.getvalue()

        xlsx_bytes = build_excel(quote_df)
        st.download_button(
            "📥 Download Quote (Excel — 1 sheet)",
            data=xlsx_bytes,
            file_name=f"SCM_Quote_{date.today().isoformat()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

# Footer
st.markdown(
    "<div style='text-align:center;color:#6B7280;font-size:12px;margin-top:10px;'>Made with 💜 • For custom scopes, contact Solutions Team.</div>",
    unsafe_allow_html=True,
)
