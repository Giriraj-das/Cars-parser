import httpx
import asyncio
from bs4 import BeautifulSoup
import logging

from playwright.async_api import async_playwright

from car_parser import ParseAutoRia

logger = logging.getLogger(__name__)

HEADERS = {
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8,uk;q=0.7',
    'Origin': 'https://auto.ria.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
}
PLAYWRIGHT_LAUNCH_ARGS = [
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-dev-shm-usage',
    '--disable-accelerated-2d-canvas',
    '--no-first-run',
    '--no-zygote',
    '--disable-gpu',
    '--disable-software-rasterizer'
]
CONTEXT_OPTIONS = {
    'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
    'viewport': {'width': 1280, 'height': 800},
    'color_scheme': 'no-preference',
    'accept_downloads': False,
    'has_touch': True,
    'locale': 'en-US',
    'timezone_id': 'Europe/Chisinau',
    'geolocation': {'latitude': 45.0203, 'longitude': 28.8396},
    'permissions': ['geolocation'],
}


async def parser():
    logger.info('Starting AutoRia scraping process (URLS by httpx, car_info by Playwright)...')

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=PLAYWRIGHT_LAUNCH_ARGS)
        context = await browser.new_context(**CONTEXT_OPTIONS)

        try:
            BASE_URL: str = f'https://auto.ria.com/car/used/'
            page_num = 1
            max_pages_to_scrape = 3  # For test

            async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True) as client:
                while page_num <= max_pages_to_scrape:
                    if page_num == 1:
                        url = BASE_URL
                    else:
                        url = f'{BASE_URL}?page={page_num}'

                    logger.info(f'Scraping page {page_num}: {url}')
                    response = await client.get(url, headers=HEADERS, timeout=20, follow_redirects=True)
                    response.raise_for_status()
                    html_content = response.text

                    def parse_listing_page_sync(html_list_content):
                        bs = BeautifulSoup(html_list_content, 'lxml')
                        car_link_elements = bs.select('a.address')
                        car_urls_on_page = []
                        seen_urls_on_page = set()
                        for link_el in car_link_elements:
                            href = link_el.get('href')
                            if href and href not in seen_urls_on_page:
                                car_urls_on_page.append(href)
                                seen_urls_on_page.add(href)
                        return car_urls_on_page

                    car_urls = await asyncio.to_thread(parse_listing_page_sync, html_content)

                    if not car_urls:
                        logger.info(f'No valid car links found on page {page_num}. Stopping.')
                        break

                    logger.info(f'Found {len(car_urls)} unique car links on page {page_num}.')

                    # Create pages for every URL
                    pages = []
                    for _ in range(min(len(car_urls), 3)):  # Limit pages
                        page = await context.new_page()
                        pages.append(page)

                    for i in range(0, len(car_urls), 3):
                        batch = car_urls[i:i + 3]
                        tasks = []
                        for j, car_url in enumerate(batch):
                            p = ParseAutoRia(url=car_url)
                            tasks.append(p.parse(pages[j]))

                        results = await asyncio.gather(*tasks, return_exceptions=True)

                    for page in pages:
                        await page.close()

                    page_num += 1

        finally:
            await context.close()
            await browser.close()

    logger.info(f"Scraping finished.")
