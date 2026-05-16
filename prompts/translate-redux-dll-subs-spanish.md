# 🚀 Translation Task

## 📥 Input Format
Each input line follows this structure:
```
{file_id}|{va}|{offset}|{max_length}|{text}
```

### Field Definitions
- `{file_id}` — File identifier  
- `{va}` — Virtual address (hex)  
- `{offset}` — Offset (hex)  
- `{max_length}` — Maximum allowed bytes for the translation encoded in utf-8 (integer)  
- `{text}` — Subtitle text in English  

---

## 🎯 Objective
Translate `{text}` from **English to Spanish**.

- The translated text, encoded in utf-8, should not use **NO MORE** than `{max_length}` bytes.
- Preserve meaning, tone, and readability.

### ⚠️ Critical Constraints
- Reduce length **only when necessary**.
- **Do NOT over-abbreviate** unless required to fit the limit.
- The following fields must remain **UNCHANGED**:
  - `{file_id}`
  - `{va}`
  - `{offset}`
  - `{max_length}`

---

## 📤 Output Format
Return each line as:
```
{file_id}|{va}|{offset}|{max_length}|{length}|{translated_text}
```


### Output Fields
- `{length}` — bytes count of `{translated_text}` encoded in utf-8
- `{translated_text}` — Final Spanish translation

---

## 🧭 Translation Context
- Science fiction video game set in space
- Lines are typically **character dialogues**
- Tone must be **informal** (avoid “usted”)

### Special Cases
- `<...>` or `[...]` → Informational text
- `( ... )` → Sound/emotion descriptions (not dialogue)

---

## 🔒 Mandatory Rules

### ❌ NEVER modify:
1. Proper names (characters, places, organizations)
2. Location names
3. Special codes:
   - `[@any_text]`
4. *New line special characters* (`\n`)

### ✅ ALWAYS preserve:
- Meaning and context
- Natural, fluent Spanish
- Original tone and style
- Upper/lowercase
- Special characters (CR, LF, quotes)
- Incomplete phrases (intentional)

---

## 🔤 Fixed Translations
Use these exact translations:
- `bay` → `bahía`
- `beacon` → `baliza`
- `tick` → `garrapata`
- `drive` → `unidad`
- `Goldilocks` → `Zona Habit.`
- `Bio mass` / `Bio-mass` → `Biomasa`
- `Delta Six` → `Delta 6`
- `Delta Thirteen` → `Delta 13`
- `Popcorn` → `Palomita`
---

## 📏 🔴 LENGTH PRIORITY PRINCIPLE

**Top Priority: Preserve meaning.**

- Do NOT remove important information.

- Prefer minor overflow over semantic loss.

---

## ✂️ Abbreviation Strategies (in priority order)

1. **Use digits instead of words**
   - `tres` → `3`, `veinte` → `20`
   - Units: `20 horas` → `20h`, `3 metros` → `3m`
   - Avoid special symbols: use `1.er`, `2.a`, etc.

2. **Abbreviate titles**
   - Doctor → Dr. / Doctora → Dra.
   - Capitán/a → Cap.
   - Señor/a → Sr. / Sra.
   - Profesor/a → Prof.
   - Laboratorio → Lab.

3. **Reduce ellipsis**
   - `...` → `..`
   - At start → remove

4. **Remove filler words**
   - e.g., “pues”, “bueno”, “entonces”

5. **Eliminate redundancy**

6. **Trim non-essential modifiers**

7. **Simplify sentence structure**

8. **Use shorter synonyms**

---

## ✅ Quality Check
Ensure the final translation:
- Is grammatically correct
- Preserves original meaning
- Sounds natural when spoken
- Fits length constraints as closely as possible

---

## 📌 Lines to Process


