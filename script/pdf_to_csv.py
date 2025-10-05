import pdfplumber
import json
import sys

def pdf_to_json(pdf_path, json_path):
    all_rows = []
    max_len = 0

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables():
                for row in table:
                    # convert empty/None to None (→ null in JSON)
                    clean_row = [cell.strip() if cell else None for cell in row]
                    all_rows.append(clean_row)
                    if len(clean_row) > max_len:
                        max_len = len(clean_row)

    # pad all rows to the same length
    for row in all_rows:
        while len(row) < max_len:
            row.append(None)
        # make sure all non-empty are strings
        for i, val in enumerate(row):
            if val is not None:
                row[i] = str(val)

    # write JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_rows, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python pdf_to_json_padded.py input.pdf output.json")
    else:
        pdf_to_json(sys.argv[1], sys.argv[2])
        print(f"✅ JSON saved to {sys.argv[2]}")
