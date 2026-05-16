# Lone Echo 2 Internacionalization  Project

## Introducción

Este proyecto nació con la intención de dar soporte en idioma español al juego Lone Echo 2. Lone Echo 2 es un gran juego y una gran secuela de otro fantástico juego Lone Echo. Su estreno fue a prisa y corriendo con el juego aún sin pulir del todo y con falta de soporte a otros idiomas. Tan sólo audio en inglés y la posibilidad de subtítulos también en inglés.

Se estudiaron los ficheros binarios del juego haciendo ingeniería inversa y se descubrió una manera de poder incrustar subtítulos en otro idioma, al menos en español que era el objetivo inicial del proyecto, pero abierto a poder facilitar los mismos procesos y herramientas para generar subtítulos en otros idiomas.

## Estructura de carpetas del juego
En la carpeta instalada del juego se identificaron las siguientes carpetas y ficheros relevantes:
- `_data\5932408047\rad16\win10`:
    - `\manifests`: ficheros manifiesto de paquetes de recursos del juego. Indexa recursos dentro de los ficheros de paquetes de recursos.
    - `\packages`: ficheros paquetes de recursos del juego. Varios recursos del juego como texturas, ficheros de audio y lo que más nos interesa: subtítulos.
- `bin\win10\scripts`: Varios ficheros DLL, dentro de los cuales se hallaron fragmentos de texto y subtítulos adicionales.

Así pues la idea sería poder extrar textos y subtítulos de esos ficheros, modificarlos y volver a empaquetar los ficheros con los textos traducidos.

## Análisis de los Ficheros 

Se realizaron análisis detallados de los diferentes tipos de ficheros:
  - Ficheros Manifest: [Manifest format](MANIFEST_FORMAT.md)
  - Ficheros Resource Package: [Resource package format](RESOURCE_PACKAGE_FORMAT.md)
  - Ficheros Scripts (DLL): [Script DLL Files](SCRIPT_DLL_FILES.md)

## Proceso y Herramientas de trabajo

Principalmente se optó por la creación de scripts de **Python** para todo el proceso. A continuación se detalla el proceso seguido y las herramientas y escripts usadas en cada caso.

Se recomienda crear un entorno virtual de Python en el workspace del proyecto.

- [Procesado de ficheros de recurso](RESOURCE_PROCESSING.md)
- [Procesado de Scripts (DLL)](SCRIPT_DLL_PROCESSING.md)





