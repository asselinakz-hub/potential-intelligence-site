import datetime as dt
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Sales Ramp Diagnostic | Potential Intelligence™",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

LANDING_URL = "https://asselinakz-hub.github.io/potential-intelligence-site/"
MANAGER_REPORT_URL = "https://asselinakz-hub.github.io/potential-intelligence-site/reports/manager_report.html"
CONTACT_EMAIL = "Asselina.kz@gmail.com"

st.markdown("""
<style>
#MainMenu, footer {visibility:hidden;}
[data-testid="stHeader"] {background:transparent;}
.stApp {background:radial-gradient(circle at 80% -10%, rgba(231,182,75,.14), transparent 34%), #0b0d12; color:#f7f1e6;}
.block-container {max-width:920px; padding-top:28px; padding-bottom:58px;}
h1 {font-size:clamp(40px,6vw,62px)!important; line-height:.98!important; letter-spacing:-.055em!important;}
h2,h3 {letter-spacing:-.035em!important;}
p, label, span, div, .stMarkdown, [data-testid="stWidgetLabel"] p {color:#eef3fb!important; opacity:1!important;}
.stRadio label span, .stCheckbox label span {color:#dce5f3!important; opacity:1!important;}
.stSelectbox div, .stMultiSelect div, .stTextInput input, .stTextArea textarea {color:#111827!important;}
.pi-top {display:flex; justify-content:space-between; gap:16px; align-items:center; margin-bottom:34px; padding-bottom:16px; border-bottom:1px solid rgba(255,255,255,.1);}
.pi-brand {font-weight:900; font-size:20px; letter-spacing:-.03em;}.pi-brand span{color:#e7b64b!important;}
.pi-home {border:1px solid rgba(255,255,255,.18); color:#f7f1e6!important; text-decoration:none!important; padding:10px 14px; border-radius:999px; font-weight:800; font-size:13px;}
.pi-eyebrow {display:inline-flex; padding:7px 12px; border-radius:999px; background:rgba(231,182,75,.1); border:1px solid rgba(231,182,75,.22); color:#f4cf75!important; font-weight:900; font-size:12px; letter-spacing:.12em; text-transform:uppercase; margin-bottom:16px;}
.pi-subtitle {font-size:21px; line-height:1.45; color:#c9d3e4!important; max-width:780px; margin:12px 0 12px;}
.pi-note {color:#aab6ca!important; font-size:15px; line-height:1.5; max-width:780px; margin-bottom:28px;}
.pi-card {background:rgba(255,255,255,.045); border:1px solid rgba(255,255,255,.12); border-radius:20px; padding:20px; height:100%;}
.pi-card p, .pi-muted {color:#c9d3e4!important;}
.pi-output {border-left:4px solid #e7b64b; background:rgba(255,255,255,.06); border-radius:16px; padding:18px 20px; margin:14px 0;}
.pi-label {font-size:12px; text-transform:uppercase; letter-spacing:.12em; color:#f4cf75!important; font-weight:900;}
.pi-btn {display:inline-block; background:#e7b64b; color:#10131b!important; text-decoration:none!important; padding:13px 18px; border-radius:999px; font-weight:900; margin:6px 8px 6px 0;}
.pi-btn2 {display:inline-block; border:1px solid rgba(255,255,255,.18); color:#f7f1e6!important; text-decoration:none!important; padding:13px 18px; border-radius:999px; font-weight:800; margin:6px 8px 6px 0;}
.stFormSubmitButton > button {background:#e7b64b!important; color:#10131b!important; border:0!important; border-radius:999px!important; padding:.8rem 1.35rem!important; font-weight:900!important;}
hr {border-color:rgba(255,255,255,.1)!important;}
@media(max-width:760px){.pi-top{flex-direction:column; align-items:flex-start;}}
</style>
""", unsafe_allow_html=True)

