import sys

"""
Este script convierte un archivo de texto donde cada línea tiene el formato:
{id}|{text}
a:
{id}|{length}|{text}
donde {length} es el tamaño en bytes de {text} codificado en utf-8.

Uso:
    python add_text_length.py input.txt output.txt
"""

def process_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as infile, open(output_path, 'w', encoding='utf-8') as outfile:
        for line in infile:
            line = line.rstrip('\n')
            if not line.strip():
                continue
            parts = line.split('|', 1)
            if len(parts) != 2:
                print(f"Línea ignorada (formato incorrecto): {line}")
                continue
            id_, text = parts
            length = len(text.encode('utf-8'))
            outfile.write(f"{id_}|{length}|{text}\n")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python add_text_length.py <input.txt> <output.txt>")
        sys.exit(1)
    process_file(sys.argv[1], sys.argv[2])
