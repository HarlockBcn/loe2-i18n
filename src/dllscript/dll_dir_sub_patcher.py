import os
import sys
import codecs


# Formato de línea esperado:
# "{filename}|{va_address}|{file_offset}|{max_length}|{length}|{text}"

def parse_line(line):
    # El formato es: filename|va_address|file_offset|max_length|length|text
    parts = line.strip().split('|', 5)
    if len(parts) != 6:
        raise ValueError(f"Formato de línea incorrecto: {line}")
    filename, va_address, file_offset, max_length, length, text = parts
    return filename, va_address, int(file_offset, 16), int(max_length), int(length), text

def patch_dlls(txt_path, folder_path):
    with open(txt_path, 'r', encoding='utf-8') as f:
        lines = [line for line in f if line.strip() and not line.strip().startswith('#')]

    total = len(lines)
    processed_files = set()
    current_filename = None
    dll_file = None
    for idx, line in enumerate(lines):
        filename, va_address, file_offset, max_length, length, text = parse_line(line)
        if length > max_length:
            print(f"Error: length ({length}) > max_length ({max_length}) en línea: {line.strip()}")
            sys.exit(1)
        if filename != current_filename:
            if dll_file:
                dll_file.close()
            # Asegurarse de que folder_path es correcto y no pierde separadores
            dll_path = os.path.join(os.path.normpath(folder_path), f"{filename}.dll")
            if not os.path.isfile(dll_path):
                print(f"Error: No se encontró el fichero {dll_path}")
                sys.exit(1)
            dll_file = open(dll_path, 'r+b')
            current_filename = filename
            processed_files.add(filename)
        # Escribir el texto en el offset
        dll_file.seek(file_offset)
        # Eliminar saltos de línea del texto
        text_bytes = text.replace('\n', '').replace('\r', '').encode('utf-8')
        if len(text_bytes) != length:
            print(f"Error: length real ({len(text_bytes)}) != length declarado ({length}) en línea: {line.strip()}. Text bytes: {text_bytes}")
            sys.exit(1)
        dll_file.write(text_bytes)
        dll_file.write(b'\x00' * (max_length - length))
        # Progreso
        print(f"Procesando: {len(processed_files)}/{len(set(l.split('|',1)[0] for l in lines))} ficheros...", end='\r', flush=True)
    if dll_file:
        dll_file.close()
    print(f"\nCompletado: {len(processed_files)} ficheros procesados.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python dll_sub_patcher.py <fichero_txt> <carpeta_dlls>")
        sys.exit(1)
    patch_dlls(sys.argv[1], sys.argv[2])
