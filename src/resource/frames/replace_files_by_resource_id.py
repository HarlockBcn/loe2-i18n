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
    # Indexar los ficheros de la carpeta destino por resource_id
    dst_files = [f for f in os.listdir(dst_folder) if f.lower().endswith('.' + ext) and os.path.isfile(os.path.join(dst_folder, f))]
    dst_by_resource = {}
    for fname in dst_files:
        parts = fname.split('-', 3)
        if len(parts) < 3:
            continue
        resource_id = parts[2]
        dst_by_resource[resource_id] = fname

    # Para cada fichero en origen, buscar en destino por resource_id y reemplazar si existe
    src_files = [f for f in os.listdir(src_folder) if f.lower().endswith('.' + ext) and os.path.isfile(os.path.join(src_folder, f))]
    replaced = 0
    for fname in src_files:
        parts = fname.split('-', 3)
        if len(parts) < 3:
            continue
        resource_id = parts[2]
        if resource_id in dst_by_resource:
            src_path = os.path.join(src_folder, fname)
            dst_path = os.path.join(dst_folder, dst_by_resource[resource_id])
            shutil.copy2(src_path, dst_path)
            replaced += 1
            print(f"Reemplazado: {dst_by_resource[resource_id]} <- {fname}")
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
