"""CivicSense app: citizen reporting + public board + officer dashboard.  Run:  streamlit run app.py"""
import os
import re
import time
from datetime import datetime

import pandas as pd
import streamlit as st

import db
import service
from civicsense.data import generate, LOCATIONS

try:                                   # optional: "use my phone's GPS" button (pip install streamlit-geolocation)
    from streamlit_geolocation import streamlit_geolocation
except ImportError:
    streamlit_geolocation = None

def _admin_password():
    """Officer password: environment variable, else Streamlit secret, else the demo default. NOT real security."""
    if os.environ.get("CIVICSENSE_ADMIN"):
        return os.environ["CIVICSENSE_ADMIN"]
    try:
        return st.secrets["CIVICSENSE_ADMIN"]
    except Exception:
        return "admin123"


ADMIN_PASSWORD = _admin_password()

st.set_page_config(page_title="CivicSense", layout="wide", initial_sidebar_state="collapsed")
db.init()

CSS = """<style>
[data-testid="stToolbar"], [data-testid="stHeader"], footer, #MainMenu {display: none !important;}
.block-container {padding-top: 1.5rem; max-width: 1200px;}
.cs-hero {background: linear-gradient(135deg, #0B2545 0%, #13478a 100%); color: #fff; padding: 22px 28px; border-radius: 16px; margin-bottom: 12px;}
.cs-brand {font-size: 30px; font-weight: 800; letter-spacing: .3px;}
.cs-tag {opacity: .85; font-size: 15px; margin-top: 2px;}
div[data-testid="stMetric"] {background: #fff; border: 1px solid #D9E0E7; border-radius: 14px; padding: 14px 18px;}
.stButton > button, .stFormSubmitButton > button {border-radius: 10px; font-weight: 600;}
div[data-testid="stFormSubmitButton"], div[data-testid="stFormSubmitButton"] > button, .stFormSubmitButton, .stFormSubmitButton > button {width: 100% !important;}
div[data-testid="stFormSubmitButton"] > button {padding: 0.6rem 0;}
.cs-info {background: #fff; border: 1px solid #D9E0E7; border-radius: 14px; padding: 12px 16px; height: 100%;}
.cs-info .l {color: #6B7280; font-size: 13px;}
.cs-info .v {color: #0B2545; font-size: 19px; font-weight: 700; line-height: 1.25;}
.cs-ticket {background: #fff; border: 2px solid #0F766E; border-radius: 16px; padding: 18px 22px; text-align: center; margin: 6px 0 14px;}
.cs-ticket .label {color: #6B7280; font-size: 13px; text-transform: uppercase; letter-spacing: .08em;}
.cs-ticket .num {color: #0B2545; font-size: 36px; font-weight: 800;}
.cs-ticket .hint {color: #6B7280; font-size: 13px;}
.cs-steps {display: flex; gap: 8px; margin: 8px 0 16px;}
.cs-steps div {flex: 1; text-align: center; padding: 10px 6px; border-radius: 10px; background: #E5E7EB; color: #6B7280; font-weight: 600;}
.cs-steps .done {background: #0F766E; color: #fff;}
.cs-steps .now {background: #F4A261; color: #1F2937;}
.cs-chips {display: flex; gap: 10px; flex-wrap: wrap; margin: 4px 0 12px;}
.cs-chips span {background: #fff; border: 1px solid #D9E0E7; border-radius: 999px; padding: 6px 14px; font-size: 14px; color: #0B2545;}
</style>"""
st.markdown(CSS, unsafe_allow_html=True)
st.markdown('<div class="cs-hero"><div class="cs-brand">CivicSense</div>'
            '<div class="cs-tag">Report it. Rank it. Fix it. Every priority comes with a reason.</div></div>', unsafe_allow_html=True)


@st.cache_resource(show_spinner="Starting the CivicSense engine...")
def pipeline():
    return service.build_pipeline()


@st.cache_data(show_spinner=False)
def results(sig):
    df = db.open_complaints()
    scored, ranked = service.analyse(pipeline(), df, datetime.now())
    return df, scored, ranked


def ticket(i):
    return f"CS-{int(i):06d}"


def stepper(status):
    steps = ["Received", "Assigned", "Resolved"]
    i = steps.index(status)
    html = "".join('<div class="%s">%s</div>' % ("done" if (k < i or status == "Resolved") else ("now" if k == i else ""), name)
                   for k, name in enumerate(steps))
    st.markdown(f'<div class="cs-steps">{html}</div>', unsafe_allow_html=True)


