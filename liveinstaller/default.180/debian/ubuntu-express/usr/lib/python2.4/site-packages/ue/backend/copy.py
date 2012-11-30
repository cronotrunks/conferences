#!/usr/bin/python

import os
from ue import misc


class Copy:

  def __init__(self, mountpoints):
    self.source = '/source'
    self.target = '/target'
    self.mountpoints = mountpoints

  def run(self):
    print '0 Preparing the target in the disc'
    if self.mount_target():
      print '5 Prepared the target in the disc'
      misc.pre_log('info', 'Mounting target')
    else:
      misc.pre_log('error', 'Mounting target')
      return False
      
    print '7 Getting the distro to copy'
    if self.mount_source():
      print '10 Got the distro to copy'
      misc.pre_log('info', 'Mounting source')
    else:
      misc.pre_log('error', 'Mounting source')
      return False
      
    print '12 Copying the distro files to the disc'
    if self.copy_all():
      print '85 Copied the distro files to the disc'
      misc.pre_log('info', 'Copying distro')
    else:
      misc.pre_log('error', 'Copying distro')
      return False
      
    print '86 Copying the logs files to the disc'
    if self.copy_logs():
      print '90 Copied the logs files to the disc'
      misc.post_log('info', 'Copying logs files')
    else:
      misc.pre_log('error', 'Copying logs files')
      return False
      
    print '91 Releasing the copied distro image'
    if self.mount_source():
      print '92 Released the copied distro image'
      misc.post_log('info', 'Umounting source')
    else:
      misc.post_log('error', 'Umounting source')
      return False
     

  def mount_target(self):
    if not os.path.isdir(self.target):
      os.mkdir(self.target)
    misc.ex('mount', self.mountpoints['/'], self.target)

    for path, device in self.mountpoints.items():
      if path in ('/', 'swap'):
          continue
      path = os.path.join(self.target, path[1:])
      os.mkdir(path)
      if not misc.ex('mount', device, path):
        return False
    return True

  def copy_all(self):
    files = []
    total_size = 0
    
    for dirpath, dirnames, filenames in os.walk(self.source):
      sourcepath = dirpath[len(self.source)+1:]

      for name in dirnames + filenames:
        relpath = os.path.join(sourcepath, name)
        fqpath = os.path.join(self.source, dirpath, name)

        if os.path.isfile(fqpath):
          size = os.path.getsize(fqpath)
          total_size += size	
          files.append((relpath, size))
        else:
          files.append((relpath, None))

    copy = subprocess.Popen(['cpio', '-d0mp', self.target],
                            cwd=self.source,
                            stdin=subprocess.PIPE)

    copied_bytes = 0
    for path, size in files:
      copy.stdin.write(path + '\0')
      if size is not None:
        copied_bytes += size
      per = (copied_bytes * 100) / total_size
      print per

    copy.stdin.close()
    copy.wait()
    
  def copy_logs(self):
    try:
      misc.ex('cp', '-a', '/var/log/installer', os.path.join(self.target,'/var/log/installer'))
    except IOError, error:
      misc.pre_log('error', error)
      return False
    return True

  def mount_source(self):
    from os import path
    files = ['/cdrom/casper/filesystem.cloop', '/cdrom/META/META.squashfs']
    for f in files:
      if path.isfile(f) and path.splitext(f)[1] == '.cloop':
    	file = f
    	self.dev = '/dev/cloop1'
      elif path.isfile(f) and path.splitext(f)[1] == '.squashfs':
    	file = f
    	self.dev = '/dev/loop3'
      else:
        return -1			

    misc.ex('losetup', self.dev, file)
    os.mkdir(self.source)
    misc.ex('mount', self.dev, self.source)
    return 0

  def unmount_source(self):
    misc.ex('umount', self.source)
    misc.ex('losetup', '-d', self.dev)


if __name__ == '__main__':
  mountpoints = misc.get_vars()
  copy = Copy(mountpoints)
  copy.run()

# vim:ai:et:sts=2:tw=80:sw=2:
