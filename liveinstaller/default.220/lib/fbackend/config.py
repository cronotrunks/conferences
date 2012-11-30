#!/usr/bin/python

import debconf
from ue import fmisc
from time import sleep

class Config:

  def __init__(self, vars):
      # We get here the current kernel version
      self.kernel_version = open('/proc/sys/kernel/osrelease').readline().strip()
      self.distro = open('/etc/lsb-release').readline().strip().split('=')[1].lower()
      self.target = '/target/'
      # Getting vars: fullname, username, password, hostname
      # and mountpoints
      for var in vars.keys():
        setattr(self,var,vars[var])

  def run(self):
      
    print '92 Configuring the hardware and system'
    fmisc.post_log('info', 'Configuring distro')
    if self.get_locales():
      print '92 Configured the hardware and system'
      fmisc.post_log('info', 'Configured distro')
      return True
    else:
      fmisc.post_log('error', 'Configuring distro')
      return False
    print '93 Configuring the hardware and system'
    fmisc.post_log('info', 'Configuring distro')
    if self.configure_fstab():
      print '93 Configured the hardware and system'
      fmisc.post_log('info', 'Configured distro')
      return True
    else:
      fmisc.post_log('error', 'Configuring distro')
      return False
    print '94 Configuring the hardware and system'
    fmisc.post_log('info', 'Configuring distro')
    if self.configure_timezone():
      print '94 Configured the hardware and system'
      fmisc.post_log('info', 'Configured distro')
      return True
    else:
      fmisc.post_log('error', 'Configuring distro')
      return False
    print '95 Configuring the hardware and system'
    fmisc.post_log('info', 'Configuring distro')
    if self.configure_user():
      print '95 Configured the hardware and system'
      fmisc.post_log('info', 'Configured distro')
      return True
    else:
      fmisc.post_log('error', 'Configuring distro')
      return False
    print '96 Configuring the hardware and system'
    fmisc.post_log('info', 'Configuring distro')
    if self.configure_hostname():
      print '96 Configured the hardware and system'
      fmisc.post_log('info', 'Configured distro')
      return True
    else:
      fmisc.post_log('error', 'Configuring distro')
      return False
    print '97 Configuring the hardware and system'
    fmisc.post_log('info', 'Configuring distro')
    if self.configure_hardware():
      print '97 Configured the hardware and system'
      fmisc.post_log('info', 'Configured distro')
      return True
    else:
      fmisc.post_log('error', 'Configuring distro')
      return False
    print '98 Configuring the hardware and system'
    fmisc.post_log('info', 'Configuring distro')
    if self.configure_network():
      print '98 Configured the hardware and system'
      fmisc.post_log('info', 'Configured distro')
      return True
    else:
      fmisc.post_log('error', 'Configuring distro')
      return False
    print '99 Configuring the hardware and system'
    fmisc.post_log('info', 'Configuring distro')
    if self.configure_bootloader():
      print '100 Configured the hardware and system'
      fmisc.post_log('info', 'Configured distro')
      return True
    else:
      fmisc.post_log('error', 'Configuring distro')
      return False


  def get_locales(self):
      '''get_locales() -> timezone, keymap, locales
      
      Get the timezone, keymap and locales from the
      Debconf database and return them.
      '''
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
      fstab = open('/tmp/fstab', 'w')
      for path, device in self.mountpoints.items():
          if path == '/':
              passno = 1
          else:
              passno = 2
  
          filesystem = 'ext3'
          options = 'defaults'
          sleep(1)
          
          print >>fstab, '%s\t%s\t%s\t%s\t%d\t%d' % (device, path, filesystem, options, 0, passno)
      fstab.close()
  
  def configure_timezone(self):
      # tzsetup ignores us if these exist
      for tzfile in ('etc/timezone', 'etc/localtime'):
          path = os.path.join(self.target, tzfile)
  
      self.set_debconf('base-config', 'tzconfig/preseed_zone', self.timezone)
      fmisc.pre_log('info','tzsetup -y')
  
  def configure_keymap(self):
      self.set_debconf('debian-installer', 'debian-installer/keymap', self.keymap)
      fmisc.pre_log('into','install-keymap ' + self.keymap)
  
  def configure_user(self):
      fmisc.pre_log('info','passwd -l root')
      self.set_debconf('passwd', 'passwd/username', self.username)
      self.set_debconf('passwd', 'passwd/user-fullname', self.fullname)
      self.set_debconf('passwd', 'passwd/user-password', self.password)
      self.set_debconf('passwd', 'passwd/user-password-again', self.password)
      self.reconfigure('passwd')
  
  def configure_hostname(self):
      sleep(1)
  
  def configure_hardware(self):
      fmisc.pre_log('info','mount -t proc proc /proc')
      fmisc.pre_log('info','mount -t sysfs sysfs /sys')
  
      packages = ['gnome-panel', 'xserver-xorg', 'linux-image-' + self.kernel_version]
      
      try:
          for package in packages:
              self.copy_debconf(package)
              self.reconfigure(package)
      finally:
          fmisc.pre_log('info''umount', '/proc')
          fmisc.pre_log('info''umount', '/sys')
  
  def configure_network(self):
      fmisc.pre_log('info','/usr/share/setup-tool-backends/scripts/network-conf --get > ' + self.target + '/tmp/network.xml')
      fmisc.pre_log('info','/usr/share/setup-tool-backends/scripts/network-conf --set < /tmp/network.xml')
  
  def configure_bootloader(self):
      # Copying the old boot config
      files = ['/etc/lilo.conf', '/boot/grub/menu.lst','/etc/grub.conf',
               '/boot/grub/grub.conf']
      TEST = '/'
      target_dev = self.mountpoints['/']
      grub_dev = fmisc.grub_dev(target_dev)
      distro = self.distro.capitalize()
      proc_file = open('/proc/partitions').readlines()
      parts = []
  
      for entry in proc_file[2:]:
          dev = entry.split()
          if len(dev[3]) == 4:
              parts.append(dev[3])
      fmisc.pre_log('info','mkdir' + TEST)
      for part in parts:
          if fmisc.pre_log('info','mount /dev/%s %s' % (part, TEST)):
              for file in files:
                  if os.path.exists(TEST + file):
                      fmisc.pre_log('info','cp %s %s' % (TEST + file, self.target + file))
                      
              fmisc.pre_log('info','umount ' + TEST)
  
      # The new boot
      fmisc.pre_log('info','/usr/sbin/mkinitrd')
      # For the Grub
      grub_conf = open('/tmp/menu.lst', 'a')
      grub_conf.write(' \
      e %s \
      (%s) \
      el (%s)/vmlinuz-%s root=%s ro vga=791 quiet \
      rd (%s)/initrd.img-%s \
      default ' % \
      (distro, grub_dev, grub_dev, self.kernel_version, target_dev, grub_dev, self.kernel_version) )
  
      grub_conf.close()
  
      # For the Yaboot
      if not os.path.exists('/tmp/etc/yaboot.conf'):
          fmisc.ex('mkdir','/tmp/etc')
          fmisc.make_yaboot_header(self.target, target_dev)
      yaboot_conf = open('/tmp/etc/yaboot.conf', 'a')
      yaboot_conf.write(' \
      default=%s \
      \
      image=/boot/vmlinux-%s \
        label=%s \
        read-only \
        initrd=/boot/initrd.img-%s \
        append="quiet splash" \
      ' % (distro, self.kernel_version, distro, self.kernel_version) )
  
      yaboot_conf.close()
  
      fmisc.pre_log('info','/usr/share/setup-tool-backends/scripts/boot-conf --get > ' + self.target + '/tmp/boot.xml')
      fmisc.pre_log('info','/usr/share/setup-tool-backends/scripts/boot-conf --set < /tmp/boot.xml')
  
  def chrex(self, *args):
    msg = ''
    for word in args:
      msg += str(word) + ' '
    if not fmisc.pre_log('info','chroot ' + self.target + msg):
      post_log('error', 'chroot' + msg)
      return False
    post_log('info', 'chroot' + msg)
    return True

  
  def copy_debconf(self, package):
    sleep(1)
  
  def set_debconf(self, owner, question, value):
    fmisc.pre_log('info', '%s %s %s' % (owner, question, value))
    sleep(1)
  
  def reconfigure(self, package):
    sleep(1)
  

if __name__ == '__main__':
  vars = fmisc.get_var()
  config = Config(vars)
  config.run()
  print 101

# vim:ai:et:sts=2:tw=80:sw=2:
