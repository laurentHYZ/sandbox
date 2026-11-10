# 汉字 · Pinyin Flashcards

A self-contained flashcard app for learning Chinese characters and their pinyin.
No framework, no CDN, no build step needed to *use* it — `index.html` has the whole
deck inlined and progress lives in the browser's localStorage.

## Use it

Tailnet only (phone + desktop, both already on the tailnet):

```
https://vps-c281b2f4.tailfefed3.ts.net/hanzi/
```

Or open `index.html` locally from any machine — it works offline as a `file://` page.

## What it does

- **Study** — Leitner spaced repetition, 7 boxes. Intervals: 10 min → 1 day → 3 days
  → 1 week → 3 weeks → 2 months. A card graded *Again* resets to box 0 and comes back
  in the same session; *Good* advances one box; *Easy* advances two.
- **Quiz** — 10 multiple-choice questions, three prompt types (character→pinyin,
  character→meaning, pinyin→character). Quizzes feed the same scheduling as Study.
- **Browse** — search by character, tone-marked pinyin (`shuǐ`), tone numbers (`shui3`),
  or English. Tap a row to hear it.
- **Progress** — box distribution, accuracy, review counts, export/reset.
- **Audio** — uses the browser's Web Speech API with a `zh-CN` voice (installed voices
  vary by device; Android Chrome and desktop Chrome both ship one).
- Category filters (numbers, verbs, food, …) apply to Study and Quiz.

Keyboard: `space` flip · `1` `2` `3` grade or pick option · `s` speak · `esc` home.

## Deck

156 entries, 11 categories. Each entry: character, tone-marked pinyin, tone numbers,
English gloss, category.

Pinyin is **hand-authored** in `deck_src.py` and then cross-checked against `pypinyin`
at build time. The build refuses to run if the two disagree, except for entries listed
in `WORD_LEVEL_NEUTRAL` (real word-level neutral tones like péngyou, xué sheng, shí hou)
and `ACCEPTED_ALT` (legitimate alternative readings like 谁 shéi/shuí, 长 cháng/zhǎng).
That means a pinyin typo cannot silently reach the app.

## Add or change cards

Edit `deck_src.py`, appending tuples of `(character, "tone numbers", "meaning", "category")`:

```python
("北京", "bei3 jing1", "Beijing", "places"),
```

Then rebuild:

```bash
cd ~/chinese-flashcards
~/.venvs/hanzi/bin/python build_app.py     # validates, then rewrites index.html
```

The rebuild is live immediately — the server serves the directory, so just reload the
page. If the build reports `BLOCKED`, it lists the characters where your hand-written
pinyin and pypinyin disagree; fix the pinyin or, if it is a word-level neutral tone,
add the word to `WORD_LEVEL_NEUTRAL` in `build_app.py`.

## Serving

| Piece | What |
|---|---|
| Static server | systemd unit `hanzi-cards` → `python3 -m http.server 8099` bound to 127.0.0.1, root `/home/ubuntu/chinese-flashcards` |
| Public-to-tailnet | `tailscale serve --https=443 --set-path=/hanzi http://127.0.0.1:8099` |

```bash
systemctl status hanzi-cards
sudo systemctl restart hanzi-cards
tailscale serve status            # shows the /hanzi mount alongside herdr at /
```

The mount is path-based on the same 443 listener that fronts herdr, so both coexist:
`/` is herdr, `/hanzi` is this app. Nothing is exposed to the public internet.

## Progress storage

localStorage key `hanzi-flashcards.v1`, per browser + per origin. Phone and desktop keep
separate progress. Use *Progress → Export JSON* to move it.
