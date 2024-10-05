import requests
from bs4 import BeautifulSoup
import sqlite3

# URL of the Leafly strains page
URL = 'https://www.leafly.com/strains'

# Set up headers to avoid being blocked
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

try:
    response = requests.get(URL, headers=headers)
    response.raise_for_status()  # Raise an HTTPError for bad responses
    soup = BeautifulSoup(response.text, 'html.parser')

    # Example: Extracting strain information
    strains = []
    for strain in soup.find_all('div', class_='strain-card'):
        name = strain.find('h2').text.strip()
        description = strain.find('p', class_='description').text.strip()
        # Add other relevant fields as needed
        strains.append((name, description))

    # Connect to SQL database
    with sqlite3.connect('leafly.db') as conn:
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
        ''' , strains)

        conn.commit()

except requests.RequestException as e:
    print(f"An error occurred while making the HTTP request: {e}")
except sqlite3.Error as e:
    print(f"An error occurred while interacting with the database: {e}")