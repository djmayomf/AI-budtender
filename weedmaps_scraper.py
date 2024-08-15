import requests
from bs4 import BeautifulSoup
import sqlite3
import time

# URL of the Weedmaps dispensaries page
URL = 'https://weedmaps.com/dispensaries'

try:
    response = requests.get(URL)
    response.raise_for_status()  # Raise an error for bad responses
except requests.RequestException as e:
    print(f"Error fetching the URL: {e}")
    exit()

soup = BeautifulSoup(response.text, 'html.parser')

# Example: Extracting dispensary information
dispensaries = []
for dispensary in soup.find_all('div', class_='dispen-card'):
    name = dispensary.find('h2').text.strip() if dispensary.find('h2') else 'N/A'
    address = dispensary.find('p', class_='address').text.strip() if dispensary.find('p', class_='address') else 'N/A'
    phone = dispensary.find('p', class_='phone').text.strip() if dispensary.find('p', class_='phone') else 'N/A'
    
    # Add other relevant fields as needed
    dispensaries.append((name, address, phone))

# Connect to SQL database
conn = sqlite3.connect('weedmaps.db')
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''
CREATE TABLE IF NOT EXISTS dispensaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    phone TEXT NOT NULL
)
''')

# Insert scraped data into table
try:
    cursor.executemany('''
    INSERT INTO dispensaries (name, address, phone)
    VALUES (?, ?, ?)
    ''', dispensaries)
    conn.commit()
except sqlite3.Error as e:
    print(f"Database error: {e}")
finally:
    conn.close()

print(f"Inserted {len(dispensaries)} dispensaries into the database.")