PATTERNS = {
    "Momentum Breakdown": {
        "short": "Reps may create interest, but deals slow down before clear next steps or commitment.",
        "action": "In the next 1:1, review one stalled deal and ask: where exactly did momentum drop? Then test one clear next-step commitment script."
    },
    "Trust-Building Gap": {
        "short": "Buyers may not feel enough clarity, credibility, or confidence to move forward.",
        "action": "Coach the rep to restate the buyer’s problem in the buyer’s own words before pitching."
    },
    "Pressure Response Issue": {
        "short": "Execution may change when the conversation becomes uncomfortable: pricing, objections, urgency, or closing.",
        "action": "Role-play only the uncomfortable moment. Ask: what part of the conversation did you avoid because it felt risky?"
    },
    "Structure / Manager-Support Mismatch": {
        "short": "The rep may need a different mix of structure, autonomy, feedback, or prioritization.",
        "action": "Set one weekly success definition and one checkpoint. Ask: what needs to be true by Friday for this to be on track?"
    },
    "Role-Fit Friction": {
        "short": "Parts of the role may require execution patterns that cost too much energy or do not come naturally.",
        "action": "Map the strongest and weakest sales-cycle stage. Coach the weak stage or pair the rep with someone complementary."
    },
}

def bump(scores, key, value=1):
    scores[key] = scores.get(key, 0) + value

def calculate(answers):
    scores = {k: 0 for k in PATTERNS}
    for item in answers["challenge"]:
        if "move deals" in item or "follow-up" in item:
            bump(scores, "Momentum Breakdown", 2)
        if "avoid difficult" in item:
            bump(scores, "Pressure Response Issue", 2)
        if "varies" in item:
            bump(scores, "Role-Fit Friction", 1)
        if "take too long" in item:
            bump(scores, "Structure / Manager-Support Mismatch", 1)
    if answers["stage"] in ["After a positive first conversation", "After demo / presentation", "Follow-up / next step", "Closing"]:
        bump(scores, "Momentum Breakdown", 2)
    if answers["stage"] in ["Discovery", "Prospecting / first contact"]:
        bump(scores, "Trust-Building Gap", 1)
    if answers["stage"] in ["Pricing / negotiation", "Closing"]:
        bump(scores, "Pressure Response Issue", 2)
    if "active" in answers["familiar"]:
        bump(scores, "Momentum Breakdown", 2)
    if "avoid closing" in answers["familiar"]:
        bump(scores, "Pressure Response Issue", 2)
    if "manager direction" in answers["familiar"]:
        bump(scores, "Structure / Manager-Support Mismatch", 2)
    if "interview" in answers["familiar"]:
        bump(scores, "Role-Fit Friction", 2)
    if answers["likely"] == "Trust-building with buyers":
        bump(scores, "Trust-Building Gap", 3)
    if answers["likely"] == "Pressure / confidence":
        bump(scores, "Pressure Response Issue", 3)
    if answers["likely"] == "Manager support" or answers["likely"] == "Lack of structure":
        bump(scores, "Structure / Manager-Support Mismatch", 3)
    if answers["likely"] == "Role fit":
        bump(scores, "Role-Fit Friction", 3)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)

def pilot_fit(role, manage, useful, pilot):
    score = 0
    if role in ["VP Sales / Head of Sales", "Sales Manager", "CRO / Revenue Leader"]: score += 3
    elif role in ["Founder", "Sales Enablement"]: score += 2
    if manage != "No": score += 2
    if useful >= 4: score += 2
    if pilot == "Yes, I’d like to test it": score += 3
    elif pilot == "Maybe, send me more information": score += 1
    if score >= 9: return "Strong pilot fit", score
    if score >= 6: return "Possible pilot fit", score
    return "Research / future fit", score

