import sys
import os

def process_file(input_path, output_path, only_problems=False):
    with open(input_path, 'r', encoding='utf-8') as fin:
        lines = fin.readlines()
    out_lines = []
    for line in lines:
        if not line.strip() or line.strip().startswith('#'):
            if not only_problems:
                out_lines.append(line)
            continue
        parts = line.rstrip('\n').split('|', 5)
        if len(parts) != 6:
            if not only_problems:
                out_lines.append(line)
            continue
        filename, va, file_offset, max_length, length, text = parts
        max_length = int(max_length)
        text_bytes = text.encode('utf-8')
        new_length = len(text_bytes)
        length_str = str(new_length)
        problem = False
        if new_length > max_length:
            length_str += '*'
            problem = True
        new_line = f"{filename}|{va}|{file_offset}|{max_length}|{length_str}|{text}\n"
        if only_problems:
            if problem:
                out_lines.append(new_line)
        else:
            out_lines.append(new_line)
    with open(output_path, 'w', encoding='utf-8') as fout:
        fout.writelines(out_lines)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Corrige el campo length en el fichero de subtítulos DLL.")
    parser.add_argument("input_file", help="Fichero de entrada")
    parser.add_argument("output_file", help="Fichero de salida")
    parser.add_argument("--only-problems", action="store_true", help="Sólo escribir líneas con problemas de longitud")
    args = parser.parse_args()
    process_file(args.input_file, args.output_file, only_problems=args.only_problems)
