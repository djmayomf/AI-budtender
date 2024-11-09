from typing import Optional, Dict, List
from dataclasses import dataclass
from datetime import datetime
import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from ratelimit import limits, sleep_and_retry
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

@dataclass
class ScraperConfig:
    CALLS: int = 30
    RATE_LIMIT: int = 60
    MAX_RETRIES: int = 3
    BACKOFF_FACTOR: float = 0.3
    TIMEOUT: int = 10

class BaseWebScraper:
    def __init__(self, config: Optional[ScraperConfig] = None):
        self.config = config or ScraperConfig()
        self.session = self._setup_session()
        self.ua = UserAgent(verify_ssl=False)
        self.logger = logging.getLogger(__name__)

    def _setup_session(self) -> requests.Session:
        session = requests.Session()
        retry = Retry(
            total=self.config.MAX_RETRIES,
            backoff_factor=self.config.BACKOFF_FACTOR,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry, pool_maxsize=100)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    @sleep_and_retry
    @limits(calls=ScraperConfig.CALLS, period=ScraperConfig.RATE_LIMIT)
    def _make_request(self, url: str) -> Optional[requests.Response]:
        try:
            headers = {
                'User-Agent': self.ua.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive'
            }
            response = self.session.get(
                url, 
                headers=headers,
                timeout=self.config.TIMEOUT,
                verify=False
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching {url}: {str(e)}")
            return None

class WeedmapsScraper(BaseWebScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://weedmaps.com"

    def scrape_deals(self, location: Optional[str] = None) -> List[Dict]:
        url = f"{self.base_url}/deals"
        if location:
            url = f"{url}/{location}"
            
        try:
            response = self._make_request(url)
            if not response:
                return []
                
            soup = BeautifulSoup(response.text, 'html.parser')
            deals = []
            
            for deal_elem in soup.select('.deal-card'):
                try:
                    deal = self._parse_deal_element(deal_elem)
                    if deal:
                        deals.append(deal)
                except Exception as e:
                    logger.error(f"Error parsing deal element: {str(e)}")
                    continue
                    
            return deals
            
        except Exception as e:
            logger.error(f"Error scraping deals: {str(e)}")
            return []

    def _parse_deal_element(self, element: BeautifulSoup) -> Optional[Dict]:
        try:
            return {
                'title': element.select_one('.deal-title').text.strip(),
                'dispensary': element.select_one('.dispensary-name').text.strip(),
                'location': element.select_one('.location').text.strip(),
                'price': self._parse_price(element),
                'image_url': self._get_image_url(element),
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error parsing element: {str(e)}")
            return None

    def _parse_price(self, element: BeautifulSoup) -> Dict:
        try:
            price_elem = element.select_one('.price')
            original = float(price_elem.select_one('.original-price')
                           .text.strip().replace('$', ''))
            discounted = float(price_elem.select_one('.discounted-price')
                             .text.strip().replace('$', ''))
            
            return {
                'original': original,
                'discounted': discounted,
                'savings': round(((original - discounted) / original) * 100, 2)
            }
        except Exception as e:
            logger.error(f"Error parsing price: {str(e)}")
            return {'original': 0, 'discounted': 0, 'savings': 0}

    def _get_image_url(self, element: BeautifulSoup) -> Optional[str]:
        try:
            img = element.select_one('img')
            return img['src'] if img else None
        except Exception:
            return None