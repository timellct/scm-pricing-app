import streamlit as st
import pandas as pd
from math import ceil
from datetime import date
from io import BytesIO

# =========================
# BRAND / THEME (Pastel + readable)
# =========================
BRAND_NAME = "Security Pitch"
TAGLINE    = "SCM Pricing Calculator"

PRIMARY    = "#7C83FD"   # lavender
ACCENT     = "#111827"   # near-black readable text
BG1        = "#FFF7FB"   # blush
BG2        = "#F3F7FF"   # baby-blue
SOFT_LINE  = "#E8ECF3"
LOGO_PATH  = "logo.png"
FAVICON    = "🪙"

st.set_page_config(
    page_title=f"{BRAND_NAME} — {TAGLINE}",
    page_icon=FAVICON,
    layout="centered",
    initial_sidebar_state="collapsed",
)

# =========================
# GLOBAL STYLES (pastel theme + caret fix + clearer errors)
# =========================
st.markdown(
    f"""
    <style>
      /* Layout */
      section[data-testid="stSidebar"] {{ display:none !important; }}
      div[data-testid="collapsedControl"] {{ display:none !important; }}
      .stApp {{ background: linear-gradient(180deg, {BG1} 0%, {BG2} 100%); }}

      /* Font */
      @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
      html, body, [class^="css"], [class*="css"] {{
        font-family: 'Plus Jakarta Sans', system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
        color: {ACCENT} !important;
      }}

      /* Header card */
      .app-header {{
        display:flex; align-items:center; gap:16px; padding:18px 20px;
        border-radius:18px; background: rgba(255,255,255,0.85);
        border:1px solid {SOFT_LINE}; backdrop-filter: blur(6px);
        box-shadow: 0 8px 24px rgba(124,131,253,0.12); margin-bottom: 6px;
      }}
      .brand-title {{ font-weight:800; font-size:26px; color:{ACCENT}; margin:0; }}
      .brand-subtitle{{ font-size:13px; color:#6B7280; margin:3px 0 0 0; }}

      /* Section title */
      .section-title {{
        display:flex; align-items:center; gap:10px; font-weight:800; font-size:22px;
        color:{ACCENT}; margin:6px 0 12px 0;
      }}

      /* Text colors */
      label, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
      .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {{ color:{ACCENT} !important; }}

      /* Inputs / selects */
      div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {{
        background:#FFFFFF !important; color:{ACCENT} !important;
        border:1px solid #E5E7EB !important; border-radius:12px !important;
        box-shadow:none !important;
      }}
      div[data-baseweb="input"] input, div[data-baseweb="select"] input {{
        color:{ACCENT} !important; background:#FFFFFF !important;
      }}
      .stNumberInput > div > div {{ background:#FFFFFF !important; border:1px solid #E5E7EB !important; border-radius:12px !important; }}
      .stNumberInput input {{ color:{ACCENT} !important; background:#FFFFFF !important; }}

      .stSelectbox > div {{ background:#FFFFFF !important; border:1px solid #E5E7EB !important; border-radius:12px !important; }}
      div[role="listbox"] * {{ color:{ACCENT} !important; }}
      div[role="listbox"] {{ background:#FFFFFF !important; }}

      /* Dropdown arrow color */
      div[data-baseweb="select"] svg, div[data-baseweb="select"] svg path {{
        color:#111827 !important; fill:#111827 !important;
      }}

      /* Buttons */
      .stButton > button {{
        background:{PRIMARY} !important; color:#FFFFFF !important; border:0 !important;
        border-radius:14px !important; padding:10px 16px !important;
        box-shadow:0 8px 24px rgba(124,131,253,0.30) !important;
      }}
      .stButton > button:hover {{ filter:brightness(1.05); }}

      /* Metrics + table */
      [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {{ color:{ACCENT} !important; }}
      [data-testid="stDataFrame"] * {{ color:{ACCENT} !important; }}
      [data-testid="stDataFrame"] div[role="columnheader"] {{ background:#F7F8FF !important; }}

      /* DataFrame toolbar icons (make visible) */
      [data-testid="stDataFrame"] [data-testid="stElementToolbar"] button svg {{
        color:#FFFFFF !important; fill:none !important; stroke:#FFFFFF !important; stroke-width:1.5 !important;
      }}
      [data-testid="stDataFrame"] [data-testid="stElementToolbar"] button:hover svg {{ filter:brightness(1.2); }}

      /* ===== Caret (typing cursor) visibility fix ===== */
      .stNumberInput input,
      div[data-baseweb="input"] input[type="number"],
      div[data-baseweb="input"] input[type="text"],
      div[data-baseweb="select"] input[type="text"] {{
        caret-color: #111827 !important;    /* visible black caret */
        color: #111827 !important;          /* ensure dark text */
        background: #FFFFFF !important;     /* solid background behind caret */
      }}
      /* Focus outline for active inputs */
      .stNumberInput > div > div:focus-within,
      div[data-baseweb="input"]:focus-within {{
        border-color: {PRIMARY} !important;
        box-shadow: 0 0 0 2px rgba(124,131,253,0.25) !important;
        outline: none !important;
      }}
      /* Text selection color */
      .stNumberInput input::selection,
      div[data-baseweb="input"] input::selection {{ background: rgba(124,131,253,0.25); }}
      /* Safari/WebKit caret fallback */
      @supports (-webkit-touch-callout: none) {{
        input[type="number"] {{ -webkit-text-fill-color: #111827 !important; }}
      }}

      /* ===== High-contrast error messages (st.error) ===== */
      [data-testid="stNotification"] {{
        border-radius: 12px !important;
        border: 1px solid #FCA5A5 !important;         /* border red */
        background: #FEE2E2 !important;               /* soft red bg */
        box-shadow: 0 2px 6px rgba(249,112,112,.25) !important;
        padding: 14px 18px !important;
      }}
      [data-testid="stNotification"] p,
      [data-testid="stNotification"] span,
      [data-testid="stNotification"] div {{
        color: #B91C1C !important;                    /* deep red text */
        font-weight: 700 !important;
        font-size: 15px !important;
      }}
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
            <div class='brand-title'> {BRAND_NAME}</div>
            <div class='brand-subtitle'>{TAGLINE}</div>
          </div>
        </div>
        """, unsafe_allow_html=True,
    )

