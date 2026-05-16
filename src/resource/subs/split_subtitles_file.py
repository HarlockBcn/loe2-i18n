import os
import sys

def split_subtitles(input_file, output_folder):
    if not os.path.isfile(input_file):
        print(f"Input file not found: {input_file}")
        return
    os.makedirs(output_folder, exist_ok=True)

    # Dictionary to group lines by (frame, block)
    groups = {}
    with open(input_file, 'r', encoding='utf-8') as fin:
        for line in fin:
            line = line.rstrip('\n\r')
            if not line or not line.startswith('$') or '|' not in line:
                continue
            try:
                prefix, text = line.split('|', 1)
                # prefix: $XXX-YY-<sub_id>
                if '-' not in prefix:
                    continue
                prefix = prefix[1:]  # remove $
                frame, bloque, sub_id = prefix.split('-', 2)
                key = (frame, bloque)
                if key not in groups:
                    groups[key] = []
                # reconstruct line without the special prefix
                groups[key].append(f"${frame}-{bloque}-{sub_id}|{text}")
            except Exception:
                continue

    # Write the files
    for (frame, bloque), lines in groups.items():
        fname = f"{frame}-{bloque}-split.txt"
        fpath = os.path.join(output_folder, fname)
        with open(fpath, 'w', encoding='utf-8') as fout:
            for l in lines:
                fout.write(l + '\n')
    print(f"Written {len(groups)} files to {output_folder}")


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <subtitles_file> <output_folder>")
        sys.exit(1)
    input_file = sys.argv[1]
    output_folder = sys.argv[2]
    split_subtitles(input_file, output_folder)


if __name__ == "__main__":
    main()
