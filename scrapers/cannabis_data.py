from bs4 import BeautifulSoup
import requests
import json
import time
from typing import Dict, List
import logging
from fake_useragent import UserAgent
import os

class CannabisDataScraper:
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.ua.random
        })
        self.data_dir = 'data'
        os.makedirs(self.data_dir, exist_ok=True)

    def scrape_weedmaps_prices(self, location: str) -> List[Dict]:
        """Scrape current prices from Weedmaps"""
        prices = []
        base_url = f"https://weedmaps.com/dispensaries/in/{location}"
        
        try:
            response = self.session.get(base_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract product listings
            products = soup.select('.product-card')
            
            for product in products:
                try:
                    price_info = {
                        'name': product.select_one('.product-name').text.strip(),
                        'price': product.select_one('.product-price').text.strip(),
                        'dispensary': product.select_one('.dispensary-name').text.strip(),
                        'category': product.select_one('.product-category').text.strip(),
                        'image_url': product.select_one('img')['src'],
                        'rating': product.select_one('.rating-score').text.strip(),
                        'reviews': product.select_one('.review-count').text.strip()
                    }
                    prices.append(price_info)
                except Exception as e:
                    logging.error(f"Error parsing product: {str(e)}")
                    
            return prices
            
        except Exception as e:
            logging.error(f"Error scraping Weedmaps: {str(e)}")
            return []

    def scrape_leafly_strains(self) -> Dict:
        """Scrape strain information from Leafly"""
        strains = {}
        base_url = "https://www.leafly.com/strains"
        
        try:
            response = self.session.get(base_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract strain listings
            strain_cards = soup.select('.strain-card')
            
            for card in strain_cards:
                try:
                    strain_name = card.select_one('.strain-name').text.strip()
                    strain_url = card.select_one('a')['href']
                    
                    # Get detailed strain info
                    strain_info = self._get_strain_details(strain_url)
                    strains[strain_name.lower()] = strain_info
                    
                    # Respect rate limiting
                    time.sleep(1)
                    
                except Exception as e:
                    logging.error(f"Error parsing strain: {str(e)}")
                    
            return strains
            
        except Exception as e:
            logging.error(f"Error scraping Leafly: {str(e)}")
            return {}

    def _get_strain_details(self, strain_url: str) -> Dict:
        """Get detailed information about a specific strain"""
        try:
            response = self.session.get(strain_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            return {
                'type': soup.select_one('.strain-type').text.strip(),
                'thc': soup.select_one('.thc-percentage').text.strip(),
                'cbd': soup.select_one('.cbd-percentage').text.strip(),
                'effects': [effect.text.strip() for effect in soup.select('.effects-list li')],
                'flavors': [flavor.text.strip() for flavor in soup.select('.flavors-list li')],
                'description': soup.select_one('.strain-description').text.strip(),
                'image_url': soup.select_one('.strain-image img')['src']
            }
        except Exception as e:
            logging.error(f"Error getting strain details: {str(e)}")
            return {}

    def save_data(self):
        """Save scraped data to JSON files"""
        try:
            # Scrape and save Weedmaps prices
            prices = self.scrape_weedmaps_prices('san-francisco')
            with open(os.path.join(self.data_dir, 'prices.json'), 'w') as f:
                json.dump(prices, f, indent=2)
                
            # Scrape and save Leafly strains
            strains = self.scrape_leafly_strains()
            with open(os.path.join(self.data_dir, 'strains.json'), 'w') as f:
                json.dump(strains, f, indent=2)
                
        except Exception as e:
            logging.error(f"Error saving data: {str(e)}") 