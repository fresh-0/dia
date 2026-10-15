#!/usr/bin/env python3
"""Збирає zarma/index.html зі словника data/slovnyk.tsv і шаблону data/page_template.html."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
THEMES = {
    "00_core": "Базові слова", "01_tilo": "Тіло і здоров'я", "02_lyudy": "Люди і стосунки",
    "03_emotsii": "Емоції і характер", "04_rozum": "Розум і освіта", "05_mova": "Мова і література",
    "06_pryroda": "Природа і погода", "07_roslyny": "Рослини", "08_tvaryny": "Тварини",
    "09_yizha": "Їжа", "10_dim": "Дім і інструменти", "11_odyag": "Одяг і краса",
    "12_misto": "Місто і подорожі", "13_robota": "Робота і гроші", "14_vlada": "Влада і право",
    "15_viyna": "Армія і безпека", "16_mify": "Віра і міфи", "17_mystetstvo": "Мистецтво",
    "18_sport": "Спорт і дозвілля", "19_tekhnika": "Техніка й інтернет", "20_nauka": "Наука і числа",
    "21_chas": "Час", "22_prostir": "Простір і рух", "23_vidchuttya": "Відчуття і кольори",
    "24_diyi": "Дії", "25_stany": "Стани і мовлення", "26_prykmetnyky": "Якості",
    "27_sluzhbovi": "Службові слова", "28_kosmos": "Матеріали і космос", "29_sleng": "Сленг і ідіоми",
    "30_abstraktne": "Абстрактне",
}


def main():
    rows = []
    with open(os.path.join(HERE, "slovnyk.tsv"), encoding="utf-8") as f:
        next(f)
        for line in f:
            r = line.rstrip("\n").split("\t")
            if len(r) == 7:
                rows.append(r)
    used = {r[6] for r in rows}
    themes = {k: v for k, v in THEMES.items() if k in used}
    with open(os.path.join(HERE, "page_template.html"), encoding="utf-8") as f:
        page = f.read()
    page = page.replace("/*DATA*/[]", json.dumps(rows, ensure_ascii=False, separators=(",", ":")))
    page = page.replace("/*THEMES*/{}", json.dumps(themes, ensure_ascii=False))
    out = os.path.join(os.path.dirname(HERE), "index.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"{out}: {len(rows)} слів, {os.path.getsize(out) // 1024} КБ")


if __name__ == "__main__":
    main()
