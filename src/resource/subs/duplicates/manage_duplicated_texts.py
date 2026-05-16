import sys

"""
manage_duplicated_texts.py

Usage:
    python manage_duplicated_texts.py input.txt output.txt duplicates.txt

- input.txt:    Input subtitles file (format: ${frame}-${block}-0x{id}|{text})
- output.txt:   Output file without duplicate lines
- duplicates.txt: File with the codes of duplicate lines and their original lines (format: duplicate|original)
"""

def main():
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <input.txt> <output.txt> <duplicates.txt>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    duplicates_file = sys.argv[3]

    text_to_code = {}
    duplicates = []
    unique_lines = []

    with open(input_file, 'r', encoding='utf-8') as fin:
        for line in fin:
            line = line.rstrip('\n')
            if not line.strip():
                continue
            try:
                code, text = line.split('|', 1)
            except ValueError:
                # Línea malformada, la ignoramos
                continue
            if text in text_to_code:
                # Duplicado
                duplicates.append(f"{code}|{text_to_code[text]}")
            else:
                text_to_code[text] = code
                unique_lines.append(line)

    with open(output_file, 'w', encoding='utf-8') as fout:
        for line in unique_lines:
            fout.write(line + '\n')

    with open(duplicates_file, 'w', encoding='utf-8') as fdup:
        for dup in duplicates:
            fdup.write(dup + '\n')

if __name__ == "__main__":
    main()
