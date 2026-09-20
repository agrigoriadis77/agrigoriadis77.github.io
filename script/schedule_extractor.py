# -*- coding: utf-8 -*-
"""
Extract and print the weekly schedule of a single class (e.g. "Γ2") from the
school's master timetable, which is pasted in as tab-separated text (copied
straight out of Excel).

Usage (paste mode - no file needed):
    python3 schedule_extractor.py Γ2
    -> then paste the Excel data, and press Ctrl-D (on its own line) to finish.

Usage (from a file, if you'd rather save one):
    python3 schedule_extractor.py schedule_input.txt Γ2

If you run it with no arguments at all, it assumes the default class code
Γ2 before waiting for the pasted data.
"""

import sys
import re
import csv
import io
import os
import tempfile
import webbrowser
from abbreviations import ABBREVIATIONS

DAYS = ["ΔΕΥΤΕΡΑ", "ΤΡΙΤΗ", "ΤΕΤΑΡΤΗ", "ΠΕΜΠΤΗ", "ΠΑΡΑΣΚΕΥΗ"]
PERIODS_PER_DAY = 7
META_LABELS = {"α/α", "Διδάσκων", "Ονοματεπώνυμο", "ΠΕ"}
TEACHER_LABELS = {"Διδάσκων", "Ονοματεπώνυμο"}


def translate_subject(abbr: str) -> str:
    """Turn a raw subject abbreviation into its full name using the regex map."""
    abbr = abbr.strip()
    for pattern, full_name in ABBREVIATIONS.items():
        if re.fullmatch(pattern, abbr):
            return full_name
    return f"{abbr} (?)"  # unknown abbreviation - flagged so you notice it


def extract_hour(value: str):
    """Return an int hour if the value starts with a numeric hour, e.g. '1', '1η', '1ο', '2η'."""
    text = str(value).strip()
    if not text:
        return None

    match = re.match(r"^(\d+)(?:[ηο])?", text)
    if match:
        return int(match.group(1))

    return None


def normalize_cell(value):
    """Collapse whitespace and strip common quote characters from pasted cells."""
    text = str(value).replace("\r", " ").replace("\n", " ")
    text = text.replace("“", '"').replace("”", '"').replace("„", '"')
    text = text.strip().strip('"').strip("'")
    return re.sub(r"\s+", " ", text).strip()


def parse_class_subject(value: str):
    """Split a lesson cell like 'Γ2 ΑχΓλ' or 'Α4ΠΤ Τχν' into class + subject."""
    normalized = normalize_cell(value)
    if not normalized:
        return None, None
    parts = normalized.split()
    if len(parts) < 2:
        return None, None
    class_code = parts[0]
    subject = ' '.join(parts[1:])
    return class_code, subject


def is_day_header_row(row):
    """A row that names at least one weekday (e.g. the 'ΔΕΥΤΕΡΑ ... ΤΡΙΤΗ ...' row)."""
    return any(cell.strip() in DAYS for cell in row)


def is_period_header_row(row):
    """
    A row of period labels, e.g. '1η 2η 3η ...', possibly preceded by meta
    labels like 'α/α', 'Διδάσκων', 'ΠΕ' (the full master-table format) or
    with no meta labels at all (a single-day excerpt).
    """
    non_empty = [cell.strip() for cell in row if cell.strip()]
    if len(non_empty) < 2:
        return False
    for cell in non_empty:
        if cell in META_LABELS:
            continue
        if extract_hour(cell) is None:
            return False
    # Require at least one cell to actually look like a period label.
    return any(extract_hour(cell) is not None for cell in non_empty)


def build_day_map(row):
    """Map column index -> day name, filling merged/blank cells forward."""
    day_map = {}
    current_day = None
    for idx, cell in enumerate(row):
        value = cell.strip()
        if value in DAYS:
            current_day = value
        day_map[idx] = current_day
    return day_map


def build_period_map(row):
    """Map column index -> period number, and find the teacher column if present."""
    period_map = {}
    teacher_col = None
    for idx, cell in enumerate(row):
        value = cell.strip()
        if value in TEACHER_LABELS:
            teacher_col = idx
        hour = extract_hour(value) if value not in META_LABELS else None
        period_map[idx] = hour
    return period_map, teacher_col


