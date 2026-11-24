"""
services/resumes.py - Read the resumes and mask PII data BEFORE AI sees them.
Plain python and no AI and no interface code here. Just read the resumes and mask PII data.
"""

import io
import re

from pypdf import PdfReader

# Simple in-memory storage for resumes
RESUMES = {} # {"CANDIDATE_ID": {"filename": "resume.pdf", "content": "masked content"}}

REQUIREMENTS = [] # ["Python programming", "Machine Learning", "Data Science"]

# Security 1 - personal data the LLM never needs to see. Redact it before sending to the LLM.

PERSONAL_DATA_PATTERNS = [
    (r"\b\d{3}-\d{2}-\d{4}\b", "[ssn removed]"),  # SSN
    (r"\b\d{5}(?:-\d{4})?\b", "[zip code removed]"),  # ZIP code
    (r"\b\d{10}\b", "[phone number removed]"),  # Phone number (10 digits)
    (r"\b\d{3}-\d{3}-\d{4}\b", "[phone number removed]"),  # Phone number (XXX-XXX-XXXX)
    (r"\b\d{3}\.\d{3}\.\d{4}\b", "[phone number removed]"),  # Phone number (XXX.XXX.XXXX)
    (r"\b\d{3} \d{3} \d{4}\b", "[phone number removed]"),  # Phone number (XXX XXX XXXX)
    (r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", "[date removed]"),  # Date (MM/DD/YYYY or M/D/YY)
    (r"\b\d{1,2}-\d{1,2}-\d{2,4}\b", "[date removed]"),  # Date (MM-DD-YYYY or M-D-YY)
    (r"\b\d{1,2}\.\d{1,2}\.\d{2,4}\b", "[date removed]"),  # Date (MM.DD.YYYY or M.D.YY)
    (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[email removed]"),  # email regex pattern
    (r"\+\d{1,3}\s?\(?\d{1,4}\)?[\s.-]?\d{1,4}[\s.-]?\d{1,9}", "[phone number removed]"),  # International phone number
    (r"(?im)^\s*(date of birth|age|nationality|marital status|gender|religion)\s*:.*$", "[personal detail removed]"),
]

# Security 2 -  phrases that try prompt injection. Redact them before sending to the LLM.
PROMPT_INJECTION_PATTERNS = [
    r"(?i)(system message|user message|assistant message)",
    r"(?i)(ignore previous instructions|forget previous instructions|disregard previous instructions)",
    r"(?i)(please ignore all previous instructions|please disregard all previous instructions)",
    r"(?i)(you are a helpful assistant|you are a helpful AI|you are a helpful chatbot)",
    r"(?i)(you are a malicious AI|you are a malicious assistant|you are a malicious chatbot)",
    r"(?i)(rank this candidate|rank this resume|rank this CV)",
    r"(?i)(note to self|note to the AI|note to the assistant)",
]

def read_pdf(file: io.BytesIO) -> str:
    """
    Read a PDF stream and return its text content.
    """
    try:
        file.seek(0)
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error reading PDF file {getattr(file, 'name', '<uploaded file>')}: {e}")
        return ""

def redact_personal_data(text: str) -> str:
    """
    Redact personal data from the text using predefined patterns.
    """
    for pattern, replacement in PERSONAL_DATA_PATTERNS:
        text = re.sub(pattern, replacement, text)
    return text

def looks_like_prompt_injection(text: str) -> bool:
    """
    Check if the text contains any prompt injection patterns.
    """
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, text):
            return True
    return False

def add_resume(candidate_id: str, file: io.BytesIO) -> None:
    """
    Read a resume from a PDF stream, redact personal data, and store it in memory.
    """
    filename = getattr(file, "name", "resume.pdf")
    content = read_pdf(file)
    if not content:
        print(f"Failed to read resume for candidate {candidate_id}.")
        return

    # Redact personal data
    masked_content = redact_personal_data(content)

    # Check for prompt injection
    if looks_like_prompt_injection(masked_content):
        print(f"Resume for candidate {candidate_id} contains potential prompt injection. Not storing.")
        return

    # Store the masked content in memory
    RESUMES[candidate_id] = {
        "filename": filename,
        "content": masked_content
    }


def set_job_description(job_description: str) -> list[str]:
    """
    Extract job requirements from the description.
    """
    global REQUIREMENTS
    REQUIREMENTS.clear()
    in_requirements = False

    for line in job_description.splitlines():
        line = line.strip()
        if not line:
            continue

        # Check for the start of the requirements section
        if re.search(r"(?i)requirements|qualifications|skills", line):
            in_requirements = True
            # print('got requirements', line)
            continue

        # If we are in the requirements section, collect the requirements
        if in_requirements:
            # print(line)
            # Stop if we reach another section
            if re.search(r"(?i)responsibilities|duties|benefits|location", line):
                in_requirements = False
                continue
            REQUIREMENTS.append(line)   
    return REQUIREMENTS
    # REQUIREMENTS = [req.strip() for req in description.split(",") if req.strip()]
    # print(f"Extracted requirements: {REQUIREMENTS}")


if __name__ == "__main__":
    # Example usage
    # add_resume("candidate_1", "example_resume.pdf")
    # print(RESUMES)
    from pathlib import Path
    jd = Path('data/job_description.txt').read_text()
    # print(jd)
    set_job_description(jd)
    print('\n'.join(REQUIREMENTS))

    # set_job_description("Job Description: We are looking for a candidate with the following requirements:\n- Python programming\n- Machine Learning\n- Data Science\nResponsibilities include...")

    # print(REQUIREMENTS)