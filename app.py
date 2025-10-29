# app.py
import streamlit as st
import pandas as pd
from math import ceil
from datetime import date
from io import BytesIO

# =========================
# BRAND / PAGE
# =========================
BRAND_NAME = "Security Pitch"
TAGLINE    = "SCM Pricing Calculator"
FAVICON    = "📸"
LOGO_PATH  = "logo.png"  # วางไฟล์โลโก้ไว้ข้าง app.py; ถ้าไม่มีจะไม่แสดง

st.set_page_config(
    page_title=f"{BRAND_NAME} — {TAGLINE}",
    page_icon=FAVICON,
    layout="centered",
    initial_sidebar_state="collapsed",
)

# =========================
# STYLE (Minimal, single-border)
# =========================
st.markdown("""
<style>
/* Hide sidebar */
section[data-testid="stSidebar"] { display:none !important; }
div[data-testid="collapsedControl"] { display:none !important; }

/* Page background (soft gradient) */
.stApp {
  background: linear-gradient(180deg, #FFF7FB 0%, #F3F7FF 100%);
  color:#111827;
}

/* Typography */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
html, body, [class^="css"], [class*="css"] {
  font-family: 'Plus Jakarta Sans', system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
  color:#111827 !important;
}

/* Header card */
.app-header {
  display:flex; align-items:center; gap:14px; padding:16px 18px;
  border-radius:16px; background: rgba(255,255,255,0.9);
  border:1px solid #E8ECF3; backdrop-filter: blur(6px);
  box-shadow: 0 6px 18px rgba(17,24,39,0.06); margin-bottom: 10px;
}
.brand-title { font-weight:800; font-size:24px; margin:0; }
.brand-subtitle { font-size:13px; color:#6B7280; margin:2px 0 0 0; }

/* Section title */
.section-title { font-weight:800; font-size:22px; margin:8px 0 12px 0; }

/* ===== Minimal inputs: single clean border for all fields ===== */
label, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
.stMarkdown h4, .stMarkdown h5, .stMarkdown h6 { color:#111827 !important; }

/* 1) NUMBER/TEXT INPUT (outer) */
div[data-baseweb="input"] > div {
  background:#FFFFFF !important;
  color:#111827 !important;
  border:1px solid #111827 !important;
  border-radius:12px !important;
  box-shadow:none !important;
  outline:none !important;
  overflow:hidden;           /* cut inner borders */
}
/* inner layer remove borders */
div[data-baseweb="input"] > div > div {
  border:0 !important; box-shadow:none !important; background:transparent !important;
}
/* text color */
div[data-baseweb="input"] input { color:#111827 !important; background:#FFFFFF !important; }
/* stepper +/- divider */
div[data-baseweb="input"] [role="button"] {
  border-left:1px solid #111827 !important; box-shadow:none !important;
}

/* 2) SELECT (single clean border) */
div[data-baseweb="select"] > div {
  background:#FFFFFF !important;
  color:#111827 !important;
  border:1px solid #111827 !important;
  border-radius:12px !important;
  box-shadow:none !important;
  outline:none !important;
  overflow:hidden;
}
div[data-baseweb="select"] > div > div {
  border:0 !important; box-shadow:none !important; background:transparent !important;
}
div[data-baseweb="select"] svg { color:#111827 !important; opacity:1 !important; }
div[data-baseweb="select"] svg path { fill:#111827 !important; }
div[role="listbox"]   { background:#FFFFFF !important; border:1px solid #111827 !important; }
div[role="listbox"] * { color:#111827 !important; }

/* 3) Main button */
.stButton > button {
  background:#111827 !important; color:#FFFFFF !important; border:0 !important;
  border-radius:12px !important; padding:12px 18px !important; box-shadow:none !important;
}
.stButton > button:hover { filter:brightness(1.05); }

/* Dataframe & metrics text */
[data-testid="stMetricValue"], [data-testid="stMetricLabel"] { color:#111827 !important; }
[data-testid="stDataFrame"] * { color:#111827 !important; }
</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
c_logo, c_head = st.columns([1, 7])
with c_logo:
    try:
        if LOGO_PATH:
            st.image(LOGO_PATH, use_container_width=True)
    except Exception:
        pass
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
# Cameras (per camera)
CAMERA_TIERS = [(10, 1800), (30, 1600), (50, 1500), (100, 1300)]
# AI licenses (per license)
T1_TIERS     = [(50, 11000), (100, 8000)]
T2_TIERS     = [(50, 5600), (100, 4500)]

# Storage base cost (before markup)
STORAGE_BASE = {1:1670, 2:2030, 4:2930, 6:4990, 8:6890, 10:10990}

BASE_LICENSE     = 45000
AI_BASE_LICENSE  = 15000
T1_CAP, T2_CAP   = 10, 14            # processing capacity per unit
HW_BASE          = 65000             # base hardware unit price (before markup)
SI_MU, NONSI_MU  = 0.20, 0.30        # markup for storage & hardware
MA_RATE          = 0.20              # info only
SI_PARTNER_DISC  = 0.20              # SI discount applied to Grand Total

def tier_price(qty: int, tiers):
    """Return unit price for qty based on tiers; None if beyond last tier (=> contact sales)"""
    if qty == 0: return 0
    for bound, price in tiers:
        if qty <= bound: return price
    return None

def choose_storage_combo(required_tb: int):
    """
    Pick HDD combination such that total capacity >= required_tb with simple greedy:
    always take the smallest SKU that reaches/just passes the remaining.
    Eg 15 TB -> 10 + 6 (16 TB)
    """
    if required_tb <= 0: return {}
    sizes = sorted(STORAGE_BASE.keys())  # [1,2,4,6,8,10]
    combo, remaining = {}, required_tb
    while remaining > 0:
        pick = sizes[-1] if remaining > sizes[-1] else next(s for s in sizes if s >= remaining)
        combo[pick] = combo.get(pick, 0) + 1
        remaining -= pick
    return combo

def calc(total, cust_type, t1, t2, include_storage, storage_tb_total):
    if t1 + t2 > total:
        return {"status":"ERROR","message":"AI cameras exceed total cameras."}
    if total > 100 or t1 > 100 or t2 > 100:
        return {"status":"CONTACT_SALES","reason":"Total cameras or an AI tier exceeds 100."}

    cam_unit = tier_price(total, CAMERA_TIERS)
    t1_unit  = tier_price(t1, T1_TIERS)
    t2_unit  = tier_price(t2, T2_TIERS)

    # markups
    mu = SI_MU if cust_type == "SI" else NONSI_MU

    # line subtotals
    base_sub    = BASE_LICENSE
    cams_sub    = total * (cam_unit or 0)
    ai_base_sub = (1 if t1 + t2 > 0 else 0) * AI_BASE_LICENSE
    ai_t1_sub   = t1 * (t1_unit or 0)
    ai_t2_sub   = t2 * (t2_unit or 0)

    # processing hardware (optimized by tiers)
    hw_units      = ceil((t1 / T1_CAP) + (t2 / T2_CAP)) if (t1 + t2) > 0 else 0
    hw_unit_price = (HW_BASE * (1 + mu)) if hw_units > 0 else 0
    hw_sub        = hw_units * hw_unit_price

    # storage
    storage_lines, storage_sub = [], 0
    if include_storage:
        if storage_tb_total is None or storage_tb_total <= 0:
            return {"status":"ERROR","message":"Please enter required Storage TB (>0)."}
        combo = choose_storage_combo(int(storage_tb_total))
        for size_tb, qty in sorted(combo.items(), reverse=True):
            unit_after_markup = STORAGE_BASE[size_tb] * (1 + mu)   # apply markup by customer type
            sub = qty * unit_after_markup
            storage_sub += sub
            storage_lines.append((f"HDD {size_tb} TB", qty, unit_after_markup, sub))

    grand = base_sub + cams_sub + ai_base_sub + ai_t1_sub + ai_t2_sub + hw_sub + storage_sub
    discount = -SI_PARTNER_DISC * grand if cust_type == "SI" else 0
    net = grand + discount
    ma  = MA_RATE * net

    lines = [
        ("Base License", 1, BASE_LICENSE, base_sub),
        ("Cameras", total, cam_unit or 0, cams_sub),
        ("AI Base License", (1 if t1 + t2 > 0 else 0), AI_BASE_LICENSE, ai_base_sub),
        ("AI Licenses — Tier 1", t1, t1_unit or 0, ai_t1_sub),
        ("AI Licenses — Tier 2", t2, t2_unit or 0, ai_t2_sub),
        ("AI Processing Equipment", hw_units, hw_unit_price, hw_sub),
    ]
    lines.extend(storage_lines)

    return {
        "status":"OK",
        "lines":lines,
        "grand_total":grand,
        "discount":discount,
        "net_total":net,
        "ma_yearly":ma
    }

def thb(n):
    try: return f"{int(round(n)):,}"
    except Exception: return "-"

# =========================
# INPUTS
# =========================
st.markdown("<div class='section-title'>🧁 Project Inputs</div>", unsafe_allow_html=True)
with st.form("inputs", border=False):
    c1, c2 = st.columns(2, vertical_alignment="center")
    total      = c1.number_input("Total Cameras", min_value=0, value=22, step=1)
    cust_type  = c2.selectbox("Customer Type", ["SI", "Non-SI"])
    t1         = c1.number_input("AI Tier 1 Cameras", min_value=0, value=5, step=1)
    t2         = c2.number_input("AI Tier 2 Cameras", min_value=0, value=7, step=1)
    include    = c1.selectbox("Include Storage?", ["No", "Yes"]) == "Yes"
    storage_tb = c2.number_input("Storage Required (TB)", min_value=1, value=8, step=1) if include else None
    submitted  = st.form_submit_button("Calculate ✨", use_container_width=True)

# =========================
# RESULTS
# =========================
if submitted:
    r = calc(total, cust_type, t1, t2, include, storage_tb)

    if r["status"] == "ERROR":
        st.error(r["message"])

    elif r["status"] == "CONTACT_SALES":
        st.markdown("<div class='section-title'>📞 Contact Sales</div>", unsafe_allow_html=True)
        st.write("Totals are hidden for projects with more than 100 cameras or any AI tier above 100.")

    else:
        # Summary
        st.markdown("<div class='section-title'>🧾 Summary</div>", unsafe_allow_html=True)
        k1, k2, k3, k4 = st.columns(4)
        with k1: st.metric("Grand Total (THB)", thb(r["grand_total"]))
        with k2: st.metric("Partner Discount",   thb(r["discount"]))
        with k3: st.metric("Net Total (THB)",    thb(r["net_total"]))
        with k4: st.metric("MA 20%/yr (THB)",    thb(r["ma_yearly"]))

        # One unified quote table (Line Items + Totals)
        line_rows = [
            {"Item": n, "Qty": q, "Unit Price (THB)": (thb(u) if u else "-"), "Subtotal (THB)": (thb(s) if s else "-")}
            for (n, q, u, s) in r["lines"] if not (q == 0 and s == 0)
        ]
        totals_rows = [
            {"Item":"", "Qty":"", "Unit Price (THB)":"", "Subtotal (THB)":""},
            {"Item":"Grand Total (THB)",      "Qty":"", "Unit Price (THB)":"", "Subtotal (THB)": thb(r["grand_total"])},
            {"Item":"Partner Discount (THB)", "Qty":"", "Unit Price (THB)":"", "Subtotal (THB)": thb(r["discount"])},
            {"Item":"Net Total (THB)",        "Qty":"", "Unit Price (THB)":"", "Subtotal (THB)": thb(r["net_total"])},
            {"Item":"MA 20%/yr (info)",       "Qty":"", "Unit Price (THB)":"", "Subtotal (THB)": thb(r["ma_yearly"])},
        ]
        quote_df = pd.DataFrame(line_rows + totals_rows)
        st.dataframe(quote_df, use_container_width=True)

        # Excel: single sheet "Quote"
        def build_excel(df: pd.DataFrame) -> bytes:
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Quote")
                ws = writer.sheets["Quote"]
                for i, col in enumerate(df.columns):
                    width = max(14, int(df[col].astype(str).map(len).max()) + 2)
                    ws.set_column(i, i, width)
            return buffer.getvalue()

        xlsx = build_excel(quote_df)
        st.download_button(
            "📥 Download Quote (Excel — 1 sheet)",
            data=xlsx,
            file_name=f"SCM_Quote_{date.today().isoformat()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

# Footer
st.markdown(
    "<div style='text-align:center;color:#6B7280;font-size:12px;margin-top:10px;'>Made for easy quoting • For non-standard scopes, contact the Solutions Team.</div>",
    unsafe_allow_html=True,
)
