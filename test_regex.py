import re
with open("sample_data/notes.txt") as f:
    notes_text = f.read()

name_match = re.search(r'(?:candidate|name):\s*([^\n\r]+)', notes_text, re.IGNORECASE)
print(repr(name_match.group(1)))