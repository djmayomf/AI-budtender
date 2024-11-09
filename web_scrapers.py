import requests
from bs4 import BeautifulSoup

def scrape_leafly_strains():
    leafly_url = 'https://www.leafly.com/strains'
    try:
        response = requests.get(leafly_url)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
    except requests.RequestException as e:
        print(f"Error: {e}")
        return None

    # ... rest of the code remains the same ...

def scrape_weedmaps_deals() -> list:
    """Scrape deals from Weedmaps."""
    url = 'https://weedmaps.com/deals'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    deals = []
    for deal in soup.select('.deal-card'):
        title = deal.select_one('.deal-title').text
        description = deal.select_one('.deal-description').text
        deals.append({'title': title, 'description': description})

    return deals
