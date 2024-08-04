import requests
from bs4 import BeautifulSoup

def scrape_leafly_strains():
    url = 'https://www.leafly.com/strains'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    strains = []
    for strain in soup.select('.strain-card'):
        name = strain.select_one('.strain-name').text
        description = strain.select_one('.strain-description').text
        strains.append({'name': name, 'description': description})

    return strains

def scrape_weedmaps_deals():
    url = 'https://weedmaps.com/deals'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    deals = []
    for deal in soup.select('.deal-card'):
        title = deal.select_one('.deal-title').text
        description = deal.select_one('.deal-description').text
        deals.append({'title': title, 'description': description})

    return deals
