import sqlite3

def create_database():
    try:
        with sqlite3.connect('preferences.db') as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS preferences (
                            user_id INTEGER,
                            product_id INTEGER,
                            rating INTEGER
                        )''')
            conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    create_database()