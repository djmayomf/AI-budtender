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
                            comment TEXT,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                            PRIMARY KEY (user_id, product_id)
                        )''')
            conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred while creating the database: {e}")

def insert_preference(user_id, product_id, rating, comment=None):
    """Insert a user preference into the preferences table."""
    try:
        with sqlite3.connect('preferences.db') as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO preferences (user_id, product_id, rating, comment)
                VALUES (?, ?, ?, ?)
            ''', (user_id, product_id, rating, comment))
            conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred while inserting data: {e}")

def get_preferences(user_id):
    """Retrieve preferences for a specific user."""
    try:
        with sqlite3.connect('preferences.db') as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM preferences WHERE user_id = ?', (user_id,))
            return c.fetchall()
    except sqlite3.Error as e:
        print(f"An error occurred while retrieving data: {e}")
        return []

if __name__ == '__main__':
    create_database()
    # Example usage
    insert_preference(1, 101, 5, "Great product!")
    preferences = get_preferences(1)
    print(preferences)