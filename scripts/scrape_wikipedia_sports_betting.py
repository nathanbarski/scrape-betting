#!/usr/bin/env python3
"""Scrape Wikipedia Sports betting page for 'odds' sections and tables and write CSV."""
import requests
from bs4 import BeautifulSoup
import csv
import re

URL = "https://en.wikipedia.org/wiki/Sports_betting"
OUT_CSV = "best_sports_betting_odds.csv"


def get_soup(url):
    headers = {"User-Agent":"scrape-betting-bot/1.0 (mailto:noreply@example.com)"}
    r = requests.get(url, headers=headers, timeout=15)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")


def text_from_element(el):
    return ' '.join(el.stripped_strings)


def extract_sections_with_odds(soup):
    rows = []
    headings = soup.find_all(['h2','h3','h4'])
    for h in headings:
        title = h.get_text(" ", strip=True)
        if 'odds' in title.lower():
            section_title = re.sub(r'\[\d+\]$', '', title).strip()
            for sib in h.find_next_siblings():
                if sib.name and re.match(r'h[2-4]', sib.name):
                    break
                if sib.name == 'p':
                    rows.append({'section': section_title, 'entry_type':'paragraph', 'content': text_from_element(sib)})
                elif sib.name in ['ul','ol']:
                    for li in sib.find_all('li'):
                        rows.append({'section': section_title, 'entry_type':'list_item', 'content': text_from_element(li)})
                elif sib.name == 'table':
                    table_text = table_to_text(sib)
                    rows.append({'section': section_title, 'entry_type':'table', 'content': table_text})
    return rows


def table_to_text(table):
    out_rows = []
    for tr in table.find_all('tr'):
        cols = [text_from_element(td) for td in tr.find_all(['th','td'])]
        if cols:
            out_rows.append(' | '.join(cols))
    return '\n'.join(out_rows)


def extract_wikitable_tables(soup):
    rows = []
    for idx, table in enumerate(soup.find_all('table', class_='wikitable')):
        table_title = table.get('summary') or f"wikitable_{idx+1}"
        rows.append({'section': table_title, 'entry_type':'table', 'content': table_to_text(table)})
    return rows


def main():
    print("Fetching", URL)
    soup = get_soup(URL)
    rows = []
    rows += extract_sections_with_odds(soup)
    rows += extract_wikitable_tables(soup)
    if not rows:
        print("No rows found with 'odds' in headings or wikitable tables; extracting page intro as fallback.")
        intro = soup.select_one('#mw-content-text p')
        if intro:
            rows.append({'section':'intro', 'entry_type':'paragraph', 'content': text_from_element(intro)})
    with open(OUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['section','entry_type','content'], quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    print("Wrote", OUT_CSV, "with", len(rows), "rows")


if __name__ == '__main__':
    main()
