import os
import sys
import shutil

def replace_by_frame_block_subtitles(src_folder, dst_folder):
    if not os.path.isdir(src_folder):
        print(f"Source folder not found: {src_folder}")
        return
    if not os.path.isdir(dst_folder):
        print(f"Destination folder not found: {dst_folder}")
        return

    # Index the files in the destination folder by (frame, block)
    dst_files = [f for f in os.listdir(dst_folder) if f.lower().endswith('.txt') and os.path.isfile(os.path.join(dst_folder, f))]
    dst_by_frame_block = {}
    for fname in dst_files:
        parts = fname.split('-', 2)
        if len(parts) < 3:
            continue
        frame = parts[0]
        block = parts[1]
        dst_by_frame_block[(frame, block)] = fname

    # For each file in the source folder, look for a matching (frame, block) in the destination folder and replace if it exists
    src_files = [f for f in os.listdir(src_folder) if f.lower().endswith('.txt') and os.path.isfile(os.path.join(src_folder, f))]
    replaced = 0
    for fname in src_files:
        parts = fname.split('-', 2)
        if len(parts) < 3:
            continue
        frame = parts[0]
        block = parts[1]
        key = (frame, block)
        if key in dst_by_frame_block:
            src_path = os.path.join(src_folder, fname)
            dst_path = os.path.join(dst_folder, dst_by_frame_block[key])
            shutil.copy2(src_path, dst_path)
            replaced += 1
            print(f"Replaced: {dst_by_frame_block[key]} <- {fname}")
    print(f"Total replaced: {replaced}")


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <source_folder> <destination_folder>")
        sys.exit(1)
    src_folder = sys.argv[1]
    dst_folder = sys.argv[2]
    replace_by_frame_block_subtitles(src_folder, dst_folder)


if __name__ == "__main__":
    main()
