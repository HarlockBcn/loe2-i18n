# Lone Echo 2 Internationalization Project

## Introduction

This project was created to provide Spanish language support for the game Lone Echo 2. Lone Echo 2 is a great game and a fantastic sequel to another great game, Lone Echo. Its release was rushed, with the game still not fully polished and lacking support for other languages. Only English audio and the possibility of English subtitles were available.

The game's binary files were reverse engineered, and a way was found to embed subtitles in another language, at least in Spanish, which was the initial goal of the project, but open to providing the same processes and tools to generate subtitles in other languages.

## Game Folder Structure
In the installed game folder, the following relevant folders and files were identified:
- `_data\5932408047\rad16\win10`:
    - `\manifests`: resource package manifest files. Indexes resources within the resource package files.
    - `\packages`: resource package files. Various game resources such as textures, audio files, and most importantly: subtitles.
- `bin\win10\scripts`: Various DLL files, inside which text fragments and additional subtitles were found.

The idea is to extract texts and subtitles from these files, modify them, and repackage the files with the translated texts.

## File Analysis

Detailed analyses were performed on the different file types:
  - Manifest files: [Manifest format](MANIFEST_FORMAT.md)
  - Resource Package files: [Resource package format](RESOURCE_PACKAGE_FORMAT.md)
  - Script files (DLL): [Script DLL Files](SCRIPT_DLL_FILES.md)

## Process and Tools

Python scripts were mainly used for the entire process. Below is a detailed description of the process and the tools/scripts used in each case.

It is recommended to create a Python virtual environment in the project workspace.

- [Resource file processing](RESOURCE_PROCESSING.md)
- [Script (DLL) processing](SCRIPT_DLL_PROCESSING.md)