def show_confirmation(cid):
    df, scored, ranked = results(db.signature())
    row = scored[scored.complaint_id == cid].iloc[0]
    issue = ranked[ranked.issue_id == row.issue_id].iloc[0]
    st.success("Report received. Keep your ticket number to track progress.")
    st.markdown(f'<div class="cs-ticket"><div class="label">Your ticket number</div><div class="num">{ticket(cid)}</div>'
                f'<div class="hint">Use it on the Track my report page</div></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    for col, label, value in [(c1, "Category", service.PRETTY[row.predicted_category]), (c2, "People who reported this", int(issue.reports)), (c3, "Status", issue.status)]:
        col.markdown(f'<div class="cs-info"><div class="l">{label}</div><div class="v">{value}</div></div>', unsafe_allow_html=True)
    if row.needs_review:
        st.info("We were not fully sure about the category, so a staff member will double-check it.")
    with st.expander("How was this decided?"):
        st.write(issue.why)


def page_report():
    _, mid, _ = st.columns([1, 2.2, 1])
    with mid:
        top = st.container()
        st.markdown("### See a problem? Tell us in 30 seconds.")
        st.markdown('<div class="cs-chips"><span>1  Say where</span><span>2  Describe it</span><span>3  Get a ticket</span></div>', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("**1. Where is it?**")
            area = st.selectbox("Area", list(LOCATIONS))
            lat0, lon0 = LOCATIONS[area]
            if streamlit_geolocation is not None:
                st.write("Or use your phone's location:")
                loc = streamlit_geolocation()
                if loc and loc.get("latitude"):
                    lat0, lon0, area = float(loc["latitude"]), float(loc["longitude"]), "Detected by GPS"
            with st.expander("Fine-tune the exact location (recommended)"):
                lat = st.number_input("Latitude", value=float(lat0), format="%.5f", key=f"lat_{area}")
                lon = st.number_input("Longitude", value=float(lon0), format="%.5f", key=f"lon_{area}")
            st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}), zoom=15, height=260)
        with st.container(border=True):
            st.markdown("**2. What is the problem?**")
            with st.form("report_form", clear_on_submit=True, border=False):
                text = st.text_area("Describe it in your own words", height=110, placeholder="Example: Big pothole near the school, bikes are skidding")
                photo = st.file_uploader("Add a photo (optional)", type=["jpg", "jpeg", "png"])
                submitted = st.form_submit_button("Submit report", type="primary")
        if submitted:
            if len((text or "").strip()) < 10:
                st.error("Please describe the problem in a few more words.")
                return
            photo_path = None
            if photo is not None:
                os.makedirs("uploads", exist_ok=True)
                photo_path = os.path.join("uploads", f"{int(time.time())}_{os.path.basename(photo.name)}")
                with open(photo_path, "wb") as f:
                    f.write(photo.getbuffer())
            cid = db.add(text.strip(), area, lat, lon, photo_path)
            with top:
                show_confirmation(cid)


def page_track():
    _, mid, _ = st.columns([1, 2.2, 1])
    with mid:
        st.markdown("### Track my report")
        with st.container(border=True):
            t = st.text_input("Ticket number", placeholder="CS-000123")
            go = st.button("Check status", type="primary")
        if go and t:
            digits = re.sub(r"\D", "", t)
            row = db.get(int(digits)) if digits else None
            if row is None:
                st.error("We could not find that ticket number.")
                return
            with st.container(border=True):
                stepper(row.status)
                st.progress({"Received": 1, "Assigned": 2, "Resolved": 3}[row.status] / 3, text=f"Status: {row.status}")
                st.write(f"**Reported on:** {row.created_at:%d %b %Y, %I:%M %p}  |  **Area:** {row.location}")
                st.write(f"**Your description:** {row.text}")
                if row.status != "Resolved":
                    _, scored, ranked = results(db.signature())
                    m = scored[scored.complaint_id == row.id]
                    if not m.empty:
                        issue = ranked[ranked.issue_id == m.iloc[0].issue_id].iloc[0]
                        st.write(f"**People who reported this issue:** {int(issue.reports)}")


def page_board():
    _, mid, _ = st.columns([1, 3, 1])
    with mid:
        st.markdown("### Most-reported issues")
        st.caption("Open issues in the city, with the number of people who reported each one.")
        _, scored, ranked = results(db.signature())
        if ranked.empty:
            st.info("No open issues yet.")
            return
        top = ranked.sort_values(["reports", "priority"], ascending=False).head(15)
        st.dataframe(top[["category_name", "location", "reports", "age_days", "status"]], hide_index=True, column_config={
            "category_name": "Problem", "location": "Area",
            "reports": st.column_config.ProgressColumn("People reported", min_value=0, max_value=int(top.reports.max()), format="%d"),
            "age_days": "Days open", "status": "Status"})


