import sqlite3, os

db_path = os.path.join(os.path.dirname(__file__), 'instance', 'medical_analyses.db')
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("PRAGMA table_info(medical_analysis)")
existing = {row[1] for row in cur.fetchall()}

new_columns = [
    ('bilirubin_total',        'REAL'),
    ('bilirubin_direct',       'REAL'),
    ('bilirubin_indirect',     'REAL'),
    ('alkaline_phosphatase',   'REAL'),
    ('urea',                   'REAL'),
    ('gfr',                    'REAL'),
    ('ckf_total',              'REAL'),
    ('psa',                    'REAL'),
    ('microalbumin',           'REAL'),
    ('urine_specific_gravity', 'REAL'),
    ('urine_ph',               'REAL'),
    ('urine_protein',          'REAL'),
    ('urine_urobilinogen',     'REAL'),
]

for col, typ in new_columns:
    if col not in existing:
        cur.execute(f'ALTER TABLE medical_analysis ADD COLUMN {col} {typ}')
        print(f'  + добавлена колонка: {col}')
    else:
        print(f'  = уже есть: {col}')

conn.commit()
conn.close()
print('Готово!')
