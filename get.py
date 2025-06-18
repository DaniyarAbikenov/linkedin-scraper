#!/usr/bin/env python3
"""
linkedin_finder.py — Поиск страниц компаний в LinkedIn по названиям из JSON‑файла.
Python ≥ 3.9
Зависимости:  pip install rapidfuzz
(модуль search.Searcher — ваш существующий обёртка над парсером LinkedIn)
"""

from __future__ import annotations

import json
import logging
import random
import time
import unicodedata
import urllib.parse
from pathlib import Path
from typing import Any, List

from rapidfuzz import fuzz

from search import Searcher   # импортируйте свой класс Searcher

# ────────────────────────────── КОНФИГУРАЦИЯ ──────────────────────────────
INPUT_DIR      = Path("input")
OUTPUT_DIR     = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

JSON_FILE      = "Cannabis Manufacturing and Processing.json"
FUZZ_THRESHOLD = 70      # минимальный процент RapidFuzz для совпадения
SAVE_EVERY     = 50      # как часто сохранять прогресс
DELAY_RANGE    = (1.0, 3.0)   # пауза между запросами (сек)

PROHIBITED_CHARS  = set("!@#$%^&*()+=-,./\\`'\"")
PROHIBITED_WORDS  = {"llc", "inc", "corp", "corporation"}
# ──────────────────────────────────────────────────────────────────────────


def normalize(text: str) -> str:
    """
    Unicode‑нормализация, удаление лишних слов/символов, снижение регистра.
    """
    text = unicodedata.normalize("NFKD", text).casefold()
    for bad in PROHIBITED_WORDS:
        text = text.replace(bad, "")
    text = "".join(ch for ch in text if ch not in PROHIBITED_CHARS)
    return " ".join(text.split())


def linkedin_search_url(company: str) -> str:
    encoded = urllib.parse.quote_plus(company)
    return (
        "https://www.linkedin.com/search/results/companies/"
        f"?keywords={encoded}&origin=SWITCH_SEARCH_VERTICAL&sid=-PD"
    )


def load_json(path: Path) -> List[dict[str, Any]]:
    with path.open(encoding="utf-8-sig") as f:
        return json.load(f)


def save_json(path: Path, data: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8-sig") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("linkedin_finder.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )

    records  = load_json(INPUT_DIR / JSON_FILE)
    total    = len(records)
    updated  = 0

    searcher = Searcher()                     # единый экземпляр на всё выполнение

    for idx, rec in enumerate(records, start=1):
        if rec.get("linkedin"):               # пропускаем уже заполненные
            continue

        company_title = rec["title"]
        search_url    = linkedin_search_url(company_title)
        logging.info("[%d/%d] %s", idx, total, company_title)

        try:
            results = searcher.search(search_url, page_end=1)
        except Exception as exc:              # фиксируем сетевые ошибки
            logging.error("Search failed: %s", exc, exc_info=True)
            continue

        target_norm = normalize(company_title)

        for res in results:
            cand_norm = normalize(res["name"])
            if fuzz.token_set_ratio(target_norm, cand_norm) >= FUZZ_THRESHOLD:
                rec["linkedin"] = res.get("linkedin_link")
                rec['linkedin_custom_search'] = True
                updated += 1
                logging.info("MATCH → %s", rec["linkedin"])
                break

        if idx % SAVE_EVERY == 0:             # периодическое сохранение
            save_json(OUTPUT_DIR / JSON_FILE, records)

        time.sleep(random.uniform(*DELAY_RANGE))

    save_json(OUTPUT_DIR / JSON_FILE, records)
    logging.info("Завершено. Найдено ссылок: %d", updated)


if __name__ == "__main__":
    main()
