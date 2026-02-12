#!/usr/bin/env python3
"""Test single translation to verify prompt quality."""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
TRANSLATION_MODEL = "google/gemini-2.5-flash"

# Sample definition_en from root "أله" (Allah)
SAMPLE_TEXT = """اللّٰهُ اللٰه اللٰة , [written with the disjunctive alif اَللّٰهُ , meaning God, i. e. the only true god, ] accord. to the most correct of the opinions respecting it, which are twenty in number, (K,) or more than thirty, (MF,) is a proper name, (Msb, K,) applied to the Being who exists necessarily, by Himself, comprising all the attributes of perfection; (TA;) a proper name denoting the true god, comprising all the excellent divine names; a unity comprising all the essences of existing things; (Ibn-El- 'Arabee, TA;) the ال being inseparable from it: (Msb:) not derived: (Lth, Msb, K:) or it is originally إِلهٌ , or إِلَاهٌ , (Sb, A Heyth, S, Msb, K,) of the measure فِعَالٌ in the sense of the measure مَفْعُولٌ , meaning مَأْلُوهٌ , (S, K, *) with [the article] ال prefixed to it."""

READABLE_PROMPT = (
    "You are a Quranic Arabic lexicography expert specializing in classical Arabic roots. "
    "Translate the following Lane's Arabic-English Lexicon definition to READABLE modern Turkish. "
    "\n\n"
    "CRITICAL REQUIREMENTS:\n"
    "1. EXPAND abbreviations inline - NEVER leave them as-is:\n"
    "   SOURCE ABBREVIATIONS (Dictionary References):\n"
    "   - S → Sihâh'a göre (es-Sıhâh sözlüğüne göre)\n"
    "   - K → Kámoos'a göre (el-Kâmûs sözlüğüne göre)\n"
    "   - TA → Tâcu'l-Arûs'a göre (en kapsamlı kaynak)\n"
    "   - Msb → Misbáh'a göre (el-Misbâhu'l-Münîr sözlüğüne göre)\n"
    "   - Bd → Beyzâvî Tefsiri'ne göre\n"
    "   - A → Esâsu'l-Belâga'ya göre (mecaz sözlüğü)\n"
    "   - Lh → El-Lihyânî'ye göre (dilbilimci)\n"
    "   - IAar → İbnu'l-A'râbî'ye göre (dilbilimci)\n"
    "   \n"
    "   GRAMMAR ABBREVIATIONS:\n"
    "   - aor. → muzari fiil (geniş/şimdiki zaman)\n"
    "   - inf. n. → mastar (fiilin isim hali)\n"
    "   - pl. → çoğul\n"
    "   - subst. → isim\n"
    "   \n"
    "   REFERENCE ABBREVIATIONS:\n"
    "   - q. v. → (bakınız)\n"
    "   - accord. → ...-e göre\n"
    "   - app. → zahiren / görünüşe göre\n"
    "   - And → ve\n"
    "   - or → veya\n"
    "   \n"
    "   SEMANTIC MARKERS:\n"
    "   - tropical → mecaz (mecazi anlam)\n"
    "   - assumed tropical → varsayılan mecaz\n"
    "   - syn. → eş anlamlı\n"
    "   - contr. → zıt anlamlı\n"
    "\n"
    "2. Convert 19th-century dense academic English to CLEAR modern Turkish:\n"
    "   - Break long sentences into shorter ones\n"
    "   - Use active voice instead of passive where possible\n"
    "   - Replace archaic constructions with contemporary Turkish\n"
    "   - Simplify complex nested clauses\n"
    "\n"
    "3. PRESERVE ALL CONTENT - nothing removed, nothing added:\n"
    "   - All meanings, nuances, and usage examples must be included\n"
    "   - All scholarly citations preserved (just expanded)\n"
    "   - All cross-references maintained\n"
    "\n"
    "4. Target audience: Quran readers with basic Islamic knowledge (not Arabic scholars)\n"
    "   - Use standard Islamic Turkish terminology (tövbe, salat, sadaka)\n"
    "   - Explain technical terms in parentheses when first used\n"
    "   - Make it readable without sacrificing accuracy\n"
    "\n"
    'Return JSON: {"translation": "...", "confidence": 0.0-1.0}'
)


def translate():
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY not set")
        return 1

    print("=" * 80)
    print("ORIGINAL ENGLISH (Lane's Lexicon):")
    print("=" * 80)
    print(SAMPLE_TEXT[:500] + "...")
    print()

    print("=" * 80)
    print("TRANSLATING WITH READABLE PROMPT...")
    print("=" * 80)

    resp = requests.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": TRANSLATION_MODEL,
            "messages": [
                {"role": "system", "content": READABLE_PROMPT},
                {"role": "user", "content": SAMPLE_TEXT},
            ],
            "response_format": {"type": "json_object"},
            "max_tokens": 4096,
            "temperature": 0.1,
        },
        timeout=90.0,
    )

    resp.raise_for_status()
    data = resp.json()
    content = data["choices"][0]["message"]["content"]

    result = json.loads(content)
    translation = result.get("translation", "")
    confidence = result.get("confidence", 0.0)

    print()
    print("=" * 80)
    print("READABLE TURKISH TRANSLATION:")
    print("=" * 80)
    print(translation)
    print()
    print(f"Confidence: {confidence:.2f}")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    raise SystemExit(translate())
