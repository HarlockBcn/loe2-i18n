# Resource File Processing

- [Resource File Processing](#resource-file-processing)
  - [1. Extraction of Internationalizable Resources](#1-extraction-of-internationalizable-resources)
    - [Script extract.py](#script-extractpy)
    - [Extraction Folder](#extraction-folder)
    - [Subtitle Text Files](#subtitle-text-files)
  - [2. Subtitle Translation](#2-subtitle-translation)
    - [Helper Scripts](#helper-scripts)
    - [AI Automation](#ai-automation)
    - [QA](#qa)
    - [Special Characters and Font Textures](#special-characters-and-font-textures)
    - [Replacing Files in "subtitles" Folder](#replacing-files-in-subtitles-folder)
  - [3. Font Texture Adaptation](#3-font-texture-adaptation)
  - [4. Repacking (repack.py)](#4-repacking-repackpy)


## 1. Extraction of Internationalizable Resources

The English and Spanish manifest and resource files were identified. There is no trace or option to select Spanish in the game, but an incomplete resource file was found, half-done, with subtitles (a very small part) poorly translated automatically and some early-stage audio files generated with some "text-to-speech" utility.
In contrast, the original game does allow English subtitles, so it was expected that in the English resources, all texts could be obtained for translation.

### Script extract.py
The script `resource/extract.py` was created:
```
python ./src/resource/extract.py
usage: extract.py [-h] [--packages PACKAGES] manifest_path packages_dir output_dir
```

This script allows you to extract all resources of a language into a folder. We are interested in extracting the resources for **English and Spanish** (even if incomplete), and later it will be explained why.

**NOTE**: For translation to another language, you must extract the resources for **English** and the **target language**.

See [Manifest format](MANIFEST_FORMAT.md) to know which folder corresponds to each language.

So, run the following commands:

```
python .\src\extract.py ${lone-echo2-game-path}\_data\5932408047\rad16\win10\manifests\ff715342fa4b2d8f ${lone-echo2-game-path}\_data\5932408047\rad16\win10\packages .\output\ff715342fa4b2d8f

python .\src\extract.py ${lone-echo2-game-path}\_data\5932408047\rad16\win10\manifests\5f7991e1f1909a1f ${lone-echo2-game-path}\_data\5932408047\rad16\win10\packages .\output\5f7991e1f1909a1f
```

In the `output` folder, the following file and folder structure will be generated:

```
├───5f7991e1f1909a1f        # Spanish resources (incomplete)
│   └───0
│       └───subtitles
├───ff715342fa4b2d8f        # English resources
│   └───0
│       └───subtitles
```

For translation, **always work from the English language folder** `ff715342fa4b2d8f` and use the other only to obtain resources related to text fonts. This will be explained later.

### Extraction Folder

Inside a specific language folder:

- **Package "0" Folder**: corresponds to the package number. For language resource files, there is only one package. In this folder, the different resource files found within the package are extracted: DDS (textures), BIN (binaries), BNK (audio), SUB (subtitles).

    ```
    ...
    005-06-a3a1d2c7ef582375-02db12a32f783bef.sub
    005-07-41f87e0f47280d77-02db12a32f783bef.sub
    005-08-104bb5b03ced07ac-a0b80093c4324c4a.bin
    005-09-c3c3cd0465869276-a0b80093c4324c4a.bin
    005-10-1c3949c13ae503c4-a0b80093c4324c4a.bin
    005-11-c0e1c53322201a2b-a0b80093c4324c4a.bin
    006-00-dfaaf3ca83578e14-61887bcb6919acbe.dds
    007-00-9d18103af94cae71-985ab87bef8e356d.bnk
    008-00-104bb5b03ced07ac-61887bcb6919acbe.dds
    009-00-c3c3cd0465869276-61887bcb6919acbe.dds
    ...
    ```
    The file name format is as follows:

    `{frame-number}-{resource-index}-{resource-id}-{resource-type-id}.{extension}`
    - **Frame number**: indicates the frame number corresponding to the ZSTD compression format.
    - **Resource index**: resource index within the frame (from 0 to n).
    - **Resource id**: unique resource identifier.
    - **Resource type id**: resource type identifier. See: [Manifest format](MANIFEST_FORMAT.md)


- **"subtitles" Folder**: contains the SUB binary files converted to an editable text format to facilitate translation. A TXT file with **UTF-8** encoding is generated for each SUB file.
    
    ```
    ...
    090-04-dc197e957826a4c3.txt
    090-05-2e8d5f35a4c1218f.txt
    095-01-22c3d222966d165b.txt
    095-02-0b5f1fcaa265a681.txt
    095-04-2ee23acc113b7ccf.txt
    095-05-adfae9f644acbb9d.txt
    ...
    ```    

    The file name format is as follows:

     `{frame-number}-{resource-index}-{subtitle-id}.{extension}`

    - **Frame number**: indicates the frame number of the original subtitle file, corresponding to the ZSTD compression format.
    - **Resource index**: resource index within the frame (from 0 to n).
    - **Subtitle id**: subtitle identifier/hash.

### Subtitle Text Files

Example content of a subtitle text file:
```txt
$090-04-0x813139be438d8ff5|[irked hoot]
$090-04-0x813c68e9168ad4a1|Ticks are an evolved form of the bio-mass.
$090-04-0x813d68eb45dad9a4|How did you know?
$090-04-0x816a3deb17d5d8f2|Ticks are an evolved form of the bio-mass.
$090-04-0x826b69b9448fdda0|[enthused squeak]
$090-04-0x843968eb44888af5|[beckoning chatter]
$090-04-0x843969be17dddcf0|Yeah, but not by choice.
$090-04-0x856a61e9128edfa6|[revolted buzz]
$090-04-0x863a3bec12d5dba3|Ticks are an evolved
```

The format of each line in the subtitle file is as follows:

`${frame-number}-{resource-index}-{subtitle-id}|{text}`

- **Frame number**: indicates the frame number of the original subtitle file, corresponding to the ZSTD compression format.
- **Resource index**: resource index within the frame (from 0 to n).
- **Subtitle id**: subtitle identifier/hash.
- **text**: subtitle text literal.

## 2. Subtitle Translation

At this point, you can start translating all the subtitle text files from the English version.

**IMPORTANT**: 
- Only modify the text literal part, never modify the numbers and identifiers.
- Use **UTF-8** encoding

For the text literals, keep these considerations in mind:
- If you find a string like `[@variable_name]`, leave it intact and do not translate it. It is used for dynamic text that includes variable values.
- Texts include line breaks expressed with the string `\n`. Leave them as is, do not modify them.
- Translated texts should never exceed the length of the English version, as this would increase the delay between subtitle display and audio.
- Be careful with special characters, accents, etc. See: [Special Characters and Font Textures](#special-characters-and-font-textures)

### Helper Scripts

A series of scripts were created in `src/resource/subs` to assist in subtitle processing.

- **concat_subtitles.py**: concatenates several subtitle TXT files into a single one.
- **add_text_length.py**: adds the length of the text of each line. Useful to know the length not to exceed or to indicate to an AI prompt that the translated text should never exceed this length. The length considers that characters are encoded in **utf-8** and may take up to 2 bytes.


### AI Automation
For the Spanish translation, batch processing using AI was used, reviewing the result iteratively (it can always be improved).

It was decided to do it in 2 steps:
- English to Spanish translation:
    - All subtitle text files were unified into a single one using the **subs/concat_subtitles.py** script.
    - The **subs/add_text_length.py** script was used to add text length information.
    - The prompt [translate-subs-file-spanish.md](../../prompts/translate-subs-file-spanish.md) was used
- Abbreviation process to adapt the length of the texts to the original in English:
    - The **subs/QA/compare_subtitles_length.py** script was used to obtain a file with information on the difference in text length between the original and translated texts.
    - The prompt [abbreviate-subs-file-spanish.md](../../prompts/abbreviate-subs-file-spanish.md) was used

(There was a question whether everything could have been done in a single step)

### QA

A series of scripts were created in `src/resource/subs` to assist in the quality control of translated subtitles.
The quality of the scripts is poor (they were made quickly and with AI), but they are fully functional and were very useful.

**Duplicate Handling**
- **duplicates/manage_duplicated_texts.py**: creates a subtitle file without duplicates and a registry indicating duplicated texts. 
- **duplicates/recreate_subtitles_with_dups_registry.py**: regenerates a complete subtitle file using a duplicates registry.

**QA**
- **QA/check_sub_file_by_frame_block_sub_id.py**: compares a translated subtitle file with the original English one to detect missing subtitles, altered identifiers, etc.
- **QA/compare_subtitles_length.py**: compares a translated subtitle file with the original English one to detect if the translated text length exceeds the original text length.

### Special Characters and Font Textures

When translating to a specific language, be careful with the special characters used. To render the text, the game uses textures containing all supported characters. There are specific textures for each language. Characters not present in those textures should not be used.

- [English](../images/text_eng.png)
- [Spanish](../images/text_spa.png)
- [French](../images/text_fre.png)
- [German](../images/text_ger.png)
- [Japanese](../images/text_jap.png)
- [Korean](../images/text_cor.png): We believe Korean fonts are not supported because the found textures do not contain Korean characters 😞

More details on how to consider these textures will be explained later.

### Replacing Files in "subtitles" Folder

Once the translation is done, if you have not worked directly on the files in the `output\0\subtitles` folder (not recommended), you will usually have a single text file with all the translated literals, where each line has the following format:

`${frame-number}-{resource-index}-{subtitle-id}|{text}` or  
`${frame-number}-{resource-index}-{subtitle-id}|..{length indicators}..|{text}`

You need to split this single file back into several. For this, use the **subs/split_subtitles.py** script:
```
python .\src\resource\subs\split_subtitles_file.py 
Usage: .\src\resource\subs\split_subtitles_file.py <subtitles_file> <output_folder>
```

Specify a temporary folder as the destination, for example `translated_subtitles_split`. 

```
python .\src\resource\subs\split_subtitles.py subtitles_file.txt  translated_subtitles_split
``` 

Then use the **subs/replace_sub_files_by_frame_block.py** script to update the subtitles in the `output\0\subtitles` folder:

```
python .\src\resource\subs\replace_sub_files_by_frame_block.py 
Usage: .\src\resource\subs\replace_sub_files_by_frame_block.py <source_folder> <destination_folder>
```

The command would be:
```
python .\src\resource\subs\replace_sub_files_by_frame_block.py .\translated_subtitles_split  .\output\0\subtitles
``` 

(These 2 steps should ideally be unified into one, but for now, that's how it is.)

## 3. Font Texture Adaptation

At this point, recall that in the [extraction](#1-extraction-of-internationalizable-resources) step, we also extracted the incomplete resources for the target language.

We need to replace the **BIN** and **DDS** resources from the English language package with those from the target language package (in this case, Spanish). For this, use the script `resource\frames\replace_files_by_resource_id.py`:
```
Usage: .\src\resource\frames\replace_files_by_resource_id.py <source_folder> <destination_folder> <extension>
Example extensions: sub, bin, bnk, dds, txt
```

``` 
python .\src\resource\frames\replace_files_by_resource_id.py .\output\5f7991e1f1909a1f\0 .\output\ff715342fa4b2d8f\0 dds
python .\src\resource\frames\replace_files_by_resource_id.py .\output\5f7991e1f1909a1f\0 .\output\ff715342fa4b2d8f\0 bin
``` 

This will make the game use the correct font textures and mapping for the target language.

## 4. Repacking (repack.py)

The script `resource/repack.py` was created:
```
python ./src/resource/repack.py
usage: repack.py [-h] [--packages PACKAGES] extracted_dir original_manifest output_dir
```

This script allows you to repackage the resources and regenerate the resource package file.

If you run:
```
python src\resource\repack.py .\output\ff715342fa4b2d8f ${lone-echo2-game-path}\_data\5932408047\rad16\win10\manifests\ff715342fa4b2d8f ${lone-echo2-game-path}\_data\5932408047\rad16\win10\manifests\5f7991e1f1909a1f .\output\repacked
```

**NOTE**: The code `5f7991e1f1909a1f` is used for Spanish. For other languages, you will need to change it.


In the `output\repacked` folder, it will generate two files:
- `ff715342fa4b2d8f`
- `ff715342fa4b2d8f_0`

You can copy these files to the appropriate location in the original game installation folder.
(It is recommended to back up the originals)