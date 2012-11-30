#!/usr/bin/python
# -*- coding: utf-8 -*-

# Last modified by A. Olmo on 4 oct 2005.

import os
import subprocess
import time
from ue import misc
from ue.settings import *
from sys import stderr

class Copy:

  def __init__(self, mountpoints):
    """Initial attributes."""

    self.source = '/source'
    self.target = '/target'
    self.mountpoints = mountpoints
    self.unionfs = False

  def run(self, queue):
    """Run the copy stage. This is the second step from the installation
    process."""

    queue.put( '3 Preparando el directorio de instalación')
    misc.pre_log('info', 'Mounting target')
    if self.mount_target():
      queue.put( '3 Directorio de instalación listo')
      misc.pre_log('info', 'Mounted target')
    else:
      misc.pre_log('error', 'Mounting target')
      return False

    queue.put( '4 Obteniendo la distribución a copiar')
    misc.pre_log('info', 'Mounting source')
    if self.mount_source():
      queue.put( '5 Distribución obtenida')
      misc.pre_log('info', 'Mounted source')
    else:
      misc.pre_log('error', 'Mounting source')
      return False

    queue.put( '6 Preparando la copia a disco')
    misc.pre_log('info', 'Copying distro')
    if self.copy_all(queue):
      queue.put( '90 Ficheros copiados')
      misc.pre_log('info', 'Copied distro')
    else:
      misc.pre_log('error', 'Copying distro')
      return False

    queue.put( '91 Copiando registros de instalación al disco')
    misc.pre_log('info', 'Copying logs files')
    if self.copy_logs():
      queue.put( '92 Registros de instalación listos')
      misc.post_log('info', 'Copied logs files')
    else:
      misc.pre_log('error', 'Copying logs files')
      return False

    queue.put( '93 Desmontando la imagen original de la copia')
    misc.post_log('info', 'Umounting source')
    if self.umount_source():
      queue.put( '94 Imagen de la copia desmontada')
      misc.post_log('info', 'Umounted source')
    else:
      misc.post_log('error', 'Umounting source')
      return False


  def mount_target(self):
    """mount selected partitions on /target ."""

