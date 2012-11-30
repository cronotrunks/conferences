# -*- coding: utf-8 -*-

# «part» - etapa de particionamiento
# 
# Copyright (C) 2005 Junta de Andalucía
# 
# Autor/es (Author/s):
# 
# - Juan Jesús Ojeda Croissier <juanje#interactors._coop>
# - Javier Carranza <javier.carranza#interactors._coop>
# - Antonio Olmo Titos <aolmo#emergya._info>
# 
# Este fichero es parte del instalador en directo de Guadalinex 2005.
# 
# El instalador en directo de Guadalinex 2005 es software libre. Puede
# redistribuirlo y/o modificarlo bajo los términos de la Licencia Pública
# General de GNU según es publicada por la Free Software Foundation, bien de la
# versión 2 de dicha Licencia o bien (según su elección) de cualquier versión
# posterior. 
# 
# El instalador en directo de Guadalinex 2005 se distribuye con la esperanza de
# que sea útil, pero SIN NINGUNA GARANTÍA, incluso sin la garantía MERCANTIL
# implícita o sin garantizar la CONVENIENCIA PARA UN PROPÓSITO PARTICULAR. Véase
# la Licencia Pública General de GNU para más detalles.
# 
# Debería haber recibido una copia de la Licencia Pública General junto con el
# instalador en directo de Guadalinex 2005. Si no ha sido así, escriba a la Free
# Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301
# USA.
# 
# -------------------------------------------------------------------------
# 
# This file is part of Guadalinex 2005 live installer.
# 
# Guadalinex 2005 live installer is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the License, or
# at your option) any later version.
# 
# Guadalinex 2005 live installer is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
# 
# You should have received a copy of the GNU General Public License along with
# Guadalinex 2005 live installer; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

""" U{pylint<http://logilab.org/projects/pylint>} mark: -6.50!! (bad
    indentation) """

# Last modified by A. Olmo on 20 oct 2005.

from subprocess import *
from os import system
from ue import misc
import sys

def call_autoparted (assistant, drive, progress = None):

  """ Perform automatic partition.
      @return: a dictionary containing a device for each mount point (i.e.
      C{{'/dev/hda5': '/', '/dev/hda7': '/home', '/dev/hda6': 'swap'}}). """

  return assistant.auto_partition (drive, steps = progress)

def percentage(per, num):
  re = (num * per)/100
  return re

def calc_sizes(tam):
  '''
     /      ->  2355 Mb > x < 20 Gb   -> 25 %
     /home  ->   512 Mb > x           ->  5 %
     swap   ->   205 Mb > x <  1 Gb   -> 70 %
  '''
  if tam < 3072:
    return None
    
  sizes = {}
  sizes['root'] = percentage(tam,25)
  sizes['swap'] = percentage(tam,5)
  #home = percentage(tam,70)

  if sizes['root'] < 2355:
    sizes['root'] = 2355
  elif sizes['root'] > 20480:
    sizes['root'] = 20480

  if sizes['swap'] < 205:
    sizes['swap'] = 205
  elif sizes['swap'] > 1024:
    sizes['swap'] = 1024

  sizes['home'] = tam - sizes['root'] - sizes['swap']
  if sizes['home'] < 512:
    return None

  return sizes
  
def get_disk_size(drive):
  out = Popen(['/sbin/sfdisk', '-s', drive], stdin=PIPE, stdout=PIPE,
              close_fds=True)
  tam = int(out.stdout.readline().strip())
  tam = tam/1024
  return tam
  
def extend(drive):
  out = Popen(['/sbin/fdisk', '-l', drive], stdin=PIPE, stdout=PIPE, close_fds=True)
  cont = out.stdout.readlines()
  for i in cont:
      if i.startswith("/dev/"):
              line = i.split()
              if line[4] == '5':
                return True
  return False
 
def limits_for_scheme(begin, end, scheme):
    mega_scheme = {}
    beg = begin+1
    en  = beg+scheme['root']
    mega_scheme['root'] = [beg, en]
    beg = en+1
    en  = beg+scheme['home']
    mega_scheme['home'] = [beg, en]
    beg = en+1
    en  = end-2
    mega_scheme['swap'] = [beg, en]
    return mega_scheme


def part_scheme(drive, scheme):
    if scheme.has_key('extended'):
        misc.ex("parted -s %s mkpart extended %d %d" % (drive, scheme['extended'][0], scheme['extended'][1]) )
    misc.ex("parted -s %s mkpart logical ext2 %d %d" % (drive, scheme['root'][0], scheme['root'][1]) )
    misc.ex("parted -s %s mkpart logical ext2 %d %d" % (drive, scheme['home'][0], scheme['home'][1]) )
    misc.ex("parted -s %s mkpart logical linux-swap %d %d" % (drive, scheme['swap'][0], scheme['swap'][1]) )
    # TODO: Some error code handling needed with the execution of this commands
    # above
    return True


