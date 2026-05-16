# Procesado de Ficheros de Recurso

- [Procesado de Ficheros de Recurso](#procesado-de-ficheros-de-recurso)
  - [1. Extracción de recursos internacionalizables](#1-extracción-de-recursos-internacionalizables)
    - [Script extract.py](#script-extractpy)
    - [Carpeta de extracción](#carpeta-de-extracción)
    - [Ficheros de texto de subtítulos](#ficheros-de-texto-de-subtítulos)
  - [2. Traducción de subtítulos](#2-traducción-de-subtítulos)
    - [Scripts de ayuda](#scripts-de-ayuda)
    - [Automatización con IA](#automatización-con-ia)
    - [QA](#qa)
    - [Caracteres especiales y texturas de fuentes](#caracteres-especiales-y-texturas-de-fuentes)
    - [Reemplazo de ficheros de carpeta "subtitles"](#reemplazo-de-ficheros-de-carpeta-subtitles)
  - [3. Adaptación de texturas de fuentes](#3-adaptación-de-texturas-de-fuentes)
  - [4. Re-empaquetado (repack.py)](#4-re-empaquetado-repackpy)


## 1. Extracción de recursos internacionalizables

Se identificaron el manifest y fichero de recursos correspondientes al idioma inglés y también al español. En el juego no hay rastro ni opción de seleccionar idioma español, pero sí se encontró un fichero de recursos sin completar, a medio hacer, con subtítulos (una parte muy pequeña) traducidos de forma automática muy pobre y algunos ficheros de audio en fase temprana generados con alguna utilidad "text-to-speech".
En cambio, el juego original sí que da la opción de activar subtítulos en inglés, así que esperábamos que en los recursos en inglés, obtuviéramos todos los textos para poderlos traducir.

### Script extract.py
Se creó el script `resource/extract.py`:
```
python ./src/resource/extract.py
usage: extract.py [-h] [--packages PACKAGES] manifest_path packages_dir output_dir
```

Este script nos permite extraer todos los recursos de un idioma en una carpeta. Nos interesa extraer los recursos de los idiomas **inglés y español** (aunque esté sin completar), luego se explicará por qué. 

**NOTA**: En el caso de traducción a otro idioma, habrá que extraer los recursos de los idiomas **inglés** y el **idioma a traducir**.

Ver [Manifest format](MANIFEST_FORMAT.md) para saber qué carpeta corresponde a cada idioma.

Así pues, ejecutamos los siguientes comandos:

```
python .\src\extract.py ${lone-echo2-game-path}\_data\5932408047\rad16\win10\manifests\ff715342fa4b2d8f ${lone-echo2-game-path}\_data\5932408047\rad16\win10\packages .\output\ff715342fa4b2d8f

python .\src\extract.py ${lone-echo2-game-path}\_data\5932408047\rad16\win10\manifests\5f7991e1f1909a1f ${lone-echo2-game-path}\_data\5932408047\rad16\win10\packages .\output\5f7991e1f1909a1f
```

En la carpeta `output` nos habrá generado la siguiente estructura de ficheros y carpetas:

```
├───5f7991e1f1909a1f        # Recursos en Español (incompletos)
│   └───0
│       └───subtitles
├───ff715342fa4b2d8f        # Recursos en Inglés
│   └───0
│       └───subtitles
```

Para la traducción, **trabajaremos siempre a partir de la carpeta corresponiendte al idioma inglés** `ff715342fa4b2d8f` y usaremos la otra sólo para obtener unos recursos relacionados con las fuentes de texto. Se explicará más adelante.

### Carpeta de extracción

Dentro de la carpeta de un idioma en concreto:

- **Carpeta Paquete "0"**: correspondiente al número de paquete. En el caso de ficheros de recursos de idioma, sólo tenemos un único paquete. En esta carpeta se extraen los diferentes ficheros de recursos encontrados dentro del paquete: DDS (texturas), BIN (binarios), BNK (audio), SUB (subtítulos).

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
    El formato de nombre de los ficheros es el siguiente:

    `{número-frame}-{índice-recurso}-{id-recurso}-{id-tipo-recurso}.{extension}`
    - **Número de frame**: indica el número de frame correspondiente al formato de compresión ZSTD.
    - **Número de recurso**: índice de recurso dentro del frame (de 0 a n).
    - **Id de recurso**: identificador único del recurso.
    - **Id tipo de recurso**: identificador del tipo de recurso. Ver: [Manifest format](MANIFEST_FORMAT.md)


- **Carpeta "subtitles"**: contiene los ficheros SUB binarios convertidos a un formato de texto editable y que facilita la traducción. Se genera un fichero TXT con codificación **UTF-8** para cada fichero SUB.
    
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

    El formato de nombre de los ficheros es el siguiente:

     `{número-frame}-{índice-recurso}-{id-recurso}-{id-tipo-recurso}.{extension}`

    - **Número de frame**: indica el número de frame correspondiente al formato de compresión ZSTD.
    - **Número de recurso**: índice de recurso dentro del frame (de 0 a n).
    - **Id de recurso**: identificador único del recurso.

### Ficheros de texto de subtítulos

Ejemplo de contenido de un fichero de texto de subtítulos:
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

El formato de cada linea del fichero de subtítulos es el siguiente:

`${número-frame}-{número-recurso}-{id-subtítulo}|{texto}`

- **Número de frame**: indica el número de frame del fichero original de subtítulos, correspondiente al formato de compresión ZSTD.
- **Número de recurso**: índice de recurso dentro del frame (de 0 a n).
- **Id de subtítulo**: identificador/hash del subtítulo.
- **text**: literal de texto del subtítulo.

## 2. Traducción de subtítulos

En este punto ya podemos empezar a traducir todos los ficheros de texto de subtítulos de la versión en inglés.

**IMPORTANTE**: 
- Hay que modificar únicamente la parte de literal de texto, nunca modificar los números e identificadores.
- Usar codificación **UTF-8**

Sobre los literales de texto, hay que tener en cuenta estas consideraciones:
- Si se encuentra una cadena del tipo `[@nombre_de_variable]`, hay que dejarla intacta y no traducirla. Se usa para texto dinámico en el que se incluyen valores de variables.
- Los textos incluyen saltos de linea expresados con la cadena `\n`. Hay que dejarlos tal cual, no modificarlos.
- Los textos traducidos nunca deberían exceder la versión en inglés porque esto haría que aumentase el desfase entre visionado de subtítulos y el audio.
- Ojo con el uso de caracteres especiales, acentos, etc. Ver: [Caracteres especiales y texturas de fuentes](#caracteres-especiales-y-texturas-de-fuentes)

### Scripts de ayuda

Se crearon una serie de scripts en `src/resource/subs` para ayudar en el procesado de subtítulos.

- **concat_subtitles.py**: concatena varios ficheros TXT de subtítulos en uno único.
- **add_text_length.py**: añade la longitud del texto de cada linea. Útil para sabe la longitud que no podemos exceder o para indicarle a un prompt de IA que el texto traducido nunca exceda de esta longitud. En la longitud se tiene en cuenta que los caracteres se codifican en **utf-8** y pueden llegar a ocupar 2 bytes.


### Automatización con IA
En la traducción a español se usó un procesado en batch usando IA, revisando el resultado iterativamente (siempre se puede mejorar).

Se decidió realizarla en 2 pasos:
- Traducción de inglés a español:
    - Se unificaron todos los ficheros de texto de subtítulos en uno único usando el script **subs/concat_subtitles.py**.
    - Se usó el script `subs/add_text_length.py` para añadir información de longitud de textos.
    - Se usó el prompt [translate-subs-file-spanish.md](../../prompts/translate-subs-file-spanish.md)
- Proceso de abreviación para adaptar la longitud de los textos a la original en inglés:
    - Se usó el script `subs/QA/compare_subtitles_length.py` para obtener un fichero con información de la diferencia de longitud de texto original/traducido.
    - Se usó el promp [abbreviate-subs-file-spanish.md](../../prompts/abbreviate-subs-file-spanish.md)

(Quedó la duda de si se podría haber hecho todo en un único paso)

### QA

Se crearon una serie de scripts en `src/resource/subs` para ayudar en el control de calidad de los subtítulos traducidos.
La calidad de los scripts es pobre (se hicieron rápido y con IA), pero son totalmente funcionales y fueron de mucha utilidad.

**Tratamiento de duplicados**
- `duplicates/manage_duplicated_texts.py`: crea un fichero de subtítulos sin duplicados y un registro indicando textos duplicados. 
- `duplicates/recreate_subtitles_with_dups_registry.py`: regenera un fichero de subtítulos completo usando un registro de duplicados.

**QA**
- `QA/check_sub_file_by_frame_block_sub_id.py`: compara un fichero de subtítulos traducido con el original en inglés para detectar si faltan subtítulos, si se alteraron identificadores...
- `QA/compare_subtitles_length.py`: compara un fichero de subtítulos traducido con el original en inglés para detectar si la longitud del texto traducido es mayor al del texto original.

### Caracteres especiales y texturas de fuentes

En la traducción a un idioma en concreto, hay que tener cuidado con los caracteres especiales que se usan. Para renderizar el texto el juego usa unas texturas donde están todos los caracteres soportados. Hay unas texturas específicas para cada idioma. Los caracteres que no estén presentes en esas texturas no deberían ser utilizados.

- [Inglés](../images/text_eng.png)
- [Español](../images/text_spa.png)
- [Francés](../images/text_fre.png)
- [Alemán](../images/text_ger.png)
- [Japonés](../images/text_jap.png)
- [Coreano](../images/text_cor.png): Creemos que las fuetens coreanas no están soportadas porque las texturas encontradas no contienen caracteres coreanos 😞

Más adelante, explicaremos más de cómo hay que tener en cuenta estas texturas.

### Reemplazo de ficheros de carpeta "subtitles"

Una vez realizada la traducción, si no se ha trabajado directamente sobre los ficheros de la carpeta `output\0\subtitles` (no aconsejado), lo normal es tener un único fichero de texto con todos los literales traducidos, donde cada linea tiene el formato siguiente:

`${número-frame}-{número-recurso}-{id-subtítulo}|{texto}` o bien  
`${número-frame}-{número-recurso}-{id-subtítulo}|..{indicadores de logitud}..|{texto}`

Hay que volver a dividir este único fichero en varios. Para ello se usa el script `subs/split_subtitles.py`:
```
python .\src\resource\subs\split_subtitles_file.py 
Usage: .\src\resource\subs\split_subtitles_file.py <subtitles_file> <output_folder>
```

Le indicaremos como carpeta destino una carpeta temporal, por ejemplo `translated_subtitles_split`. 

```
python .\src\resource\subs\split_subtitles.py subtitles_file.txt  translated_subtitles_split
``` 

Luego se usará el script `subs/replace_sub_files_by_frame_block.pu` para actualizar los subtítulos de la carpeta `output\0\subtitles`:

```
python .\src\resource\subs\replace_sub_files_by_frame_block.py 
Usage: .\src\resource\subs\replace_sub_files_by_frame_block.py <source_folder> <destination_folder>
```

El comando sería así:
```
python .\src\resource\subs\replace_sub_files_by_frame_block.py .\translated_subtitles_split  .\output\0\subtitles
``` 

(Estos 2 pasos sería mejor unificarlos en uno sólo, pero no por ahora está así.)

## 3. Adaptación de texturas de fuentes

En este punto, recordamos que en el paso de [extracción](#1-extracción-de-recursos-internacionalizables) habíamos extraído también los recursos incompletos del idioma al que queremos traducir.

Necesitamos reemplazar los recursos tipo **BIN** y **DDS** del paquete de idioma inglés con los del paquete del idioma a traducir (en este caso el español). Para poder eso usaremos el siguiente script `resource\frames\replace_files_by_resource_id.py`:
```
Uso: .\src\resource\frames\replace_files_by_resource_id.py <carpeta_origen> <carpeta_destino> <extension>
Ejemplo de extensiones: sub, bin, bnk, dds, txt
```

``` 
python .\src\resource\frames\replace_files_by_resource_id.py .\output\5f7991e1f1909a1f\0 .\output\ff715342fa4b2d8f\0 dds
python .\src\resource\frames\replace_files_by_resource_id.py .\output\5f7991e1f1909a1f\0 .\output\ff715342fa4b2d8f\0 bin
``` 

Esto hará que el juego use las texturas de fuentes y mapeado de las mismas correctos para el idioma a traducir.

## 4. Re-empaquetado (repack.py)

Se creó el script `resource/repack.py`:
```
python ./src/resource/repack.py
usage: repack.py [-h] [--packages PACKAGES] extracted_dir original_manifest translation_manifest output_dir
```

Este script permite re-empaquetar los recursos y regenerar el fichero paquete de recursos.

Si ejecutamos:
```
python src\resource\repack.py .\output\ff715342fa4b2d8f ${lone-echo2-game-path}\_data\5932408047\rad16\win10\manifests\ff715342fa4b2d8f ${lone-echo2-game-path}\_data\5932408047\rad16\win10\manifests\5f7991e1f1909a1f .\output\repacked
```

**NOTA**: Se usa `5f7991e1f1909a1f` que corresponde al idioma español. Para otros idiomas habrá que cambiarlo.

En la carpeta `output\repacked` nos generará dos archivos:
- `ff715342fa4b2d8f`
- `ff715342fa4b2d8f_0`

Estos archivos podremos copiarlos donde corresponda en la carpeta de instalación del juego original.
(Se recomienda hacer backup de los originales)