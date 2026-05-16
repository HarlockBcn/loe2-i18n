import sys

"""
merge_dll_resource_subs.py

Uso:
    python merge_dll_resource_subs.py <dll_subs_file> <resource_subs_file> <output_file>

Descripción:
    - Lee dll_subs_file con formato: {id1}|{id2}|{id3}|{length}|{text}
    - Lee resource_subs_file con formato: {res_id}|{length}|{text}
    - El resultado contiene todas las líneas de dll_subs_file.
    - Para cada línea de resource_subs_file, si el {text} ya existe en dll_subs_file, añade el {res_id} a la línea correspondiente de dll_subs_file antes del texto, generando:
        {id1}|{id2}|{id3}|{res_id}|{length}|{text}
      Si no existe, añade la línea de resource_subs_file tal cual.
"""

def parse_dll_line(line):
    parts = line.rstrip('\n').split('|', 4)
    if len(parts) != 5:
        raise ValueError(f"Formato incorrecto en dll_subs_file: {line}")
    return parts  # [id1, id2, id3, length, text]

def parse_resource_line(line):
    parts = line.rstrip('\n').split('|', 2)
    if len(parts) != 3:
        raise ValueError(f"Formato incorrecto en resource_subs_file: {line}")
    return parts  # [res_id, length, text]

def main():

    if len(sys.argv) != 4:
        print("Uso: python merge_dll_resource_subs.py <dll_subs_file> <resource_subs_file> <output_file>")
        sys.exit(1)

    dll_file = sys.argv[1]
    resource_file = sys.argv[2]
    output_file = sys.argv[3]

    # Generar nombres de salida
    if output_file.lower().endswith('.txt'):
        base = output_file[:-4]
    else:
        base = output_file
    dll_out = base + '-dllscript.txt'
    resource_out = base + '-resource.txt'

    # Leer dll_subs_file
    dll_lines = []
    dll_text_to_line = {}
    with open(dll_file, encoding='utf-8') as f:
        for line in f:
            if line.strip() == '':
                continue
            parts = parse_dll_line(line)
            text = parts[4]
            dll_lines.append(parts)
            dll_text_to_line[text] = parts

    # Leer resource_subs_file
    resource_lines = []
    with open(resource_file, encoding='utf-8') as f:
        for line in f:
            if line.strip() == '':
                continue
            parts = parse_resource_line(line)
            resource_lines.append(parts)

    # Generar líneas de salida
    dll_output_lines = []
    resource_output_lines = []
    matched_texts = set()

    # Primero, procesar dll_lines y buscar matches
    for parts in dll_lines:
        text = parts[4]
        # Buscar si hay un resource que haga matching
        match = None
        for res_id, length, res_text in resource_lines:
            if res_text == text:
                match = res_id
                matched_texts.add(text)
                break
        if match:            
            merged = parts[:3] + [match] + parts[3:4] + [text]
            dll_output_lines.append('|'.join(merged))
        else:
            dll_output_lines.append('|'.join(parts))

    # Ahora, las líneas de resource que no hicieron matching
    for res_id, length, text in resource_lines:
        if text not in matched_texts:
            resource_output_lines.append(f"{res_id}|{length}|{text}")

    # Escribir resultados
    with open(dll_out, 'w', encoding='utf-8') as f:
        for line in dll_output_lines:
            f.write(line + '\n')

    with open(resource_out, 'w', encoding='utf-8') as f:
        for line in resource_output_lines:
            f.write(line + '\n')

if __name__ == "__main__":
    main()