def page_officer():
    if not st.session_state.get("officer_ok"):
        _, mid, _ = st.columns([1, 1, 1])
        with mid:
            st.markdown("### Officer login")
            with st.container(border=True):
                pw = st.text_input("Password", type="password")
                if st.button("Log in", type="primary"):
                    if pw == ADMIN_PASSWORD:
                        st.session_state["officer_ok"] = True
                        st.rerun()
                    else:
                        st.error("Wrong password.")
        return
    df, scored, ranked = results(db.signature())
    k = st.columns(4)
    k[0].metric("Open complaints", len(df))
    k[1].metric("Open issues", len(ranked))
    k[2].metric("Duplicates merged", len(df) - len(ranked))
    k[3].metric("High priority (70+)", int((ranked.priority >= 70).sum()) if not ranked.empty else 0)
    t1, t2, t3, t4 = st.tabs(["Ranked issues", "Map and trend", "Needs review", "Admin"])
    with t1:
        if ranked.empty:
            st.info("No open complaints. Use the Admin tab to load demo data.")
        else:
            left, right = st.columns([3, 2])
            with left:
                cats = st.multiselect("Filter by category", sorted(ranked.category_name.unique()))
                view = ranked[ranked.category_name.isin(cats)] if cats else ranked
                st.dataframe(view[["rank", "category_name", "location", "priority", "reports", "age_days"]],
                             hide_index=True, height=430, column_config={
                    "rank": st.column_config.NumberColumn("#", width="small"), "category_name": "Problem", "location": "Area",
                    "priority": st.column_config.ProgressColumn("Priority", min_value=0, max_value=100, format="%.0f"),
                    "reports": st.column_config.NumberColumn("Reports", width="small"), "age_days": st.column_config.NumberColumn("Days open", width="small")})
            with right:
                with st.container(border=True):
                    st.markdown("**Issue details**")
                    iid = st.selectbox("Open an issue", list(view.issue_id), format_func=lambda i: "#%d  %s, %s" % (
                        ranked[ranked.issue_id == i].iloc[0]["rank"], ranked[ranked.issue_id == i].iloc[0].category_name, ranked[ranked.issue_id == i].iloc[0].location))
                    if iid is not None:
                        issue = ranked[ranked.issue_id == iid].iloc[0]
                        st.write(f"**Department:** {issue.department}  |  **Severity:** {int(issue.severity)}/5  |  **Status:** {issue.status}")
                        st.write("**Why this priority:** " + issue.why)
                        ids = list(scored[scored.issue_id == iid].complaint_id)
                        st.write("**Citizen reports:**")
                        for txt in df[df.id.isin(ids)].text:
                            st.write("- " + txt)
                        b1, b2 = st.columns(2)
                        if b1.button("Mark as assigned"):
                            db.set_status(ids, "Assigned")
                            st.rerun()
                        if b2.button("Mark as resolved", type="primary"):
                            db.set_status(ids, "Resolved")
                            st.rerun()
    with t2:
        if ranked.empty:
            st.info("No data yet.")
        else:
            a, b = st.columns([3, 2])
            with a:
                st.markdown("**Where issues are** (bigger dot = more reports)")
                st.map(ranked.assign(size=30 + ranked.reports * 20), latitude="lat", longitude="lon", size="size", height=420)
            with b:
                st.markdown("**Complaints per day**")
                st.line_chart(df.groupby(df.created_at.dt.date).size().rename("Complaints per day"), height=420)
    with t3:
        flagged = scored[scored.needs_review] if not scored.empty else scored
        if flagged.empty:
            st.write("Nothing to review.")
        else:
            st.write("The model was not confident about these. Check the category by hand.")
            st.dataframe(df.merge(flagged, left_on="id", right_on="complaint_id")[["id", "text", "predicted_category", "confidence"]], hide_index=True)
    with t4:
        if st.button("Load 150 demo complaints"):
            db.add_many(generate(150, seed=5, now=datetime.now())[["text", "location", "lat", "lon", "created_at"]])
            st.rerun()
        if not scored.empty:
            full = df.merge(scored.drop(columns=["status"]), left_on="id", right_on="complaint_id")
            st.download_button("Download complaints CSV (for Power BI)", full.to_csv(index=False), "complaints_scored.csv")
            st.download_button("Download ranked issues CSV (for Power BI)", ranked.to_csv(index=False), "ranked_issues.csv")
        if st.checkbox("I understand this deletes ALL complaints") and st.button("Delete all data"):
            db.delete_all()
            st.rerun()
        if st.button("Log out"):
            st.session_state["officer_ok"] = False
            st.rerun()


PAGES = {"Report a problem": page_report, "Track my report": page_track, "Most-reported issues": page_board, "Officer dashboard": page_officer}
choice = st.radio("Navigate", list(PAGES), horizontal=True, label_visibility="collapsed")
PAGES[choice]()
st.caption("CivicSense prototype. The category model is trained on synthetic data.")
