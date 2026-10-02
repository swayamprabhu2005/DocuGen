"""International currency formatting and number-to-words conversions."""

from __future__ import annotations

import math
from typing import Union

_ONES = [
    "", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
    "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
    "Seventeen", "Eighteen", "Nineteen",
]
_TENS = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]

_CURRENCY_NAMES = {
    "USD": ("Dollar", "Dollars", "Cent", "Cents"),
    "EUR": ("Euro", "Euros", "Cent", "Cents"),
    "GBP": ("Pound", "Pounds", "Penny", "Pence"),
    "INR": ("Rupee", "Rupees", "Paisa", "Paise"),
    "CAD": ("Dollar", "Dollars", "Cent", "Cents"),
    "AUD": ("Dollar", "Dollars", "Cent", "Cents"),
    "JPY": ("Yen", "Yen", "", ""),
}

_CURRENCY_SYMBOLS = {
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "INR": "₹",
    "CAD": "CA$",
    "AUD": "A$",
    "JPY": "¥",
}


def _number_to_words_below_1000(n: int) -> str:
    """Helper to convert integer 0-999 to English words."""
    if n == 0:
        return ""
    if n < 20:
        return _ONES[n]
    if n < 100:
        remainder = _number_to_words_below_1000(n % 10)
        return _TENS[n // 10] + (f" {remainder}" if remainder else "")
    remainder = _number_to_words_below_1000(n % 100)
    return f"{_ONES[n // 100]} Hundred" + (f" {remainder}" if remainder else "")


def integer_to_words(n: int) -> str:
    """Convert any non-negative integer into English words."""
    if n == 0:
        return "Zero"

    parts = []
    billions = n // 1_000_000_000
    if billions:
        parts.append(f"{_number_to_words_below_1000(billions)} Billion")
        n %= 1_000_000_000

    millions = n // 1_000_000
    if millions:
        parts.append(f"{_number_to_words_below_1000(millions)} Million")
        n %= 1_000_000

    thousands = n // 1_000
    if thousands:
        parts.append(f"{_number_to_words_below_1000(thousands)} Thousand")
        n %= 1_000

    if n > 0:
        parts.append(_number_to_words_below_1000(n))

    return " ".join(parts).strip()


def integer_to_indian_words(n: int) -> str:
    """Convert non-negative integer into Indian numbering words (Crore, Lakh, Thousand)."""
    if n == 0:
        return "Zero"

    parts = []
    crores = n // 10_000_000
    if crores:
        parts.append(f"{integer_to_indian_words(crores)} Crore")
        n %= 10_000_000

    lakhs = n // 100_000
    if lakhs:
        parts.append(f"{_number_to_words_below_1000(lakhs)} Lakh")
        n %= 100_000

    thousands = n // 1_000
    if thousands:
        parts.append(f"{_number_to_words_below_1000(thousands)} Thousand")
        n %= 1_000

    if n > 0:
        parts.append(_number_to_words_below_1000(n))

    return " ".join(parts).strip()


def amount_to_words(
    amount: Union[float, int, str],
    currency_code: str = "USD",
    add_only: bool = True,
    currency: Optional[str] = None,
) -> str:
    """Convert a financial currency amount to legal text representation.

    Supports both Western (Millions/Billions) and Indian (Lakhs/Crores) numbering.
    """
    code = (currency or currency_code).strip().upper()
    curr_info = _CURRENCY_NAMES.get(code, ("Unit", "Units", "Cent", "Cents"))

    try:
        val = float(str(amount).replace(",", "").replace("$", "").replace("€", "").replace("£", "").replace("₹", ""))
    except ValueError:
        return str(amount)

    dollars = int(math.floor(val))
    cents = int(round((val - dollars) * 100))

    dollar_unit = curr_info[0] if dollars == 1 else curr_info[1]
    if code == "INR":
        dollar_words = integer_to_indian_words(dollars)
    else:
        dollar_words = integer_to_words(dollars)

    res = f"{dollar_words} {dollar_unit}"

    if cents > 0 and curr_info[2]:
        cent_unit = curr_info[2] if cents == 1 else curr_info[3]
        if code == "INR":
            cent_words = integer_to_indian_words(cents)
        else:
            cent_words = integer_to_words(cents)
        res += f" and {cent_words} {cent_unit}"

    if add_only:
        res += " Only"

    return res


def format_currency(
    amount: Union[float, int, str],
    currency_code: str = "USD",
    show_symbol: bool = True,
    currency: Optional[str] = None,
) -> str:
    """Format a monetary value with proper currency symbol and 2 decimal places."""
    code = (currency or currency_code).strip().upper()
    symbol = _CURRENCY_SYMBOLS.get(code, "$") if show_symbol else f"{code} "

    try:
        val = float(str(amount).replace(",", "").replace("$", "").replace("€", "").replace("£", "").replace("₹", ""))
        return f"{symbol}{val:,.2f}"
    except (ValueError, TypeError):
        return f"{symbol}{amount}"
