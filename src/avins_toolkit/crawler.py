from collections import deque
from avins_toolkit.configs import CrawlerConfig
import httpx
import logging
from bs4 import BeautifulSoup
from urllib.parse import urlsplit, urljoin, urldefrag
import time
import urllib.robotparser
from functools import cache

logger = logging.getLogger(__name__)


class Crawler:
    def __init__(self, config: CrawlerConfig = None):
        self.config = config if config is not None else CrawlerConfig()
        self.q = deque(self.config.seeds)
        self.visited = set()
        self.failures = {}
        self.seen = set(self.config.seeds)
        self.robots_cache = {}
        self.client = httpx.Client(
            follow_redirects=True, headers=self.config.header, timeout=self.config.timeout
        )

    def bfs(self):
        depth = 0
        while (
            depth < self.config.max_depth and self.q and len(self.visited) < self.config.max_pages
        ):
            k = len(self.q)
            depth += 1
            for _ in range(k):
                if len(self.visited) >= self.config.max_pages:
                    break
                site = self.q.popleft()
                if site not in self.visited and site not in self.failures:
                    self.scrape(site)
        self.client.close()

    def scrape(self, site: str):
        # three things required in scrape:
        # Scrape data and identify hyperlinks
        # Add the extracted hyperlinks to q
        # Log errors in case of unreachable hyperlinks
        if not self.roboprotocol(site):
            return None
        time.sleep(self.config.delay)
        try:
            r = self.client.get(site)
        except httpx.RequestError as err:
            logger.warning(f"{site}: Network_error")
            self.failures[site] = "Network_error"
            return None
        if not r.is_success:
            status_code = r.status_code
            request_url = r.request.url
            if status_code == 404:
                logger.warning(f"Resource not found (404) at {request_url}")
            elif 400 <= status_code < 500:
                logger.error(f"Client error {status_code} for {request_url}")
            elif status_code >= 500:
                logger.warning(f"Server error {status_code} from {request_url}")
            self.failures[site] = status_code
            return None
        else:
            clean_text = ""
            if "text/html" in r.headers.get("content-type", "").lower():
                self.visited.add(site)
                soup = BeautifulSoup(r.text, "html.parser")
                clean_text = soup.get_text(separator=" ", strip=True)
                for a in soup.find_all("a", href=True):
                    cleaned_link = self._clean_link(a.get("href"), site)
                    if cleaned_link is not None and cleaned_link not in self.seen:
                        self.q.append(cleaned_link)
                        self.seen.add(cleaned_link)
                with open("src/extracted_data.txt", "a", encoding="utf-8") as file:
                    file.write(site + "\n" + clean_text + "\n")
            else:
                logger.debug(f"{site} does not return pdf")

    def _clean_link(self, href, site):
        href = href.strip()
        site = site.strip()
        site = urljoin(site, href)
        split = urlsplit(site)
        if split.hostname is None or href == "":
            return None
        if (split.scheme == "http" or split.scheme == "https") and (
            split.hostname in self.config.allowed_domains
            or any(split.hostname.endswith("." + s) for s in self.config.allowed_domains)
        ):
            return urldefrag(site).url
        else:
            return None

    def roboprotocol(self, url):
        split = urlsplit(url)
        source = split.scheme + "://" + split.netloc
        if source in self.robots_cache:
            rp = self.robots_cache[source]
            if rp == "Allow all":
                return True
            elif rp == "Deny all":
                return False
        else:
            try:
                r = self.client.get(urljoin(source, "/robots.txt"))
            except httpx.RequestError:
                logger.warning(f"{urljoin(source, '/robots.txt')}: Network_error")
                self.failures[urljoin(source, "/robots.txt")] = "Network_error"
                self.robots_cache[source] = "Deny all"
                return False
            if not r.is_success:
                status_code = r.status_code
                if status_code == 404:
                    logger.debug("Robots.txt not found:allowing all")
                    self.robots_cache[source] = "Allow all"
                    return True
                else:
                    logger.warning("Inaccessable")
                    self.robots_cache[source] = "Deny all"
                    return False
            else:
                rp = urllib.robotparser.RobotFileParser()
                rp.parse(r.text.splitlines())
                self.robots_cache[source] = rp
        return rp.can_fetch("AvinsCrawler", url)
