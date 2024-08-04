import sqlite3

def create_database():
    conn = sqlite3.connect('preferences.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS preferences (
                    user_id INTEGER,
                    product_id INTEGER,
                    rating INTEGER
                )''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_database()
