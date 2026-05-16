# Procesado de Scripts DLL
- [Procesado de Scripts DLL](#procesado-de-scripts-dll)
  - [1. Extracción de textos](#1-extracción-de-textos)
  - [2. Filtrado manual](#2-filtrado-manual)
  - [3. Traducción de textos](#3-traducción-de-textos)
    - [Automatización con IA](#automatización-con-ia)
    - [QA y Scripts de ayuda](#qa-y-scripts-de-ayuda)
  - [4. Parcheado de Scripts DLL](#4-parcheado-de-scripts-dll)

## 1. Extracción de textos

Se ha creado el script **dllscript/dll_dir_sub_extractor.py** que es capaz de extraer los textos de todos los ficheros **dll** presentes en la carpeta que se le pasa por parámetro.

```
.\src\dllscript\dll_dir_sub_extractor.py ${lone-echo2-game-path}\bin\win10\scripts output\scripts_dll_subs_english.txt
```

El formato del fichero generado es el siguiente:

```
{filename}|{va_address}|{file_offset}|{max_size}|{text}
```

Siendo:
- **filename**: nombre del fichero DLL (sin la extensión)
- **va_address**: va_address donde dentro de la DLL donde se encontró el literal de texto
- **file_offset**: offset dentro del fichero DLL donde se encuentra el literal de texto
- **max_length**: máxima longitud que se le permite al literal de texto. (En este caso estamos editando una DLL y estamos limitados). Hay que tener en cuenta que la longitud es en bytes y hay caracteres que codificados en **utf-8** ocupan 2 bytes.
- **text**: texto

Contenido de ejemplo:
```
0001cf5152080030|0x180007300|0x6700|39|Liv. That's not going to happen to you.
0001cf5152080030|0x18000706c|0x646c|7|Yeah.
0001cf5152080030|0x1800072d0|0x66d0|47|Whatever it takes, we'll find a solution.
0001cf5152080030|0x1800072c0|0x66c0|15|I know Jack.
001562b639bcb14f|0x1800082b8|0x6ab8|39|Lucky for us, it was still functional.
```

## 2. Filtrado manual

Una vez obtenido el fichero con todos los textos, se hizo un tratamiento manual eliminado textos que no eran traducibles: contenían variables o bien se veía que podrían dar problemas.
(Lamentablemente no hay automatización para este proceso)

## 3. Traducción de textos

En este punto ya podemos empezar a traducir todos los ficheros de texto de subtítulos de la versión en inglés.

**IMPORTANTE**: 
    - Hay que modificar únicamente la parte de literal de texto, nunca modificar los números e identificadores.
    - Usar codificación **UTF-8**

### Automatización con IA
En la traducción a español se usó un procesado en batch usando IA, revisando el resultado iterativamente (siempre se puede mejorar).

En este caso se usó un único paso con un prompt [translate-redux-dll-subs-spanish.md](../../prompts/translate-redux-dll-subs-spanish.md) que pide una traducción bajo unas reglas de máxima longitud que han de tener los textos.

### QA y Scripts de ayuda

Se crearon una serie de scripts en `src/dllscript` para ayudar en el procesado de subtítulos.
La calidad de los scripts es pobre (se hicieron rápido y con IA), pero son totalmente funcionales y fueron de mucha utilidad.

Se parte de un fichero de subtítulos donde cada linea tiene este formato:

```
{file_id}|{va_address}|{file_offset}|{max_length}|{length}|{text}
```

Este es el formato que genera nuestro prompt de IA usado al hacer la traducción. Siendo:

- `{filename}`: nombre del fichero DLL (sin extensión) del texto.
- `{va_address}`: a_address donde dentro de la DLL del texto.
- `{file_offset}`: offset del fichero DLL donde va el texto.
- `{max_length}`: limitación que teníamos de longitud en bytes.
- `{length}`: número de bytes que ocupa `{text}` codificado en **utf-8**.
- `{text}`: texto traducido.

**Ayuda General**
- `merge_subs_by_key`: permite hacer merge de 2 ficheros de subtítulos.

**QA**
- `QA/fix_sub_lengths.py`: recalcula el campo `{translated_length}` y reporta los casos en que la longitud de la traducción sobrepasa el límite marcado por `{max_length}`.
- `QA/fix_sub_lengths_utf8.py`: sirve para comprobar que todos los identificadores de subtítulos del fichero traducido están en el original y así encontrar alteraciones de ids que podrían haberse hecho por la IA, por ejemplo.

## 4. Parcheado de Scripts DLL

Se parte de un fichero con el siguiente formato:
```
{filename}|{va_address}|{file_offset}|{max_length}|{length}|{text}
```

Se creó el script `dllscript/dll_dir_sub_patcher.py`:
```
python ./src/dllscript/dll_dir_sub_patcher.py
usage: dll_sub_patcher.py <fichero_txt> <carpeta_dlls>
```

Este script realiza el parche de los ficheros DLL de la carpeta indicada sustituyendo los textos originales por los traducidos.

Si ejecutamos:
```
src/dllscript\dll_dir_sub_patcher.py  fichero_subs_traducido.txt ${lone-echo2-game-path}\bin\win10\scripts
```

Conseguiremos parchear los ficheros DLL del juego que contienen estos textos.

(Se recomienda hacer backup de la carpeta `scripts` original del juego)