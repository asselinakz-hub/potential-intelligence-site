import datetime as dt
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Sales Ramp Diagnostic | Potential Intelligence™",
    page_icon="✦",
    layout="centered",
    initial_sidebar_state="collapsed",
)

LANDING_URL = "https://asselinakz-hub.github.io/potential-intelligence-site/"
MANAGER_REPORT_URL = "https://asselinakz-hub.github.io/potential-intelligence-site/reports/manager_report.html"
CONTACT_EMAIL = "Asselina.kz@gmail.com"

st.markdown("""
<style>
#MainMenu, footer {visibility:hidden;}
[data-testid="stHeader"] {background:transparent;}
.stApp {
  background: radial-gradient(circle at 82% -12%, rgba(231,182,75,.13), transparent 32%), #0b0d12;
  color:#f7f1e6;
}
.block-container {max-width:900px; padding-top:26px; padding-bottom:58px;}

/* Strong dark-theme readability overrides */
.stApp h1, .stApp h2, .stApp h3, .stApp h4,
.stApp p, .stApp label, .stApp span,
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p,
[data-testid="stRadio"] label,
[data-testid="stRadio"] label p,
[data-testid="stRadio"] span,
[data-testid="stCheckbox"] label,
[data-testid="stCheckbox"] label p,
[data-testid="stMultiSelect"] label,
[data-testid="stSelectbox"] label {
  color:#f1f5fb!important;
  opacity:1!important;
}
[data-testid="stWidgetLabel"] p {font-weight:800!important; color:#f7f1e6!important;}

/* Keep form inputs readable on light input backgrounds */
.stTextInput input, .stTextArea textarea,
[data-baseweb="select"] div,
[data-baseweb="select"] span,
[data-baseweb="select"] input {
  color:#111827!important;
}
[data-baseweb="popover"] div, [data-baseweb="menu"] div {color:#111827!important;}

h1 {font-size:clamp(36px,6vw,56px)!important; line-height:1!important; letter-spacing:-.055em!important; margin-bottom:8px!important;}
h2,h3 {letter-spacing:-.035em!important;}
hr {border-color:rgba(255,255,255,.10)!important; margin:24px 0!important;}

.pi-top {display:flex; justify-content:space-between; gap:16px; align-items:center; margin-bottom:28px; padding-bottom:14px; border-bottom:1px solid rgba(255,255,255,.10);}
.pi-brand {font-weight:900; font-size:20px; letter-spacing:-.03em; color:#f7f1e6!important;}
.pi-brand span{color:#e7b64b!important;}
.pi-home {border:1px solid rgba(255,255,255,.18); color:#f7f1e6!important; text-decoration:none!important; padding:10px 14px; border-radius:999px; font-weight:800; font-size:13px;}
.pi-eyebrow {display:inline-flex; padding:7px 12px; border-radius:999px; background:rgba(231,182,75,.1); border:1px solid rgba(231,182,75,.22); color:#f4cf75!important; font-weight:900; font-size:12px; letter-spacing:.12em; text-transform:uppercase; margin-bottom:14px;}
.pi-subtitle {font-size:19px; line-height:1.45; color:#cfd8e8!important; max-width:760px; margin:10px 0 8px;}
.pi-note {color:#aeb9cb!important; font-size:14px; line-height:1.45; max-width:760px; margin-bottom:20px;}
.pi-output {border-left:4px solid #e7b64b; background:rgba(255,255,255,.065); border-radius:16px; padding:18px 20px; margin:14px 0;}
.pi-output p, .pi-muted {color:#d6deeb!important;}
.pi-label {font-size:12px; text-transform:uppercase; letter-spacing:.12em; color:#f4cf75!important; font-weight:900; margin-top:16px;}
.pi-btn {display:inline-block; background:#e7b64b; color:#10131b!important; text-decoration:none!important; padding:13px 18px; border-radius:999px; font-weight:900; margin:6px 8px 6px 0;}
.pi-btn2 {display:inline-block; border:1px solid rgba(255,255,255,.22); color:#f7f1e6!important; text-decoration:none!important; padding:13px 18px; border-radius:999px; font-weight:800; margin:6px 8px 6px 0;}
.stFormSubmitButton > button {background:#e7b64b!important; color:#10131b!important; border:0!important; border-radius:999px!important; padding:.8rem 1.35rem!important; font-weight:900!important;}
.stDownloadButton > button {border-radius:999px!important;}

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
    if answers["likely"] in ["Manager support", "Lack of structure"]:
        bump(scores, "Structure / Manager-Support Mismatch", 3)
    if answers["likely"] == "Role fit":
        bump(scores, "Role-Fit Friction", 3)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)

def pilot_fit(role, manage, useful, pilot):
    score = 0
    if role in ["VP Sales / Head of Sales", "Sales Manager", "CRO / Revenue Leader"]:
        score += 3
    elif role in ["Founder", "Sales Enablement"]:
        score += 2
    if manage != "No":
        score += 2
    if useful >= 4:
        score += 2
    if pilot == "Yes, I’d like to test it":
        score += 3
    elif pilot == "Maybe, send me more information":
        score += 1
    if score >= 9:
        return "Strong pilot fit", score
    if score >= 6:
        return "Possible pilot fit", score
    return "Research / future fit", score

st.markdown(f"""
<div class="pi-top">
  <div class="pi-brand">Potential <span>Intelligence™</span></div>
  <a class="pi-home" href="{LANDING_URL}" target="_blank">Back to landing</a>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="pi-eyebrow">5-minute diagnostic</div>', unsafe_allow_html=True)
st.title("Where does sales execution break?")
st.markdown('<div class="pi-subtitle">Answer 7 quick questions. Get a possible friction pattern and one manager action to test next.</div>', unsafe_allow_html=True)
st.markdown('<div class="pi-note">For sales leaders. Not a personality test. Not a performance evaluation.</div>', unsafe_allow_html=True)

with st.form("diagnostic"):
    st.subheader("1. About you")
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("Your name *")
        email = st.text_input("Work email *")
        role = st.selectbox("Your role", ["VP Sales / Head of Sales", "Sales Manager", "CRO / Revenue Leader", "Founder", "Sales Enablement", "HR / People / L&D", "Other"])
    with c2:
        company = st.text_input("Company")
        manage = st.selectbox("Do you manage or support sales reps?", ["Yes, I directly manage reps", "Yes, I support sales managers / enablement", "Not directly, but I’m involved in sales performance", "No"])

    st.subheader("2. Sales ramp problem")
    challenge = st.multiselect("Biggest challenge right now", ["New hires take too long to become productive", "Reps know the process but do not execute consistently", "Reps create interest but do not move deals forward", "Reps struggle with follow-up / next steps", "Reps avoid difficult conversations", "Performance varies too much between similar reps", "Other"])
    stage = st.radio("Where do deals most often lose momentum?", ["Prospecting / first contact", "Discovery", "After a positive first conversation", "After demo / presentation", "Follow-up / next step", "Pricing / negotiation", "Closing", "Hard to tell"])
    familiar = st.radio("Which statement feels most familiar?", ["They know what to do, but they don’t do it consistently.", "They are active, but deals don’t move.", "They are good with people, but avoid closing.", "They understand the product, but don’t create urgency.", "They need too much manager direction.", "They looked strong in interview but struggle in the role."])

    st.subheader("3. Next step")
    likely = st.radio("What do you think the issue usually is?", ["Skill gap", "Motivation / effort", "Role fit", "Manager support", "Pressure / confidence", "Lack of structure", "Trust-building with buyers", "Not sure"])
    useful = st.slider("How useful would this signal be for your managers?", 1, 5, 4)
    pilot = st.radio("Would you test this with 1–3 reps?", ["Yes, I’d like to test it", "Maybe, send me more information", "Not now", "I’m not the right person"])
    submit = st.form_submit_button("See my diagnostic result")

if submit:
    if not name or not email:
        st.error("Please add your name and work email.")
        st.stop()
    answers = {
        "timestamp_utc": dt.datetime.utcnow().isoformat(timespec="seconds"),
        "name": name,
        "email": email,
        "role": role,
        "company": company,
        "manage_reps": manage,
        "challenge": challenge,
        "stage": stage,
        "familiar": familiar,
        "likely": likely,
        "usefulness": useful,
        "pilot_interest": pilot,
    }
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
      <p>{data['short']}</p>
      <p><b>Manager action to test next:</b><br>{data['action']}</p>
      <p><b>Secondary signal:</b> {second}</p>
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
