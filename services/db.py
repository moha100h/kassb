import sqlite3, json, os
from config import DB_PATH

def _conn():
    os.makedirs(os.path.dirname(os.path.abspath(DB_PATH)), exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.execute(
        'CREATE TABLE IF NOT EXISTS cache ('
        'id INTEGER PRIMARY KEY AUTOINCREMENT,'
        'city TEXT, category TEXT, data TEXT,'
        'created_at DATETIME DEFAULT CURRENT_TIMESTAMP)'
    )
    c.commit()
    return c

def save_results(city, category, results):
    c = _conn()
    c.execute('DELETE FROM cache WHERE city=? AND category=?', (city, category))
    c.execute('INSERT INTO cache (city,category,data) VALUES (?,?,?)',
              (city, category, json.dumps(results, ensure_ascii=False)))
    c.commit()
    c.close()

def get_cached(city, category):
    c = _conn()
    row = c.execute(
        'SELECT data FROM cache WHERE city=? AND category=? '
        'AND created_at > datetime("now","-24 hours") ORDER BY id DESC LIMIT 1',
        (city, category)
    ).fetchone()
    c.close()
    return json.loads(row[0]) if row else None
