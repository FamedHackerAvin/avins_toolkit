from dataclasses import dataclass, field
import logging
import httpx

logger = logging.getLogger(__name__)


@dataclass
class CrawlerConfig:
    max_pages: int = 100
    max_depth: int = 5
    delay: float = 1.0
    seeds: list[str] = field(default_factory=lambda: ["https://example.com/"])
    allowed_domains: list[str] = field(default_factory=lambda: ["https://example.com/"])
    timeout: float = 10.0
    retries: int = 2
    output_directory: list[str] = field(default_factory=lambda: ["https://example.com/"])
    max_pdf_size: int = 10  # in mbs if max pages is 100 then 1000mb only
    header: dict[str, str] = field(
        default_factory=lambda: {"user-agent": "AvinsCrawler/1.0(+repo-link)"}
    )  # add repo link after repo is public

    def __post_init__(self):
        if self.max_pages < 1:
            raise ValueError("Max pages cannot be less than zero.")
        if self.max_depth < 1:
            raise ValueError("Max depth cannot be less than zero.")
        if self.delay < 0:
            raise ValueError("Delay cannot be negative")
        if self.seeds == []:
            raise ValueError("Seeds list cannot be empty")
        for i in self.seeds:
            if httpx.URL(i).scheme == "https":
                pass
            else:
                raise httpx.InvalidURL("URL is not valid")
        if self.allowed_domains == []:
            raise ValueError("Allowed domains cannot be empty")
        if self.timeout <= 0:
            raise ValueError("Timeout has to be positive")
        if self.retries < 0:
            raise ValueError("Retries cannot be negative")
        if self.max_pdf_size <= 0:
            raise ValueError("Max_pdf_size shld be positive")
