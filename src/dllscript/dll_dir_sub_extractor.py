import pefile
import re
import sys
import os

def extract_strings_with_padding(dll_path):
    # Definimos las constantes de control
    START_MARKER = "Blocking node (%%08x) used in Initialize thread"
    END_MARKER = "Node (%08x) had no execute function"
    
    try:
        pe = pefile.PE(dll_path)
        image_base = pe.OPTIONAL_HEADER.ImageBase

        # Expresión regular para buscar strings ASCII legibles
        string_regex = re.compile(rb'[\x20-\x7e]{3,}')

        all_extracted = []

        # Obtener el nombre del archivo sin extensión
        filename = os.path.splitext(os.path.basename(dll_path))[0]

        # 1. Primero extraemos todas las constantes de las secciones indicadas
        for section in pe.sections:
            section_name = section.Name.decode().strip('\x00')
            # Mantenemos la búsqueda en .text como en tu script original
            if section_name not in ['.rdata', '.text', '.data']:
                continue

            data = section.get_data()
            section_va = section.VirtualAddress + image_base
            section_file_offset = section.PointerToRawData

            for match in string_regex.finditer(data):
                start_offset = match.start()
                text_bytes = match.group()
                text = text_bytes.decode('ascii', errors='ignore')

                # Calcular padding (ceros extra después del string)
                remaining_data = data[match.end():]
                padding_count = 0
                for byte in remaining_data:
                    if byte == 0:
                        padding_count += 1
                    else:
                        break

                va_address = hex(section_va + start_offset)
                file_offset = hex(section_file_offset + start_offset)

                # max_size en bytes: longitud de los bytes del texto + padding - 1
                max_size = len(text_bytes) + padding_count - 1
                if max_size < 0:
                    max_size = 0

                # Guardamos temporalmente como una tupla para facilitar el filtrado
                all_extracted.append({
                    "line": f"{filename}|{va_address}|{file_offset}|{max_size}|{text}",
                    "text": text
                })

        # 2. Aplicamos el filtro de rango
        filtered_results = []
        is_recording = False

        for item in all_extracted:
            # Si encontramos la marca de inicio, empezamos a grabar
            if item["text"] == START_MARKER:
                is_recording = True
                continue # Saltamos la propia marca de inicio si no la quieres incluir
            
            # Si encontramos la marca de fin, paramos
            if item["text"] == END_MARKER:
                is_recording = False
                break 
            
            # Si el interruptor está encendido, guardamos la línea
            if is_recording:
                filtered_results.append(item["line"])

        return filtered_results

    except Exception as e:
        return [f"Error: {e}"]

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {os.path.basename(sys.argv[0])} <input_folder> <output_file>")
        sys.exit(1)

    input_folder = sys.argv[1]
    output_file = sys.argv[2]

    # Buscar todos los archivos .dll en la carpeta
    dll_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.dll')]
    total_files = len(dll_files)
    if total_files == 0:
        print(f"No DLL files found in {input_folder}")
        sys.exit(1)

    with open(output_file, "w", encoding="utf-8") as f:
        for idx, dll_filename in enumerate(dll_files, 1):
            dll_path = os.path.join(input_folder, dll_filename)
            print(f"Procesando [{idx}/{total_files}]: {dll_filename}", end='\r', flush=True)
            extracted_strings = extract_strings_with_padding(dll_path)
            for line in extracted_strings:
                f.write(line + "\n")
    print(f"\nHecho. Procesados {total_files} archivos DLL. Resultados guardados en {output_file}.")