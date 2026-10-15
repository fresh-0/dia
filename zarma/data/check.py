#!/usr/bin/env python3
"""Перевірка TSV-файлів словника зарьми. Використання: check.py файл.tsv [...]"""
import re
import sys

HEADER = ["зарьма", "чм", "українська", "стиль", "синоніми", "примітка"]
LETTERS = "абвгдеѣжзийклмнопрстухцчшѳыьъѫ"
WORD_RE = re.compile(f"^[{LETTERS}{LETTERS.upper()}]+( [{LETTERS}{LETTERS.upper()}]+)*$")
POS = {"ім", "дс", "пр", "присл", "займ", "числ", "спол", "част", "вигук", "післ", "вираз"}
STYLES = {"", "нейтр", "поет", "розм", "зневаж", "офіц", "застар", "наук", "дит"}


def check(path):
    errors = []
    seen = {}
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    if not lines or lines[0].split("\t") != HEADER:
        errors.append("рядок 1: неправильний заголовок")
    for n, line in enumerate(lines[1:], start=2):
        if not line.strip():
            continue
        cols = line.split("\t")
        if len(cols) != 6:
            errors.append(f"рядок {n}: {len(cols)} колонок замість 6: {line!r}")
            continue
        word, pos, uk, style = cols[0], cols[1], cols[2], cols[3]
        if not WORD_RE.match(word):
            bad = sorted(set(c for c in word if c.lower() not in LETTERS and c != " "))
            errors.append(f"рядок {n}: '{word}' має заборонені символи {bad}")
        if " " in word and pos != "вираз":
            errors.append(f"рядок {n}: '{word}' містить пробіл, але чм не 'вираз'")
        if pos not in POS:
            errors.append(f"рядок {n}: невідома частина мови '{pos}'")
        if pos == "дс" and not word.endswith("ѫн"):
            errors.append(f"рядок {n}: дієслово '{word}' не закінчується на -ѫн")
        if pos != "дс" and pos != "вираз" and word.endswith("ѫн"):
            errors.append(f"рядок {n}: '{word}' закінчується на -ѫн, але це не дієслово")
        if style not in STYLES:
            errors.append(f"рядок {n}: невідомий стиль '{style}'")
        if not uk.strip():
            errors.append(f"рядок {n}: немає перекладу")
        if word in seen:
            errors.append(f"рядок {n}: дублікат '{word}' (вже в рядку {seen[word]})")
        seen[word] = n
    return len(lines) - 1, errors


if __name__ == "__main__":
    total_err = 0
    for p in sys.argv[1:]:
        count, errs = check(p)
        total_err += len(errs)
        print(f"{p}: {count} рядків, {len(errs)} помилок")
        for e in errs[:200]:
            print("  " + e)
    sys.exit(1 if total_err else 0)
