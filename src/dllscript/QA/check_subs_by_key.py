import sys

"""
check_subs_by_key.py

Uso:
    python check_subs_by_key.py <file> <key_lookup_file> <output_file>

Dado dos archivos con líneas en el formato:
    {filename}|{va_address}|{file_offset}|{anything}

Genera un archivo con las líneas de <file> cuyo key ({filename}|{va_address}|{file_offset}) NO está en <key_lookup_file>.
"""

def extract_key(line):
    parts = line.rstrip('\n').split('|', 3)
    if len(parts) < 3:
        return None
    return '|'.join(parts[:3])

def main():
    if len(sys.argv) != 4:
        print("Uso: python check_subs_by_key.py <file> <key_lookup_file> <output_file>")
        sys.exit(1)
    file, key_lookup_file, output_file = sys.argv[1:4]

    # Leer claves del key_lookup_file
    with open(key_lookup_file, 'r', encoding='utf-8') as f1:
        keys = set()
        for line in f1:
            key = extract_key(line)
            if key:
                keys.add(key)

    # Filtrar líneas de file que NO estén en keys
    with open(file, 'r', encoding='utf-8') as f2, open(output_file, 'w', encoding='utf-8') as fout:
        for line in f2:
            key = extract_key(line)
            if key and key not in keys:
                fout.write(line)

if __name__ == "__main__":
    main()
