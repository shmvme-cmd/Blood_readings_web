import sys, glob, re
sys.path.insert(0, 'C:/Project/Python/Blood_readings_web')
import pdfplumber

files = glob.glob('C:/Project/Python/Blood_readings_web/*.pdf')
all_rows = {}  # filename -> list of (test_name, result, unit)

for f in sorted(files):
    fname = f.replace('\\', '/').split('/')[-1]
    rows = []
    try:
        with pdfplumber.open(f) as pdf:
            for page in pdf.pages:
                for table in (page.extract_tables() or []):
                    for row in table:
                        if not row or not row[0]:
                            continue
                        label = str(row[0]).strip()
                        if label in ('Тест', '', 'None'):
                            continue
                        result = str(row[1]).strip() if len(row) > 1 and row[1] else ''
                        unit = str(row[-1]).strip() if row[-1] else ''
                        rows.append((label, result, unit))
    except Exception as e:
        rows.append((f'ERROR: {e}', '', ''))
    all_rows[fname] = rows

print('=' * 70)
for fname, rows in all_rows.items():
    print(f'\n[{fname}]')
    for label, result, unit in rows:
        print(f'  {label!r:60s} | {result:10s} | {unit}')
