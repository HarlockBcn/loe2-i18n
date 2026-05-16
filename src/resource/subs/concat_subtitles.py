import os
import sys

def concat_subtitles(input_folder, output_file):
    # List all .txt subtitle files and sort them by name
    txt_files = sorted([
        f for f in os.listdir(input_folder)
        if f.lower().endswith('.txt') and os.path.isfile(os.path.join(input_folder, f))
    ])

    if not txt_files:
        print(f"No .txt subtitle files found in {input_folder}")
        return

    with open(output_file, 'w', encoding='utf-8') as fout:
        for fname in txt_files:
            # Extraer frame y bloque del nombre: XXX-YY-
            parts = fname.split('-', 2)
            if len(parts) < 3:
                continue
            frame = parts[0]
            bloque = parts[1]
            fpath = os.path.join(input_folder, fname)
            with open(fpath, 'r', encoding='utf-8') as fin:
                for line in fin:
                    line = line.rstrip('\n\r')
                    if not line:
                        continue
                    if '|' not in line:
                        continue
                    sub_id, text = line.split('|', 1)
                    
                    fout.write(f"{sub_id}|{text}\n")
    print(f"Concatenated {len(txt_files)} files into {output_file}")


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input_folder> <output_file>")
        sys.exit(1)
    input_folder = sys.argv[1]
    output_file = sys.argv[2]
    concat_subtitles(input_folder, output_file)


if __name__ == "__main__":
    main()
