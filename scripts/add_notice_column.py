import sqlite3, os
candidates = ["student_manager.db", os.path.join('instance','student_manager.db')]
for p in candidates:
    if not os.path.exists(p):
        print(f"Not found: {p}")
        continue
    print(f"Checking: {p}")
    try:
        conn = sqlite3.connect(p)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notice'")
        if not cur.fetchone():
            print(' - notice table not present, skipping')
            conn.close()
            continue
        cur.execute("PRAGMA table_info(notice)")
        cols = [r[1] for r in cur.fetchall()]
        print(' - columns:', cols)
        if 'teacher_id' in cols:
            print(' - teacher_id already present')
        else:
            try:
                cur.execute('ALTER TABLE notice ADD COLUMN teacher_id INTEGER')
                conn.commit()
                print(' - Added teacher_id column')
            except Exception as e:
                print(' - Failed to add column:', e)
        conn.close()
    except Exception as e:
        print('Error opening', p, e)
