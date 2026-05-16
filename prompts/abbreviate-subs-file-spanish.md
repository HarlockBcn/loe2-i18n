# Subtitle Length Reduction Task

## Input Format
You will receive lines in the following format:
```
{code}|{original_length}|+{excess_length}|{text}
```

**Field Definitions:**
- `{code}` — Unique subtitle identifier
- `{original_length}` — Text Length to match.
- `{excess_length}` — Positive integer indicating how many characters must be removed
- `{text}` — Spanish subtitle text that exceeds the maximum allowed length

## Output Format
Return each line in this format:
```
{code}|{shortened_text}
```

## Objective
Shorten each subtitle text so that it ends up using **no more** than the number of characters specified in `{desired_length}` value while maintaining meaning and readability.

⚠️ **Critical:** Reduce by the minimum necessary. Do NOT over-abbreviate, unless it is the only way to shorten the text to meet the minimum required reduction.

## 🔴 PRIORITY PRINCIPLE

**MOST IMPORTANT:** Do NOT lose relevant information when abbreviating. Preserving meaning is the absolute priority.

- If you cannot abbreviate without losing important information, abbreviate as much as possible even if you exceed the character limit.
- It is better to slightly exceed the limit than to remove critical information that changes the meaning or context of the subtitle.

## Mandatory Restrictions

**Special Characters**
- Don't use special characters like "«","»","º","ª" or special characters for exponent numbers.

**NEVER modify or remove:**
1. **Proper names** — Character names, place names, organizations, etc.
2. **Location names** — Geographic locations, place names, or any spatial references
3. **Bracketed codes** — Text in these formats:
   - `[@any_text]` — Variable references or dynamic content placeholders
4. *New line special characters* (`\n`)

**Preserve:**
- Original meaning and context
- Natural, fluent Spanish
- Game's tone and style
- Respect upper and lower case
- **Incomplete phrases** — Some texts are dialogues that include intentionally incomplete phrases. Do NOT remove or ignore these incomplete phrases as they are part of the natural dialogue flow.

## Abbreviation Strategies

Apply these techniques in order of preference:

1. **Convert written numbers to digits** — "tres" → "3", "veinte" → "20", "cien" → "100", "doscientos cincuenta y dos" → "252"
   - This is one of the most effective ways to save space
   - Always prefer numeric format over written words for numbers
   - **For time or metric units**, write using numbers and unit letters: "veinte horas" → "20h", "tres metros" → "3m", "dos kilogramos" → "2kg", but don't use exponent numbers: "tres metros cúbicos" → "3m cúbicos"
   - Don't use "º" "ª" special characters. Use the forms: "1.er" / "1.era", "2.o" / "2.a" , "3.er" / "3.era", "4.o" / "4.a", "5.o" / "5.a"
2. **Abbreviate titles and ranks** — Use standard abbreviations for professional titles and military/formal ranks:
   - "Doctor" → "Dr." 
   - "Doctora" → "Dra." 
   - "Capitán" / "Capitana" → "Cap." 
   - "Señor" / "Señora" → "Sr." / "Sra."
   - "Profesor" / "Profesora" → "Prof."
   - "Laboratorio" -> "Lab."
   - Similar formal titles can be abbreviated following standard conventions
3. **Replace ellipsis with comma** — "..." → ".." except at the beginning of the text, where it should be replaced with "".
   - Use when the pause or trailing off can be represented with a comma
   - Maintains natural reading flow while saving space
4. **Remove filler words** — "pues", "bueno", "entonces", etc.
5. **Eliminate redundancy** — Repeated ideas or unnecessary repetition
6. **Trim unnecessary modifiers** — Non-essential adjectives/adverbs
8. **Simplify structure** — Make sentences more concise without losing clarity
9. **Synonyms** — Use shorter equivalents when appropriate

**Quality Check:** After shortening, verify that:
- The subtitle remains grammatically correct
- The meaning is unchanged
- The text sounds natural when read aloud
- Character count reduction meets the target

---

## Lines to Process:

