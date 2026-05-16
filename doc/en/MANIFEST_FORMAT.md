# Lone Echo 2 Manifest Format

> ⚠️ **Warning:** This document is based on reverse engineering.

---

- [Lone Echo 2 Manifest Format](#lone-echo-2-manifest-format)
  - [Overview](#overview)
    - [Manifests](#manifests)
    - [Packages](#packages)
  - [Concepts](#concepts)
  - [Manifest Header](#manifest-header)
  - [ZSTD Binary Content](#zstd-binary-content)
  - [Decompressed Frame Structure](#decompressed-frame-structure)
    - [1. General Index](#1-general-index)
    - [2. Resource Blocks Index 1](#2-resource-blocks-index-1)
    - [3. Resource Blocks Index 2](#3-resource-blocks-index-2)
    - [4. Data Frames Index](#4-data-frames-index)
    - [4. Final Frames Index](#4-final-frames-index)

---

## Overview
The manifest file is a compressed file using [Zstandard (ZSTD)](https://facebook.github.io/zstd/). The decompressed content contains metadata that indexes game resources stored in one or more files called data packages. These data packages associated with the manifest are also compressed with ZSTD, but with the particularity that they are multi-frame (contain independent compressed fragments).

### Manifests
In the folder `_data\5932408047\rad16\win10\manifests` there are several manifest files, each identified by a hexadecimal value. The associated packages will have the same name but with the suffix _X indicating the package number (from 0 to n).

Language resource manifest files:

- `ff715342fa4b2d8f`: English (complete).
- `5f7991e1f1909a1f`: Spanish (incomplete)
- `a960d5177e5af4ae`: French (incomplete)
- `a960d5177e5af8bd`: Japanese (incomplete)
- `a960d5177e5af6b9`: German (incomplete)
- `a960d5177e5af9b3`: Korean (incomplete)

Main game resource manifest file:
- `6242ff7e5bc499ee`

### Packages
In the folder `_data\5932408047\rad16\win10\packages` are the resource packages associated with the manifests. They are named with the same hexadecimal value as the manifest, but including the suffix `_X` indicating the package number (from 0 to n).

**Language resource packages**:
- `ff715342fa4b2d8f_0`: English (complete).
- `5f7991e1f1909a1f_0`: Spanish (incomplete)
- `a960d5177e5af4ae_0`: French (incomplete)
- `a960d5177e5af8bd_0`: Japanese (incomplete)
- `a960d5177e5af6b9_0`: German (incomplete)
- `a960d5177e5af9b3_0`: Korean (incomplete)

So far, only the English language package (`ff715342fa4b2d8f_0`) seems to be complete and functional. The others may be incomplete or lack certain resources, which could limit their usefulness or cause errors if used in the game.

**Main game resource packages** (10 packages):
- `6242ff7e5bc499ee_0`
- `6242ff7e5bc499ee_1`
- `6242ff7e5bc499ee_2`
- `6242ff7e5bc499ee_3`
- `6242ff7e5bc499ee_4`
- `6242ff7e5bc499ee_5`
- `6242ff7e5bc499ee_6`
- `6242ff7e5bc499ee_7`
- `6242ff7e5bc499ee_8`
- `6242ff7e5bc499ee_9`

It is important that the manifest and its corresponding resource file match, as the manifest acts as an index for the data stored in the resource.

## Concepts

**Package**: Game resource file consisting of multiple frames. Identified by a number from 0 to n.
**Package Data Frame**: Set of Resource Blocks within a package file. Identified by a number from 0 to n within the global set of packages associated with the manifest.
**Package Final Frame**: Special frame that closes a package. It does not contain resource blocks.
**Resource**: A game resource identified by an 8-byte hexadecimal number. The same resource can have different data blocks of different types (audio, texture, subtitles, etc.).
**Resource Block**: Data block of a game resource of a certain type (audio, texture, subtitles, etc.). Identified by Resource Id. (8 bytes) + Resource Type Id. (8 bytes)

## Manifest Header
At the beginning of the manifest file, there are 24 bytes that are not part of the compressed ZSTD content. Their structure is as follows:

| Offset | Size | Description                                   |
|--------|------|-----------------------------------------------|
| 0x00   | 4    | String "ZSTD"                                 |
| 0x04   | 4    | Value 0x10000000 (not identified)             |
| 0x08   | 8    | Decompressed size of the Manifest (Little Endian) |
| 0x10   | 8    | Compressed size of the Manifest (Little Endian)   |

## ZSTD Binary Content
After the header, the ZSTD-compressed content begins. This block consists of a single frame, identified by the **magic number** `0x28B52FFD` at the start of the compressed block.

## Decompressed Frame Structure
The decompressed frame has the following general structure:

### 1. General Index
    
A table of **200 bytes** with the following binary format:

| Offset | Size | Description |
|--------|------|-------------|
| 0x0000 | 4    | Number of Packages (Little Endian)|
| 0x0004 | 4    | Fixed value 0x00000800 |
| 0x0008 | 16   | Fixed value 0 |
| 0x0018 | 8    | Number of bytes of **Resource Blocks Index 1** (Little Endian) |
| 0x0038 | 8    | Number of Resource Blocks (Little Endian) |
| 0x0040 | 8    | Number of Resource Blocks (Little Endian) |
| 0x0048 | 16   | Fixed value 0 |
| 0x0058 | 8    | Number of bytes of **Resource Blocks Index 2**(Little Endian) |
| 0x0060 | 8    | Fixed value 0 |
| 0x0068 | 8    | Fixed value 0x0000000001000000 | 
| 0x0070 | 8    | Fixed value 0x2000000000000000 |
| 0x0078 | 8    | Number of Resource Blocks (Little Endian) |
| 0x0080 | 8    | Number of Resource Blocks (Little Endian) |
| 0x0088 | 16   | Fixed value 0 |
| 0x0098 | 8    | Number of bytes of the sum of the indices **Data Frames Index** + **Final Frames Index** (Little Endian) |
| 0x00A0 | 8    | Fixed value 0 |
| 0x00A8 | 8    | Fixed value 0x0000000001000000 | 
| 0x00B0 | 8    | Fixed value 0x2000000000000000 |
| 0x00B8 | 8    | Number of Frames (Little Endian) | 
| 0x00C0 | 8    | Number of Frames (Little Endian) |

**Notes**:
- Both the number of Resource Blocks and the number of Frames refer to the sum of those existing in the set of Packages.
- The frame number indicators count the **Data Frames** and **Final Frames** of all packages. 

### 2. Resource Blocks Index 1

A table with an entry of **32 bytes for each Resource Block** with the following binary format:
    
| Offset | Size | Description |
|--------|------|-------------|
| 0x00   | 8    | Resource Block Type (see table) |
| 0x08   | 8    | Resource ID |
| 0x0C   | 4    | Data Frame Number (Little Endian) (Value from 0 to n) |
| 0x10   | 4    | Initial offset within the Data Frame (Little Endian) |
| 0x14   | 4    | Size in bytes of the Resource (Little Endian) |
| 0x18   | 4    | Unknown value |

**Notes**:
- The table is grouped by resource type, always showing resources of the same type continuously, but the order used is unknown.
- The frame number is global for all packages. (It does not start at 0 at the beginning of each package)
- There may be more than one Block for the same Resource. This happens, for example, with BNK-type resources that also have associated unidentified BIN types.

**Resource Block Types**:
- Present in language resource packages:
    - `0x02db12a32f783bef`: SUB (Subtitle texts: dialogues, objectives, but does not include tablet dialogues)
    - `0x61887bcb6919acbe`: DDS (Textures: character maps)
    - `0x985ab87bef8e356d`: BNK (Audio banks: dialogues)
    - `0xa0b80093c4324c4a`: BIN (Unidentified: possible character-to-texture mapping)
    - `0xdcf039b76eda705e`: BIN (Unidentified: possible character-to-texture mapping)
- Some present in the main game resource package (many and unidentified):
    - `0xb8856ed460260c82`
    - `0x3c8a2eb4ccd42f82`
    - `0x482d6b8bac990284`
    - `0x645f65d5bb558085` 
    - `0xf8836a0fe28cd285`
    - `0xf6cf703951ef1e87`
    - `0xb259975d1c480788`      
    - `0x2240263fb74a2e88`
    - `0x03ef709bee281b8b`
    - `0x54059e1cf736258c`
    - `0xb0f5c22b267b398f`
    - `0x9632f6e302974990`
    - `0xb286c7ce28d91e91`
    - `0xe658c1afa91b4c91`
    - `0x282b4db96c568c91`
    - `0x0e5badd9e5cf3492`
    - `0xe8f52b43e1d3ab92`
    - `0xdeec6024652b8396`
    - `0x069c7c2eb6638896`
    - `0xb8d440ababadbd97`
    - `0x0c9a38e43fa5a398`
    - etc.

### 3. Resource Blocks Index 2

A table with an entry of **40 bytes for each Resource Block** with the following binary format:

| Offset | Size | Description |
|--------|------|-------------|
| 0x00   | 8    | Resource Block Type (see table) |
| 0x08   | 8    | Resource ID |
| 0x0C   | 20   | Unknown value |
| 0x14   | 4    | Unknown value |

**Notes**:
- The table is grouped by resource type, always showing resources of the same type continuously, but the order used is unknown.


### 4. Data Frames Index

A table with an entry of **16 bytes for each Data Frame** of each Package with the following binary format:

| Offset | Size | Description |
|--------|------|-------------|
| 0x00   | 4    | Package Number (Little Endian)  (from 0 to n) |
| 0x04   | 4    | Offset with accumulated compressed size of Data Frames of that package (Little Endian) (Value 0 at the start of each package)|
| 0x08   | 4    | Compressed size of the Data Frame (Little Endian) |
| 0x0C   | 4    | Decompressed size of the Data Frame (Little Endian) |

**Notes**:
- The table is sorted in ascending order by package number and accumulated offset of each Data Frame.

### 4. Final Frames Index

A table with an entry of **16 bytes for each Final Frame** of each Package with the following binary format:
| Offset | Size | Description |
|--------|------|-------------|
| 0x00   | 4    | Package Number (Little Endian)  (from 0 to n) |
| 0x04   | 4    | Total compressed size of all Data Frames of that Package (Little Endian)|
| 0x08   | 8    | Unknown, but it makes the language's own fonts work |

**Notes**:
- Each Package has 1 Final Frame.
- The table is sorted in ascending order by package number.