# =========================
# PRICING CONSTANTS (One-Time Sell)
# =========================
# One-Time (เดิม)
CAMERA_TIERS_ONETIME = [(10, 1800), (30, 1600), (50, 1500), (100, 1300)]
T1_TIERS_ONETIME      = [(50, 11000), (100, 8000)]
T2_TIERS_ONETIME      = [(50, 5600),  (100, 4500)]
OVER_100_CAMERA_PRICE_ONETIME = 1200
OVER_100_T1_PRICE_ONETIME     = 6000
OVER_100_T2_PRICE_ONETIME     = 3500
BASE_LICENSE_ONETIME          = 45000
AI_BASE_LICENSE_ONETIME       = 15000

# =========================
# PRICING CONSTANTS (Subscription)
# =========================
CAMERA_TIERS_SUB = [(10, 200), (30, 180), (50, 170), (100, 150)]
T1_TIERS_SUB     = [(50, 3500), (100, 3000)]
T2_TIERS_SUB     = [(50, 1800), (100, 1500)]
OVER_100_CAMERA_PRICE_SUB = 130
OVER_100_T1_PRICE_SUB     = 2500
OVER_100_T2_PRICE_SUB     = 1200
BASE_LICENSE_SUB          = 10000
AI_BASE_LICENSE_SUB       = 10000

