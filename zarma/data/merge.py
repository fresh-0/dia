#!/usr/bin/env python3
"""Зливає data/raw/*.tsv та базовий slovnyk.md у єдиний словник data/slovnyk.tsv.

- Рядки з помилками (заборонені літери, неправильна кількість колонок тощо) відкидаються
  і записуються в data/merge_log.txt.
- Однакова форма + однаковий переклад -> дублікат, відкидається.
- Однакова форма + різний переклад -> колізія: пізніша форма змінюється
  (заміна останньої голосної), а посилання на неї в колонці синонімів того ж
  файлу оновлюються.
"""
import glob
import os
import re

import check

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VOWELS = "аеѣиоѫуы"
ROTATE = {"а": "ѣ", "ѣ": "е", "е": "ы", "ы": "ѫ", "ѫ": "о", "о": "у", "у": "и", "и": "а"}

CORE_POS = {
    "Люди та тіло": "ім", "Природа": "ім", "Час": "ім", "Дім і речі": "ім",
    "Почуття та ідеї": "ім", "Дієслова": "дс", "Прикметники": "пр",
    "Службові слова": "част", "Вигуки та ввічливість": "вигук",
}


def load_core():
    rows, section = [], None
    with open(os.path.join(ROOT, "slovnyk.md"), encoding="utf-8") as f:
        for line in f:
            if line.startswith("## "):
                section = line[3:].strip()
            if section not in CORE_POS or not line.startswith("| ") or "---" in line:
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if cells[0] in ("Зарьма",) or "/" in cells[0]:
                continue
            word = cells[0].rstrip("!").lower()
            pos = CORE_POS[section]
            if section == "Час" and word in ("сѣдьѣн", "заутр", "вчерѣ", "нынѣ", "всѣгд", "жавсѣгд"):
                pos = "присл"
            rows.append([word, pos, cells[1], "нейтр", "", "базовий словник"])
    return rows


def mutate(word, taken):
    stem, suffix = (word[:-2], "ѫн") if word.endswith("ѫн") else (word, "")
    idxs = [i for i, c in enumerate(stem) if c in VOWELS]
    for i in reversed(idxs):
        cand_stem = stem
        for _ in range(len(ROTATE) - 1):
            c = cand_stem[i]
            cand_stem = cand_stem[:i] + ROTATE[c] + cand_stem[i + 1:]
            if cand_stem + suffix not in taken:
                return cand_stem + suffix
    n = 2
    while f"{stem}ъ{VOWELS[n % len(VOWELS)]}{suffix}" in taken:
        n += 1
    return f"{stem}ъ{VOWELS[n % len(VOWELS)]}{suffix}"


def norm_uk(s):
    return re.sub(r"\s+", " ", s.strip().lower())


def main():
    log = []
    sources = [("00_core", load_core())]
    for path in sorted(glob.glob(os.path.join(HERE, "raw", "*.tsv"))):
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()[1:]
        name = os.path.splitext(os.path.basename(path))[0]
        sources.append((name, [l.split("\t") for l in lines if l.strip()]))

    entries = {}  # form -> row
    out = []
    for name, rows in sources:
        renames = {}
        accepted = []
        for row in rows:
            row = [c.strip() for c in row]
            if len(row) != 6:
                log.append(f"{name}: колонок {len(row)}: {row}")
                continue
            word, pos = row[0], row[1]
            if not check.WORD_RE.match(word) or pos not in check.POS:
                log.append(f"{name}: некоректне слово/чм: {row[:3]}")
                continue
            if pos == "дс" and not word.endswith("ѫн"):
                log.append(f"{name}: дієслово без -ѫн: {row[:3]}")
                continue
            if word in entries:
                prev = entries[word]
                if norm_uk(prev[2]) == norm_uk(row[2]) or prev[0] == word and name == prev[6]:
                    continue  # дублікат
                new = mutate(word, entries)
                renames[word] = new
                log.append(f"{name}: колізія '{word}' ({row[2]}) з '{prev[2]}' -> '{new}'")
                row[5] = (row[5] + "; " if row[5] else "") + f"змінено з '{word}' через збіг"
                row[0] = word = new
            row.append(name)
            entries[word] = row
            accepted.append(row)
        for row in accepted:
            if row[4]:
                syns = [s.strip() for s in row[4].split(",")]
                row[4] = ", ".join(renames.get(s, s) for s in syns if s)
        out.extend(accepted)

    out.sort(key=lambda r: r[0])
    with open(os.path.join(HERE, "slovnyk.tsv"), "w", encoding="utf-8") as f:
        f.write("\t".join(check.HEADER + ["тема"]) + "\n")
        for r in out:
            f.write("\t".join(r) + "\n")
    with open(os.path.join(HERE, "merge_log.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log) + "\n")

    by_pos = {}
    for r in out:
        by_pos[r[1]] = by_pos.get(r[1], 0) + 1
    print(f"Усього слів: {len(out)}; записів у лозі: {len(log)}")
    print(", ".join(f"{k}: {v}" for k, v in sorted(by_pos.items(), key=lambda x: -x[1])))


if __name__ == "__main__":
    main()
