"""
AgenticSeek implementation for NIA.
A strict Local-Only Proxy to ensure outbound research requests never leak
12th-grade or sensitive project data.
"""
import requests
from urllib.parse import urlparse
import re

class LocalProxy:
    def __init__(self, allowed_domains: list[str] = None):
        self.allowed_domains = allowed_domains or ["wikipedia.org", "github.com", "arxiv.org"]
        self.sensitive_patterns = [
            r"12th_grade", r"personal", r"password", r"api_key"
        ]
        print(f"[Network] AgenticSeek initialized. Allowed: {self.allowed_domains}")

    def _is_safe_query(self, query: str) -> bool:
        """Checks if the query contains sensitive local data concepts."""
        for pattern in self.sensitive_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                print(f"[Network] BLOCK: Query contains restricted local pattern: {pattern}")
                return False
        return True

    def _is_allowed_domain(self, url: str) -> bool:
        """Validates outbound domain."""
        try:
            domain = urlparse(url).netloc
            for allowed in self.allowed_domains:
                if allowed in domain:
                    return True
            print(f"[Network] BLOCK: Domain {domain} is not in the allowed list.")
            return False
        except Exception:
            return False

    def fetch(self, url: str, query_context: str = "") -> str:
        """Proxies fetch request with strict checks."""
        if not self._is_safe_query(query_context):
            return "Blocked by LocalProxy: Query unsafe."
            
        if not self._is_allowed_domain(url):
            return "Blocked by LocalProxy: Domain unrestrained."

        print(f"[Network] AgenticSeek fetching (SAFE): {url}")
        try:
            # Mocking fetch to avoid hanging in offline contexts
            # response = requests.get(url, timeout=5)
            # return response.text[:500]
            return f"Mock response from {url}"
        except requests.RequestException as e:
            return f"Network Error: {e}"

if __name__ == "__main__":
    proxy = LocalProxy()
    print(proxy.fetch("https://en.wikipedia.org/wiki/India", "What is India?"))
    print(proxy.fetch("https://malicious.com", "My 12th_grade marks are..."))
