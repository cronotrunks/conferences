The Ubuntu Package ubuntu-express
---------------------------------

El instalador de Guadalinex se ha caracterizado hasta ahora por ser muy
sencillo, amigable y gráfico.1)

Para esta versión desarrollaremos un instalador nuevo, aún más potente, usando
como lenguaje Python

Haremos especial incapié en el proceso de particionado, para que sea tan
automático y seguro como sea posible.


Especificaciones
================

Introducción
------------

El instalador de Guadalinex2005 Live será un instalador sencillo, bien
integrado con el sistema Debian y compatible con Ubuntu.


Casos de uso
------------

    * Un usuario arranca la Guadalinex2005, le gusta y la quiere tener
instalada, tal cuál, en su ordenador.
    * Un usuario arranca la Guadalinex2005, le gusta, la prueba, la configura
y la quiere tener instalada, con esas configuraciones hechas, en su ordenador.
    * Un usuario ha probado la Guadalinex2005, sabe que le gusta y que la
quiere instalar, pero ni quiere ni necesita arrancar la distro completa (con
su escritorio y demás), sólo instalarla de manera rápida y sencilla.
    * Un usuario ha instalado la Guadalinex2005 desde su versión Live y quiere
poder tener un archivo de configuración con las opciones elegidas, por si
necesita reinstalar o para instalar en equipos parecidos.


Precondiciones
--------------

(Condiciones que han de darse antes de usar el instalador)

    * El instalador debe estar en un sistema live
    * Debe existir una imagen de la distribución en:
/cdrom/casper/filesystem.cloop o /cdrom/META/META.squashfs.
    * Deben estar instalados en la distribución (en la imagen) Python, sus
librerias para debconf y las necesarias para la interfaz de usuario que se
vaya a usar (gráfica o no gráfica).


Postcondiciones
---------------

(Condiciones que han de darse después de usar el instalador)

    * Disco particionado con una partición para la distribución y una para la
swap (partición de intercambio), como mínimo.
    * Partición de la distribución formateada.
    * Copiada la distribución de la imagen a la partición formateada para tal
fin.
    * Hardware configurado.
    * Un usuario creado.
    * Idioma, teclado, red y nombre de la máquina configurados.
    * Detectados otros sistemas operativos existentes y añadidos al Grub y al
fstab.
    * El sistema instalado debe estar configurado a la Debian, como desde el
debian-installer.
    * Si se configura algo(red, idioma, hora, tecaldo, X, sonido, etc) en la
sesión Live, debe estar configurado en la versión instalada.
    * Deben generarse unos logs bien completos para poder depurar.
    * Debe generarse un archivo con las configuraciones seleccionadas, para en
caso de querer reinstalar, poder hacerlo de forma automatizada.


Puntos a destacar
-----------------

    * Se debe preguntar lo mínimo.
    * Debe ser posible personalizarlo.
    * Debe soportar diferentes interfaces de usuarios: gráfica (Gtk+, Qt,
etc), no gráfica e incluso no interactiva.
    * No usar archivos de configuración, sino debconf y convenciones de
nombres.
    * Se debe informar al usuario de manera clara y sencilla de lo que está
pasando en cada momento.
    * Ha de ser posible preconfigurar (preseed) toda o parte de la información
necesaria para la instalación.
    * Si la información de un diálogo está preconfigurada (preseed), no se
mostrará ese diálogo.
    * Ha de ser posible instalar el HOME en una partición aparte.
    * La opción predeterminada para el particionado debe ser el particionado
automático.
    * No se ofrecerán opciones que no se pueden hacer (ej: autoparticionado).
    * Se debe poder internacionalizar.
    * Debe poder respetar los datos y sistemas operativos existentes en el
disco antes de instalar.
    * Se ha de poder redimensionar una partición, con espacio suficiente, si
no hay espacio sin particionar disponible en el disco.


Secuencia
---------

   1. Saludos e información de lo que va a pasar.
   2. Nombre completo, nickname y clave del de usuario. Nombre del equipo.
   3. Particionado.
   4. Barra de progreso (formateo, copia de la distro y configuración)
   5. Despedida.


Dependencias
------------

    * Una distribución live basada en Ubuntu o en Metadistros.
    * Gparted.
    * partman.
    * Python.
    * Paquete de Debconf, express[1], cargado por el sistema Live.
    * Detección y notificación en el sistema live del estado de la red.


Debatir
=======

Puntos
------

   1. Partición de /home separada.
   2. Posibilidad de guardar las selecciones de una instalación.
   3. Posibilidad de añadir módulos en tiempo real.
   4. Eliminación de los diálogos de idioma y de la red.
   5. Limitaciones en la longitud del nombre de usuario, de la contraseña y
del nombre del equipo. (Provisionalmente: nombre de usuario entre 3 y 24
carateres; contraseña entre 4 y 16 caracteres; nombre del computador entre 3 y
18 caracteres).
   6. Qué hacer con las posibles cuentas de usuario creadas durante la sesión
live. (Básicamente, hay 3 posibilidades: ignorarlas, mantenerlas machacando el
/home/ correspondiente con /etc/skel/, o bien mantener tanto la cuenta como
los archivos del usuario).

(el debate se desarrolla en las Listas de Distribución)


Conclusiones
------------

   1. No hay problema para hacer ésto y además facilita la migración a nuevas
versiones.
   2. Se guardarán las configuraciones elegidas durante la instalación en un
archivo.
   3. Este punto hay que aclararlo un poco más.
   4. El del idioma y demás no afecta a Guadalinex. Sobre el de la red se ha
dicho que esta opción va en la línea de aumentar la usabilidad, aunque todavía
no se he decidido nada.

[1] Esto no sería más que una plantilla de debconf con las preguntas y
respuestas necesarias para preconfigurar (preseed) el instalador

--
Javier Carranza <javier.carranza@interactors.coop>, Fri, 29 Jul 2005 17:04:51 +0200
