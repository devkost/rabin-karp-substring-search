"""Консольный интерфейс для поиска подстрок алгоритмом Рабина—Карпа."""

import argparse
import sys
import time
from pathlib import Path
from typing import Callable, TypeVar

from search import search

T = TypeVar("T")

COLORS = ("\033[91m", "\033[92m", "\033[93m", "\033[94m", "\033[95m", "\033[96m")
RESET = "\033[0m"


def measure_time(function: Callable[..., T]) -> Callable[..., T]:
    """Вывести время выполнения обёрнутой функции."""

    def wrapper(*args: object, **kwargs: object) -> T:
        started = time.perf_counter()
        result = function(*args, **kwargs)
        elapsed = time.perf_counter() - started
        print(f"Время поиска: {elapsed:.6f} с")
        return result

    return wrapper


def parse_args() -> argparse.Namespace:
    """Разобрать параметры командной строки."""
    parser = argparse.ArgumentParser(
        description="Поиск подстрок алгоритмом Рабина—Карпа."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--text", help="Текст, в котором выполняется поиск.")
    source.add_argument("--file", type=Path, help="Путь к файлу с текстом.")
    parser.add_argument(
        "-p",
        "--patterns",
        nargs="+",
        required=True,
        help="Одна или несколько искомых подстрок.",
    )
    parser.add_argument(
        "--case-sensitive",
        "--case-sensitivity",
        "--case_sensitivity",
        dest="case_sensitive",
        action="store_true",
        help="Учитывать регистр символов.",
    )
    parser.add_argument(
        "--method",
        choices=("first", "last"),
        default="first",
        help="Направление поиска (по умолчанию: first).",
    )
    parser.add_argument(
        "-k",
        "--count",
        type=int,
        help="Максимальное число совпадений для каждой подстроки.",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Отключить цветовую подсветку.",
    )
    args = parser.parse_args()
    if args.count is not None and args.count < 1:
        parser.error("--count должен быть положительным числом")
    return args


def read_source(args: argparse.Namespace) -> str:
    """Получить исходный текст из аргумента или файла."""
    if args.text is not None:
        return args.text
    return args.file.read_text(encoding="utf-8")


def normalize_results(
    patterns: list[str],
    result: tuple[int, ...] | dict[str, tuple[int, ...]] | None,
) -> dict[str, tuple[int, ...]]:
    """Привести результат поиска к словарю подстрока -> индексы."""
    if isinstance(result, dict):
        return {pattern: positions or () for pattern, positions in result.items()}
    if len(patterns) == 1:
        return {patterns[0]: result or ()}
    return {pattern: () for pattern in patterns}


def _render_highlighted_line(
    text: str,
    spans: list[tuple[int, int, int]],
    line_start: int,
    line_end: int,
    use_color: bool,
) -> str:
    """Собрать строку с подсветкой совпадений."""
    pieces: list[str] = []
    cursor = line_start

    for start, end, pattern_index in spans:
        if end <= line_start or start >= line_end:
            continue

        visible_start = max(start, line_start, cursor)
        visible_end = min(end, line_end)

        if visible_start > cursor:
            pieces.append(text[cursor:visible_start])

        if visible_end > visible_start:
            value = text[visible_start:visible_end]
            if use_color:
                value = f"{COLORS[pattern_index % len(COLORS)]}{value}{RESET}"
            pieces.append(value)
            cursor = visible_end

    if cursor < line_end:
        pieces.append(text[cursor:line_end])

    return "".join(pieces)


def print_highlighted(
    text: str,
    results: dict[str, tuple[int, ...]],
    patterns: list[str],
    use_color: bool,
) -> None:
    """Напечатать исходный текст с цветной подсветкой, не более 10 строк."""
    spans = [
        (start, start + len(pattern), pattern_index)
        for pattern_index, pattern in enumerate(patterns)
        for start in results.get(pattern, ())
    ]
    spans.sort(key=lambda item: (item[0], item[1]))

    print("\nТекст с выделенными совпадениями:")
    lines = text.splitlines(keepends=True) or [text]
    offset = 0

    for line_number, line in enumerate(lines[:10], start=1):
        line_end = offset + len(line)
        rendered = _render_highlighted_line(text, spans, offset, line_end, use_color)
        if not rendered.endswith(("\n", "\r")):
            rendered += "\n"
        print(f"{line_number:>2}: {rendered}", end="")
        offset = line_end

    if len(lines) > 10:
        print("... (показаны первые 10 строк)")


@measure_time
def run_search(
    text: str,
    patterns: list[str],
    case_sensitive: bool,
    method: str,
    count: int | None,
) -> tuple[int, ...] | dict[str, tuple[int, ...] | None] | None:
    """Выполнить поиск одной или нескольких подстрок."""
    search_patterns = patterns[0] if len(patterns) == 1 else patterns
    return search(
        text,
        search_patterns,
        case_sensitivity=case_sensitive,
        method=method,
        count=count,
    )


def main() -> int:
    """Выполнить консольную программу."""
    args = parse_args()
    try:
        text = read_source(args)
    except (OSError, UnicodeError) as error:
        print(f"Не удалось прочитать файл: {error}", file=sys.stderr)
        return 1

    result = run_search(
        text, args.patterns, args.case_sensitive, args.method, args.count
    )
    results = normalize_results(args.patterns, result)
    for pattern in args.patterns:
        positions = results.get(pattern, ())
        print(f"{pattern!r}: {positions if positions else 'совпадений нет'}")

    use_color = sys.stdout.isatty() and not args.no_color
    print_highlighted(text, results, args.patterns, use_color)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