# =========================
# COMMON CONSTANTS
# =========================
STORAGE_BASE = {1:1670, 2:2030, 4:2930, 6:4990, 8:6890, 10:10990}
T1_CAP, T2_CAP   = 10, 14
HW_BASE          = 65000
PARTNER_MU, NONPARTNER_MU  = 0.20, 0.30  # Partner / Non-Partner
MA_RATE_ONETIME  = 0.20  # one-time เท่านั้น
MA_RATE_SUB      = 0.00  # subscription ไม่มี MA

# =========================
# HELPERS
# =========================
def tier_price(qty: int, tiers):
    if qty == 0: return 0
    for bound, price in tiers:
        if qty <= bound:
            return price
    return None  # exceed max tier

def choose_storage_combo(required_tb: int):
    if required_tb <= 0: return {}
    sizes_sorted = sorted(STORAGE_BASE.keys())  # [1,2,4,6,8,10]
    combo, remaining = {}, required_tb
    while remaining > 0:
        if remaining > sizes_sorted[-1]:
            pick = sizes_sorted[-1]
        else:
            pick = next(s for s in sizes_sorted if s >= remaining)
        combo[pick] = combo.get(pick, 0) + 1
        remaining -= pick
    return combo

def get_price_tables(mode: str):
    """Return a dict of prices based on pricing mode."""
    if mode == "Subscription":
        return dict(
            base=BASE_LICENSE_SUB,
            ai_base=AI_BASE_LICENSE_SUB,
            cam_tiers=CAMERA_TIERS_SUB,
            t1_tiers=T1_TIERS_SUB,
            t2_tiers=T2_TIERS_SUB,
            over100_cam=OVER_100_CAMERA_PRICE_SUB,
            over100_t1=OVER_100_T1_PRICE_SUB,
            over100_t2=OVER_100_T2_PRICE_SUB,
            ma_rate=MA_RATE_SUB,
        )
    # One-Time Sell (default)
    return dict(
        base=BASE_LICENSE_ONETIME,
        ai_base=AI_BASE_LICENSE_ONETIME,
        cam_tiers=CAMERA_TIERS_ONETIME,
        t1_tiers=T1_TIERS_ONETIME,
        t2_tiers=T2_TIERS_ONETIME,
        over100_cam=OVER_100_CAMERA_PRICE_ONETIME,
        over100_t1=OVER_100_T1_PRICE_ONETIME,
        over100_t2=OVER_100_T2_PRICE_ONETIME,
        ma_rate=MA_RATE_ONETIME,
    )

