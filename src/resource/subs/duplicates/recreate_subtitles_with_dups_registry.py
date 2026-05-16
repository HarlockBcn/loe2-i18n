import sys

"""
recreate_subtitles_with_dups_registry.py

Usage:
    python recreate_subtitles_with_dups_registry.py subs_no_dups_file dups_registry_file subs_full_reference_file output_file

- subs_no_dups_file: subtitles without duplicates (code|text)
- dups_registry_file: duplicate registry (duplicate_code|original_code)
- subs_full_reference_file: full subtitles (code|text, all codes in order)
- output_file: result with all codes from dups_registry and correct texts
"""

def main():
    if len(sys.argv) != 5:
        print(f"Usage: {sys.argv[0]} <subs_no_dups_file> <dups_registry_file> <subs_full_reference_file> <output_file>")
        sys.exit(1)

    file_nodups = sys.argv[1]
    file_dups = sys.argv[2]
    file_full = sys.argv[3]    
    file_out = sys.argv[4]

    # 1. Leer fichero1: código -> texto
    code_to_text = {}
    with open(file_nodups, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if not line.strip():
                continue
            try:
                code, text = line.split('|', 1)
                code_to_text[code] = text
            except ValueError:
                continue

    # 2. Leer fichero3: código_duplicado -> código_origen
    dup_to_origin = {}
    with open(file_dups, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if not line.strip():
                continue
            try:
                dup, origin = line.split('|', 1)
                dup_to_origin[dup] = origin
            except ValueError:
                continue

    # 3. Procesar fichero2 y reconstruir
    with open(file_full, 'r', encoding='utf-8') as fin, \
         open(file_out, 'w', encoding='utf-8') as fout:
        for line in fin:
            line = line.rstrip('\n')
            if not line.strip():
                continue
            try:
                code, _ = line.split('|', 1)
            except ValueError:
                continue
            if code in code_to_text:
                text = code_to_text[code]
            elif code in dup_to_origin and dup_to_origin[code] in code_to_text:
                text = code_to_text[dup_to_origin[code]]
            else:
                text = ''  # No encontrado, dejar vacío
            fout.write(f"{code}|{text}\n")

if __name__ == "__main__":
    main()
