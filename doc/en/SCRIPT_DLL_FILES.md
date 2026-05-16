# Script DLL Files

> ⚠️ **Warning:** This document is based on reverse engineering.

---

The DLL files present in the `bin\win10\scripts` folder of the game were analyzed, and it was discovered that some game literals not present in the internationalizable resource files are stored there.

Since these are binary DLL files, reverse engineering was performed by analyzing the binary content, identifying patterns to search and replace the desired text literals.

The following pattern was found: 
- Search in the `.rdata`, `.text`, and `.data` sections of the DLL.
- All texts found between the following two markers are candidates for translation:
    - Start marker: `Blocking node (%%08x) used in Initialize thread`
    - End marker: `Node (%08x) had no execute function`

**Limitation**: In this case, we are limited to overwriting the texts without exceeding the original length. If they are shorter, it's fine as long as a `0x00` byte is added at the end of the text.