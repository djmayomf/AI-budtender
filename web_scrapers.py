import requests
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def scrape_leafly_strains():
    url = 'https://www.leafly.com/strains'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        soup = BeautifulSoup(response.text, 'html.parser')

        strains = []
        for strain in soup.select('.strain-card'):
            name = strain.select_one('.strain-name').text.strip()
            description = strain.select_one('.strain-description').text.strip()
            strains.append({'name': name, 'description': description})

        logging.info(f"Scraped {len(strains)} strains from Leafly")
        return strains
    except requests.RequestException as e:
        logging.error(f"Error fetching Leafly strains: {e}")
        return []
    except Exception as e:
        logging.error(f"Error parsing Leafly strains: {e}")
        return []

def scrape_weedmaps_deals():
    url = 'https://weedmaps.com/deals'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        soup = BeautifulSoup(response.text, 'html.parser')

        deals = []
        for deal in soup.select('.deal-card'):
            title = deal.select_one('.deal-title').text.strip()
            description = deal.select_one('.deal-description').text.strip()
            deals.append({'title': title, 'description': description})

        logging.info(f"Scraped {len(deals)} deals from Weedmaps")
        return deals
    except requests.RequestException as e:
        logging.error(f"Error fetching Weedmaps deals: {e}")
        return []
    except Exception as e:
        logging.error(f"Error parsing Weedmaps deals: {e}")
        return []

# Example usage
if __name__ == "__main__":
    leafly_strains = scrape_leafly_strains()
    weedmaps_deals = scrape_weedmaps_deals()
    print(leafly_strains)
    print(weedmaps_deals)