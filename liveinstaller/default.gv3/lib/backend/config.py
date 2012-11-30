#!/usr/bin/python
# -*- coding: utf-8 -*-

from ue import misc
from ue.settings import *

import debconf, os
import subprocess

class Config:

  def __init__(self, vars):
    """Initial attributes."""

    # We get here the current kernel version
    self.kernel_version = open('/proc/sys/kernel/osrelease').readline().strip()
    # FIXME: Hack (current kernel loaded on liveCD doesn't work on installed systems)
    self.kernel_version = '2.6.12-9-386'
    self.distro = open('/etc/lsb-release').readline().strip().split('=')[1].lower()
    self.target = '/target/'
    # Getting vars: fullname, username, password, hostname
    # and mountpoints
    for var in vars.keys():
      setattr(self,var,vars[var])


  def run(self, queue):
    """Run configuration stage. These are the last steps to launch in live
    installer."""

    #queue.put('92 92% Configurando sistema locales')
    #misc.post_log('info', 'Configuring distro')
    #if self.get_locales():
    #  queue.put('92 92% Sistema locales configurado')
    #  misc.post_log('info', 'Configured distro')
    #else:
    #  misc.post_log('error', 'Configuring distro')
    #  return False
    queue.put('93 93% Configurando sistema de particiones en disco')
    misc.post_log('info', 'Configuring distro')
    if self.configure_fstab():
      queue.put('93 93% Sistema de particiones en disco configurado')
      misc.post_log('info', 'Configured distro')
    else:
      misc.post_log('error', 'Configuring distro')
      return False
    #queue.put('94 94% Configurando zona horaria')
    #misc.post_log('info', 'Configuring distro')
    #if self.configure_timezone():
    #  queue.put('94 94% Zona horaria configurada')
    #  misc.post_log('info', 'Configured distro')
    #else:
    #  misc.post_log('error', 'Configuring distro')
    #  return False
    queue.put('95 95% Creando usuario')
    misc.post_log('info', 'Configuring distro')
    if self.configure_user():
      queue.put('95 95% Usuario creado')
      misc.post_log('info', 'Configured distro')
    else:
      misc.post_log('error', 'Configuring distro')
      return False
    queue.put('96 96% Configurando hardware')
    misc.post_log('info', 'Configuring distro')
    if self.configure_hardware():
      queue.put('96 96% Hardware configurado')
      misc.post_log('info', 'Configured distro')
    else:
      misc.post_log('error', 'Configuring distro')
      return False
    queue.put('97 97% Configurando red')
    misc.post_log('info', 'Configuring distro')
    if self.configure_network():
      queue.put('97 97% Red configurada')
      misc.post_log('info', 'Configured distro')
    else:
      misc.post_log('error', 'Configuring distro')
      return False
    queue.put('98 98% Bautizando ordenador')
    misc.post_log('info', 'Configuring distro')
    if self.configure_hostname():
      queue.put('98 98% Ordenador bautizado')
      misc.post_log('info', 'Configured distro')
    else:
      misc.post_log('error', 'Configuring distro')
      return False
    queue.put('99 99% Configurando sistema de arranque')
    misc.post_log('info', 'Configuring distro')
    if self.configure_bootloader():
      queue.put('100 100% Instalación finalizada')
      misc.post_log('info', 'Configured distro')
    else:
      misc.post_log('error', 'Configuring distro')
      return False


  def get_locales(self):
    """set timezone and keymap attributes from debconf. It uses the same values
    the user have selected on live system.

    get_locales() -> timezone, keymap, locales"""

    debconf.runFrontEnd()
    db = debconf.Debconf()

    try:
      self.timezone = db.get('express/timezone')
      if self.timezone == '':
          self.timezone = db.get('tzconfig/choose_country_zone_multiple')
    except:
      self.timezone = open('/etc/timezone').readline().strip()
    self.keymap = db.get('debian-installer/keymap')

    self.locales = db.get('locales/default_environment_locale')
    return True


  def configure_fstab(self):
    """create and configure /etc/fstab depending on our installation selections.
    It creates a swapfile instead of swap partition if it isn't defined along the
    installation process. """
    print "creating fstab"
    # Remove all dirs in /target/media; they will be recreated
    dirs_to_remove=os.listdir(os.path.join(self.target,'media'))
    for dir in dirs_to_remove:
        try:
           os.rmdir(os.path.join(self.target,'media',dir))
        except:
           pass

    
    swap = 0
    fstab = open(os.path.join(self.target,'etc/fstab'), 'w')
    # add standard fstab header
    print >>fstab, "# /etc/fstab: static file system information."
    print >>fstab, "#"
    print >>fstab, "# <file system> <mount point>   <type>  <options>  <dump>  <pass>"
    print >>fstab, "proc            /proc           proc    defaults      0       0"
    print >>fstab, "#sys             /sys            sysfs   defaults      0       0"
    # Creating proc entry
    #print >>fstab, 'proc\t/proc\tproc\tdefaults\t0\t0\nsysfs\t/sys\tsysfs\tdefaults\t0\t0'
    # Creating installed system defined partitions
    for device, path in self.mountpoints.items():
        if path == '/':
            passno, options, filesystem = 1, 'defaults,errors=remount-ro', 'ext3'
        elif path == 'swap':
            swap, passno, filesystem, options, path = 1, 0, 'swap', 'sw', 'none'
        else:
            passno, filesystem, options = 2, 'ext3', 'defaults,errors=remount-ro'

        print >>fstab, '%s\t%s\t%s\t%s\t%d\t%d' % (device, path, filesystem, options, 0, passno)

    win_counter = 1
    for new_device, fs in misc.get_filesystems().items():
      if new_device in [ele[0] for ele in self.mountpoints.items()]:
        continue
      if ( fs in ['vfat', 'ntfs'] ):
        passno = 2
        if fs == 'vfat' :
          options ='rw,gid=100,users,umask=0002,fmask=0113,sync,noauto,defaults'
        else:
          options ='gid=100,users,umask=0222,fmask=0333,sync,nls=utf8,noauto,defaults'
        path = '/media/Windows%d' % win_counter
        os.mkdir(os.path.join(self.target, path[1:]))
        win_counter += 1
      elif fs == 'ext3':
              options = 'defaults,users,exec,noauto'
              path = '/media/%s%d' % (new_device[5:8],int(new_device[8:]))
              os.mkdir(os.path.join(self.target, path[1:]))
      elif fs == 'swap':
              options = 'sw'
              path = 'none'
              passno = 0
      print >>fstab, '%s\t%s\t%s\t%s\t%d\t%d' % (new_device, path, fs, options, 0, passno)


    # if swap partition isn't defined, we create a swapfile
    if ( swap != 1 ):
      print >>fstab, '/swapfile\tnone\tswap\tsw\t0\t0'
      os.system("dd if=/dev/zero of=%s/swapfile bs=1024 count=%d" % (self.target, MINIMAL_PARTITION_SCHEME ['swap'] * 1024) )
      os.system("mkswap %s/swapfile" % self.target)

    fstab.close()
    return True


  def configure_timezone(self):
    """set timezone on installed system (which was obtained from get_locales)."""

    # tzsetup ignores us if these exist
    for tzfile in ('etc/timezone', 'etc/localtime'):
        path = os.path.join(self.target, tzfile)
        if os.path.exists(path):
            os.unlink(path)

    self.set_debconf('base-config', 'tzconfig/preseed_zone', self.timezone)
    self.chrex('tzsetup', '-y')
    return True


  def configure_keymap(self):
    """set keymap on installed system (which was obtained from get_locales)."""

    self.set_debconf('debian-installer', 'debian-installer/keymap', self.keymap)
    self.chrex('install-keymap', self.keymap)
    return True


  def configure_user(self):
    """create the user selected along the installation process into the installed
    system. Default user from live system is deleted and skel for this new user is
    copied to $HOME."""

    self.chrex('passwd', '-l', 'root')
    #self.set_debconf('passwd', 'passwd/username', self.username)
    #self.set_debconf('passwd', 'passwd/user-fullname', self.fullname)
    #self.set_debconf('passwd', 'passwd/user-password', self.password)
    #self.set_debconf('passwd', 'passwd/user-password-again', self.password)
    #self.reconfigure('passwd')

    # FIXME: Only for Guadalinex (This is ugly!)
    self.chrex('deluser', 'guada')
    self.chrex('rm', '-rf', '/home/guada')
    self.chrex('delgroup', 'guada')

    self.chrex('useradd', '-u', '1000', '-d', '/home/' + self.username, '-m', '-s',
        '/bin/bash', '-c', '"' + self.fullname + '"', self.username)
    passwd = subprocess.Popen(['echo', self.username + ':' + self.password],
        stdout=subprocess.PIPE)
    subprocess.Popen(['chroot', self.target, 'chpasswd', '--md5'], stdin=passwd.stdout)
    self.chrex('mkdir', '/home/%s' % self.username)
    self.chrex('chown %s' % self.username, '/home/%s' % self.username)
    self.chrex('chgrp %s' % self.username, '/home/%s' % self.username)
    self.chrex('chmod 755', '/home/%s' % self.username) # To be able to share folders in home
    self.chrex('adduser', self.username, 'admin')
    if not self.chrex('/usr/local/sbin/adduser.local', self.username):
      for group in GROUPS:
        self.chrex('adduser', self.username, group)

    # Copying skel
    #
    #def visit (arg, dirname, names):
    #  for name in names:
    #    oldname = os.path.join (dirname, name)
    #    for pattern in str(dirname).split('/')[2:]:
    #      dir = os.path.join('', pattern)
    #    newname = os.path.join (self.target, 'home/%s/' % self.username, dir, name)
    #    if ( os.path.isdir(oldname) ):
    #      os.mkdir(newname)
    #    else:
    #      os.system('cp ' + oldname + ' ' + newname)
    #
    #os.path.walk('/etc/skel/', visit, None)

    self.chrex('chown', '-R', self.username, '/home/%s' % self.username)

    # configuring /etc/aliases
    aliases = open(os.path.join(self.target, 'etc/aliases'), 'w')
    print >>aliases, "root: %s" % self.username
    aliases.close()

    return True


  def configure_hostname(self):
    """setting hostname into installed system from data got along the installation
    process."""

    fp = open(os.path.join(self.target, 'etc/hostname'), 'w')
    print >>fp, self.hostname
    fp.close()

    hosts = open(os.path.join(self.target, 'etc/hosts'), 'w')
    print >>hosts, """127.0.0.1       localhost.localdomain   localhost  %s

# The following lines are desirable for IPv6 capable hosts
::1     ip6-localhost ip6-loopback
fe00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
ff02::3 ip6-allhosts""" % self.hostname
    hosts.close()

    return True


  def configure_hardware(self):
    """reconfiguring several packages which depends on the hardware system in
    which has been installed on and need some automatic configurations to get
    work."""

    self.chrex('mount', '-t', 'proc', 'proc', '/proc')
    self.chrex('mount', '-t', 'sysfs', 'sysfs', '/sys')

    misc.ex('cp', '/etc/X11/xorg.conf', os.path.join(self.target, 'etc/X11/xorg.conf') )
    packages = ['gnome-panel', 'gnome-panel-data', 'ssh', 'linux-image-' + self.kernel_version]

    try:
        for package in packages:
            self.copy_debconf(package)
            self.reconfigure(package)
    finally:
        self.chrex('umount', '/proc')
        self.chrex('umount', '/sys')
    return True


  def configure_network(self):
    """setting network configuration into installed system from live system data. It's
    provdided by setup-tool-backends."""

    conf = subprocess.Popen(['/usr/share/setup-tool-backends/scripts/network-conf',
        '--platform', 'ubuntu-5.04', '--get'], stdout=subprocess.PIPE)
    call = subprocess.Popen(['chroot', self.target, '/usr/share/setup-tool-backends/scripts/network-conf', 
        '--platform', 'ubuntu-5.04', '--set'], stdin=conf.stdout)
    call.wait()
    return True


  def configure_bootloader(self):
    """configuring and installing boot loader into installed hardware system."""

    import re

    target_dev = self.mountpoints.keys()[self.mountpoints.values().index('/')]
    distro = self.distro.capitalize()

    misc.ex('mount', '/proc', '--bind', self.target + '/proc')
    misc.ex('mount', '/sys', '--bind', self.target + '/sys')
    misc.ex('mount', '/dev', '--bind', self.target + '/dev')

    if not os.path.exists(self.target + '/boot/grub'):
          os.mkdir(self.target + '/boot/grub')

    #/target/etc/mtab creation - temporary bugfix for buggy grub-install
    mtab = open(os.path.join(self.target,'etc/mtab'), 'w')
    print >>mtab, '%s\t%s\t%s\t%s\t%s' % (target_dev, '/', 'auto', 'defaults', '0 0')
    mtab.close()

    #grub-install it's enough, because it calls grub-shell with setup command
    #device_regex = re.compile(r'/dev/[a-z]+')
    #device = device_regex.search(target_dev).group()
    #if not os.path.exists ( device ) or os.path.isdir ( device ):
    #  device = target_dev
    self.chrex ('rm', '-f', '/boot/grub/device.map')
    #self.chrex ('grub-install', device )
    self.chrex ('grub-install', 'hd0')

    # creates grub menu.lst on target
    self.chrex ('rm', '-f', '/boot/grub/menu.lst')
    #self.chrex('update-grub', '-y')
    # guess root device
    for ele in self.mountpoints.items():
      if ele[1]=="/":
        root_device=ele[0]
        break
    
    self.chrex('/usr/lib/python2.4/site-packages/ue/backend/grub-config.sh', root_device)
    misc.ex('umount', '-f', self.target + '/proc')
    misc.ex('umount', '-f', self.target + '/sys')
    misc.ex('umount', '-f', self.target + '/dev')
    return True


  def chrex(self, *args):
    """executes commands on chroot system (provided by *args)."""

    msg = ''
    for word in args:
      msg += str(word) + ' '
    if not misc.ex('chroot', self.target, *args):
      misc.post_log('error', 'chroot' + msg)
      return False
    misc.post_log('info', 'chroot' + msg)
    return True


  def copy_debconf(self, package):
    """setting debconf database into installed system."""

    targetdb = os.path.join(self.target, 'var/cache/debconf/config.dat')
    misc.ex('debconf-copydb', 'configdb', 'targetdb', '-p', '^%s/' % package,
            '--config=Name:targetdb', '--config=Driver:File','--config=Filename:' + targetdb)


  def set_debconf(self, owner, question, value):
    dccomm = subprocess.Popen(['chroot', self.target, 'debconf-communicate', '-fnoninteractive', owner],
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE, close_fds=True)
    dc = debconf.Debconf(read=dccomm.stdout, write=dccomm.stdin)
    dc.set(question, value)
    dc.fset(question, 'seen', 'true')
    dccomm.stdin.close()
    dccomm.wait()


  def reconfigure(self, package):
    """executes a dpkg-reconfigure into installed system to each package which
    provided by args."""

    self.chrex('dpkg-reconfigure', '-fnoninteractive', package)


if __name__ == '__main__':
  from Queue import Queue
  queue = Queue ()
  vars = misc.get_var()
  config = Config(vars)
  config.run(queue)
  print 101

# vim:ai:et:sts=2:tw=80:sw=2:
