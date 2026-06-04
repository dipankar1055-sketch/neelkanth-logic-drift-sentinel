import streamlit as st
import pandas as pd
import uuid
from datetime import datetime

# ---------- Page Setup ----------
st.set_page_config(page_title="Neelkanth Protocol MVP", layout="wide")
st.title("🧠 Neelkanth Protocol – MVP V1.0")
st.caption("Governance‑as‑Code · Logic Drift · Human‑on‑the‑Loop · Immutable Audit Trail")

# ---------- Session State (Audit Log) ----------
if "audit_log" not in st.session_state:
    st.session_state.audit_log = pd.DataFrame(columns=[
        "Timestamp", "Trace‑ID", "HAT‑ID", "LOB", "Risk Score", "Drift %", "Decision", "Reviewer"
    ])

# ---------- Drift Detection Rules ----------
def detect_drift(amount, jurisdiction, risk_score):
    reasons = []
    decision = "APPROVE"
    hat_required = False

    # Rule 1: Risk Score > 80 = ESCALATE
    if risk_score > 80:
        reasons.append("Risk Score > 80")
        decision = "ESCALATE"
        hat_required = True

    # Rule 2: Amount > 1,00,000 = HOLD
    if amount > 100000:
        reasons.append("Amount > ₹1,00,000")
        if decision != "ESCALATE":
            decision = "HOLD"
        hat_required = True

    # Rule 3: High‑Risk Jurisdiction = ESCALATE
    high_risk_zones = ["High‑Risk", "Sanctioned", "Embargoed"]
    if jurisdiction in high_risk_zones:
        reasons.append(f"Jurisdiction = {jurisdiction}")
        decision = "ESCALATE"
        hat_required = True

    # Drift % (just for display)
    drift_percent = min(len(reasons) * 1.5, 10.0)
    return drift_percent, decision, hat_required, reasons

# ---------- ID Generators ----------
def generate_trace_id():
    return str(uuid.uuid4())[:8].upper()

def generate_hat_id():
    return f"HAT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"

def add_to_audit(trace_id, hat_id, lob, risk_score, drift, decision, reviewer):
    new_row = pd.DataFrame([{
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Trace‑ID": trace_id,
        "HAT‑ID": hat_id,
        "LOB": lob,
        "Risk Score": risk_score,
        "Drift %": drift,
        "Decision": decision,
        "Reviewer": reviewer
    }])
    st.session_state.audit_log = pd.concat([st.session_state.audit_log, new_row], ignore_index=True)

# ---------- Input Form ----------
with st.form("transaction_form"):
    st.subheader("📝 Transaction Input")
    col1, col2 = st.columns(2)

    with col1:
        amount = st.number_input("Transaction Amount (₹)", min_value=0, step=1000, value=50000)
        jurisdiction = st.selectbox("Jurisdiction", ["Low‑Risk", "Medium‑Risk", "High‑Risk", "Sanctioned"])
        lob = st.selectbox("Line of Business", ["Credit Card", "Insurance", "Mortgage", "Crypto/Fraud", "AI Help Desk", "O2C"])

    with col2:
        risk_score = st.slider("Risk Score (0–100)", 0, 100, 50)
        reviewer = st.text_input("Reviewer Name (HITL)", placeholder="e.g., TIGER or your name")

    submitted = st.form_submit_button("🚀 Submit Transaction")

# ---------- Process Transaction ----------
if submitted:
    if not reviewer.strip():
        st.error("❌ Reviewer name is required.")
        st.stop()

    drift_percent, decision, hat_required, reasons = detect_drift(amount, jurisdiction, risk_score)
    trace_id = generate_trace_id()
    hat_id = generate_hat_id() if hat_required else "AUTO‑APPROVED"

    st.subheader("⚙️ Governance Engine Output")
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Trace‑ID", trace_id)
    col_b.metric("HAT‑ID", hat_id if hat_required else "No HAT needed")
    col_c.metric("Logic Drift %", f"{drift_percent:.1f}%")
    st.write("**Drift triggers:**", ", ".join(reasons) if reasons else "No drift")
    st.write("**Decision:**", f"🔴 {decision}" if decision != "APPROVE" else f"🟢 {decision}")

    if hat_required:
        st.warning("⚠️ Human attestation required. Click below to approve.")
        if st.button("✍️ Attest & Generate HAT‑ID"):
            final_hat = generate_hat_id()
            add_to_audit(trace_id, final_hat, lob, risk_score, drift_percent, decision, reviewer)
            st.success(f"✅ Attested! HAT‑ID: {final_hat} | Logged to audit.")
            st.rerun()
    else:
        add_to_audit(trace_id, hat_id, lob, risk_score, drift_percent, decision, reviewer)
        st.success("✅ Decision auto‑logged (no HAT required).")

# ---------- Audit Trail ----------
st.subheader("📋 Audit Trail")
if not st.session_state.audit_log.empty:
    st.dataframe(st.session_state.audit_log, use_container_width=True)
    st.caption(f"Total decisions: {len(st.session_state.audit_log)}")
else:
    st.info("No decisions yet. Submit a transaction.")

# ---------- Mock Foundry IQ ----------
with st.expander("📚 Foundry IQ – Policy Citations (Mock)", expanded=False):
    st.markdown("""
    **KYC Policy:** `KYC-POL-2026-02` – High‑risk jurisdictions require enhanced due diligence.  
    **AML Policy:** `AML-POL-2026-17` – Transactions > ₹1,00,000 need HITL attestation.  
    **RBI Guidelines:** Digital lending & KYC norms (Sept 2025).
    """)

# ---------- Sidebar ----------
st.sidebar.header("📊 Summary")
st.sidebar.metric("Audit Log Size", len(st.session_state.audit_log))
st.sidebar.markdown("**Active Drift Rules**")
st.sidebar.markdown("""
- Risk > 80 → ESCALATE
- Amount > ₹1L → HOLD
- High‑Risk Jurisdiction → ESCALATE
- Multiple triggers → HOLD + HAT
""")
