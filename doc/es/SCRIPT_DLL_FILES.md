# Ficheros Script DLL

> ⚠️ **Advertencia:** Este documento se basa en ingeniería inversa.

---

Se analizaron los ficheros DLL presentes en la carpeta `bin\win10\scripts` del juego y se descubrió que allí se guardan algunos literales del juego que no están presentes en los ficheros de recursos internacionalizables del juego.

Al tratarse de ficheros DLL binarios, se tuvo que hacer ingeniería inversa analizando el contenido de binario, identificando patrones para poder hacer una búsqueda y reemplazo de los literales de texto deseados.

Se encontró el siguiente patrón: 
- Se busca en las secciones `.rdata`, `.text` y `.data`de la DLL.
- Todos los textos encontrados entre los 2 siguientes textos, serán los candidatos a traducir:
    - Texto marca de Inicio: `Blocking node (%%08x) used in Initialize thread`
    - Texto marca de Fin: `Node (%08x) had no execute function`

**Limitación**: Hay que tener en cuenta que en este caso estamos limitados a sobreescribir los textos sin llegar a ocupar más de lo que ocupa su versión en idioma original. Si son más cortos, no hay problema, siempre que se añada un byte `0x00` al final del texto.
