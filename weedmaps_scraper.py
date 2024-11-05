import requests
from bs4 import BeautifulSoup
import sqlite3

# URL of the Weedmaps dispensaries page
URL = 'https://weedmaps.com/dispensaries'

response = requests.get(URL)
soup = BeautifulSoup(response.text, 'html.parser')

# Example: Extracting dispensary information
dispensaries = []
for dispensary in soup.find_all('div', class_='dispen-card'):
    name = dispensary.find('h2').text.strip()
    address = dispensary.find('p', class_='address').text.strip()
    phone = dispensary.find('p', class_='phone').text.strip()
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
cursor.executemany('''
INSERT INTO dispensaries (name, address, phone)
VALUES (?, ?, ?)
''', dispensaries)

conn.commit()
conn.close()