def calc(mode, total, cust_type, ai_enabled, t1, t2, include_storage, storage_tb_total):
    # guard AI counts if disabled
    if not ai_enabled:
        t1, t2 = 0, 0

    if t1 + t2 > total:
        return {"status":"ERROR","message":"AI cameras exceed total cameras."}

    P = get_price_tables(mode)
    mu = PARTNER_MU if cust_type == "Partner" else NONPARTNER_MU

    cam_unit = tier_price(total, P["cam_tiers"])
    if cam_unit is None:
        cam_unit = P["over100_cam"]

    t1_unit  = tier_price(t1, P["t1_tiers"])
    if t1_unit is None:
        t1_unit = P["over100_t1"]

    t2_unit  = tier_price(t2, P["t2_tiers"])
    if t2_unit is None:
        t2_unit = P["over100_t2"]

    # Subtotals
    base_sub     = P["base"]
    cams_sub     = total * (cam_unit or 0)
    ai_base_sub  = (P["ai_base"] if ai_enabled and (t1 + t2) > 0 else 0)
    ai_t1_sub    = t1 * (t1_unit or 0)
    ai_t2_sub    = t2 * (t2_unit or 0)

    # AI Processing Equipment
    hw_units      = ceil((t1 / T1_CAP) + (t2 / T2_CAP)) if (t1 + t2) > 0 else 0
    hw_unit_price = (HW_BASE * (1 + mu)) if hw_units > 0 else 0
    hw_sub        = hw_units * hw_unit_price

    # Storage (มี markup, ไม่นำไปคิดส่วนลด)
    storage_lines = []
    storage_sub   = 0
    if include_storage:
        if storage_tb_total is None or storage_tb_total <= 0:
            return {"status":"ERROR","message":"Please enter required Storage TB (>0)."}
        combo = choose_storage_combo(int(storage_tb_total))
        for size_tb, qty in sorted(combo.items(), reverse=True):
            unit_after_markup = STORAGE_BASE[size_tb] * (1 + mu)
            sub = qty * unit_after_markup
            storage_sub += sub
            storage_lines.append((f"HDD {size_tb} TB", qty, unit_after_markup, sub))

    # Partner Discount -20% เฉพาะ 5 รายการ: Base, Cameras, AI Base, AI T1, AI T2
    discount_base_amount = base_sub + cams_sub + ai_base_sub + ai_t1_sub + ai_t2_sub
    partner_discount = -0.20 * discount_base_amount if cust_type == "Partner" else 0

    grand = base_sub + cams_sub + ai_base_sub + ai_t1_sub + ai_t2_sub + hw_sub + storage_sub
    net   = grand + partner_discount
    ma    = P["ma_rate"] * net  # Subscription = 0

    # Build lines
    lines = [
        (f"{mode} — Base License", 1, P["base"], base_sub),
        ("Cameras", total, cam_unit or 0, cams_sub),
    ]
    if ai_enabled and (t1 + t2) > 0:
        lines.append(("AI Base License", 1, P["ai_base"], ai_base_sub))
        lines.append(("AI Licenses — Tier 1", t1, t1_unit or 0, ai_t1_sub))
        lines.append(("AI Licenses — Tier 2", t2, t2_unit or 0, ai_t2_sub))
    else:
        # แสดงว่าไม่ได้ใช้ AI
        lines.append(("AI (not enabled)", 0, 0, 0))

    lines.append(("AI Processing Equipment", hw_units, hw_unit_price, hw_sub))
    lines.extend(storage_lines)

    return {
        "status":"OK",
        "mode": mode,
        "lines":lines,
        "grand_total":grand,
        "discount":partner_discount,
        "net_total":net,
        "ma_yearly":ma,
        "ma_rate": P["ma_rate"],
    }

def thb(n):
    try: return f"{int(round(n)):,}"
    except Exception: return "-"

# =========================
# INPUTS (Live Interactive Mode)
# =========================
st.markdown("<div class='section-title'>🚀 Project Inputs</div>", unsafe_allow_html=True)

# Split columns
c1, c2 = st.columns(2)

# Pricing model + customer type
mode = c1.selectbox("Pricing Model", ["One-Time Sell", "Subscription"])
cust_type = c2.selectbox("Customer Type", ["Partner", "Non-Partner"])

# Cameras + AI usage
total = c1.number_input("Total Cameras", min_value=0, value=22, step=1)
ai_enabled = c2.selectbox("Use AI Analytics?", ["No", "Yes"], index=1) == "Yes"

# AI tiers (auto-hide if AI not used)
if ai_enabled:
    t1 = c1.number_input("AI Tier 1 Cameras", min_value=0, value=5, step=1)
    t2 = c2.number_input("AI Tier 2 Cameras", min_value=0, value=7, step=1)
else:
    t1, t2 = 0, 0

# Storage (auto-hide)
include_storage = c1.selectbox("Include Storage?", ["No", "Yes"], index=1) == "Yes"
if include_storage:
    with c2:
        # Label row with link beside label
        st.markdown(
            """
            <div style='display:flex; align-items:center; gap:10px; margin:0 0 6px 2px;'>
              <span style='font-size:14px; font-weight:600; color:#111827;'>Storage Required (TB)</span>
              <a href='https://www.jvsg.com/storage-bandwidth-calculator/'
                 target='_blank' rel='noopener noreferrer'
                 style='font-size:13px; color:#111827; text-decoration:none;'>
                 🔗 Need an estimate?
              </a>
            </div>
            """,
            unsafe_allow_html=True,
        )
        storage_tb_total = st.number_input("", min_value=1, value=8, step=1, label_visibility="collapsed")
