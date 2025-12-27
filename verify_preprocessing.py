"""Verify preprocessing on multiple verses"""
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('data/quran_preprocessed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Test verses from different surahs
test_ids = ['1:1', '1:5', '2:45', '2:255', '3:19', '36:1', '55:13', '112:1']

print("="*70)
print("PREPROCESSING VERIFICATION - MULTIPLE VERSES")
print("="*70)

all_pass = True
issues = []

for vid in test_ids:
    verses = [x for x in data if x['id']==vid]
    if not verses:
        print(f"\n❌ {vid}: NOT FOUND")
        all_pass = False
        continue
    
    v = verses[0]
    print(f"\n{'='*70}")
    print(f"[{vid}] {v['surah_name']}")
    print("-"*70)
    print(f"Original   : {v['translation'][:80]}...")
    print(f"Normalized : {v['translation_normalized'][:80]}...")
    print(f"Lemmatized : {v['translation_lemma'][:80]}...")
    
    # Checks
    orig = v['translation']
    norm = v['translation_normalized']
    lemm = v['translation_lemma']
    
    checks = []
    
    # 1. No apostrophe in normalized
    if "'" in norm or "'" in norm:
        checks.append("❌ Apostrophe found in normalized")
        all_pass = False
    else:
        checks.append("✅ No apostrophe")
    
    # 2. No Turkish chars in normalized
    turkish_chars = ['ş', 'ü', 'ö', 'ç', 'ğ', 'ı', 'Ş', 'Ü', 'Ö', 'Ç', 'Ğ', 'İ']
    has_turkish = any(c in norm for c in turkish_chars)
    if has_turkish:
        checks.append("❌ Turkish chars in normalized")
        all_pass = False
    else:
        checks.append("✅ No Turkish chars")
    
    # 3. Lemma not empty
    if not lemm.strip():
        checks.append("❌ Empty lemma")
        all_pass = False
    else:
        checks.append("✅ Has lemma")
    
    # 4. No "yarmak" in lemma (known bug)
    if "yarmak" in lemm:
        checks.append("❌ 'yarmak' bug in lemma")
        all_pass = False
    else:
        checks.append("✅ No 'yarmak' bug")
    
    print(f"Checks: {' | '.join(checks)}")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"Total verses checked: {len(test_ids)}")
print(f"Overall status: {'✅ ALL PASS' if all_pass else '❌ SOME ISSUES'}")

# Stats
print(f"\nDataset stats:")
print(f"  Total verses: {len(data)}")
print(f"  First verse: {data[0]['id']}")
print(f"  Last verse: {data[-1]['id']}")
