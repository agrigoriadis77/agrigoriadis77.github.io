========================================================
  HOW TO UPDATE THE SCHEDULE  (new workflow — no browser/debugger needed)
========================================================

When you receive a new .xlsx / .xls schedule file:

1. Run the conversion script (venv is created automatically on first run):
       ./script/update_schedule.sh path/to/schedule.xlsx

   This overwrites  js/schedule_data.js  automatically.

2. Open index.html in your browser locally and verify the schedule looks correct.
   The "Σε ισχύ από:" date is read automatically from the data — no manual edit needed.

3. Commit & push:
       git add js/schedule_data.js
       git commit -m "Update schedule - <date>"
       git push

That's it.

========================================================
  FILE LAYOUT
========================================================

  js/schedule_data.js   ← THE ONLY FILE YOU EVER CHANGE (auto-generated)
  js/data.js            ← static config: replacements + background images (rarely changes)
  js/main.js            ← application logic (never changes for a schedule update)
  index.html            ← update the "Σε ισχύ από:" date when needed

========================================================
  LEGACY: convert a PDF instead of XLS
========================================================

If you only have a PDF (no XLS):

    python3 -m venv ~/pdfenv
    source ~/pdfenv/bin/activate
    pip install pdfplumber
    python3 script/pdf_to_csv.py ~/Downloads/schedule.pdf /tmp/schedule.json
    deactivate
    rm -rf ~/pdfenv

Then paste the contents of /tmp/schedule.json as the value of `defaultData`
inside  js/schedule_data.js  (wrap it: const defaultData = <paste here>;)



