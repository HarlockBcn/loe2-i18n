import sys
import os

def extract_subtitle_ids_and_lines(concat_file):
    subtitle_ids = set()
    subtitle_ids_by_line = []
    with open(concat_file, 'r', encoding='utf-8') as fin:
        for line in fin:
            line = line.rstrip('\n\r')
            if not line or not line.startswith('$') or '|' not in line:
                subtitle_ids_by_line.append(None)
                continue
            prefix = line.split('|', 1)[0]
            parts = prefix[1:].split('-', 2)
            if len(parts) < 3:
                subtitle_ids_by_line.append(None)
                continue
            subtitle_id = parts[2]
            subtitle_ids.add(subtitle_id)
            subtitle_ids_by_line.append(subtitle_id)
    return subtitle_ids, subtitle_ids_by_line

def print_subtitle_diffs(base_concat, check_concat):
    # Error codes
    CODE_MISSING = "MISSING "  # subtitle_id in check not in base
    CODE_EXTRA   = "EXTRA   "  # subtitle_id in base not in check
    CODE_MISALIGN = "MISALIGN"  # same line, different subtitle_id

    base_ids, base_ids_by_line = extract_subtitle_ids_and_lines(base_concat)
    check_ids, check_ids_by_line = extract_subtitle_ids_and_lines(check_concat)

    # MISALIGN: only show the first found
    min_lines = min(len(base_ids_by_line), len(check_ids_by_line))
    misalign_found = False
    with open(base_concat, 'r', encoding='utf-8') as fin1, open(check_concat, 'r', encoding='utf-8') as fin2:
        for idx in range(min_lines):
            subid1 = base_ids_by_line[idx]
            subid2 = check_ids_by_line[idx]
            line1 = next(fin1).rstrip('\n\r')
            line2 = next(fin2).rstrip('\n\r')
            if subid1 and subid2 and subid1 != subid2:
                print(f"{idx+1}: {CODE_MISALIGN} base: {line1}")
                print(f"{idx+1}: {CODE_MISALIGN} check: {line2}")
                misalign_found = True
                break

    # MISSING: subtitle_id in check not in base
    with open(check_concat, 'r', encoding='utf-8') as fin:
        for idx, line in enumerate(fin, 1):
            subid = check_ids_by_line[idx-1] if idx-1 < len(check_ids_by_line) else None
            if subid and subid not in base_ids:
                print(f"{idx}: {CODE_MISSING} {line}")

    # EXTRA: subtitle_id in base not in check
    with open(base_concat, 'r', encoding='utf-8') as fin:
        for idx, line in enumerate(fin, 1):
            subid = base_ids_by_line[idx-1] if idx-1 < len(base_ids_by_line) else None
            if subid and subid not in check_ids:
                print(f"{idx}: {CODE_EXTRA} {line}")



def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <file_to_check.txt> <file_to_compare.txt>")
        sys.exit(1)
    base_concat = sys.argv[1]
    check_concat = sys.argv[2]
    print_subtitle_diffs(base_concat, check_concat)

if __name__ == "__main__":
    main()