else:
    storage_tb_total = None

# Add spacing and button
st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
submitted = st.button("Calculate ✨", use_container_width=True)


# =========================
# RESULTS
# =========================
if submitted:
    r = calc(mode, total, cust_type, ai_enabled, t1, t2, include_storage, storage_tb_total)

    if r["status"] == "ERROR":
        st.error(r["message"])
    else:
        st.balloons()
        st.markdown("<div class='section-title'>🧁 Summary</div>", unsafe_allow_html=True)
        k1, k2, k3, k4 = st.columns(4)
        with k1: st.metric("Grand Total (THB)", thb(r["grand_total"]))
        with k2: st.metric("Partner Discount",   thb(r["discount"]))
        with k3: st.metric("Net Total (THB)",    thb(r["net_total"]))
        # Subscription ไม่มี MA (แสดงเป็น 0) — ไว้เป็น option ไม่รวมยอด
        with k4: st.metric(("MA 20%/yr (THB)" if r["ma_rate"] > 0 else "MA (Subscription includes)"),
                           (thb(r["ma_yearly"]) if r["ma_rate"] > 0 else "-"))

        # Quote table
        st.markdown("<div class='section-title'>🧾 Quote Table</div>", unsafe_allow_html=True)
        line_rows = [
            {"Item": n, "Qty": q, "Unit Price (THB)": (thb(u) if u else "-"), "Subtotal (THB)": (thb(s) if s else "-")}
            for (n, q, u, s) in r["lines"] if not (q == 0 and s == 0 and "not enabled" in str(n))
        ]
        totals_rows = [
            {"Item":"", "Qty":"", "Unit Price (THB)":"", "Subtotal (THB)":""},
            {"Item":"Grand Total (THB)",      "Qty":"", "Unit Price (THB)":"", "Subtotal (THB)": thb(r["grand_total"])},
            {"Item":"Partner Discount (THB)", "Qty":"", "Unit Price (THB)":"", "Subtotal (THB)": thb(r["discount"])},
            {"Item":"Net Total (THB)",        "Qty":"", "Unit Price (THB)":"", "Subtotal (THB)": thb(r["net_total"])},
        ]
        # MA แสดงเป็น option ด้านล่างสุด ไม่รวมยอด
        if r["ma_rate"] > 0:
            totals_rows.append({"Item":"MA 20%/yr (info)", "Qty":"", "Unit Price (THB)":"", "Subtotal (THB)": thb(r["ma_yearly"])})
        else:
            totals_rows.append({"Item":"Warranty & Maintenance", "Qty":"", "Unit Price (THB)":"",
                                "Subtotal (THB)":"Included in Subscription (not charged)"})

        quote_df = pd.DataFrame(line_rows + totals_rows)
        st.dataframe(quote_df, use_container_width=True)

        # Excel export
        def build_excel(df: pd.DataFrame) -> bytes:
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                df.to_excel(writer, sheet_name="Quote", index=False)
                ws = writer.sheets["Quote"]
                for i, col in enumerate(df.columns):
                    width = max(14, int(df[col].astype(str).map(len).max()) + 2)
                    ws.set_column(i, i, width)
            return buffer.getvalue()

        xlsx_bytes = build_excel(quote_df)
        st.download_button(
            "📥 Download Quote",
            data=xlsx_bytes,
            file_name=f"SCM_Quote_{date.today().isoformat()}_{'SUB' if mode=='Subscription' else 'OT'}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

# Footer
st.markdown(
    "<div style='text-align:center;color:#6B7280;font-size:12px;margin-top:10px;'>Made with 💜 • For custom scopes, contact Solutions Team.</div>",
    unsafe_allow_html=True,
)
