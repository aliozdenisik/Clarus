#!/usr/bin/env python3
"""Quick check for Daniel 6 in KJVA"""
import json
d = json.load(open('data/bible_kjva.json', encoding='utf-8'))
books = d.get('books', d)
book_list = list(books.values()) if isinstance(books, dict) else books
daniel = [b for b in book_list if b.get('name') == 'Daniel'][0]
chapters = daniel.get('chapters', [])
if isinstance(chapters, dict):
    ch6 = list(chapters.values())[5]
else:
    ch6 = chapters[5]
verses = ch6.get('verses', [])
if isinstance(verses, dict):
    verses = list(verses.values())

print("Daniel 6 - Lions' Den Story:")
for v in verses[:10]:
    print(f"  6:{v.get('verse')}: {v.get('text')[:100]}...")
