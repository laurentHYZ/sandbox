"""Build a single-file HTML flashcard app from the curated deck.

Pipeline: deck_src.py (hand-authored) -> pypinyin cross-check -> tone-mark rendering
-> index.html with the deck inlined (no network, no build step to run it).
"""
import json, os, sys, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from deck_src import ENTRIES
from pypinyin import pinyin, Style

# Neutral-tone readings (5) that pypinyin reports with a full tone are intentional:
# these are the real word-level pronunciations (péngyou, xuésheng, shíhou, ...).
WORD_LEVEL_NEUTRAL = {"多少", "认识", "朋友", "学生", "妈妈", "爸爸", "衣服",
                      "早上", "晚上", "时候", "漂亮"}
# Legitimate alternative readings where pypinyin's default differs from the taught one.
ACCEPTED_ALT = {"谁": {"shui2"}, "长": {"zhang3"}}

MARKS = {
    "a": "āáǎà", "e": "ēéěè", "i": "īíǐì", "o": "ōóǒò", "u": "ūúǔù", "ü": "ǖǘǚǜ",
}

def tone_mark(syl: str) -> str:
    """'ni3' -> 'nǐ', 'ma5' -> 'ma', 'lv4' -> 'lǜ'."""
    syl = syl.strip()
    if not syl:
        return ""
    tone = 5
    if syl[-1].isdigit():
        tone = int(syl[-1])
        syl = syl[:-1]
    syl = syl.replace("v", "ü").replace("u:", "ü")
    if tone == 5 or not syl:
        return syl
    # placement rule: a or e wins; in 'ou' the o; otherwise the last vowel
    idx = -1
    if "a" in syl:
        idx = syl.index("a")
    elif "e" in syl:
        idx = syl.index("e")
    elif "ou" in syl:
        idx = syl.index("o")
    else:
        for i, ch in enumerate(syl):
            if ch in MARKS:
                idx = i
    if idx < 0:
        return syl
    base = syl[idx]
    return syl[:idx] + MARKS[base][tone - 1] + syl[idx + 1:]

def render(pinyin_field: str) -> str:
    return " ".join(tone_mark(s) for s in pinyin_field.split())

# ---- validation gate: refuse to build a deck that disagrees with pypinyin ----
errors, reviewed = [], []
for char, mine, meaning, cat in ENTRIES:
    gen = " ".join(s[0] for s in pinyin(char, style=Style.TONE3,
                                        neutral_tone_with_five=True, errors="ignore"))
    ok_alt = gen in ACCEPTED_ALT.get(char, set())
    if gen.replace(" ", "") != mine.replace(" ", "") and not (char in WORD_LEVEL_NEUTRAL) and not ok_alt:
        errors.append(f"{char}: hand={mine} pypinyin={gen} ({meaning})")
    if char in WORD_LEVEL_NEUTRAL or ok_alt:
        reviewed.append((char, mine, gen))

if errors:
    print("BLOCKED — unresolved pinyin disagreements:")
    for e in errors:
        print("  ", e)
    sys.exit(1)

print(f"validated {len(ENTRIES)} entries ({len(reviewed)} reviewed as word-level/alternative)")

deck = []
for i, (char, mine, meaning, cat) in enumerate(ENTRIES):
    deck.append({
        "id": i,
        "c": char,
        "p": render(mine),          # tone-marked, for display
        "n": mine,                  # tone numbers, for typing practice
        "m": meaning,
        "t": cat,
        "len": len(char),
    })

cats = sorted({d["t"] for d in deck})
html = open(os.path.join(HERE, "app_template.html"), encoding="utf-8").read()
html = html.replace("/*__DECK__*/[]", json.dumps(deck, ensure_ascii=False))
html = html.replace("/*__CATS__*/[]", json.dumps(cats, ensure_ascii=False))
out = os.path.join(HERE, "index.html")
open(out, "w", encoding="utf-8").write(html)
print(f"wrote {out}  ({len(html):,} bytes, {len(deck)} cards, {len(cats)} categories)")
print("categories:", ", ".join(cats))