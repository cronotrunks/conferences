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

def call_autoparted (assistant, drive, progress = None):

  """ Perform automatic partition.
      @return: a dictionary containing a device for each mount point (i.e.
      C{{'/dev/hda5': '/', '/dev/hda7': '/home', '/dev/hda6': 'swap'}}). """

  return assistant.auto_partition (drive, steps = progress)


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


def clear_disk (selected_drive):

  output = Popen (['echo', '-e', selected_drive, ':', 'start=', '0,', 'size=', '0,', 'Id='], stdout=PIPE, close_fds=True)
  try:
    Popen (['sfdisk', '--force', selected_drive], stdin=output.stdout, close_fds=True).wait()
  except:
    return False
  return True


def create_fullpartitions (selected_drive):

  import os

  output = Popen (['echo', '-e', ',61,S\n62,,L,*'], stdout=PIPE, close_fds=True)
  try:
    Popen (['sfdisk', '--force', selected_drive], stdin=output.stdout, close_fds=True).wait()
  except:
    return False
  return True

# vim:ai:et:sts=2:tw=80:sw=2:
