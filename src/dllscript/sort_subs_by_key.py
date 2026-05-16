import sys

"""
Script to sort a subtitles file by filename, va_address, and file_offset (all ascending).
Input format (one line per entry):
{filename}|{va_address}|{file_offset}|{max_length}|{text}

Usage:
    python sort_subs_by_key.py input_file.txt output_file.txt
"""

def parse_line(line):
    parts = line.rstrip('\n').split('|', 4)
    if len(parts) < 5:
        raise ValueError(f"Malformed line: {line}")
    filename, va_address, file_offset, max_length, text = parts
    return filename, va_address, int(file_offset, 0), line


def main():
    if len(sys.argv) != 3:
        print("Usage: python sort_subs_by_key.py input_file.txt output_file.txt")
        sys.exit(1)
    input_path, output_path = sys.argv[1:3]
    with open(input_path, 'r', encoding='utf-8') as fin:
        lines = [line for line in fin if line.strip()]
    parsed = [parse_line(line) for line in lines]
    parsed.sort(key=lambda x: (x[0], x[1], x[2]))
    with open(output_path, 'w', encoding='utf-8') as fout:
        for entry in parsed:
            fout.write(entry[3])

if __name__ == "__main__":
    main()
