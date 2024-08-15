import sqlite3

def create_database():
    """Create a SQLite database and a preferences table if it doesn't exist."""
    try:
        with sqlite3.connect('preferences.db') as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS preferences (
                            user_id INTEGER NOT NULL,
                            product_id INTEGER NOT NULL,
                            rating INTEGER CHECK(rating >= 1 AND rating <= 5),
                            PRIMARY KEY (user_id, product_id)
                        )''')
            conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred while creating the database: {e}")

if __name__ == '__main__':
    create_database()