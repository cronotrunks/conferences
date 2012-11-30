#! /bin/sh
# Crea el archivo menu.lst de GRUB para su sistema
# Copyright (C) 2002 A.Ullán-J.L.Redrejo.
#
# This file is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#

# Algunas funciones de log
# Libreria para depuracion y salidas de error

DEBUG=1
DEBUGFILE="/tmp/debug.log"
ERRORFILE="/tmp/error.log"

debug()
{
        ret=$?
        MSG=$1
        TIME=`timestamp`
        if [ $DEBUG -eq 1 ]; then
                echo "DEBUG $TIME: $MSG" >> $DEBUGFILE
        fi
        return $ret
}

error()
{
        ret=$?
        MSG=$1
        debug "ERROR: $MSG"
        TIME=`timestamp`
        echo "ERROR $TIME: $MSG" >> $ERRORFILE
        return $ret
}

fatal()
{
        MSG=$1
        debug "FATAL: $MSG"
        TIME=`timestamp`
        echo "FATAL $TIME: $MSG" >> $ERRORFILE
        exit 1
}

timestamp()
{
        ret=$?
        date +"%d/%m %H:%M:%S"
        return $ret
}

# Versión del núcleo de la distro
KERNEL_VERSION=`uname -r`

# Nombre de la distro
DISTRO="Guadalinex"

# Primero ver si está instalado GRUB, busca el directorio
if [ -d /boot/grub ]; then
        :
else
	debug "Creamos dir /boot/grub"
	mkdir -p /boot/grub/
	grub --batch --device-map=/boot/grub/device.map <<EOT
quit
EOT
fi

# empieza el trabajo de localizar discos, particiones y sistemas
###########################################################
for i in {a,b,c,d,e,f,g};
 do
	DISCO=hd$i
	esta=`grep $DISCO /boot/grub/device.map | cut -c12-14`
	if [ -z "$esta" ]; then :
	else 
		fdisk -l /dev/$DISCO | grep ^/dev/ >> /tmp/salfdisk
	fi
done

# SCSI
for i in {a,b,c,d,e,f,g};
 do
	DISCO=sd$i
	esta=`grep $DISCO /boot/grub/device.map | cut -c12-14`
	if [ -z "$esta" ]; then :
	else fdisk -l /dev/$DISCO | grep ^/dev/ >> /tmp/salfdisk
	fi
 done

########################
# función para convertir las unidades y particiones en
# formato GRUB. uso: convierte tipo disco parte
TIPOL=""
DISCOL=""
PARTIL=""
convierte () {
# Ahora el nombre en formato GRUB
  DRIVE=$1$2
  NUMERO=`grep $DRIVE /boot/grub/device.map | cut -c2-4`
  let PART=$3-1
  NOMBRE="(${NUMERO},${PART})"
if [ "$1" = "sd" ]; then INFORME="SCSI"
	else INFORME="IDE"
fi
}
# fin de funcion
#
# lineas para LinEx
debug "Borramos antiguo menu.lst"
rm -f /boot/grub/menu.lst
SOS=1
echo "
default 0
timeout 1
fallback 1
" >> /boot/grub/menu.lst

# veamos Linux
TIPOL=`echo $1 | cut -c6-7`
DISCOL=`echo $1 | cut -c8-8`
PARTIL=`echo $1 | cut -c9-9`

convierte "$TIPOL" "$DISCOL" "$PARTIL"

nucleo="/boot/vmlinuz-$KERNEL_VERSION"
debug "El nucleo activo sera el $nucleo"

echo "
splashimage=$NOMBRE/boot/grub/splash.xpm.gz" >> /boot/grub/menu.lst

PARAMS=" ro auto quiet splash"

echo "
title $DISTRO, kernel $KERNEL_VERSION
root $NOMBRE
kernel $nucleo root=/dev/${TIPOL}${DISCOL}${PARTIL} ${PARAMS}
initrd /boot/initrd.img-$KERNEL_VERSION
savedefault
boot" >> /boot/grub/menu.lst

echo "
title $DISTRO, kernel $KERNEL_VERSION (recovery mode)
root $NOMBRE
kernel $nucleo root=/dev/${TIPOL}${DISCOL}${PARTIL} ro auto single
initrd /boot/initrd.mag-$KERNEL_VERSION
savedefault
boot" >> /boot/grub/menu.lst

echo "
title           Guadalinex, memtest86+
root            $NOMBRE
kernel          /boot/memtest86+.bin
boot" >> /boot/grub/menu.lst



#
# lineas de WIN
win () {
	let SOS=SOS+1
	echo "##########################
title $TITULO en Disco $INFORME $TIPOD$DISCO$PARTI $TIPOP
rootnoverify $NOMBRE
makeactive
chainloader +1 " >> /boot/grub/menu.lst
}
# fin de la función win

