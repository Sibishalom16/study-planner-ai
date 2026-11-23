"""
tools.py
---------
Contains exactly two custom Python tools for the Study Planner AI application:
1. days_until_exam: Calculates remaining days until an examination date.
2. split_study_hours: Divides available study hours equally among subjects.

Both tools are registered as LangChain-compatible tools.
"""

from datetime import datetime, date
from typing import List, Union
from langchain_core.tools import tool
from dateutil import parser as date_parser


@tool
def days_until_exam(exam_date: str) -> str:
    """Calculates the number of days remaining until an examination date from today."""
    if not exam_date or not isinstance(exam_date, str) or not exam_date.strip():
        return "Error: Please provide a valid examination date string (e.g., '2026-12-15' or '15 December 2026')."

    cleaned_date_str = exam_date.strip()

    # Attempt to parse date using dateutil parser with multiple fallbacks
    parsed_date: date | None = None
    try:
        # dateutil parser handles strings like "15 December 2026", "2026-12-15", "15-12-2026", etc.
        parsed_dt = date_parser.parse(cleaned_date_str, dayfirst=True)
        parsed_date = parsed_dt.date()
    except (ValueError, TypeError, OverflowError):
        # Fallback to explicit common formats
        formats_to_try = [
            "%Y-%m-%d",
            "%d-%m-%Y",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%d %B %Y",
            "%d %b %Y",
            "%B %d, %Y",
            "%b %d, %Y",
        ]
        for fmt in formats_to_try:
            try:
                parsed_dt = datetime.strptime(cleaned_date_str, fmt)
                parsed_date = parsed_dt.date()
                break
            except ValueError:
                continue

    if parsed_date is None:
        return f"Error: Unable to parse '{cleaned_date_str}' as a valid date. Please use formats like YYYY-MM-DD (e.g., 2026-12-15) or '15 December 2026'."

    today = date.today()
    delta_days = (parsed_date - today).days

    if delta_days == 0:
        return "Your examination is today! Best of luck with your test!"
    elif delta_days == 1:
        return "Your examination is 1 day away (tomorrow). Make sure to do a quick final revision!"
    elif delta_days > 1:
        return f"Your examination is {delta_days} days away."
    else:
        past_days = abs(delta_days)
        return f"The examination date ({parsed_date.strftime('%d %B %Y')}) has already passed {past_days} day{'s' if past_days > 1 else ''} ago."


@tool
def split_study_hours(total_hours: Union[float, int, str], subjects: Union[List[str], str]) -> str:
    """Divides available study hours equally across a provided list of subjects."""
    # Validate and parse total_hours
    try:
        if isinstance(total_hours, str):
            # Strip whitespace and common units like "hrs", "hours"
            cleaned_hrs_str = total_hours.lower().replace("hours", "").replace("hour", "").replace("hrs", "").replace("hr", "").strip()
            hours_val = float(cleaned_hrs_str)
        else:
            hours_val = float(total_hours)
    except (ValueError, TypeError):
        return f"Error: Invalid study hours '{total_hours}'. Please provide a valid positive number of hours (e.g., 12 or 8.5)."

    if hours_val <= 0:
        return "Error: Total available study hours must be greater than zero. Negative or zero hours cannot be distributed."

    # Validate and parse subjects
    subject_list: List[str] = []
    if isinstance(subjects, list):
        subject_list = [str(s).strip() for s in subjects if str(s).strip()]
    elif isinstance(subjects, str):
        # Allow comma, semicolon, or newline delimited string
        for delimiter in [",", ";", "\n"]:
            if delimiter in subjects:
                parts = subjects.split(delimiter)
                subject_list = [p.strip() for p in parts if p.strip()]
                break
        if not subject_list and subjects.strip():
            subject_list = [subjects.strip()]
    else:
        return "Error: Subjects must be provided as a list of subject names or a comma-separated string."

    if not subject_list:
        return "Error: The subject list cannot be empty. Please provide at least one subject to divide hours."

    num_subjects = len(subject_list)
    allocated_hours = hours_val / num_subjects

    # Format allocated hours cleanly (e.g., 3 hours vs 2.5 hours vs 1 hour)
    if allocated_hours.is_integer():
        hrs_str = f"{int(allocated_hours)}"
    else:
        hrs_str = f"{allocated_hours:.2f}".rstrip("0").rstrip(".")

    unit_str = "hour" if hrs_str == "1" else "hours"

    lines = [f"{subj}: {hrs_str} {unit_str}" for subj in subject_list]
    return "\n".join(lines)


# Exactly two custom tools registered for LangChain
CUSTOM_TOOLS = [days_until_exam, split_study_hours]
