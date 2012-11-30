#!/usr/bin/python

import os
import subprocess
from ue import misc
from time import sleep

class Copy:

  def __init__(self, mountpoints):
    self.source = '/source'
    self.target = '/target'
    self.mountpoints = mountpoints

  def run(self):
    print '3 Preparing the target in the disc'
    misc.pre_log('info', 'Mounting target')
    if self.mount_target():
      print '3 Prepared the target in the disc'
      misc.pre_log('info', 'Mounted target')
    else:
      misc.pre_log('error', 'Mounting target')
      return False
      
    print '4 Getting the distro to copy'
    misc.pre_log('info', 'Mounting source')
    if self.mount_source():
      print '5 Got the distro to copy'
      misc.pre_log('info', 'Mounted source')
    else:
      misc.pre_log('error', 'Mounting source')
      return False
      
    print '6 Copying the distro files to the disc'
    misc.pre_log('info', 'Copying distro')
    if self.copy_all():
      print '90 Copied the distro files to the disc'
      misc.pre_log('info', 'Copied distro')
    else:
      misc.pre_log('error', 'Copying distro')
      return False
      
    print '91 Copying the logs files to the disc'
    misc.pre_log('info', 'Copying logs files')
    if self.copy_logs():
      print '92 Copied the logs files to the disc'
      misc.post_log('info', 'Copied logs files')
    else:
      misc.pre_log('error', 'Copying logs files')
      return False
      
    print '93 Releasing the copied distro image'
    misc.post_log('info', 'Umounting source')
    if self.unmount_source():
      print '94 Released the copied distro image'
      misc.post_log('info', 'Umounted source')
    else:
      misc.post_log('error', 'Umounting source')
      return False
     

  def mount_target(self):
    misc.pre_log('info','mount %s %s' % (self.mountpoints['/'], self.target))
    sleep(1)

    for path, device in self.mountpoints.items():
      if path in ('/', 'swap'):
          continue
      path = os.path.join(self.target, path[1:])
      sleep(1)
      if not misc.pre_log('info','mount', device, path):
        return False
      sleep(1)
    return True

  def copy_all(self):
    files = []
    total_size = 0
    
    misc.pre_log('info','Recolecting files to copy')
    for dirpath, dirnames, filenames in os.walk(self.source):
      sourcepath = dirpath[len(self.source)+1:]
      if sourcepath.startswith('etc'):
        print 7
      elif sourcepath.startswith('home'):
        print 8
      elif sourcepath.startswith('media'):
        print 10
      elif sourcepath.startswith('usr/doc'):
        print 11
      elif sourcepath.startswith('usr/local'):
        print 13
      elif sourcepath.startswith('usr/src'):
        print 15
      elif sourcepath.startswith('var/backups'):
        print 16
      elif sourcepath.startswith('var/tmp'):
        print 17


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

    copied_bytes = 0
    for path, size in files:
      sleep(1)
      if size is not None:
        copied_bytes += size
      per = (copied_bytes * 100) / total_size
      # Adjusting the percentage
      per = (per*73/100)+17
      print per

    return True
    
  def copy_logs(self):
    try:
      misc.pre_log('info','cp -a /var/log/installer ' +
              os.path.join(self.target,'/var/log/installer'))
      sleep(1)
    except IOError, error:
      misc.pre_log('error', error)
      return False

    return True

  def mount_source(self):
    from os import path
    self.dev = ''
    files = ['/cdrom/casper/filesystem.cloop','/cdrom/META/META.squashfs']
    for f in files:
      if path.isfile(f) and path.splitext(f)[1] == '.cloop':
    	file = f
        self.dev = '/dev/cloop1'
      elif path.isfile(f) and path.splitext(f)[1] == '.squashfs':
    	file = f
    	self.dev = '/dev/loop3'

    if self.dev == '':
      return False

    misc.pre_log('info','losetup %s %s' % (self.dev, file))
    sleep(1)
    if not os.path.isdir(self.source):
      misc.pre_log('info','mkdir %s' % self.source)
    misc.pre_log('info','mount %s %s' % (self.dev, self.source))
    sleep(1)
    return True

  def unmount_source(self):
    if not misc.pre_log('info','umount ' + self.source):
      return False
    sleep(1)
    if not misc.pre_log('info','losetup -d ' + self.dev):
      return False
    sleep(1)
    return True


if __name__ == '__main__':
  mountpoints = misc.get_var()['mountpoints']
  copy = Copy(mountpoints)
  copy.run()
  print 101

# vim:ai:et:sts=2:tw=80:sw=2:
