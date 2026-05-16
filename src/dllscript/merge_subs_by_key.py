import sys

"""
merge_subs_by_key.py

Usage:
    python merge_subs_by_key.py <file_src> <file_dst> <output_file>

Given two files with lines in the format:
    {filename}|{va_address}|{file_offset}|{anything}

Outputs a file with all lines from <file_dst>, but if a key ({filename}|{va_address}|{file_offset}) exists in <file_src>, the line from <file_src> replaces the one from <file_dst>.
"""

def extract_key(line):
    parts = line.rstrip('\n').split('|', 3)
    if len(parts) < 3:
        return None
    return '|'.join(parts[:3])

def main():
    if len(sys.argv) != 4:
        print("Usage: python merge_subs_by_key.py <file_src> <file_dst> <output_file>")
        sys.exit(1)
    file_src, file_dst, output_file = sys.argv[1:4]

    # Read lines from file_src into a dict by key
    file_src_lines = {}
    with open(file_src, 'r', encoding='utf-8') as f1:
        for line in f1:
            key = extract_key(line)
            if key:
                file_src_lines[key] = line

    # Merge with file_dst
    with open(file_dst, 'r', encoding='utf-8') as f2, open(output_file, 'w', encoding='utf-8') as fout:
        for line in f2:
            key = extract_key(line)
            if key and key in file_src_lines:
                fout.write(file_src_lines[key])
            else:
                fout.write(line)

if __name__ == "__main__":
    main()
