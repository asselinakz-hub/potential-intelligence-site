import datetime as dt
import urllib.parse
from typing import Dict, List, Tuple

import pandas as pd
import streamlit as st


# -----------------------------
# Basic configuration
# -----------------------------
st.set_page_config(
    page_title="Sales Ramp Diagnostic | Potential Intelligence™",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

LANDING_URL = "https://asselinakz-hub.github.io/potential-intelligence-site/"
PARTICIPANT_REPORT_URL = "https://asselinakz-hub.github.io/potential-intelligence-site/reports/participant_report.html"
MANAGER_REPORT_URL = "https://asselinakz-hub.github.io/potential-intelligence-site/reports/manager_report.html"
TALENT_REPORT_URL = "https://asselinakz-hub.github.io/potential-intelligence-site/reports/talent_report.html"
CONTACT_EMAIL = "Asselina.kz@gmail.com"


# -----------------------------
# Styling
# -----------------------------
st.markdown(
    """
    <style>
      [data-testid="stHeader"] {background: transparent;}
      #MainMenu, footer {visibility: hidden;}
      .stApp {
        background: radial-gradient(circle at 82% -10%, rgba(231,182,75,.12), transparent 34%), #0b0d12;
        color: #f7f1e6;
      }
      .block-container {max-width: 1060px; padding-top: 42px; padding-bottom: 64px;}
      h1, h2, h3 {letter-spacing: -0.04em;}
      .pi-eyebrow {
        display:inline-flex; padding:7px 12px; border-radius:999px;
        background:rgba(231,182,75,.10); border:1px solid rgba(231,182,75,.22);
        color:#f4cf75; font-weight:900; font-size:12px; letter-spacing:.12em; text-transform:uppercase;
        margin-bottom:18px;
      }
      .pi-subtitle {font-size:22px; line-height:1.45; color:#b9bec8; max-width:820px; margin-top:8px;}
      .pi-card {
        background:rgba(255,255,255,.045); border:1px solid rgba(255,255,255,.12);
        border-radius:22px; padding:24px; height:100%;
      }
      .pi-card-gold {
        background:linear-gradient(135deg, rgba(231,182,75,.14), rgba(255,255,255,.04));
        border:1px solid rgba(231,182,75,.28); border-radius:26px; padding:28px;
      }
      .pi-muted {color:#b9bec8;}
      .pi-dim {color:#7f8796; font-size:14px;}
      .pi-gold {color:#e7b64b;}
      .pi-link-btn {
        display:inline-block; background:#e7b64b; color:#10131b!important; text-decoration:none!important;
        padding:13px 18px; border-radius:999px; font-weight:900; margin:6px 8px 6px 0;
      }
      .pi-link-btn-secondary {
        display:inline-block; border:1px solid rgba(255,255,255,.18); color:#f7f1e6!important; text-decoration:none!important;
        padding:13px 18px; border-radius:999px; font-weight:800; margin:6px 8px 6px 0;
      }
      .pi-output {
        border-left:4px solid #e7b64b; padding:16px 18px; background:rgba(255,255,255,.045);
        border-radius:14px; margin:12px 0;
      }
      .pi-small-label {font-size:12px; text-transform:uppercase; letter-spacing:.12em; color:#f4cf75; font-weight:900;}
      .stButton > button {
        background:#e7b64b; color:#10131b; border:0; border-radius:999px;
        padding:0.75rem 1.2rem; font-weight:900;
      }
      .stDownloadButton > button {
        border-radius:999px; font-weight:800;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Diagnostic logic
# -----------------------------
PATTERN_LIBRARY: Dict[str, Dict[str, str]] = {
    "Momentum Breakdown": {
        "short": "Reps may create interest, but deals slow down before clear next steps or commitment.",
        "what_it_looks_like": "Positive conversations do not consistently convert into scheduled next steps, follow-up rhythm, or deal ownership.",
        "manager_action": "In the next 1:1, review one stalled deal and ask: ‘Where exactly did momentum drop — after interest, after demo, before next step, or near close?’ Then test a simple next-step commitment script.",
    },
    "Trust-Building Gap": {
        "short": "Buyers may not feel enough clarity, credibility, or confidence to move forward.",
        "what_it_looks_like": "The rep may be active and knowledgeable, but the buyer does not fully trust the problem framing, urgency, or path forward.",
        "manager_action": "Coach the rep to summarize the buyer’s problem in the buyer’s words before pitching. Ask: ‘What did the buyer trust you about — and what did they still not believe?’",
    },
    "Pressure Response Issue": {
        "short": "Execution may change when the conversation becomes uncomfortable: pricing, objections, urgency, or closing.",
        "what_it_looks_like": "The rep knows what to do, but avoids direct asks, softens the message too much, overpushes, or freezes when pressure rises.",
        "manager_action": "Role-play the uncomfortable moment, not the whole call. Ask: ‘What part of the conversation did you avoid because it felt risky?’ Then test one specific objection or pricing response.",
    },
    "Structure / Manager-Support Mismatch": {
        "short": "The issue may not be more effort. The rep may need a different mix of structure, autonomy, feedback, or prioritization.",
        "what_it_looks_like": "The rep may work hard but scatter effort, wait for direction, misread priorities, or lose consistency without clear checkpoints.",
        "manager_action": "Give one clear weekly success definition and one checkpoint. Ask: ‘What needs to be true by Friday for this deal or activity to be considered on track?’",
    },
    "Role-Fit Friction": {
        "short": "The rep may have skills, but parts of the role may require execution patterns that cost too much energy or do not come naturally.",
        "what_it_looks_like": "The person may perform well in one part of the sales cycle and consistently stall in another, even after training.",
        "manager_action": "Map the rep’s strongest and weakest stage: prospecting, discovery, demo, follow-up, negotiation, closing, expansion. Coach the weak stage or pair them with someone complementary.",
    },
}


def add(scores: Dict[str, int], key: str, points: int = 1) -> None:
    scores[key] = scores.get(key, 0) + points


def score_patterns(answers: Dict[str, object]) -> List[Tuple[str, int]]:
    scores = {k: 0 for k in PATTERN_LIBRARY}

    challenges = answers.get("biggest_challenge", []) or []
    usual = answers.get("usual_first_reaction", "")
    stage = answers.get("momentum_stage", "")
    familiar = answers.get("familiar_statement", "")
    likely = answers.get("likely_issue", "")
    valuable_outputs = answers.get("valuable_outputs", []) or []

    for item in challenges:
        if "do not move deals" in item or "follow-up" in item or "move deals forward" in item:
            add(scores, "Momentum Breakdown", 2)
        if "avoid difficult" in item:
            add(scores, "Pressure Response Issue", 2)
        if "Performance varies" in item:
            add(scores, "Role-Fit Friction", 1)
        if "take too long" in item:
            add(scores, "Structure / Manager-Support Mismatch", 1)

    if stage in ["After a positive first conversation", "After demo / presentation", "Follow-up / next step", "Closing"]:
        add(scores, "Momentum Breakdown", 2)
    if stage in ["Discovery", "Prospecting / first contact"]:
        add(scores, "Trust-Building Gap", 1)
    if stage in ["Pricing / negotiation", "Closing"]:
        add(scores, "Pressure Response Issue", 2)

    if "know what to do" in familiar:
        add(scores, "Structure / Manager-Support Mismatch", 2)
    if "active, but deals" in familiar:
        add(scores, "Momentum Breakdown", 2)
    if "good with people" in familiar or "avoid closing" in familiar:
        add(scores, "Pressure Response Issue", 2)
    if "don’t create urgency" in familiar:
        add(scores, "Trust-Building Gap", 1)
        add(scores, "Momentum Breakdown", 1)
    if "too much manager direction" in familiar:
        add(scores, "Structure / Manager-Support Mismatch", 2)
    if "looked strong in interview" in familiar:
        add(scores, "Role-Fit Friction", 2)

    if likely == "Skill gap":
        add(scores, "Structure / Manager-Support Mismatch", 1)
    if likely == "Motivation / effort":
        add(scores, "Pressure Response Issue", 1)
    if likely == "Role fit":
        add(scores, "Role-Fit Friction", 3)
    if likely == "Manager support":
        add(scores, "Structure / Manager-Support Mismatch", 3)
    if likely == "Pressure / confidence":
        add(scores, "Pressure Response Issue", 3)
    if likely == "Lack of structure":
        add(scores, "Structure / Manager-Support Mismatch", 3)
    if likely == "Trust-building with buyers":
        add(scores, "Trust-Building Gap", 3)

    for output in valuable_outputs:
        if "loses momentum" in output:
            add(scores, "Momentum Breakdown", 1)
        if "pressure" in output:
            add(scores, "Pressure Response Issue", 1)
        if "Trust-building" in output:
            add(scores, "Trust-Building Gap", 1)
        if "support the rep" in output:
            add(scores, "Structure / Manager-Support Mismatch", 1)
        if "skill gap vs role-fit" in output:
            add(scores, "Role-Fit Friction", 1)

    if usual in ["More training", "More scripts / playbooks"]:
        add(scores, "Structure / Manager-Support Mismatch", 1)
    if usual in ["More pressure / accountability", "More activity targets"]:
        add(scores, "Pressure Response Issue", 1)
    if usual == "Pairing with a stronger rep":
        add(scores, "Role-Fit Friction", 1)

    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


def score_icp(answers: Dict[str, object]) -> Tuple[str, int]:
    score = 0
    role = answers.get("role", "")
    manage = answers.get("manage_reps", "")
    usefulness = int(answers.get("usefulness", 3))
    pilot = answers.get("pilot_interest", "")

    if role in ["VP Sales / Head of Sales", "Sales Manager", "CRO / Revenue Leader"]:
        score += 3
    elif role in ["Founder", "Sales Enablement"]:
        score += 2
    elif role in ["HR / People / L&D"]:
        score += 1

    if manage == "Yes, I directly manage reps":
        score += 3
    elif manage in ["Yes, I support sales managers / enablement", "Not directly, but I’m involved in sales performance"]:
        score += 2

    if usefulness >= 4:
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


def make_mailto(name: str, company: str, fit: str, top_pattern: str) -> str:
    subject = "Potential Intelligence pilot request"
    body = (
        f"Hi Asselya,\n\n"
        f"I completed the Sales Ramp Diagnostic.\n\n"
        f"Name: {name}\n"
        f"Company: {company}\n"
        f"Fit: {fit}\n"
        f"Possible friction pattern: {top_pattern}\n\n"
        f"I’d like to learn more about a small pilot with 1–3 reps.\n\n"
    )
    return f"mailto:{CONTACT_EMAIL}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"


def try_save_to_gsheet(row: Dict[str, object]) -> Tuple[bool, str]:
    """Optional Google Sheet persistence.

    To enable in Streamlit Cloud secrets:
      gsheet_url = "https://docs.google.com/spreadsheets/d/..."
      [gcp_service_account]
      type = "service_account"
      project_id = "..."
      private_key_id = "..."
      private_key = "-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n"
      client_email = "..."
      client_id = "..."
      auth_uri = "https://accounts.google.com/o/oauth2/auth"
      token_uri = "https://oauth2.googleapis.com/token"
      auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
      client_x509_cert_url = "..."
    """
    if "gcp_service_account" not in st.secrets or "gsheet_url" not in st.secrets:
        return False, "Google Sheet is not configured yet."

    try:
        import gspread
        from google.oauth2.service_account import Credentials

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=scopes
        )
        gc = gspread.authorize(credentials)
        sh = gc.open_by_url(st.secrets["gsheet_url"])

        worksheet_name = "diagnostic_responses"
        try:
            ws = sh.worksheet(worksheet_name)
        except gspread.WorksheetNotFound:
            ws = sh.add_worksheet(title=worksheet_name, rows=1000, cols=40)
            ws.append_row(list(row.keys()))

        existing_headers = ws.row_values(1)
        if not existing_headers:
            ws.append_row(list(row.keys()))
            existing_headers = list(row.keys())

        values = [str(row.get(header, "")) for header in existing_headers]
        ws.append_row(values)
        return True, "Saved to Google Sheet."
    except Exception as exc:
        return False, f"Could not save to Google Sheet: {exc}"


# -----------------------------
# UI
# -----------------------------
st.markdown('<div class="pi-eyebrow">Potential Intelligence™ · Sales Ramp Diagnostic</div>', unsafe_allow_html=True)
st.title("Find where sales execution breaks before adding more training or pressure.")
st.markdown(
    '<div class="pi-subtitle">A 5-minute diagnostic for VP Sales, Sales Managers, and GTM leaders. It qualifies the sales ramp problem, gives a possible friction pattern, and shows whether a small Manager Action Report pilot makes sense.</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="pi-card-gold">
      <b>Important:</b> this is not a personality test and not a performance evaluation. The goal is to validate whether Potential Intelligence™ can help managers move from guessing to practical coaching actions.
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

with st.form("sales_ramp_diagnostic"):
    st.subheader("1. About you")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Your name *")
        email = st.text_input("Work email *")
        role = st.selectbox(
            "What best describes your role? *",
            [
                "VP Sales / Head of Sales",
                "Sales Manager",
                "CRO / Revenue Leader",
                "Founder",
                "Sales Enablement",
                "HR / People / L&D",
                "Other",
            ],
        )
    with col2:
        company = st.text_input("Company")
        company_size = st.selectbox(
            "Company size",
            ["1–10", "11–50", "51–200", "201–500", "501–1000", "1000+", "Not sure"],
        )
        manage_reps = st.selectbox(
            "Do you manage or support sales reps? *",
            [
                "Yes, I directly manage reps",
                "Yes, I support sales managers / enablement",
                "Not directly, but I’m involved in sales performance",
                "No",
            ],
        )

    st.subheader("2. Sales ramp / execution problem")
    biggest_challenge = st.multiselect(
        "What is your biggest sales ramp challenge right now?",
        [
            "New hires take too long to become productive",
            "Reps know the process but do not execute consistently",
            "Reps create interest but do not move deals forward",
            "Reps struggle with follow-up / next steps",
            "Reps avoid difficult conversations",
            "Performance varies too much between similar reps",
            "Other",
        ],
    )

    usual_first_reaction = st.radio(
        "When a rep is not ramping, what do you usually try first?",
        [
            "More training",
            "More activity targets",
            "More manager check-ins",
            "More pressure / accountability",
            "More scripts / playbooks",
            "Pairing with a stronger rep",
            "I’m not sure",
        ],
    )

    momentum_stage = st.radio(
        "Where do deals most often lose momentum?",
        [
            "Prospecting / first contact",
            "Discovery",
            "After a positive first conversation",
            "After demo / presentation",
            "Follow-up / next step",
            "Pricing / negotiation",
            "Closing",
            "Hard to tell",
        ],
    )

    familiar_statement = st.radio(
        "Which statement feels most familiar?",
        [
            "They know what to do, but they don’t do it consistently.",
            "They are active, but deals don’t move.",
            "They are good with people, but avoid closing.",
            "They understand the product, but don’t create urgency.",
            "They need too much manager direction.",
            "They looked strong in interview but struggle in the role.",
        ],
    )

    likely_issue = st.radio(
        "What do you think the issue usually is?",
        [
            "Skill gap",
            "Motivation / effort",
            "Role fit",
            "Manager support",
            "Pressure / confidence",
            "Lack of structure",
            "Trust-building with buyers",
            "Not sure",
        ],
    )

    usefulness = st.slider(
        "How useful would it be to know where each rep’s execution breaks?",
        min_value=1,
        max_value=5,
        value=4,
        help="1 = not useful, 5 = very useful",
    )

    valuable_outputs = st.multiselect(
        "Which output would be most valuable for your managers?",
        [
            "Specific 1:1 coaching questions",
            "Where the rep loses momentum in the sales cycle",
            "How the rep responds to pressure",
            "Trust-building style",
            "Whether this is skill gap vs role-fit friction",
            "How to support the rep next week",
            "All of the above",
        ],
    )

    pilot_interest = st.radio(
        "Would you be open to testing a free pilot with 1–3 reps?",
        [
            "Yes, I’d like to test it",
            "Maybe, send me more information",
            "Not now",
            "I’m not the right person",
        ],
    )

    comments = st.text_area("Anything else you want to add?", height=100)

    submitted = st.form_submit_button("See my diagnostic result")

if submitted:
    if not name or not email:
        st.error("Please add your name and work email so the diagnostic result can be connected to your response.")
        st.stop()

    answers = {
        "timestamp_utc": dt.datetime.utcnow().isoformat(timespec="seconds"),
        "name": name,
        "email": email,
        "role": role,
        "company": company,
        "company_size": company_size,
        "manage_reps": manage_reps,
        "biggest_challenge": biggest_challenge,
        "usual_first_reaction": usual_first_reaction,
        "momentum_stage": momentum_stage,
        "familiar_statement": familiar_statement,
        "likely_issue": likely_issue,
        "usefulness": usefulness,
        "valuable_outputs": valuable_outputs,
        "pilot_interest": pilot_interest,
        "comments": comments,
    }

    ranked_patterns = score_patterns(answers)
    top_pattern, top_score = ranked_patterns[0]
    second_pattern, second_score = ranked_patterns[1]
    fit, icp_score = score_icp(answers)

    row = {
        **answers,
        "top_pattern": top_pattern,
        "top_pattern_score": top_score,
        "second_pattern": second_pattern,
        "second_pattern_score": second_score,
        "pilot_fit": fit,
        "icp_score": icp_score,
    }
    # Flatten list fields for storage / download.
    row_for_storage = {k: "; ".join(v) if isinstance(v, list) else v for k, v in row.items()}
    saved, save_msg = try_save_to_gsheet(row_for_storage)

    st.success("Diagnostic complete.")
    st.markdown(f"<div class='pi-small-label'>Pilot qualification</div>", unsafe_allow_html=True)
    st.markdown(f"## {fit}")
    st.caption(f"Internal score: {icp_score}/11. This is only for founder-led validation prioritization.")

    st.markdown("---")
    st.markdown("## Possible execution friction pattern")
    data = PATTERN_LIBRARY[top_pattern]
    st.markdown(
        f"""
        <div class="pi-output">
          <div class="pi-small-label">Primary signal</div>
          <h3>{top_pattern}</h3>
          <p class="pi-muted">{data['short']}</p>
          <p><b>What this can look like:</b><br>{data['what_it_looks_like']}</p>
          <p><b>What the sales manager can try next:</b><br>{data['manager_action']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    second = PATTERN_LIBRARY[second_pattern]
    st.markdown(
        f"""
        <div class="pi-output">
          <div class="pi-small-label">Secondary signal</div>
          <h3>{second_pattern}</h3>
          <p class="pi-muted">{second['short']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("## Recommended next step")
    if fit == "Strong pilot fit":
        st.write(
            "Your answers suggest this may be a strong fit for a small Sales Ramp Intelligence pilot. The next step is to invite 1–3 reps to complete the full assessment voluntarily. Then you receive a Manager Action Report for each participant."
        )
    elif fit == "Possible pilot fit":
        st.write(
            "Your answers show a possible sales execution friction point. The next step is to review the sample Manager Action Report and decide whether this would be useful for your team."
        )
    else:
        st.write(
            "This may not be the strongest pilot fit right now, but your response is still useful for validation. You can review the sample reports or follow the founder-led validation."
        )

    mailto = make_mailto(name, company, fit, top_pattern)
    st.markdown(
        f"""
        <a class="pi-link-btn" href="{mailto}">Request a small team pilot</a>
        <a class="pi-link-btn-secondary" href="{MANAGER_REPORT_URL}" target="_blank">View Manager Action sample</a>
        <a class="pi-link-btn-secondary" href="{PARTICIPANT_REPORT_URL}" target="_blank">View Rep Insight sample</a>
        <a class="pi-link-btn-secondary" href="{TALENT_REPORT_URL}" target="_blank">View Talent Signal sample</a>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    if saved:
        st.info("Response saved to your Google Sheet.")
    else:
        st.warning(
            f"Response was not saved to Google Sheet yet: {save_msg} You can still download this response as CSV below."
        )

    df = pd.DataFrame([row_for_storage])
    st.download_button(
        "Download this response as CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="sales_ramp_diagnostic_response.csv",
        mime="text/csv",
    )

    with st.expander("Founder/admin view: raw response"):
        st.dataframe(df, use_container_width=True)
else:
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<div class='pi-card'><h3>1. Diagnostic</h3><p class='pi-muted'>VP Sales answers 10 questions about ramp, execution, and coaching pain.</p></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='pi-card'><h3>2. Friction signal</h3><p class='pi-muted'>The app returns a possible execution friction pattern and manager action to test.</p></div>", unsafe_allow_html=True)
    with c3:
        st.markdown("<div class='pi-card'><h3>3. Team pilot</h3><p class='pi-muted'>If useful, 1–3 reps complete the full assessment and the manager receives action reports.</p></div>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <p class="pi-dim">Sample reports:</p>
        <a class="pi-link-btn-secondary" href="{PARTICIPANT_REPORT_URL}" target="_blank">Rep Insight</a>
        <a class="pi-link-btn-secondary" href="{MANAGER_REPORT_URL}" target="_blank">Manager Action</a>
        <a class="pi-link-btn-secondary" href="{TALENT_REPORT_URL}" target="_blank">Talent Signal</a>
        """,
        unsafe_allow_html=True,
    )
