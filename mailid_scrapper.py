import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse

class EmailScraper:
    def __init__(self, start_url):
        self.start_url = start_url
        self.visited_urls = set()
        self.emails = set()

    def scrape_emails(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all email addresses on the current page
            new_emails = set(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", response.text))
            self.emails.update(new_emails)
        
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch {url}: {e}")
        
    def find_target_pages(self, soup):
        targets = ["about", "contact"]
        for anchor in soup.find_all("a", href=True):
            link = anchor["href"]
            print("Finding Pages")
            if any(target in link.lower() for target in targets):
                full_url = urljoin(self.start_url, link)
                if self.is_valid_url(full_url):
                    print("page found:", full_url)
                    return full_url
        return None

    def is_valid_url(self, url):
        parsed_url = urlparse(url)
        is_internal = parsed_url.netloc == urlparse(self.start_url).netloc
        is_new = url not in self.visited_urls
        return is_internal and is_new

    def run(self):
        try:
            response = requests.get(self.start_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            target_url = self.find_target_pages(soup)
            if target_url:
                self.visited_urls.add(target_url)
                self.scrape_emails(target_url)
            return self.emails
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch {self.start_url}: {e}")
            return set()

if __name__ == "__main__":
    start_url = input("Enter Your URL:")
    scraper = EmailScraper(start_url)
    emails = scraper.run()
    print("Emails found:")
    for email in emails:
        print(email)
