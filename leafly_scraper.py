import requests
from bs4 import BeautifulSoup
import sqlite3

def fetch_strains(url):
    """https://www.leafly.com/strains"""
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses
        soup = BeautifulSoup(response.text, 'html.parser')
        
        strains = []
        for strain in soup.find_all('div', class_='strain-card'):
            name_tag = strain.find('h2')
            description_tag = strain.find('p', class_='description')
            
            if name_tag and description_tag:  # Check if tags exist
                name = name_tag.text.strip()
                description = description_tag.text.strip()
                strains.append((name, description))
        
        return strains
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return []

def create_database():
    """Create a SQLite database and a strains table if it doesn't exist."""
    try:
        with sqlite3.connect('leafly.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS strains (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL
            )
            ''')
            conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred while creating the database: {e}")

def insert_strains(strains):
    """Insert strain data into the database."""
    try:
        with sqlite3.connect('leafly.db') as conn:
            cursor = conn.cursor()
            cursor.executemany('''
            INSERT INTO strains (name, description)
            VALUES (?, ?)
            ''', strains)
            conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred while inserting data: {e}")

if __name__ == '__main__':
    URL = 'https://www.leafly.com/strains'
    create_database()
    strains = fetch_strains(URL)
    if strains:
        insert_strains(strains)
        print(f"Inserted {len(strains)} strains into the database.")
    else:
        print("No strains found or an error occurred.")