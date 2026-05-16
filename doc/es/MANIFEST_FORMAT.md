
# Formato de Manifest de Lone Echo 2

> ⚠️ **Advertencia:** Este documento se basa en ingeniería inversa.

---

- [Formato de Manifest de Lone Echo 2](#formato-de-manifest-de-lone-echo-2)
  - [Descripción general](#descripción-general)
    - [Manifests](#manifests)
    - [Packages](#packages)
  - [Conceptos](#conceptos)
  - [Cabecera de Manifest](#cabecera-de-manifest)
  - [Contenido binario ZSTD](#contenido-binario-zstd)
  - [Estructura del frame descomprimido](#estructura-del-frame-descomprimido)
    - [1. Índice general](#1-índice-general)
    - [2. Índice 1 de Resource Blocks](#2-índice-1-de-resource-blocks)
    - [3. Índice 2 de Resource Blocks](#3-índice-2-de-resource-blocks)
    - [4. Índice de Data Frames](#4-índice-de-data-frames)
    - [4. Índice de Final Frames](#4-índice-de-final-frames)


---

## Descripción general
El fichero manifest es un archivo comprimido con [Zstandard (ZSTD)](https://facebook.github.io/zstd/). El contenido descomprimido contiene metadatos que indexan recursos del juego almacenados en uno o más ficheros a los que llamaremos packages de datos. Estos packages de datos asociados al manifest también están comprimidos en ZSTD, pero con la particularidad que es multi-frame (contiene fragmentos comprimidos independientes).

### Manifests
En la carpeta `_data\5932408047\rad16\win10\manifests` se encuentran varios ficheros de manifest, cada uno identificado por un valor hexadecimal. Los packages asociados tendrán el mismo nombre pero con el sufo _X indicando el número de package (de 0 a n).

Ficheros manifest de recursos de idioma:

- `ff715342fa4b2d8f`: inglés (completo).
- `5f7991e1f1909a1f`: español (incompleto)
- `a960d5177e5af4ae`: francés (incompleto)
- `a960d5177e5af8bd`: japonés (incompleto)
- `a960d5177e5af6b9`: alemán (incompleto)
- `a960d5177e5af9b3`: coreano (incompleto)

Fichero manifest principal de recursos del juego:
- `6242ff7e5bc499ee`

### Packages
En la carpeta `_data\5932408047\rad16\win10\packages` se encuentran los packages de recursos asociados a los manifest. Tienen como nombre el mismo valor hexadecimal que identifica los manifest, pero incluyendo el sufijo `_X` que indicando el número de package (de 0 a n).

**Paquetes de recursos de idioma**:
- `ff715342fa4b2d8f_0`: inglés (completo).
- `5f7991e1f1909a1f_0`: español (incompleto)
- `a960d5177e5af4ae_0`: francés (incompleto)
- `a960d5177e5af8bd_0`: japonés (incompleto)
- `a960d5177e5af6b9_0`: alemán (incompleto)
- `a960d5177e5af9b3_0`: coreano (incompleto)

Hasta la fecha, sólo el paquete correspondiente al idioma inglés (`ff715342fa4b2d8f_0`) parece estar completo y funcional. Los demás pueden estar incompletos o carecer de ciertos recursos, lo que podría limitar su utilidad o provocar errores si se usan en el juego.

**Paquetes de recursos principal del juego** (10 paquetes):
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

Es importante que el manifest y su fichero de recursos correspondiente coincidan, ya que el manifest actúa como índice de los datos almacenados en el recurso. 

## Conceptos

**Package**: fichero con recursos del juego que consta de múltiples frames. Identificados por un número de 0 a n.
**Package Data Frame**: conjunto de Resource Blocks dentro de un fichero package. Identificados por un número de 0 a n dentro del global del conjunto de packages asociados al manifest.
**Package Final Frame**": frame especial que cierra un package. En sí no contiene resource blocks.
**Resource**: un recurso del juego identificado por un número hexadecimal de 8 bytes. Un mismo recurso puede tener diferentes blocks de datos asociados de diferente tipo (audio, textura, subtítulos...).
**Resource Block**: bloque de datos de un recurso del juego de un tipo determinado (audio, textura, subtítulos...). Vendría identificado por Resource Id. (8 bytes) + Id. Tipo de Resource (8 bytes)

## Cabecera de Manifest
Al principio del fichero manifest hay 24 bytes que no forman parte del contenido ZSTD comprimido. Su estructura es la siguiente:

| Offset | Tamaño | Descripción                                   |
|--------|--------|-----------------------------------------------|
| 0x00   | 4      | Cadena "ZSTD"                                 |
| 0x04   | 4      | Valor 0x10000000 (no identificado)            |
| 0x08   | 8      | Tamaño descomprimido del Manifest (Little Endian) |
| 0x10   | 8      | Tamaño comprimido del Manifest (Little Endian)    |

## Contenido binario ZSTD
Tras la cabecera, comienza el contenido comprimido con ZSTD. Este bloque consta de un solo frame, identificado por el **magic number** `0x28B52FFD` al inicio del bloque comprimido.


## Estructura del frame descomprimido
El frame descomprimido tiene la siguiente estructura general:

### 1. Índice general
    
Una tabla de **200 bytes** son el siguiente formato binario:

| Offset | Tamaño | Descripción |
|--------|--------|-------------|
| 0x0000 | 4      | Número de Packages (Little Endian)|
| 0x0004 | 4      | Valor fijo 0x00000800 |
| 0x0008 | 16     | Valor fijo 0 |
| 0x0018 | 8      | Número de bytes del **Índice 1 de Resource Blocks** (Little Endian) |
| 0x0020 | 8      | Valor fijo 0 |
| 0x0028 | 8      | Valor fijo 0x0000000001000000 | 
| 0x0030 | 8      | Valor fijo 0x2000000000000000 |
| 0x0038 | 8      | Número de Resource Blocks (Little Endian) |
| 0x0040 | 8      | Número de Resource Blocks (Little Endian) |
| 0x0048 | 16     | Valor fijo 0 |
| 0x0058 | 8      | Número de bytes del **Índice 2 de Resource Blocks**(Little Endian) |
| 0x0060 | 8      | Valor fijo 0 |
| 0x0068 | 8      | Valor fijo 0x0000000001000000 | 
| 0x0070 | 8      | Valor fijo 0x2000000000000000 |
| 0x0078 | 8      | Número de Resource Blocks (Little Endian) |
| 0x0080 | 8      | Número de Resource Blocks (Little Endian) |
| 0x0088 | 16     | Valor fijo 0 |
| 0x0098 | 8      | Número de bytes de la suma de los índices **Índice de Data Frames** + **Índice de Final Frames** (Little Endian) |
| 0x00A0 | 8      | Valor fijo 0 |
| 0x00A8 | 8      | Valor fijo 0x0000000001000000 | 
| 0x00B0 | 8      | Valor fijo 0x2000000000000000 |
| 0x00B8 | 8      | Número de Frames (Little Endian) | 
| 0x00C0 | 8      | Número de Frames (Little Endian) |

**Observaciones**:
- Tanto número de Resource Blocks como número de Frames hacen referencia a la suma de los existentes en el conjunto de Packages.
- En los indicadores de número de frames se cuentan los **Data Frames** y **Final Frames** de todos los package. 

### 2. Índice 1 de Resource Blocks

Una tabla con una entrada de **32 bytes para cada Resource Block** con el siguiente formato binario:
    
| Offset | Tamaño | Descripción |
|--------|--------|-------------|
| 0x00   | 8      | Tipo de Resource Block (ver tabla) |
| 0x08   | 8      | ID de Resource |
| 0x0C   | 4      | Número de Data Frame (Little Endian) (Valor de 0 a n) |
| 0x10   | 4      | Offset inicial dentro del Data Frame (Little Endian) |
| 0x14   | 4      | Tamaño en bytes del Resource (Little Endian) |
| 0x18   | 4      | Valor desconocido |

**Observaciones**:
- La tabla está agrupada por tipo de resource, mostrando siempre los recursos de un mismo tipo de forma continua, pero se desconoce el orden usado.
- El número de frame es global para todos los packages. (No se inicia a 0 al inicio de cada package)
- Puede haber más de un Block para un mismo Resource. Esto pasa por ejemplo con recursos de tipo BNK que tienen ademas asociados tipos BIN no identificados.

**Tipos de Resource Block**:
- Presentes en package de recursos de idiomas:
    - `0x02db12a32f783bef`: SUB (Textos de subtítulos: diálogos, objetivos, pero no incluye diálogos de la tablet)
    - `0x61887bcb6919acbe`: DDS (Texturas: mapas de caracteres)
    - `0x985ab87bef8e356d`: BNK (Bancos de audio: diálogos)
    - `0xa0b80093c4324c4a`: BIN (No identificado: posible mapeo de caracteres a texturas)
    - `0xdcf039b76eda705e`: BIN (No identificado: posible mapeo de caracteres a texturas)
- Algunos presentes en package principal de recursos del juego (hay muchísimos) y no identificados:
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

### 3. Índice 2 de Resource Blocks

Una tabla con una entrada de **40 bytes para cada Resource Block** con el siguiente formato binario:

| Offset | Tamaño | Descripción |
|--------|--------|-------------|
| 0x00   | 8      | Tipo de Resource Block (ver tabla) |
| 0x08   | 8      | ID de Resource |
| 0x0C   | 20     | Valor desconocido |
| 0x14   | 4      | Valor desconocido |

**Observaciones**:
- La tabla está agrupada por tipo de resource, mostrando siempre los recursos de un mismo tipo de forma continua, pero se desconoce el orden usado.


### 4. Índice de Data Frames

Una tabla con una entrada de **16 bytes para cada Data Frame** de cada Package de  con el siguiente formato binario:

| Offset | Tamaño | Descripción |
|--------|--------|-------------|
| 0x00   | 4      | Número de Package (Little Endian)  (de 0 a n) |
| 0x04   | 4      | Offset con acumulado del tamaño comprimido de Data Frames de ese package (Little Endian) (Valor 0 al inicio de cada package)|
| 0x08   | 4      | Tamaño comprimido del Data Frame (Little Endian) |
| 0x0C   | 4      | Tamaño descomprimido del Data Frame (Little Endian) |

**Observaciones**:
- La tabla está ordenada de forma creciente por número de Package y offset acumulado de cada Data Frame.

### 4. Índice de Final Frames

Una tabla con una entrada de **16 bytes para cada Final Frame** de cada Package con el siguiente formato binario:
| Offset | Tamaño | Descripción |
|--------|--------|-------------|
| 0x00   | 4      | Número de Package (Little Endian)  (de 0 a n) |
| 0x04   | 4      | Tamaño total comprimido de todos los Data Frames de ese Package (Little Endian)|
| 0x08   | 8      | Desconocido, pero hace que funcionen las fuentes propias del idioma|

**Observaciones**:
- Cada Package tiene 1 Final Frame.
- La tabla está ordenada de forma creciente por número de Package.

    
