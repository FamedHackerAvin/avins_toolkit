import logging

from avins_toolkit.configs import CrawlerConfig
from avins_toolkit.crawler import Crawler


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    logging.getLogger("avins_toolkit").setLevel(logging.DEBUG)

    config = CrawlerConfig(
        seeds=["https://www.iist.ac.in/"],
        allowed_domains=["iist.ac.in"],
        max_pages=5,
        max_depth=2,
        delay=1.5,
    )

    crawler = Crawler(config)
    crawler.bfs()

    print(f"visited: {len(crawler.visited)}")
    print(f"failures: {crawler.failures}")
    print(f"left in queue: {len(crawler.q)}")


if __name__ == "__main__":
    main()
