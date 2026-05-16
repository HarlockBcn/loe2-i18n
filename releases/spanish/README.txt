Versión
-------
v2.1.1

Instrucciones de instalación
----------------------------

1. Descarga la herramienta de parcheo open-source HDiffPatch para Windows: https://github.com/sisong/HDiffPatch/releases

2. Extrae la utilidad "hpatchz.exe"

3. Ve a la carpeta del juego donde tengas instalado el juego:

   Por ejemplo, "OculusLibrary\Software\ready-at-dawn-lone-echo-2"

4. Copia en esa carpeta los archivos del mod y la utilidad de parcheo:

    hpatchz.exe
    scripts_spa.diff
    f715342fa4b2d8f_spa.diff
    ff715342fa4b2d8f_0_spa.diff
 
5. Si no tienes instalado ya el mod en el juego, haz una copia de seguridad de los siguientes ficheros y carpetas originales del juego:
   (IMPORTANTE: Si estás actualizando el mod, ya deberías haber hecho esta copia de seguridad. Sáltate este paso)

    En "bin\win10": renombra la carpeta scripts a scripts.bak
    En "_data\5932408047\rad16\win10\manifests": renombra el fichero ff715342fa4b2d8f a ff715342fa4b2d8f.bak
    En "_data\5932408047\rad16\win10\packages": renombra el fichero ff715342fa4b2d8f_0 a ff715342fa4b2d8f_0.bak
    
6. Abre un terminal de Windows en la carpeta del juego y ejecuta los siguientes comandos de parcheo:

    .\hpatchz.exe bin\win10\scripts.bak scripts_spa.diff bin\win10\scripts
    .\hpatchz.exe _data\5932408047\rad16\win10\manifests\ff715342fa4b2d8f.bak ff715342fa4b2d8f_spa.diff _data\5932408047\rad16\win10\manifests\ff715342fa4b2d8f
    .\hpatchz.exe _data\5932408047\rad16\win10\packages\ff715342fa4b2d8f_0.bak ff715342fa4b2d8f_0_spa.diff _data\5932408047\rad16\win10\packages\ff715342fa4b2d8f_0

    NOTA: Si estás aplicando una actualización del mod, deberás antes borrar los ficheros ff715342fa4b2d8f, ff715342fa4b2d8f_0 y carpeta scripts (asegúrate antes de tener las versiones backup .bak)

7. Ahora puedes iniciar el juego.

8. Siempre puedes restaurar el juego a su estado original eliminando la carpeta y archivos modificados y restaurando la copia de seguridad (eliminando la extensión .bak).


Historial de cambios
--------------------

- V2.1.1: Corregida visualización de descripciones en tableta en sección "detalles de datos".
- v2.1: Corregidos saltos de linea en algunos textos y textos más acortados para que no se encole tanto texto en el motor de subtítulos.


Características principales
---------------------------

La gran mayoría de los subtítulos han sido traducidos: diálogos, textos y mensajes de diálogo en la tableta, registros de audio, objetivos de misión, etc.

QA
--

El juego con el mod parece ser muy estable —y digo "parece" porque aún no se ha probado con una partida de inicio a fin—. Cualquier comentario sobre errores o problemas que se encuentren se agradecerá.
Estad atentos a actualizaciones del mod que se pueden ir produciendo corrigiendo fallos detectado y no dudéis en preguntar o informar por problemas o errores encontrados.

Problemas reportados
--------------------

    - El proceso ha sido complejo, y es probable que se hayan pasado por alto algunos detalles en la traducción. Además, dado el enorme volumen de texto a traducir, se decidió utilizar IA para automatizar el proceso, aunque se hizo todo lo posible por entrenar correctamente el sistema y supervisar de cerca el trabajo.
    - El motor de visualización de subtítulos del juego no es muy eficaz durante diálogos largos y rápidos, ya que las frases se amontonan y no se muestran a la velocidad adecuada. No hemos podido resolver esto, y es un problema que ya ocurre con los subtítulos originales.
    - En muchos casos, los subtítulos han tenido que acortarse para que se ajusten lo máximo posible a la duración del diálogo en inglés, evitando así que se acumulen demasiadas líneas en el motor de subtítulos esperando a mostrarse.
    - En el caso del español, pueden producirse errores de género en algunas traducciones, ya que no fue posible extraer el contexto de los subtítulos, como qué personaje está hablando o si se refiere a un masculino o femenino.

Requisitos
----------

Por supuesto, necesitarás tener el juego original Lone Echo 2.

Agradecimientos
---------------
A todo el equipo de Ready At Dawn: ¡GRACIAS por estas dos joyas de juegos. ¡Sois increíbles!

Saludos a toda la comunidad hispana de Lecitron VR, y un agradecimiento especial a Ari, uno de sus miembros, por ayudar con la traducción asistida por IA.

Y gracias a todos los que desarrollan y/o compran juegos de VR, apoyando esta plataforma, con la esperanza de que siga creciendo y seguir recibiendo grandes juegos como la saga Lone Echo. Por desgracia, la situación es complicada ahora mismo, y prueba de ello es cómo se lanzó este juego —sin estar completamente pulido ni traducido—, pero no nos rendiremos: ¡LA VR SOBREVIVIRÁ!


Contacto
--------

email: harlockbcn@gmail.com