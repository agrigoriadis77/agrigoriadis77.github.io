python3 -m venv ~/pdfenv
source ~/pdfenv/bin/activate
pip install pdfplumber
python3 pdf_to_csv.py ~/Downloads/schedule.pdf ~/Downloads/schedule.json

deactivate
rm -rf ~/pdfenv
