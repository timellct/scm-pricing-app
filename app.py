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
FAVICON    = "🎀"

st.set_page_config(
    page_title=f"{BRAND_NAME} — {TAGLINE}",
    page_icon=FAVICON,
    layout="centered",
    initial_sidebar_state="collapsed",
)

# =========================
# GLOBAL STYLES
# =========================
st.markdown(
    f"""
    <style>
      /* ===== Minimal inputs: single clean border for all fields ===== */

/* COMMON: label/text */
label, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
.stMarkdown h4, .stMarkdown h5, .stMarkdown h6 { color:#111827 !important; }

/* 1) NUMBER & TEXT INPUT (outer wrapper) */
div[data-baseweb="input"] > div {
  background:#FFFFFF !important;
  color:#111827 !important;
  border:1px solid #111827 !important;   /* เส้นเดียวบาง */
  border-radius:12px !important;
  box-shadow:none !important;
  outline:none !important;
  overflow:hidden;                        /* ตัดขอบซ้อนของชั้นใน */
}

/* ตัดเส้น/เงาของชั้นในทั้งหมด */
div[data-baseweb="input"] > div > div {
  border:0 !important;
  box-shadow:none !important;
  background:transparent !important;
}

/* ตัวอักษรในช่อง */
div[data-baseweb="input"] input {
  color:#111827 !important;
  background:#FFFFFF !important;
}

/* ปุ่ม +/- (stepper) ให้ดูกลืน ๆ พร้อมเส้นคั่นเดียว */
div[data-baseweb="input"] [role="button"] {
  border-left:1px solid #111827 !important;   /* เส้นคั่นเดียวทางขวา */
  box-shadow:none !important;
}

/* 2) SELECT (Customer Type / Include Storage) */
div[data-baseweb="select"] > div {
  background:#FFFFFF !important;
  color:#111827 !important;
  border:1px solid #111827 !important;   /* เส้นเดียวบาง */
  border-radius:12px !important;
  box-shadow:none !important;
  outline:none !important;
  overflow:hidden;                        /* ตัดขอบซ้อน */
}

/* ตัดเส้นของชั้นใน select ทั้งหมด */
div[data-baseweb="select"] > div > div {
  border:0 !important;
  box-shadow:none !important;
  background:transparent !important;
}

/* caret (ลูกศร) เข้มชัด */
div[data-baseweb="select"] svg { color:#111827 !important; opacity:1 !important; }
div[data-baseweb="select"] svg path { fill:#111827 !important; }

/* เมนูที่ดรอปลงมา */
div[role="listbox"]   { background:#FFFFFF !important; border:1px solid #111827 !important; }
div[role="listbox"] * { color:#111827 !important; }

/* 3) ปุ่มกดหลัก */
.stButton > button {
  background:#111827 !important;
  color:#FFFFFF !important;
  border:0 !important;
  border-radius:12px !important;
  padding:12px 18px !important;
  box-shadow:none !important;
}
.stButton > button:hover { filter:brightness(1.05); }

/* 4) ตาราง/เมตริกให้ตัวอักษรอ่านง่าย */
[data-testid="stMetricValue"], [data-testid="stMetricLabel"] { color:#111827 !important; }
[data-testid="stDataFrame"] * { color:#111827 !important; }

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

# Storage base (ก่อนบวกมาร์กอัป)
STORAGE_BASE = {1:1670, 2:2030, 4:2930, 6:4990, 8:6890, 10:10990}

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
    return None  # exceeds max -> contact sales

def choose_storage_combo(required_tb: int):
    """
    เลือกชุด HDD ให้ความจุรวม >= required_tb
    กติกา: ปัดขึ้นด้วย SKU เล็กสุดที่ครอบคลุม (เช่น 15TB -> 10TB + 6TB = 16TB)
    """
    if required_tb <= 0: return {}
    sizes_sorted = sorted(STORAGE_BASE.keys())  # [1,2,4,6,8,10]
    combo, remaining = {}, required_tb
    while remaining > 0:
        if remaining > sizes_sorted[-1]:
            pick = sizes_sorted[-1]             # 10 TB
        else:
            pick = next(s for s in sizes_sorted if s >= remaining)
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
    mu       = SI_MU if cust_type == "SI" else NONSI_MU

    base_sub     = BASE_LICENSE
    cams_sub     = total * (cam_unit or 0)
    ai_base_sub  = (1 if t1 + t2 > 0 else 0) * AI_BASE_LICENSE
    ai_t1_sub    = t1 * (t1_unit or 0)
    ai_t2_sub    = t2 * (t2_unit or 0)

    hw_units      = ceil((t1 / T1_CAP) + (t2 / T2_CAP)) if (t1 + t2) > 0 else 0
    hw_unit_price = (HW_BASE * (1 + mu)) if hw_units > 0 else 0
    hw_sub        = hw_units * hw_unit_price

    storage_lines = []
    storage_sub   = 0
    if include_storage:
        if storage_tb_total is None or storage_tb_total <= 0:
            return {"status":"ERROR","message":"Please enter required Storage TB (>0)."}
        combo = choose_storage_combo(int(storage_tb_total))
        for size_tb, qty in sorted(combo.items(), reverse=True):
            unit_after_markup = STORAGE_BASE[size_tb] * (1 + mu)  # บวกมาร์กอัป
            sub = qty * unit_after_markup
            storage_sub += sub
            storage_lines.append((f"HDD {size_tb} TB", qty, unit_after_markup, sub))

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
    ]
    lines.extend(storage_lines)

    return {"status":"OK","lines":lines,"grand_total":grand,"discount":discount,"net_total":net,"ma_yearly":ma}

def thb(n):
    try: return f"{int(round(n)):,}"
    except Exception: return "-"

# =========================
# INPUTS
# =========================
st.markdown("<div class='section-title'>🧁 Project Inputs</div>", unsafe_allow_html=True)
with st.form("inputs", border=False):
    c1, c2 = st.columns(2)
    total = c1.number_input("Total Cameras", min_value=0, value=22, step=1)
    cust_type = c2.selectbox("Customer Type", ["SI", "Non-SI"])
    t1 = c1.number_input("AI Tier 1 Cameras", min_value=0, value=5, step=1)
    t2 = c2.number_input("AI Tier 2 Cameras", min_value=0, value=7, step=1)
    include_storage = c1.selectbox("Include Storage?", ["No", "Yes"]) == "Yes"
    storage_tb_total = c2.number_input("Storage Required (TB)", min_value=1, value=8, step=1) if include_storage else None
    submitted = st.form_submit_button("Calculate ✨", use_container_width=True)

# =========================
# RESULTS
# =========================
if submitted:
    r = calc(total, cust_type, t1, t2, include_storage, storage_tb_total)

    if r["status"] == "ERROR":
        st.error(r["message"])

    elif r["status"] == "CONTACT_SALES":
        st.markdown(
            "<div class='section-title'>📞 Contact Sales</div>"
            "<div>Totals are hidden for projects with more than 100 cameras or any AI tier above 100.</div>",
            unsafe_allow_html=True,
        )
        st.subheader("Grand Total")
        st.write("CONTACT SALES")

    else:
        st.balloons()

        # Summary metrics
        st.markdown("<div class='section-title'>🧁 Summary</div>", unsafe_allow_html=True)
        k1, k2, k3, k4 = st.columns(4)
        with k1: st.metric("Grand Total (THB)", thb(r["grand_total"]))
        with k2: st.metric("Partner Discount",   thb(r["discount"]))
        with k3: st.metric("Net Total (THB)",    thb(r["net_total"]))
        with k4: st.metric("MA 20%/yr (THB)",    thb(r["ma_yearly"]))

        # Quote table
        st.markdown("<div class='section-title'>🧾 Quote Table</div>", unsafe_allow_html=True)
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

        # Excel (ONE sheet named "Quote")
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
