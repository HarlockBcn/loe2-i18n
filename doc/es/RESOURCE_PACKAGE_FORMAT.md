# Formato de Resource Package de Lone Echo 2

> ⚠️ **Advertencia:** Este documento se basa en ingeniería inversa.

- [Formato de Resource Package de Lone Echo 2](#formato-de-resource-package-de-lone-echo-2)
  - [Descripción general](#descripción-general)
  - [Conceptos](#conceptos)
  - [Estructura multi-frame](#estructura-multi-frame)
  - [Estructura del frame descomprimido](#estructura-del-frame-descomprimido)
    - [Texturas (DDS)](#texturas-dds)
    - [Bancos de audio (BNK)](#bancos-de-audio-bnk)
      - [Encabezado especial del bloque](#encabezado-especial-del-bloque)
      - [Banco de audio en formato BNK (Wwise SoundBank)](#banco-de-audio-en-formato-bnk-wwise-soundbank)
    - [Binario no identificado (BIN) en fichero de recursos de idioma](#binario-no-identificado-bin-en-fichero-de-recursos-de-idioma)
    - [Subtítulos (SUB)](#subtítulos-sub)
      - [Formato binario propietario de subtítulos](#formato-binario-propietario-de-subtítulos)
      - [Literales de los subtítulos](#literales-de-los-subtítulos)
  - [Limitaciones conocidas](#limitaciones-conocidas)


---

## Descripción general
Los Package de recursos del juego son ficheros binarios comprimidos en formato ZSTD multi-frame. En ellos se almacenan diferentes tipos de datos de recursos del juego como subtítulos, texturas, bancos de audio, etc.

## Conceptos

**Package**: fichero con recursos del juego que consta de múltiples frames. Identificados por un número de 0 a n.
**Package Data Frame**: conjunto de Resource Blocks dentro de un fichero package. Identificados por un número de 0 a n dentro del global del conjunto de packages asociados al manifest.
**Package Final Frame**": frame especial que cierra un package. En sí no contiene resource blocks.
**Resource**: un recurso del juego identificado por un número hexadecimal de 8 bytes. Un mismo recurso puede tener diferentes blocks de datos asociados de diferente tipo (audio, textura, subtítulos...).
**Resource Block**: bloque de datos de un recurso del juego de un tipo determinado (audio, textura, subtítulos...). Vendría identificado por Resource Id. (8 bytes) + Id. Tipo de Resource (8 bytes)

## Estructura multi-frame
Los diferentes Data Frames del paquete de recursos son identificables fácilmente gracias a que todos empiezan con un **magic number** de valor `0x28B52FFD`. Cada uno de estos Data Frames encabezados por ese **magic number** se puede tratar como un fichero binario comprimido en formato ZSTD.
De esta manera, se puede dividir el paquete en varios ficheros/frames para procesarlos independientemente.

## Estructura del frame descomprimido
El contenido binario del Data Frame descomprimido puede contener uno o más Resource Blocks, del mismo tipo o diferentes. El contenido binario de estos recursos está concatenado uno detrás de otro.

Se han identificado los siguientes tipos de recursos:

- **Texturas (DDS)**
- **Bancos de audio (BNK)**
- **Subtítulos (SUB)**
- **Otros tipos de recursos desconocidos (BIN)**

### Texturas (DDS)
Si los 4 primeros bytes tienen el valor `0x44445320` correspondientes al string "DDS ", en ese punto empieza un contenido binario relacionado con texturas. Acabará donde empiece otro recurso del mismo o diferente tipo o si el fichero acaba.
Seguramente DDS se refiere a **Microsoft Direct Draw Surface** y esos 4 primeros bytes sean el inicio de la cabecera descrita así:

| Offset (byte) | Tamaño | Campo                   |
| ------------- | ------ | ----------------------- |
| 0             | 4      | Magic "DDS "            |
| 4             | 4      | Tamaño del header (124) |
| 8             | 4      | Flags                   |
| **12**        | 4      | **Height (alto)**       |
| **16**        | 4      | **Width (ancho)**       |
| 20            | 4      | Pitch o Linear Size     |
| 24            | 4      | Depth                   |
| 28            | 4      | Mipmap count            |
| ...           | ...    | Otros campos            |
| 76            | 32     | DDS_PIXELFORMAT         |
| 108           | 16     | Caps                    |
| 124           | 4      | Reserved                |

Usa formato Little-Endian.
Si fuera necesario, se podría buscar información de cómo calcular el tamaño de un bloque de texturas DDS.

### Bancos de audio (BNK)
Si encontramos 16 bytes que tienen el valor `0x424B4844` correspondientes al string "BKHD", quiere decir que se trata de un banco de audio.
El bloque de datos no empieza ahí, sino 16 bytes antes con un encabezado especial que se usa para indicar el tamaño del banco de audio.

Este banco de audio se corresponde con el formato BNK (Wwise SoundBank) y esos primeros 16 bytes con los de una cabecera "BKHD". En este formato se usa formato Little-Endian.

El bloque de datos que contiene banco de audio acaba con un separador especial de 8 bytes.

#### Encabezado especial del bloque
16 bytes que indican el tamaño del banco de audio. Por ejemplo, el valor `0xBD310400000000000000000000000000` indicaría un tamaño de 2,474,877 bytes. Ese tamaño incluye la cabecera desde "BKHD" + DIDX + DATA + HIRC. El bloque de banco de audio finaliza con un separador final que no se tiene en cuenta en ese tamaño.

#### Banco de audio en formato BNK (Wwise SoundBank)
**Cabecera del Banco (BNK):**
- 4 bytes: Marca "BKHD". Indica el inicio de un banco de audio Wwise BKHD. En hexadecimal `0x424B4844`.
- Tamaño de la sección del header: 4 bytes que indican el tamaño de la sección de header sin contar los 4 bytes anteriores "42 4B 48 44". Por ejemplo, en hexadecimal `0x1C000000` serían 28 bytes.
- Versión del formato: 4 bytes que indican la versión del formato. Por ejemplo `0x86000000`.
- Bank ID: 4 bytes identificadores del banco de audio. Por ejemplo `0x363C4C8E`.
- Desconocido/Padding: El resto de bytes hasta completar el indicado por el tamaño de la sección del header.

**Índice de Contenidos (DIDX):**
- Cabecera de DIDX: 4 bytes, en hexadecimal `0x44494458` ("DIDX")
- Tamaño de la tabla de contenido: 4 bytes indicando el tamaño de la tabla de contenido, por ejemplo `0xCC000000` en hexadecimal que indicaría 204 bytes.
- Estructura de la tabla: Cada archivo dentro del banco ocupa 12 bytes en esta sección con el siguiente orden (Little Endian):
    - ID del archivo (4 bytes): Ej. "48 FD 32 0E"
    - Offset/Posición (4 bytes): Dónde empieza el audio dentro de la sección DATA.
    - Tamaño (4 bytes): Cuánto ocupa ese audio.

**Contenedor de datos (DATA):**
- Cabecera de DATA: 4 bytes, en hexadecimal `0x44415441` ("DATA")
- Tamaño total de todos los audios combinados: 4 bytes que indican el tamaño total en bytes de todos los audios. Por ejemplo `0x8A250400` en hexadecimal little endian indicaría 271,754 bytes en total.
- A partir de aquí tendremos una serie de entradas "RIFF/WAV" que cada una empieza con los bytes "52 49 46 46".

**HIRC:**
- 4 bytes `0x48495243` que corresponden a "HIRC".
- Tamaño de firma: 4 bytes en little endian que indican el tamaño de la firma.
- Contenido de la firma: una serie de bytes del tamaño indicado anteriormente correspondientes al contenido de la firma.

**Separador final del bloque:**
- Separador: 4 bytes con el valor `0x00000000`.
- Bank ID: 4 bytes que coinciden con el identificador del banco de audio indicado anteriormente (Bank ID).

### Binario no identificado (BIN) en fichero de recursos de idioma
Se han identificado bloques binarios de 256 bytes que pueden ir apareciendo dentro del binario. En concreto estos dos con estos valores (256 bytes cada uno):
- `0xFFFF...FFFF01000000000200000002000001000000010000000000000057000000000000000100000000000000000200000002000001000000940010000008000000000000`
- `0xFFFF...FFFF0100000000020000000200000100000001000000000000003D000000000000000100000000000000000200000002000001000000940004000002000000000000`

Algunos de estos bloques binarios se sospecha que configuran el mapeo de caracteres a algunas texturas que contienen las fuentes de texto del juego.

### Subtítulos (SUB)
Si el bloque de datos no cumple las anteriores condiciones, se tratará seguramente de un bloque que contiene subtítulos.

#### Formato binario propietario de subtítulos
El formato binario de los subtítulos es el siguiente, con todos los valores en formato Little-Endian:

- **Ids:**
    - Número de identificadores: 4 bytes que indican el número de identificadores. Uno para cada subtítulo.
    - Identificadores: 8 bytes (`uint64`) dedicados para cada valor de identificador.
- **Subtítulos:**
    - Número de subtítulos: 4 bytes que indican el número de subtítulos.
    - Offsets de subtítulos: para cada subtítulo se indica su offset inicial con 4 bytes (empezando por `0x00000000`) que corresponde al primer subtítulo. Al final hay un offset adicional para saber el tamaño del último subtítulo.
    - Literales de los subtítulos: tenemos los strings de los subtítulos concatenados. Cada subtítulo acaba con el carácter en hexadecimal `0x00`.

#### Literales de los subtítulos
- Algunos literales contienen variables que son procesadas por el juego. Esas variables no se deberían traducir. El formato de estas variables es: `[@VAR]`.

## Limitaciones conocidas

- El análisis se basa en ingeniería inversa y puede contener errores o suposiciones incorrectas.
- No todos los campos y estructuras están completamente identificados.
- Algunos recursos y posibles paddings no han podido ser interpretados con certeza.
