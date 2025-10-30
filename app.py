# =========================
# INPUTS
# =========================
st.markdown("<div class='section-title'>🚀 Project Inputs</div>", unsafe_allow_html=True)
with st.form("inputs", border=False):
    c1, c2 = st.columns(2)

    # Pricing model + customer type
    mode = c1.selectbox("Pricing Model", ["One-Time Sell", "Subscription"])
    cust_type = c2.selectbox("Customer Type", ["Partner", "Non-Partner"])

    # Cameras + AI usage
    total = c1.number_input("Total Cameras", min_value=0, value=22, step=1)
    # DEFAULT = Yes (index=1 in ["No","Yes"])
    ai_enabled = c2.selectbox("Use AI Analytics?", ["No", "Yes"], index=1) == "Yes"

    # AI tiers (disabled if not using AI)
    t1 = c1.number_input("AI Tier 1 Cameras", min_value=0, value=5, step=1, disabled=not ai_enabled)
    t2 = c2.number_input("AI Tier 2 Cameras", min_value=0, value=7, step=1, disabled=not ai_enabled)

    # Storage (DEFAULT = Yes)
    include_storage = c1.selectbox("Include Storage?", ["No", "Yes"], index=1) == "Yes"
    if include_storage:
        with c2:
            # Custom label row: text + link (inline at the label)
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
            storage_tb_total = st.number_input(
                label="",
                min_value=1, value=8, step=1,
                label_visibility="collapsed"
            )
    else:
        storage_tb_total = None

    submitted = st.form_submit_button("Calculate ✨", use_container_width=True)