#    stderr.write ('PuntosDeMontaje: ' + str (self.mountpoints) + '\n')

    if not os.path.isdir(self.target) and not os.path.isfile(self.target):
      os.mkdir(self.target)

    misc.ex('mount', self.mountpoints.keys()[self.mountpoints.values().index('/')], self.target)

    for device, path in self.mountpoints.items():
      if ( path == '/' ):
          continue
      elif ( path ==  'swap' ):
          os.system('swapon %s' % device)
          continue
      path = os.path.join(self.target, path[1:])
      if not os.path.isdir(path) and not os.path.isfile(path):
        os.mkdir(path)
      else:
        misc.pre_log('error', 'Problemas al crear %s' % path)

      if not misc.ex ('mount', '-t', 'ext3', device, path):
        misc.ex('mkfs.ext3',device)
        misc.ex('mount', device, path)

    if ( 'swap' not in self.mountpoints.values() ):
      # If swap partition isn't defined, we create a swapfile
      os.system("dd if=/dev/zero of=%s/swapfile bs=1024 count=%d" % (self.target, MINIMAL_PARTITION_SCHEME ['swap'] * 1024) )
      os.system("mkswap %s/swapfile" % self.target)
      os.system("swapon %s/swapfile" % self.target)

    return True


  def umount_target(self):
    """umounting selected partitions."""

    ordered_list = []
    for device, path in self.mountpoints.items():
      if path in ('swap',):
          continue

      path = os.path.join(self.target, path[1:])
      ordered_list.append((len(path), device, path))

    ordered_list.reverse()
    for length, device, path in  ordered_list:
      try:
        misc.ex('umount', '-f', os.path.join(self.target, path))
      except Exception, e:
        print e
    return True

  def copy_all(self, queue):
    """Core copy process. This is the most important step of this stage. It clones
    live filesystem into a local partition in the selected hard disk."""

    files = []
    total_size = 0
    oldsourcepath = ''

    misc.pre_log('info','Recolecting files to copy')
    for dirpath, dirnames, filenames in os.walk(self.source):
      sourcepath = dirpath[len(self.source)+1:]
      if ( oldsourcepath.split('/')[0] != sourcepath.split('/')[0] ):
        if sourcepath.startswith('etc'):
          queue.put( '7 Recorriendo /etc' )
        elif sourcepath.startswith('home'):
          queue.put( '8 Recorriendo /home' )
        elif sourcepath.startswith('media'):
          queue.put( '10 Recorriendo /media' )
        elif sourcepath.startswith('usr/doc'):
          queue.put( '11 Recorriendo /usr/doc' )
        elif sourcepath.startswith('usr/local'):
          queue.put( '13 Recorriendo /usr/local' )
        elif sourcepath.startswith('usr/src'):
          queue.put( '15 Recorriendo /usr/src' )
        elif sourcepath.startswith('var/backups'):
          queue.put( '16 Recorriendo /var/backups' )
        elif sourcepath.startswith('var/tmp'):
          queue.put( '17 Recorriendo /var/tmp' )
        oldsourcepath = sourcepath


      for name in dirnames + filenames:
        relpath = os.path.join(sourcepath, name)
        fqpath = os.path.join(self.source, dirpath, name)

        if os.path.isfile(fqpath):
          size = os.path.getsize(fqpath)
          total_size += size
          files.append((relpath, size))
        else:
          files.append((relpath, None))

    misc.pre_log('info','About to start copying')

    copy = subprocess.Popen(['cpio', '-d0mp', self.target],
        cwd = self.source,
        stdin = subprocess.PIPE)

    copied_bytes, counter = 0, 0
    for path, size in files:
      copy.stdin.write(path + '\0')
      misc.pre_log('info', path)
      if ( size != None ):
        copied_bytes += size
      per = (copied_bytes * 100) / total_size
      # Adjusting the percentage
      per = (per*73/100)+17
      if ( counter != per and per < 34 ):
        # We start the counter until 33
        time_start = time.time()
        counter = per
        queue.put("%s Copiando %s%% - [%s]" % (per, per, path))
      elif ( counter != per and per >= 40 ):
        counter = per
        time_left = (time.time()-time_start)*57/(counter - 33) - (time.time()-time_start)
        minutes, seconds = time_left/60, time_left - int(time_left/60)*60
        queue.put("%s Copiando %s%% - Queda %02d:%02d - [%s]" % (per, per, minutes, seconds, path))
      elif ( counter != per ):
        counter = per
        queue.put("%s Copiando %s%% - [%s]" % (per, per, path))

    copy.stdin.close()
    copy.wait()

    return True


  def copy_logs(self):
    """copy logs files into installed system."""

    distro = open ('/etc/lsb-release').readline ().strip ().split ('=') [1].lower ()
    log_file = '/var/log/' + distro + '-express'

    if not misc.ex('cp', '-a', log_file, os.path.join(self.target, log_file[1:])):
      misc.pre_log('error', 'No se pudieron copiar los registros de instalación')

    return True


  def mount_source(self):
    """mounting loop system from cloop or squashfs system."""

    from os import path

    self.dev = ''
    if not os.path.isdir(self.source):
      try:
        os.mkdir(self.source)
      except Exception, e:
        print e
      misc.pre_log('info', 'mkdir %s' % self.source)

    # Autodetection on unionfs systems
    file = open('/proc/mounts').readlines()
    for line in file:
      if ( line.split()[2] == 'squashfs' ):
        misc.ex('mount', '--bind', line.split()[1], self.source)
        self.unionfs = True
        return True

    # Manual Detection on non unionfs systems
    files = ['/cdrom/casper/filesystem.cloop', '/cdrom/META/META.squashfs']

    for file in files:
      if path.isfile(file) and path.splitext(file)[1] == '.cloop':
        self.dev = '/dev/cloop1'
        break
      elif path.isfile(file) and path.splitext(file)[1] == '.squashfs':
        self.dev = '/dev/loop3'
        break

    if self.dev == '':
      return False

    misc.ex('losetup', self.dev, file)
    try:
      misc.ex('mount', self.dev, self.source)
    except Exception, e:
      print e
    return True


  def umount_source(self):
    """umounting loop system from cloop or squashfs system."""

    if not misc.ex('umount', self.source):
      return False
    if self.unionfs:
      return True
    if ( not misc.ex('losetup', '-d', self.dev) and self.dev != '' ):
      return False
    return True


if __name__ == '__main__':
  mountpoints = misc.get_var()['mountpoints']
  copy = Copy(mountpoints)
  copy.run()

# vim:ai:et:sts=2:tw=80:sw=2:
