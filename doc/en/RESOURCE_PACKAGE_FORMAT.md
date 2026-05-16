# Lone Echo 2 Resource Package Format

> ⚠️ **Warning:** This document is based on reverse engineering.

- [Lone Echo 2 Resource Package Format](#lone-echo-2-resource-package-format)
  - [Overview](#overview)
  - [Concepts](#concepts)
  - [Multi-frame Structure](#multi-frame-structure)
  - [Decompressed Frame Structure](#decompressed-frame-structure)
    - [Textures (DDS)](#textures-dds)
    - [Audio Banks (BNK)](#audio-banks-bnk)
      - [Special Block Header](#special-block-header)
      - [Audio Bank in BNK (Wwise SoundBank) Format](#audio-bank-in-bnk-wwise-soundbank-format)
    - [Unidentified Binary (BIN) in Language Resource File](#unidentified-binary-bin-in-language-resource-file)
    - [Subtitles (SUB)](#subtitles-sub)
      - [Proprietary Binary Subtitle Format](#proprietary-binary-subtitle-format)
      - [Subtitle Literals](#subtitle-literals)
  - [Known Limitations](#known-limitations)

---

## Overview
Game resource packages are binary files compressed in ZSTD multi-frame format. They store different types of game resource data such as subtitles, textures, audio banks, etc.

## Concepts

**Package**: Game resource file consisting of multiple frames. Identified by a number from 0 to n.
**Package Data Frame**: Set of Resource Blocks within a package file. Identified by a number from 0 to n within the global set of packages associated with the manifest.
**Package Final Frame**: Special frame that closes a package. It does not contain resource blocks.
**Resource**: A game resource identified by an 8-byte hexadecimal number. The same resource can have different data blocks of different types (audio, texture, subtitles, etc.).
**Resource Block**: Data block of a game resource of a certain type (audio, texture, subtitles, etc.). Identified by Resource Id. (8 bytes) + Resource Type Id. (8 bytes)

## Multi-frame Structure
The different Data Frames of the resource package are easily identifiable because they all start with a **magic number** value `0x28B52FFD`. Each of these Data Frames, headed by that **magic number**, can be treated as a binary file compressed in ZSTD format.
This way, the package can be split into several files/frames for independent processing.

## Decompressed Frame Structure
The binary content of the decompressed Data Frame may contain one or more Resource Blocks, of the same or different types. The binary content of these resources is concatenated one after another.

The following resource types have been identified:

- **Textures (DDS)**
- **Audio Banks (BNK)**
- **Subtitles (SUB)**
- **Other unknown resource types (BIN)**

### Textures (DDS)
If the first 4 bytes have the value `0x44445320` corresponding to the string "DDS ", at that point begins binary content related to textures. It ends where another resource of the same or different type begins or if the file ends.
Most likely, DDS refers to **Microsoft Direct Draw Surface** and those first 4 bytes are the start of the header described as follows:

| Offset (byte) | Size | Field                   |
| ------------- | ---- | ----------------------- |
| 0             | 4    | Magic "DDS "            |
| 4             | 4    | Header size (124)       |
| 8             | 4    | Flags                   |
| **12**        | 4    | **Height**              |
| **16**        | 4    | **Width**               |
| 20            | 4    | Pitch or Linear Size    |
| 24            | 4    | Depth                   |
| 28            | 4    | Mipmap count            |
| ...           | ...  | Other fields            |
| 76            | 32   | DDS_PIXELFORMAT         |
| 108           | 16   | Caps                    |
| 124           | 4    | Reserved                |

Uses Little-Endian format.
If necessary, information can be found on how to calculate the size of a DDS texture block.

### Audio Banks (BNK)
If we find 16 bytes with the value `0x424B4844` corresponding to the string "BKHD", it means it is an audio bank.
The data block does not start there, but 16 bytes earlier with a special header used to indicate the size of the audio bank.

This audio bank corresponds to the BNK (Wwise SoundBank) format, and those first 16 bytes are the BKHD header. This format uses Little-Endian.

The audio bank data block ends with a special 8-byte separator.

#### Special Block Header
16 bytes indicating the size of the audio bank. For example, the value `0xBD310400000000000000000000000000` would indicate a size of 2,474,877 bytes. That size includes the header from "BKHD" + DIDX + DATA + HIRC. The audio bank block ends with a final separator not included in that size.

#### Audio Bank in BNK (Wwise SoundBank) Format
**Bank Header (BNK):**
- 4 bytes: Mark "BKHD". Indicates the start of a Wwise BKHD audio bank. In hexadecimal `0x424B4844`.
- Header section size: 4 bytes indicating the size of the header section, not counting the previous 4 bytes "42 4B 48 44". For example, in hexadecimal `0x1C000000` would be 28 bytes.
- Format version: 4 bytes indicating the format version. For example `0x86000000`.
- Bank ID: 4 bytes identifying the audio bank. For example `0x363C4C8E`.
- Unknown/Padding: The rest of the bytes to complete the size indicated by the header section size.

**Content Index (DIDX):**
- DIDX header: 4 bytes, in hexadecimal `0x44494458` ("DIDX")
- Content table size: 4 bytes indicating the size of the content table, for example `0xCC000000` in hexadecimal would indicate 204 bytes.
- Table structure: Each file in the bank occupies 12 bytes in this section in the following order (Little Endian):
    - File ID (4 bytes): e.g. "48 FD 32 0E"
    - Offset/Position (4 bytes): Where the audio starts within the DATA section.
    - Size (4 bytes): How much space that audio takes.

**Data Container (DATA):**
- DATA header: 4 bytes, in hexadecimal `0x44415441` ("DATA")
- Total size of all combined audios: 4 bytes indicating the total size in bytes of all audios. For example, `0x8A250400` in hexadecimal little endian would indicate 271,754 bytes in total.
- From here, we have a series of "RIFF/WAV" entries, each starting with the bytes "52 49 46 46".

**HIRC:**
- 4 bytes `0x48495243` corresponding to "HIRC".
- Signature size: 4 bytes in little endian indicating the size of the signature.
- Signature content: a series of bytes of the indicated size corresponding to the signature content.

**Final block separator:**
- Separator: 4 bytes with the value `0x00000000`.
- Bank ID: 4 bytes matching the audio bank identifier indicated above (Bank ID).

### Unidentified Binary (BIN) in Language Resource File
256-byte binary blocks have been identified that may appear within the binary. Specifically, these two with these values (256 bytes each):
- `0xFFFF...FFFF01000000000200000002000001000000010000000000000057000000000000000100000000000000000200000002000001000000940010000008000000000000`
- `0xFFFF...FFFF0100000000020000000200000100000001000000000000003D000000000000000100000000000000000200000002000001000000940004000002000000000000`

Some of these binary blocks are suspected to configure the mapping of characters to some textures containing the game's text fonts.

### Subtitles (SUB)
If the data block does not meet the above conditions, it is likely a block containing subtitles.

#### Proprietary Binary Subtitle Format
The binary format of the subtitles is as follows, with all values in Little-Endian format:

- **Ids:**
    - Number of identifiers: 4 bytes indicating the number of identifiers. One for each subtitle.
    - Identifiers: 8 bytes (`uint64`) for each identifier value.
- **Subtitles:**
    - Number of subtitles: 4 bytes indicating the number of subtitles.
    - Subtitle offsets: for each subtitle, its initial offset is indicated with 4 bytes (starting with `0x00000000`), corresponding to the first subtitle. At the end, there is an additional offset to know the size of the last subtitle.
    - Subtitle literals: the subtitle strings are concatenated. Each subtitle ends with the character in hexadecimal `0x00`.

#### Subtitle Literals
- Some literals contain variables processed by the game. These variables should not be translated. The format of these variables is: `[@VAR]`.

## Known Limitations

- The analysis is based on reverse engineering and may contain errors or incorrect assumptions.
- Not all fields and structures are fully identified.
- Some resources and possible paddings could not be interpreted with certainty.