st.markdown(f"""
<div class="pi-top">
  <div class="pi-brand">Potential <span>Intelligence™</span></div>
  <a class="pi-home" href="{LANDING_URL}" target="_blank">Back to landing</a>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="pi-eyebrow">5-minute diagnostic</div>', unsafe_allow_html=True)
st.title("Where does sales execution break?")
st.markdown('<div class="pi-subtitle">Answer short questions about ramp, coaching, and deal momentum. Get a possible friction pattern and one manager action to test next.</div>', unsafe_allow_html=True)
st.markdown('<div class="pi-note">Not a personality test. Not a performance evaluation. Built for VP Sales, Sales Managers, and GTM leaders.</div>', unsafe_allow_html=True)

with st.form("diagnostic"):
    st.subheader("1. About you")
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("Your name *")
        email = st.text_input("Work email *")
        role = st.selectbox("Your role", ["VP Sales / Head of Sales", "Sales Manager", "CRO / Revenue Leader", "Founder", "Sales Enablement", "HR / People / L&D", "Other"])
    with c2:
        company = st.text_input("Company")
        size = st.selectbox("Company size", ["1–10", "11–50", "51–200", "201–500", "501–1000", "1000+", "Not sure"])
        manage = st.selectbox("Do you manage or support sales reps?", ["Yes, I directly manage reps", "Yes, I support sales managers / enablement", "Not directly, but I’m involved in sales performance", "No"])

    st.subheader("2. Sales ramp problem")
    challenge = st.multiselect("Biggest challenge right now", ["New hires take too long to become productive", "Reps know the process but do not execute consistently", "Reps create interest but do not move deals forward", "Reps struggle with follow-up / next steps", "Reps avoid difficult conversations", "Performance varies too much between similar reps", "Other"])
    stage = st.radio("Where do deals most often lose momentum?", ["Prospecting / first contact", "Discovery", "After a positive first conversation", "After demo / presentation", "Follow-up / next step", "Pricing / negotiation", "Closing", "Hard to tell"])
    familiar = st.radio("Which statement feels most familiar?", ["They know what to do, but they don’t do it consistently.", "They are active, but deals don’t move.", "They are good with people, but avoid closing.", "They understand the product, but don’t create urgency.", "They need too much manager direction.", "They looked strong in interview but struggle in the role."])

    st.subheader("3. What would be useful?")
    likely = st.radio("What do you think the issue usually is?", ["Skill gap", "Motivation / effort", "Role fit", "Manager support", "Pressure / confidence", "Lack of structure", "Trust-building with buyers", "Not sure"])
    useful = st.slider("How useful would it be to know where each rep’s execution breaks?", 1, 5, 4)
    pilot = st.radio("Would you be open to testing a free pilot with 1–3 reps?", ["Yes, I’d like to test it", "Maybe, send me more information", "Not now", "I’m not the right person"])
    comments = st.text_area("Optional note", height=80)
    submit = st.form_submit_button("See my diagnostic result")

if submit:
    if not name or not email:
        st.error("Please add your name and work email.")
        st.stop()
    answers = {"timestamp_utc": dt.datetime.utcnow().isoformat(timespec="seconds"), "name": name, "email": email, "role": role, "company": company, "company_size": size, "manage_reps": manage, "challenge": challenge, "stage": stage, "familiar": familiar, "likely": likely, "usefulness": useful, "pilot_interest": pilot, "comments": comments}
    ranked = calculate(answers)
    top, top_score = ranked[0]
    second, second_score = ranked[1]
    fit, score = pilot_fit(role, manage, useful, pilot)
    data = PATTERNS[top]
    st.success("Diagnostic complete.")
    st.markdown('<div class="pi-label">Possible friction pattern</div>', unsafe_allow_html=True)
    st.markdown(f"## {top}")
    st.markdown(f"""
    <div class="pi-output">
      <p class="pi-muted">{data['short']}</p>
      <p><b>Manager action to test next:</b><br>{data['action']}</p>
      <p class="pi-muted"><b>Secondary signal:</b> {second}</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="pi-label">Pilot qualification</div>', unsafe_allow_html=True)
    st.markdown(f"### {fit}")
    st.write("If this feels useful, the next step is a small voluntary pilot with 1–3 reps and a Manager Action Report.")
    st.markdown(f'<a class="pi-btn" href="mailto:{CONTACT_EMAIL}">Request small pilot</a><a class="pi-btn2" href="{MANAGER_REPORT_URL}" target="_blank">View Manager Action sample</a>', unsafe_allow_html=True)
    row = {**answers, "top_pattern": top, "top_score": top_score, "second_pattern": second, "second_score": second_score, "pilot_fit": fit, "icp_score": score}
    row = {k: "; ".join(v) if isinstance(v, list) else v for k, v in row.items()}
    df = pd.DataFrame([row])
    st.download_button("Download response as CSV", df.to_csv(index=False).encode("utf-8"), "sales_ramp_diagnostic_response.csv", "text/csv")
else:
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown("<div class='pi-card'><h3>1. Answer</h3><p>8 short questions.</p></div>", unsafe_allow_html=True)
    with c2: st.markdown("<div class='pi-card'><h3>2. See signal</h3><p>Possible friction pattern.</p></div>", unsafe_allow_html=True)
    with c3: st.markdown("<div class='pi-card'><h3>3. Decide</h3><p>Request pilot only if useful.</p></div>", unsafe_allow_html=True)
    st.markdown(f'<a class="pi-btn2" href="{MANAGER_REPORT_URL}" target="_blank">View Manager Action sample</a>', unsafe_allow_html=True)
