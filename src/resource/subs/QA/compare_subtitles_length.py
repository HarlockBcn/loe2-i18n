import sys

"""
compare_subtitles_length.py

Usage:
    python compare_subtitles_length.py <file> <file_compare_with> <threshold> <mode> <output_file>

- <file>: Subtitles file (code|text)
- <file_compare_with>: Second subtitles file to compare with(code|text)
- <threshold>: Difference limit (integer)
- <mode>: 'chars' or 'words'
- <output_file>: Output file with lines that exceed the limit

The output file will contain lines in the format:
<code>|<length2>|<diff>|<text1>
Where <length2> is the length of the second file's text (3 digits) and <diff> is the difference (+/-) with 3 digits (e.g., +005, -012)
"""

def count_words(text):
    return len(text.strip().split())

def main():
    only_exceeded = False
    sorted_flag = False
    args = sys.argv[1:]
    if '--only-exceeded' in args:
        only_exceeded = True
        args.remove('--only-exceeded')
    if '--sorted' in args:
        sorted_flag = True
        args.remove('--sorted')
    if len(args) != 5:
        print(f"Usage: {sys.argv[0]} <file> <file_compare_with> <threshold> <mode> <output_file> [--only-exceeded] [--sorted]")
        sys.exit(1)

    file1 = args[0]
    file2 = args[1]
    try:
        threshold = int(args[2])
    except ValueError:
        print("The threshold must be an integer.")
        sys.exit(1)
    mode = args[3].lower()
    if mode not in ("chars", "words"):
        print("The mode must be 'chars' or 'words'.")
        sys.exit(1)
    file_out = args[4]

    # Read both files into dictionaries: code -> text
    def read_subs(path):
        d = {}
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.rstrip('\n')
                if not line.strip():
                    continue
                try:
                    code, text = line.split('|', 1)
                    d[code] = text
                except ValueError:
                    continue
        return d

    subs1 = read_subs(file1)
    subs2 = read_subs(file2)

    resultados = []
    for code in subs1:
        if code not in subs2:
            continue
        text1 = subs1[code]
        text2 = subs2[code]
        if mode == "chars":
            length2 = len(text2)
            diff = len(text1) - len(text2)
        else:
            length2 = count_words(text2)
            diff = count_words(text1) - count_words(text2)
        if abs(diff) > threshold:
            if only_exceeded and diff <= 0:
                continue
            sign = '+' if diff >= 0 else '-'
            val = abs(diff)
            resultados.append((val, f"{code}|{length2:03d}|{sign}{val:03d}|{text1}\n"))

    if sorted_flag:
        resultados.sort(reverse=True, key=lambda x: x[0])

    with open(file_out, 'w', encoding='utf-8') as fout:
        for _, linea in resultados:
            fout.write(linea)

if __name__ == "__main__":
    main()
