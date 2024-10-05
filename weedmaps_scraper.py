import requests
from bs4 import BeautifulSoup
import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def scrape_dispensaries():
    url = 'https://weedmaps.com/dispensaries'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        soup = BeautifulSoup(response.text, 'html.parser')

        dispensaries = []
        for dispensary in soup.find_all('div', class_='dispen-card'):
            name = dispensary.find('h2').text.strip()
            address = dispensary.find('p', class_='address').text.strip()
            phone = dispensary.find('p', class_='phone').text.strip()
            dispensaries.append((name, address, phone))

        logging.info(f"Scraped {len(dispensaries)} dispensaries from Weedmaps")
        return dispensaries
    except requests.RequestException as e:
        logging.error(f"Error fetching Weedmaps dispensaries: {e}")
        return []
    except Exception as e:
        logging.error(f"Error parsing Weedmaps dispensaries: {e}")
        return []

def save_to_database(dispensaries):
    try:
        with sqlite3.connect('weedmaps.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS dispensaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                phone TEXT NOT NULL
            )
            ''')
            cursor.executemany('''
            INSERT INTO dispensaries (name, address, phone)
            VALUES (?, ?, ?)
            ''', dispensaries)
            conn.commit()
            logging.info("Dispensaries saved to database successfully")
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
    except Exception as e:
        logging.error(f"Error saving to database: {e}")

if __name__ == "__main__":
    dispensaries = scrape_dispensaries()
    if dispensaries:
        save_to_database(dispensaries)