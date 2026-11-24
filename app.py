"""
app.py - The page, in 4 steps: resumes -> job description -> analyse -> report.
Run: streamlit run app.py
"""

from pathlib import Path
import streamlit as st

from ai.agent import analyse_candidate, create_recruitment_agent
from services import resumes
from views.report import show_report

MAX_RESUMES = 10
JOB_DESCRIPTION_FILE = Path(__file__).parent / "data" / "job_description.txt"

st.set_page_config(page_title="AI Recruitment Assistant", page_icon="*")
st.title("AI Recruitment Assistant")
st.caption("Basic version . LangChain agent . Educational demo")

# 1. Resumes
st.header("1. Upload the resumes")
uploads = st.file_uploader(f"PDF resumes ( max {MAX_RESUMES})", type="pdf", accept_multiple_files=True)
st.caption("Emails, phone numbers, dates and personal details are removed before the AI reads the resumes")

# 2. Job Descripition
st.header("2. Job description")
job_description = st.text_area("Job description", JOB_DESCRIPTION_FILE.read_text(encoding="utf-8"), height=250)
requirements = resumes.set_job_description(job_description)
st.caption(f"{len(requirements)} requirements found under the 'Requirements' heading.")

# 3. Analyse
st.header("3. Analyse")
if st.button("Analyse the resumes", type="primary", disabled=not (uploads and requirements)):
    if len(uploads) > MAX_RESUMES:
        st.error(f"Please upload {MAX_RESUMES} resumes or fewer only.")
        st.stop()

    # Read and protect every resume, with an anonymous ID (CAND-01, CAND-02...)
    resumes.RESUMES.clear()
    file_names, flagged = dict(), list()
    for number, upload in enumerate(uploads, start=1):
        candidate_id = f"CAND-{number:02d}"
        file_names[candidate_id] = upload.name
        print(f"File to be uploaded: {upload.name}")
        if resumes.add_resume(candidate_id, upload):
            flagged.append(candidate_id)
        print("After the add_resume")
    try:
        agent = create_recruitment_agent()
    except Exception as error:
        st.error(f"The AI agent could not be started. Check MODEL, API_KEY in .env file. {error}")
        st.stop()

    reports = list()
    progress = st.progress(0.0)
    for number, candidate_id in enumerate(resumes.RESUMES, start=1):
        try:
            report, tools_used = analyse_candidate(agent, candidate_id)
            reports.append(report)
            st.write(f"{candidate_id}: the agent used {'->'.join(tools_used)}")
        except Exception as error:
            st.error(f"{candidate_id} analysis failed. {error}")
        progress.progress(number / len(resumes.RESUMES), text=f"{number} of {len(resumes.RESUMES)} processed") 
    st.session_state["report"] = (reports, file_names, flagged)

# 4. Report
if "report" in st.session_state:
    show_report(*st.session_state["report"])