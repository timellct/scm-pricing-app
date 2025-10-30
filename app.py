# =========================
# INPUTS (Updated with "🔗 Need an estimation?" link)
# =========================
st.markdown("<div class='section-title'>🚀 Project Inputs</div>", unsafe_allow_html=True)

# Use session state to allow dynamic updates without full form refresh
if "ai_enabled" not in st.session_state:
    st.session_state.ai_enabled = True
if "include_storage" not in st.session_state:
    st.session_state.include_storage = True

# Main layout
c1, c2 = st.columns(2)

# Pricing model & customer type
mode = c1.selectbox("Pricing Model", ["One-Time Sell", "Subscription"])
cust_type = c2.selectbox("Customer Type", ["Partner", "Non-Partner"])

# Cameras
total = c1.number_input("Total Cameras", min_value=0, value=22, step=1)

# AI Analytics toggle (default Yes)
ai_enabled = c2.selectbox(
    "Use AI Analytics?",
    ["No", "Yes"],
    index=1,
    key="ai_enabled_box"
) == "Yes"
st.session_state.ai_enabled = ai_enabled

# AI Tier Inputs — show only if AI enabled
if ai_enabled:
    t1 = c1.number_input("AI Tier 1 Cameras", min_value=0, value=5, step=1)
    t2 = c2.number_input("AI Tier 2 Cameras", min_value=0, value=7, step=1)
else:
    t1, t2 = 0, 0
    c1.write("")  # keep spacing aligned
    c2.write("")

# Storage toggle (default Yes)
include_storage = c1.selectbox(
    "Include Storage?",
    ["No", "Yes"],
    index=1,
    key="include_storage_box"
) == "Yes"
st.session_state.include_storage = include_storage

# Storage TB input + link (show only if included)
if include_storage:
    with c2:
        # Label row with underlined link text
        st.markdown(
            """
            <div style='display:flex; align-items:center; gap:10px; margin:0 0 6px 2px;'>
              <span style='font-size:14px; font-weight:600; color:#111827;'>Storage Required (TB)</span>
              <a href='https://www.jvsg.com/storage-bandwidth-calculator/'
                 target='_blank' rel='noopener noreferrer'
                 style='font-size:13px; color:#111827; text-decoration: underline; font-weight:600;'>
                 🔗 Need an estimation?
              </a>
            </div>
            """,
            unsafe_allow_html=True,
        )
        storage_tb_total = st.number_input(
            label="",
            min_value=1, value=8, step=1,
            label_visibility="collapsed"
        )
else:
    storage_tb_total = None
    c2.write("")

# Calculate button
submitted = st.button("Calculate ✨", use_container_width=True)
