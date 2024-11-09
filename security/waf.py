from flask import Request
import re
from typing import Dict, List, Pattern
import ipaddress

class WAF:
    def __init__(self):
        self.rules = self._compile_rules()
        self.blacklist = self._load_blacklist()
        self.whitelist = self._load_whitelist()

    def _compile_rules(self) -> Dict[str, List[Pattern]]:
        """Compile WAF rules"""
        return {
            'xss': [
                re.compile(r'<script.*?>.*?</script>', re.I),
                re.compile(r'on\w+\s*=.*?(?:alert|confirm|prompt)', re.I),
                re.compile(r'javascript:', re.I)
            ],
            'sql_injection': [
                re.compile(r'\b(union|select|insert|update|delete|drop)\b', re.I),
                re.compile(r'--.*$'),
                re.compile(r'/\*.*?\*/')
            ],
            'path_traversal': [
                re.compile(r'\.{2,}[/\\]'),
                re.compile(r'%2e%2e[/\\]', re.I)
            ],
            'command_injection': [
                re.compile(r'[;&|`]'),
                re.compile(r'\$\(.*?\)'),
                re.compile(r'system\s*\(')
            ]
        }

    def _load_blacklist(self) -> List[str]:
        """Load IP blacklist"""
        try:
            with open('security/blacklist.txt', 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            return []

    def _load_whitelist(self) -> List[str]:
        """Load IP whitelist"""
        try:
            with open('security/whitelist.txt', 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            return []

    def check_request(self, request: Request) -> bool:
        """Check if request passes WAF rules"""
        # Check IP
        if not self._check_ip(request.remote_addr):
            return False

        # Check request method
        if request.method not in ['GET', 'POST', 'PUT', 'DELETE']:
            return False

        # Check headers
        if not self._check_headers(request.headers):
            return False

        # Check URL
        if not self._check_url(request.url):
            return False

        # Check query parameters
        if not self._check_parameters(request.args):
            return False

        # Check body
        if request.is_json:
            if not self._check_json(request.get_json()):
                return False

        return True

    def _check_ip(self, ip: str) -> bool:
        """Check if IP is allowed"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            
            # Check whitelist
            if self.whitelist and ip not in self.whitelist:
                return False
                
            # Check blacklist
            if ip in self.blacklist:
                return False
                
            # Block private IPs in production
            if ip_obj.is_private:
                return False
                
            return True
        except ValueError:
            return False

    def _check_headers(self, headers: Dict) -> bool:
        """Check request headers"""
        # Check for required headers
        if 'User-Agent' not in headers:
            return False

        # Check for suspicious headers
        for header, value in headers.items():
            for category, patterns in self.rules.items():
                for pattern in patterns:
                    if pattern.search(str(value)):
                        return False

        return True

    def _check_url(self, url: str) -> bool:
        """Check URL for malicious patterns"""
        for category, patterns in self.rules.items():
            for pattern in patterns:
                if pattern.search(url):
                    return False
        return True

    def _check_parameters(self, params: Dict) -> bool:
        """Check query parameters"""
        for param, value in params.items():
            for category, patterns in self.rules.items():
                for pattern in patterns:
                    if pattern.search(str(value)):
                        return False
        return True

    def _check_json(self, data: Dict) -> bool:
        """Check JSON data"""
        def check_value(value):
            if isinstance(value, str):
                for category, patterns in self.rules.items():
                    for pattern in patterns:
                        if pattern.search(value):
                            return False
            elif isinstance(value, dict):
                return all(check_value(v) for v in value.values())
            elif isinstance(value, list):
                return all(check_value(v) for v in value)
            return True

        return check_value(data)