#
# otros sistemas operativos
otros_so () {
	# uso: otros_so linea_de_fichero_dev/XXXX
	# empezamos con los Win en FAT32
	TIPOD=`cat $1 | grep W  | grep FAT32 | cut -c6-7`
	DISCO=`cat $1 | grep W  | grep FAT32 | cut -c8-8`
	PARTI=`cat $1 | grep W  | grep FAT32 | cut -c9-9`
	TIPOP=FAT32
	[ ! -d /tmp/mnt ] && mkdir /tmp/mnt
	if [ -z $DISCO ]; then :
        else
		debug "Encontrada particion Windows FAT32"
		convierte "$TIPOD" "$DISCO" "$PARTI"
		debug "Montamos /dev/$TIPOD$DISCO$PARTI en /tmp/mnt"
		mount -o ro /dev/"$TIPOD""$DISCO""$PARTI" /tmp/mnt 2>>/tmp/mount-error.log
		check_mount 

		if [ -f /tmp/mnt/boot.ini ]; then
			BUSCA=`cat /tmp/mnt/boot.ini | grep Windows | grep XP`
			if [ -z "$BUSCA" ]; then
				TITULO="WINDOWS 2000 "
				win
			else
				TITULO="WINDOWS XP "
				win
			fi
                elif [ -f /tmp/mnt/autoexec.bat ]; then
				TITULO="WINDOWS 9X"
				win
                fi
		umount /tmp/mnt
	fi
	# Win en NTFS
	#
	TIPOD=`cat $1 | grep NTFS | cut -c6-7`
	DISCO=`cat $1 | grep NTFS | cut -c8-8`
	PARTI=`cat $1 | grep NTFS | cut -c9-9`
	TIPOP=NTFS
	if [ -z $DISCO ]; then :
        else
		debug "Encontrada particion Windows NTFS"
		convierte "$TIPOD" "$DISCO" "$PARTI"
		debug "Montamos /dev/$TIPOD$DISCO$PARTI en /tmp/mnt"		
		mount -o ro /dev/"$TIPOD""$DISCO""$PARTI" /tmp/mnt 2>>/tmp/mount-error.log
		check_mount
		if [ -f /tmp/mnt/boot.ini ]; then
			BUSCA=`cat /mnt/mnt/boot.ini | grep Windows | grep XP`
                        if [ -z "$BUSCA" ]; then
				debug "Encontrado fichero boot.ini -> Win 2000"
				TITULO="WINDOWS 2000 "
				win
                        else
				debug "No existe el fichero boot.ini -> Win XP"
				TITULO="WINDOWS XP "
				win
                        fi
                fi
		umount /tmp/mnt
	fi
	#
	# otros linux
	#
	TIPOD=`cat $1 | grep Linux | grep 83 | cut -c6-7`
	DISCO=`cat $1 | grep Linux | grep 83 | cut -c8-8`
	PARTI=`cat $1 | grep Linux | grep 83 | cut -c9-9`
	if [ -z $DISCO ]; then :
	else
		debug "Encontradas particiones Linux"
		TMPMOUNT=/tmp/mnt
		convierte "$TIPOD" "$DISCO" "$PARTI"
		debug "Montamos /dev/$TIPOD$DISCO$PARTI en /tmp/mnt"		
		mount -t ext2 -o ro /dev/"$TIPOD""$DISCO""$PARTI" $TMPMOUNT 2>>/tmp/mount-error.log
		check_mount
		if [ -d $TMPMOUNT/boot ]; then
			ls $TMPMOUNT/boot | grep vmlinuz > /tmp/ficheros
			debug "Kernels encontrados:"
			debug `cat /tmp/ficheros`

			nfilas=`wc -l /tmp/ficheros | cut -c1-2`

			#Lin: no sabemos para que se hizo esto
			#nfilas=`sed -n 1,1p  /tmp/filas | head --bytes=1`

		for i in `seq 1 $nfilas`;
		do
			sed -n "$i","$i"p /tmp/ficheros > /tmp/fila
			KERNEL=`cat /tmp/fila`
			NUMERACION=`cat /tmp/fila | cut -c8-22`
			if [ -f $TMPMOUNT/boot/initrd.img"$NUMERACION" ]; then
				LINEA2="initrd /boot/initrd.img"$NUMERACION""
			fi

			otrolinux
        	done
		fi
		umount $TMPMOUNT
	fi
}
#
otrolinux () {
	let SOS=SOS+1
	echo "
title Linux en Disco $INFORME "$TIPOD""$DISCO""$PARTI" Kernel"$NUMERACION"
root $NOMBRE
kernel /boot/$KERNEL root=/dev/"$TIPOD""$DISCO""$PARTI"
$LINEA2
savedefault
boot " >> /boot/grub/menu.lst
}

# comprueba si el montaje ha sido exitoso
check_mount () {
	if [ $? -ne 0 ]; then
		debug "Error al montar el dispositivo: ver /tmp/mount-error.log para mas detalles"
		error "Error al montar el dispositivo: ver /tmp/mount-error.log para mas detalles"
	fi
}

#
############################################################3
# trabajo con salfdisk
# FIXME HE CAMBIADO el wc -l por wc (teo & marti & dani)
#wc /tmp/salfdisk | cut -c6-7 > /tmp/lineas
nlineas=`cat /tmp/salfdisk |wc -l`
#nlineas=`sed -n 1,1p  /tmp/lineas | head --bytes=2`
for i in `seq 1 $nlineas`;
    do
        sed -n "$i","$i"p /tmp/salfdisk > /tmp/linea

        PRIMEROS=`cat /tmp/linea | head -c9`
        if [  "$PRIMEROS" = "/dev/"$TIPOL""$DISCOL""$PARTIL"" ]; then :
        else
            PRIMEROS=`cat /tmp/linea | head -c5`
            if [ "$PRIMEROS" = "/dev/" ]; then
	    	debug "Detectada particion No Linux. Vemos que tipo es..."
	    	otros_so /tmp/linea
            fi
        fi
    done

if [ "$SOS" -gt 1 ]; then
	sed -e 's/timeout 1/timeout 10/g' /boot/grub/menu.lst > /tmp/menut.tmp
	mv -f /tmp/menut.tmp /boot/grub/menu.lst
fi
debug "SO encontrados: $SOS"
rm -f /tmp/salfdisk
rm -f /tmp/filas
rm -f /tmp/ficheros
rm -f /tmp/lineas
rm -f /tmp/linea
rm -f /tmp/fila
