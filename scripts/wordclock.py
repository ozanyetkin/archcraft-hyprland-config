#!/usr/bin/env python3
"""
Word clock script

Outputs human-friendly time phrases like:
  "It's quarter to ten"
  "It's eighteen past seven"
  "It's noon"
  "It's seven o'clock"

Intended usage: call from a status/lock script every second or minute, e.g.:
    cmd[update:1000] /path/to/wordclock.py

The script rounds to the minute (no fractional minutes) and uses "past" for minutes <= 30
(except 15 and 30 which become "quarter past" and "half past"), and "to" for minutes > 30
(using the minutes remaining to the next hour, with "quarter to" for 45).

This implementation does not require external libraries.
"""

from __future__ import annotations

import sys
from datetime import datetime
from typing import Optional

_NUM_WORDS = {
    0: "zero",
    1: "one",
    2: "two",
    3: "three",
    4: "four",
    5: "five",
    6: "six",
    7: "seven",
    8: "eight",
    9: "nine",
    10: "ten",
    11: "eleven",
    12: "twelve",
    13: "thirteen",
    14: "fourteen",
    15: "fifteen",
    16: "sixteen",
    17: "seventeen",
    18: "eighteen",
    19: "nineteen",
    20: "twenty",
    30: "thirty",
    40: "forty",
    50: "fifty",
}


def number_to_words(n: int) -> str:
    """
    Convert integer n (0 <= n <= 59) into its English words representation.
    Examples:
      0 -> "zero"
      5 -> "five"
      18 -> "eighteen"
      21 -> "twenty one"
      45 -> "forty five"
    """
    if n < 0 or n > 59:
        raise ValueError("number_to_words supports 0..59")
    if n in _NUM_WORDS:
        return _NUM_WORDS[n]
    # 21..29, 31..39, 41..49, 51..59
    tens = (n // 10) * 10
    ones = n % 10
    tens_word = _NUM_WORDS.get(tens, "")
    ones_word = _NUM_WORDS.get(ones, "")
    if tens_word and ones_word:
        return f"{tens_word} {ones_word}"
    return tens_word or ones_word


def hour_word_12(hour24: int) -> str:
    """
    Convert a 24-hour hour to its 12-hour word representation,
    e.g. 0 -> "twelve", 13 -> "one", 12 -> "twelve"
    """
    h12 = hour24 % 12
    if h12 == 0:
        h12 = 12
    return number_to_words(h12)


def make_phrase(now: Optional[datetime] = None) -> str:
    """
    Build the human-friendly time phrase for the supplied datetime (or now if None).
    """
    if now is None:
        now = datetime.now()

    h = now.hour
    m = now.minute

    # Special cases for exact midnight and noon
    if h == 0 and m == 0:
        return "It's midnight"
    if h == 12 and m == 0:
        return "It's noon"

    # minutes = 0 -> "X o'clock"
    if m == 0:
        return f"It's {hour_word_12(h)} o'clock"

    # quarter / half handling
    if m == 15:
        return f"It's quarter past {hour_word_12(h)}"
    if m == 30:
        return f"It's half past {hour_word_12(h)}"
    if m == 45:
        next_h = (h + 1) % 24
        return f"It's quarter to {hour_word_12(next_h)}"

    # past (1..29 except 15,30) and to (31..59 except 45)
    if m < 30:
        minute_word = number_to_words(m)
        return f"It's {minute_word} past {hour_word_12(h)}"
    else:
        minutes_to = 60 - m
        minute_word = number_to_words(minutes_to)
        next_h = (h + 1) % 24
        return f"It's {minute_word} to {hour_word_12(next_h)}"


def main(argv=None) -> int:
    """
    CLI entry point.

    Options:
      --24h     : Prints also the numeric HH:MM (24-hour) after the phrase.
      --raw     : Print only the phrase without "It's " prefix (for integration).
      --utc     : Use UTC time instead of localtime.
    """
    import argparse

    parser = argparse.ArgumentParser(description="Word clock: print time as words.")
    parser.add_argument(
        "--24h",
        dest="show_24",
        action="store_true",
        help="Also show numeric 24-hour HH:MM after phrase",
    )
    parser.add_argument(
        "--raw",
        dest="raw",
        action="store_true",
        help='Print phrase without leading "It\'s "',
    )
    parser.add_argument(
        "--utc",
        dest="use_utc",
        action="store_true",
        help="Use UTC time instead of local time",
    )
    args = parser.parse_args(argv)

    now = datetime.now() if args.use_utc else datetime.now()
    phrase = make_phrase(now)

    if args.raw:
        # Remove leading "It's " if present
        if phrase.startswith("It's "):
            phrase = phrase[5:]
    out = phrase
    if args.show_24:
        out = f"{out} — {now.strftime('%H:%M')}"

    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
