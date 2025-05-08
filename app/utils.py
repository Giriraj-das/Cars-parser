import re
import logging

logger = logging.getLogger(__name__)


def clean_text(text: str) -> str | None:
    return text.strip() if text else None


def parse_price_usd(price_str: str) -> int | None:
    if not price_str:
        return None
    # Пример: "15 000 $" -> 15000
    # Пример: "15000$" -> 15000
    match = re.search(r'(\d[\d\s]*)', price_str)
    if match:
        try:
            return int(match.group(1).replace(' ', ''))
        except ValueError:
            logger.warning(f"Could not parse price: {price_str}")
    return None


def parse_odometer(odometer: str) -> int | None:
    return int(f'{odometer.strip()}000') if odometer else None


def normalize_phone_number(phone: str) -> str | None:
    if not phone:
        return None
    phone = phone.strip()
    # Delete everything except numbers
    digits = ''.join(filter(str.isdigit, phone))
    if not digits:
        return None

    if len(digits) == 10 and not phone.startswith('+'):  # 063 123 45 67
        return f'+38{digits}'
    if len(digits) == 12 and phone.startswith('+'):  # 38 063 123 45 67
        return f'+{digits}'
    if len(digits) == 9 and not phone.startswith('+'):  # 63 123 45 67
        return f'+380{digits}'

    return digits