def parse_timetable(text: str):
    """
    Parse pasted timetable text into a flat list of entries:
        {"day": ..., "period": ..., "class": ..., "subject": ..., "teacher": ...}

    Supports both the full master table (with 'α/α', 'Διδάσκων', 'ΠΕ' columns
    and all weekdays side by side) and smaller excerpts that only contain a
    day header row + a period header row (e.g. '1η'..'7η') followed directly
    by lesson cells with no row-id/teacher columns at all.

    Uses the csv module (tab-delimited) so that quoted cells with embedded
    newlines (e.g. "Γ2\\n Γαλ") and empty cells are handled the same way
    Excel produces them, keeping every column properly aligned.
    """
    entries = []
    day_map = {}
    period_map = {}
    teacher_col = None

    reader = csv.reader(io.StringIO(text), delimiter="\t", quotechar='"')
    for row in reader:
        if not row or not any(cell.strip() for cell in row):
            continue

        if is_day_header_row(row):
            day_map = build_day_map(row)
            continue

        if is_period_header_row(row):
            period_map, teacher_col = build_period_map(row)
            continue

        if not period_map:
            # Haven't seen a period header yet - nothing to map this row to.
            continue

        teacher_full = row[teacher_col].strip() if teacher_col is not None and teacher_col < len(row) else ""
        teacher_surname = teacher_full.split()[0] if teacher_full else ""

        for idx, cell in enumerate(row):
            cell = cell.strip()
            if not cell:
                continue

            period = period_map.get(idx)
            day = day_map.get(idx)
            if period is None or day is None:
                continue

            class_code, subject_raw = parse_class_subject(cell)
            if not class_code or not subject_raw:
                continue

            entries.append({
                "day": day,
                "period": period,
                "class": class_code,
                "subject": subject_raw,
                "teacher": teacher_surname,
            })
    return entries



def build_class_schedule(entries, class_code: str):
    """Return {day: {period: (subject_full, teacher_surname)}} for one class."""
    schedule = {day: {} for day in DAYS}
    for e in entries:
        if e["class"] == class_code:
            subject_full = translate_subject(e["subject"])
            schedule[e["day"]][e["period"]] = (subject_full, e["teacher"])
    return schedule


def print_schedule(class_code: str, schedule):
    print(f"\nΩρολόγιο πρόγραμμα - {class_code}\n" + "=" * 40)
    for day in DAYS:
        print(f"\n{day}")
        print("-" * len(day))
        for period in range(1, PERIODS_PER_DAY + 1):
            if period in schedule[day]:
                subject, teacher = schedule[day][period]
                if teacher:
                    print(f"  {period}. {subject} ({teacher})")
                else:
                    print(f"  {period}. {subject}")
            else:
                print(f"  {period}. -")


def build_schedule_html(class_code: str, schedule) -> str:
    """Build a minimal standalone HTML page showing the weekly schedule."""
    rows_html = []
    for period in range(1, PERIODS_PER_DAY + 1):
        cells = [f"<td>{period}</td>"]
        for day in DAYS:
            if period in schedule[day]:
                subject, teacher = schedule[day][period]
                text = f"{subject}<br><small>{teacher}</small>" if teacher else subject
            else:
                text = "-"
            cells.append(f"<td>{text}</td>")
        rows_html.append("<tr>" + "".join(cells) + "</tr>")

    header_cells = "".join(f"<th>{day}</th>" for day in DAYS)

    return f"""<!DOCTYPE html>
<html lang="el">
<head>
<meta charset="UTF-8">
<title>Ωρολόγιο πρόγραμμα - {class_code}</title>
<style>
  body {{ font-family: sans-serif; padding: 20px; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th, td {{ border: 1px solid #999; padding: 8px; text-align: center; }}
  th {{ background: #eee; }}
</style>
</head>
<body>
<h1>Ωρολόγιο πρόγραμμα - {class_code}</h1>
<table>
<thead><tr><th>Ώρα</th>{header_cells}</tr></thead>
<tbody>
{''.join(rows_html)}
</tbody>
</table>
</body>
</html>
"""


def open_schedule_in_browser(class_code: str, schedule):
    """Write the schedule to a temp HTML file and open it in the default browser."""
    html = build_schedule_html(class_code, schedule)
    fd, path = tempfile.mkstemp(suffix=".html", prefix="schedule_")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(html)
    webbrowser.open(f"file://{path}")


def main():
    if len(sys.argv) >= 3:
        input_path = sys.argv[1]
        class_code = sys.argv[2]
        with open(input_path, encoding="utf-8") as f:
            text = f.read()
    elif len(sys.argv) == 2:
        # Only a class code given - read the pasted data from stdin.
        class_code = sys.argv[1]
        print("Επικόλλησε τα δεδομένα και μετά πάτα Ctrl-D:", file=sys.stderr)
        text = sys.stdin.read()
    else:
        # No arguments at all - assume the default class code Γ2.
        class_code = "Γ2"
        print("Επικόλλησε τα δεδομένα και μετά πάτα Ctrl-D:", file=sys.stderr)
        text = sys.stdin.read()

    entries = parse_timetable(text)
    schedule = build_class_schedule(entries, class_code)

    if not any(schedule[day] for day in DAYS):
        print(f"Δεν βρέθηκαν μαθήματα για το τμήμα '{class_code}'. "
              f"Έλεγξε ότι έγραψες τον κωδικό όπως εμφανίζεται στο αρχείο.")
        return

    print_schedule(class_code, schedule)
    open_schedule_in_browser(class_code, schedule)


if __name__ == "__main__":
    main()

