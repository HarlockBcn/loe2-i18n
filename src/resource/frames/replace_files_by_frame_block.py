import os
import sys
import shutil

def replace_resource_files(src_folder, dst_folder, extension):
    if not os.path.isdir(src_folder):
        print(f"Carpeta origen no encontrada: {src_folder}")
        return
    if not os.path.isdir(dst_folder):
        print(f"Carpeta destino no encontrada: {dst_folder}")
        return

    ext = extension.lower().lstrip('.')
    # Indexar los ficheros de la carpeta destino por (frame, block)
    dst_files = [f for f in os.listdir(dst_folder) if f.lower().endswith('.' + ext) and os.path.isfile(os.path.join(dst_folder, f))]
    dst_by_frame_block = {}
    for fname in dst_files:
        parts = fname.split('-', 2)
        if len(parts) < 2:
            continue
        frame = parts[0]
        block = parts[1]
        dst_by_frame_block[(frame, block)] = fname

    # Para cada fichero en origen, buscar en destino por (frame, block) y reemplazar si existe
    src_files = [f for f in os.listdir(src_folder) if f.lower().endswith('.' + ext) and os.path.isfile(os.path.join(src_folder, f))]
    replaced = 0
    for fname in src_files:
        parts = fname.split('-', 2)
        if len(parts) < 2:
            continue
        frame = parts[0]
        block = parts[1]
        key = (frame, block)
        if key in dst_by_frame_block:
            src_path = os.path.join(src_folder, fname)
            dst_path = os.path.join(dst_folder, dst_by_frame_block[key])
            shutil.copy2(src_path, dst_path)
            replaced += 1
            print(f"Reemplazado: {dst_by_frame_block[key]} <- {fname}")
    print(f"Total reemplazados: {replaced}")

def main():
    if len(sys.argv) != 4:
        print(f"Uso: {sys.argv[0]} <carpeta_origen> <carpeta_destino> <extension>")
        print("Ejemplo de extensiones: sub, bin, bnk, dds, txt")
        sys.exit(1)
    src_folder = sys.argv[1]
    dst_folder = sys.argv[2]
    extension = sys.argv[3]
    replace_resource_files(src_folder, dst_folder, extension)


if __name__ == "__main__":
    main()
