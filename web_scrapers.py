import requests
from bs4 import BeautifulSoup
import time

def fetch_url(url):
    """Fetch the content of a URL with error handling."""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def scrape_leafly_strains() -> list:
    """Scrape strain information from Leafly."""
    url = 'https://www.leafly.com/strains'
    html_content = fetch_url(url)
    if html_content is None:
        return []

    soup = BeautifulSoup(html_content, 'html.parser')
    strains = []
    for strain in soup.select('.strain-card'):
        name = strain.select_one('.strain-name').text.strip()
        description = strain.select_one('.strain-description').text.strip()
        strains.append({'name': name, 'description': description})

    return strains

def scrape_weedmaps_deals() -> list:
    """Scrape deals from Weedmaps."""
    url = 'https://weedmaps.com/deals'
    html_content = fetch_url(url)
    if html_content is None:
        return []

    soup = BeautifulSoup(html_content, 'html.parser')
    deals = []
    for deal in soup.select('.deal-card'):
        title = deal.select_one('.deal-title').text.strip()
        description = deal.select_one('.deal-description').text.strip()
        deals.append({'title': title, 'description': description})

    return deals

def main():
    # Scrape data
    leafly_strains = scrape_leafly_strains()
    weedmaps_deals = scrape_weedmaps_deals()

    # Print results
    print("Leafly Strains:")
    for strain in leafly_strains:
        print(f"Name: {strain['name']}, Description: {strain['description']}")

    print("\nWeedmaps Deals:")
    for deal in weedmaps_deals:
        print(f"Title: {deal['title']}, Description: {deal['description']}")

    # Optional: Rate limiting
    time.sleep(1)  # Sleep for 1 second between requests

if __name__ == "__main__":
    main()