"""
views/report.py - What the user sees: the analysis report. Display only, no logic.
"""

import csv
import io

import streamlit as st

def show_report(reports: list, file_names: dict, flagged: list) -> None:
    """One folded card per candidate, then a CSV download"""
    st.header("4. Report")
    st.info("Candidates are **not ranked**. The AI organizes the evidence; you make the decisions.")

    for report in reports:
        with st.expander(f"{report.candidate_id} . {file_names[report.candidate_id]}"):
            if report.candidate_id in flagged:
                st.warning("This resume contains hidden instructions for AI tools. Check the original file")
            st.write(report.summary)

            found, missing, check = st.columns(3)
            found.markdown("** Found in the resume**")
            for item in report.found:
                found.markdown(f" - **{item.requirement}**: '{item.quote}'")
            missing.markdown("** Not mentioned**")
            for requirement in report.not_mentioned:
                missing.markdown(f" - **{requirement}**")
            check.markdown("** To check in the resume**")
            for point in report.to_check:
                check.markdown(f" - **{point}**")
    st.download_button(" Download the report (CSV)", report_to_csv(reports, file_names), "resport.csv", "text/csv")

def report_to_csv(reports: list, file_names: dict) -> bytes:
    """One row per candidate. utf-8-sig lets Excel display accents correctly."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["candidate", "file", "summary", "found", "not_mentioned", "to_check"])

    for report in reports:
        writer.writerow([
            report.candidate_id,
            file_names[report.candidate_id],
            report.summary,
            " | ".join(f"{item.requirement}: {item.quote}" for item in report.found),
            " | ".join(report.not_mentioned),
            " | ".join(report.to_check),
        ])
    return buffer.getvalue().encode("utf-8-sig")