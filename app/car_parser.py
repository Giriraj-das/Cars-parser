import asyncio
import logging
import re
from datetime import datetime, timezone

from playwright.async_api import TimeoutError as PlaywrightTimeoutError, Page

import utils
from crud import save_car
from db import db_helper

logger = logging.getLogger(__name__)


class ParseAutoRia:
    def __init__(self, url: str):
        self.url = url
        self.data = {'url': self.url}

    async def parse(self, page: Page):
        try:
            logger.info(f"Playwright: Navigating to {self.url}")
            await page.goto(self.url, timeout=20000, wait_until='networkidle')
            await self.parse_car_details(page=page)
        except PlaywrightTimeoutError:
            logger.error(f"Playwright: Timeout while processing {self.url}")
        except Exception as e:
            logger.error(f"Playwright: Page load error: {self.url}: {e}", exc_info=True)

    async def parse_car_details(self, page: Page):
        title: str = await page.locator('h1.head').inner_text()
        self.data['title']: str | None = utils.clean_text(text=title)

        price: str = await page.locator('div.price_value strong').inner_text()
        self.data['price_usd']: int | None = utils.parse_price_usd(price_str=price)

        odometer: str = await page.locator('section.price .base-information .size18').inner_text()
        self.data['odometer']: int | None = utils.parse_odometer(odometer=odometer)

        username_selector = '#userInfoBlock .seller_info_name a, #userInfoBlock .seller_info_name'
        username_locator = page.locator(username_selector)
        username: str = await username_locator.first.inner_text()
        self.data['username']: str | None = utils.clean_text(text=username)

        main_photo = page.locator('.photo-620x465.loaded img').first
        self.data['image_url']: str | None = await main_photo.get_attribute('src')

        photos_locator = page.locator('.action_disp_all_block a')
        text: str = await photos_locator.inner_text()
        if match := re.search(r'все (\d+)', text):
            self.data['images_count']: int = int(match.group(1))
        else:
            self.data['images_count'] = None

        car_vin: str = await page.locator('span.label-vin').inner_text()
        self.data['car_vin']: str | None = utils.clean_text(text=car_vin)

        car_number: str = await page.locator('.state-num.ua').evaluate('el => el.firstChild.textContent.trim()')
        self.data['car_number']: str | None = utils.clean_text(text=car_number)

        self.data['phone_number']: str | None = ','.join(await self.get_phones(page=page))
        self.data['datetime_found'] = datetime.now(timezone.utc)

        logger.info(f'__DATA__: {self.data}')

        async for session in db_helper.session_dependency():
            await save_car(session=session, data=self.data)

    async def get_phones(self, page: Page) -> list[str]:
        phones = []
        try:
            phone_button = page.locator('a.size14.phone_show_link').first
            await phone_button.wait_for(state='visible')
            await asyncio.sleep(2)
            print('---click---')
            await phone_button.tap()

            await page.wait_for_selector('.phone.bold', state='visible', timeout=5000)
            phone_locator = page.locator('.phone.bold').nth(0)
            phone: str | None = await phone_locator.inner_text()
            if phone:
                phones.append(utils.normalize_phone_number(phone=phone))
            print('___FOUND ELEMENT___')

        except PlaywrightTimeoutError:
            logger.error('Timeout waiting for phone numbers')
        except Exception as e:
            logger.error(f'Error getting phones: {e}')

        return phones