def get_empty_space(drive):
    # As sector size is supossed to be 512 the ratio MB/Sec is 1/2048
    conv_value = 2048 
    
    import os
    os.putenv('LANG','C')    
    out = Popen(['/sbin/cfdisk', '-P', 's', drive], stdin=PIPE, stdout=PIPE, close_fds=True)
    cont = out.stdout.readlines()
    cont = cont[5:]
    if extend(drive):
        extended = None
        frees = []
        list = []
        logics = 0
        for i in cont:
            j = i[3:]
            j = j.replace('*',' ')
            line = j.split()
            if line[5] == 'Extended':
                extended = cont.index(i)
            elif line[5] == 'Free':
                frees.append(cont.index(i))
    	    elif line[0] == 'Logical':
    	        logics += 1
            begin, end, length = int(line[1]), int(line[2]), int(line[4])
            list.append([begin, end, length])
        
        # If there is more than 12 logic partitions(4 primaries plus 8 logicals) exit
        if logics > 8:
    	    print "Too much logical partitions"
    	    misc.pre_log('error', "Too much logical partitions")
    	    return (None,None)
    
        sizes = []
        indexs = []
        for i in list:
            if list[extended] != i and i[-1] < list[extended][1] and i[1] > list[extended][0] and list.index(i) in frees:
                sizes.append(i[2])
                indexs.append(list.index(i))
        
        if not sizes:
	    print "No freespace has enough room"
	    misc.pre_log('error', "No freespace has enough room")
	    return (None,None)
        bigger = max(sizes)
        index = sizes.index(bigger)
        i = indexs[index]
        tam = sizes[index]/conv_value
        scheme = calc_sizes(tam)
        begin = list[i][0]/conv_value
        end = list[i][1]/conv_value
    	if not scheme:
    	    print "Not enough space"
    	    misc.pre_log('error', "Not enough space")
    	    return (None,None)
        limits = limits_for_scheme(begin, end, scheme)
        logic_dev = logics + 4
        partitions = { "%s%d" % (drive,logic_dev+1) : '/'    ,
                       "%s%d" % (drive,logic_dev+2) : '/home',
                       "%s%d" % (drive,logic_dev+3) : 'swap'  
                     }
    else:
        nonfrees = 0
        list = []
        for i in cont:
            i = i.replace('*',' ')
    	    line = i.split()
            # If there is not any number in the first value, it's not a
            # partition, but it's a free space
    	    if not line[0].isdigit():
                begin, end, length = int(line[1]), int(line[2]), int(line[4])
                list.append([begin, end, length])
            else:
                nonfrees += 1
        if nonfrees > 3:
            print "Too many primary partitions"
    	    misc.pre_log('error', "Too many primary partitions")
    	    return (None,None)
        sizes = []
        for i in list:
            sizes.append(i[2])
        if not sizes:
	    print "No freespace has enough room"
	    misc.pre_log('error', "No freespace has enough room")
	    return (None,None)
        bigger = max(sizes)
        index = sizes.index(bigger)
        tam = sizes[index]/conv_value
        scheme = calc_sizes(tam)
        begin = (list[index][0]/conv_value)+2
        end = (list[index][1]/conv_value)-2
    	if not scheme:
    	    print "Not enough space"
    	    misc.pre_log('error', "Not enough space")
    	    return (None,None)
        limits = limits_for_scheme(begin, end, scheme)
        limits['extended'] = [begin, end]
        partitions = { "%s%d" % (drive,5) : '/'    ,
                       "%s%d" % (drive,6) : '/home',
                       "%s%d" % (drive,7) : 'swap'  
                     }
                     
    print >>sys.stderr, "Limits: ", limits, "\nMountpoints: ", partitions
    return (limits,partitions)
        
 
def get_schemes_list(drive):
  # 1 - get the disk size
  tam = get_disk_size(drive)
  # 2 - get the list of sizes (50% , 25% and minimal)
  tam_list = [3072, percentage(tam,25), percentage(tam,50)]
  # 3 - get the list of schemes (one per size)
  schemes_list = []
  for size in tam_list:
    scheme = calc_sizes(size)
    schemes_list.append(scheme)
  return schemes_list
  
def call_all_disk(drive):
  # 1 - get the disk size
  tam = get_disk_size(drive)
  # 2 - call calc_sizes(tam)
  sizes = calc_sizes(tam)
  if not sizes:
    return False
  # 3 - to parte the disk using calcs
  cmd = "/sbin/sfdisk -uM %s << EOF\n,%d,L\n,%d,L\n,,S\nEOF" % (drive, sizes['root'], sizes['home'])
  try:
    ret = call(cmd, shell=True)
  except OSError, e:   
    print >>sys.stderr, "Execution failed:", e
    return False

  return True

def call_gparted(widget):

  '''call_autoparted() -> dict {'mount point' : 'dev'}
                       -> None
  '''
  import gtk
  import sys

  # plug/socket implementation (Gparted integration)
  socket = gtk.Socket()
  socket.show()
  widget.add(socket)
  Wid = str(socket.get_id())

  # TODO: rewrite next block.
  #mountpoints = None

  try:
    out = Popen(['/usr/bin/gparted', '-i', Wid], stdin=PIPE, stdout=PIPE,
                close_fds=True)
    # get the output last line 
    #line = out.readlines()[-1].strip()
  except:
    try:
      out = Popen(['/usr/local/bin/gparted', '-i', Wid], stdin=PIPE,
                  stdout=PIPE, close_fds=True)
      # get the output last line 
      line = out.readlines()[-1].strip()
    except:
      widget.destroy()
      return None

  #FIXME:We need to know how the mounpoints are showed up

  return out.pid

# vim:ai:et:sts=2:tw=80:sw=2:

