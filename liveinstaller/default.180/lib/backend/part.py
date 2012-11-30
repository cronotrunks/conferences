#!/usr/bin/python

# Last modified by Antonio Olmo <aolmo@emergya.info> on 5 august 2005.

import subprocess
from os import popen4

def call_autoparted ():

  '''call_autoparted() -> dict {'mount point' : 'dev'}
                       -> None
  '''

  result = None

  #   Needed command seemed to be 'autopartition'.
  #   Without args, starts automatically.
  #   If one argument is added, it targets this device
  #   to automatically partition.
  
  [input, output] = popen4 ('autopartition')

  return result

def call_gparted(main_window):
  '''call_autoparted() -> dict {'mount point' : 'dev'}
                       -> None
  '''
  import gtk
  mountpoints = {'/'     : '/dev/hda1',
                 'swap'  : '/dev/hda2',
                 '/home' : '/dev/hda3'}

  # plug/socket implementation (Gparted integration)
  socket = gtk.Socket()
  socket.show()
  main_window.get_widget('embedded').add(socket)
  Wid = str(socket.get_id())

  # TODO: rewrite next block.

  try:
    subprocess.Popen(['/usr/bin/gparted', '-i', Wid], stdin=subprocess.PIPE, stdout=subprocess.PIPE, close_fds=True)
  except:
    try:
      subprocess.Popen(['/usr/local/bin/gparted', '-i', Wid], stdin=subprocess.PIPE, stdout=subprocess.PIPE, close_fds=True)
    except:
      main_window.get_widget('embedded').destroy()
    
    if ( stdin is not '' ):
      mountpoints = stdin

  return mountpoints

# vim:ai:et:sts=2:tw=80:sw=2:

