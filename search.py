"""Поиск подстрок алгоритмом Рабина—Карпа с кольцевым хешированием."""

from typing import Optional, Union

BASE = 257
MODULUS = 1_000_000_007


def calculate_hash(text: str) -> int:
    """Вычислить полиномиальный хеш строки."""
    hash_result = 0
    for symbol in text:
        hash_result = (hash_result * BASE + ord(symbol)) % MODULUS
    return hash_result


def _find_occurrences(text: str, pattern: str) -> list[int]:
    """Найти все вхождения pattern в text, проверяя совпадения хеша."""
    pattern_length = len(pattern)
    text_length = len(text)
    if pattern_length == 0 or pattern_length > text_length:
        return []

    highest_power = pow(BASE, pattern_length - 1, MODULUS)
    pattern_hash = calculate_hash(pattern)
    window_hash = calculate_hash(text[:pattern_length])
    positions: list[int] = []

    for start in range(text_length - pattern_length + 1):
        if (
            window_hash == pattern_hash
            and text[start : start + pattern_length] == pattern
        ):
            positions.append(start)

        if start < text_length - pattern_length:
            outgoing = ord(text[start]) * highest_power
            window_hash = (window_hash - outgoing) % MODULUS
            window_hash = (
                window_hash * BASE + ord(text[start + pattern_length])
            ) % MODULUS

    return positions


def _find_one(
    string: str,
    sub_string: str,
    case_sensitivity: bool,
    method: str,
    count: Optional[int],
) -> Optional[tuple[int, ...]]:
    """Найти вхождения одной подстроки и применить направление и лимит."""
    if not sub_string:
        return None

    source = string if case_sensitivity else string.casefold()
    pattern = sub_string if case_sensitivity else sub_string.casefold()
    positions = _find_occurrences(source, pattern)
    if method == "last":
        positions.reverse()
    if count is not None:
        positions = positions[:count]
    return tuple(positions) if positions else None


def search(
    string: str,
    sub_string: Union[str, list[str], tuple[str, ...]],
    case_sensitivity: bool = False,
    method: str = "first",
    count: Optional[int] = None,
) -> Optional[Union[tuple[int, ...], dict[str, Optional[tuple[int, ...]]]]]:
    """Вернуть индексы вхождений одной подстроки или словарь для набора."""
    if method not in ("first", "last"):
        raise ValueError("method должен быть 'first' или 'last'")
    if count is not None and count < 1:
        raise ValueError("count должен быть положительным числом или None")

    if isinstance(sub_string, str):
        return _find_one(string, sub_string, case_sensitivity, method, count)

    if not string:
        return None

    return {
        pattern: _find_one(string, pattern, case_sensitivity, method, count)
        for pattern in sub_string
    }
