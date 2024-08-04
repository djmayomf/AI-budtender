import requests
from bs4 import BeautifulSoup
import sqlite3

# URL of the Leafly strains page
URL = 'https://www.leafly.com/strains'

response = requests.get(URL)
soup = BeautifulSoup(response.text, 'html.parser')

# Example: Extracting strain information
strains = []
for strain in soup.find_all('div', class_='strain-card'):
    name = strain.find('h2').text.strip()
    description = strain.find('p', class_='description').text.strip()
    # Add other relevant fields as needed
    strains.append((name, description))

# Connect to SQL database
conn = sqlite3.connect('leafly.db')
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''
CREATE TABLE IF NOT EXISTS strains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL
)
''')

# Insert scraped data into table
cursor.executemany('''
INSERT INTO strains (name, description)
VALUES (?, ?)
''', strains)

conn.commit()
conn.close()
