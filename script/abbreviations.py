# -*- coding: utf-8 -*-
"""
Mapping from subject abbreviations (as they appear in the timetable cells,
e.g. "ΑρχΓλ", "Γλω", "Μαθ") to their full Greek name.

Keys are regex patterns that are matched with re.fullmatch() against the
(whitespace-normalized) abbreviation found in a cell. Order matters only
when patterns could ambiguously overlap; Python dicts preserve insertion
order, and the first matching pattern wins.

Feel free to add / edit / remove entries here without touching the main
script.
"""

ABBREVIATIONS = {
    r'Α[ρχ]+\s?Γλ\d?': 'Αρχαία Γλώσσα',
    r'Γαλ': 'Γαλλικά',
    r'Γερ': 'Γερμανικά',
    r'Μαθ\d?': 'Μαθηματικά',
    r'Εργ': 'Εργαστήριο Δεξιοτήτων',
    r'Γλώ\d?': 'Γλώσσα',
    r'Γλω\d?': 'Γλώσσα',
    r'Γλ': 'Γλώσσα',
    r'Ν[εέ][Λλ]': 'Λογοτεχνία',
    r'Αγγ': 'Αγγλικά',
    r'Αρ?χ?Κμ': 'Αρχαία Κείμενα',
    r'Γεω\d?': 'Γεωγραφία',
    r'Ιστ': 'Ιστορία',
    r'Καλ': 'Εικαστικά',
    r'Θρσ': 'Θρησκευτικά',
    r'Βιο': 'Βιολογία',
    r'Φσκ': 'Φυσική',
    r'Γμν\d?': 'Γυμναστική',
    r'Οικ': 'Οικιακή Οικονομία',
    r'Πλρ(?:[12]?Πλρ|2| Πλρ)?': 'Πληροφορική',
    r'Τχν': 'Τεχνολογία',
    r'Μσκ': 'Μουσική',
    r'Χημ': 'Χημεία',
    r'Φυσ': 'Φυσική',
    r'Κπα': 'Κοινωνική και Πολιτική Αγωγή',
}
