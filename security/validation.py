from bs4 import BeautifulSoup
import bleach
import re

class InputSecurity:
    def __init__(self):
        self.allowed_tags = [
            'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'ul', 'ol', 'li', 'a', 'img'
        ]
        self.allowed_attributes = {
            'a': ['href', 'title'],
            'img': ['src', 'alt', 'title']
        }

    def sanitize_html(self, content):
        return bleach.clean(
            content,
            tags=self.allowed_tags,
            attributes=self.allowed_attributes,
            strip=True
        )

    def validate_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def validate_phone(self, phone):
        pattern = r'^\+?1?\d{9,15}$'
        return bool(re.match(pattern, phone))
