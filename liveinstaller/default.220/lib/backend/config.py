#!/usr/bin/python

from ue import misc
import debconf

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
    misc.post_log('info', 'Configuring distro')
    if self.get_locales():
      print '92 Configured the hardware and system'
      misc.post_log('info', 'Configured distro')
      return True
    else:
      misc.post_log('error', 'Configuring distro')
      return False
    print '93 Configuring the hardware and system'
    misc.post_log('info', 'Configuring distro')
    if self.configure_fstab():
      print '93 Configured the hardware and system'
      misc.post_log('info', 'Configured distro')
      return True
    else:
      misc.post_log('error', 'Configuring distro')
      return False
    print '94 Configuring the hardware and system'
    misc.post_log('info', 'Configuring distro')
    if self.configure_timezone():
      print '94 Configured the hardware and system'
      misc.post_log('info', 'Configured distro')
      return True
    else:
      misc.post_log('error', 'Configuring distro')
      return False
    print '95 Configuring the hardware and system'
    misc.post_log('info', 'Configuring distro')
    if self.configure_user():
      print '95 Configured the hardware and system'
      misc.post_log('info', 'Configured distro')
      return True
    else:
      misc.post_log('error', 'Configuring distro')
      return False
    print '96 Configuring the hardware and system'
    misc.post_log('info', 'Configuring distro')
    if self.configure_hostname():
      print '96 Configured the hardware and system'
      misc.post_log('info', 'Configured distro')
      return True
    else:
      misc.post_log('error', 'Configuring distro')
      return False
    print '97 Configuring the hardware and system'
    misc.post_log('info', 'Configuring distro')
    if self.configure_hardware():
      print '97 Configured the hardware and system'
      misc.post_log('info', 'Configured distro')
      return True
    else:
      misc.post_log('error', 'Configuring distro')
      return False
    print '98 Configuring the hardware and system'
    misc.post_log('info', 'Configuring distro')
    if self.configure_network():
      print '98 Configured the hardware and system'
      misc.post_log('info', 'Configured distro')
      return True
    else:
      misc.post_log('error', 'Configuring distro')
      return False
    print '99 Configuring the hardware and system'
    misc.post_log('info', 'Configuring distro')
    if self.configure_bootloader():
      print '100 Configured the hardware and system'
      misc.post_log('info', 'Configured distro')
      return True
    else:
      misc.post_log('error', 'Configuring distro')
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
      fstab = open(os.path.join(self.target,'etc/fstab'), 'w')
      for path, device in self.mountpoints.items():
          if path == '/':
              passno = 1
          else:
              passno = 2
  
          filesystem = 'ext3'
          options = 'defaults'
          
          print >>fstab, '%s\t%s\t%s\t%s\t%d\t%d' % (device, path, filesystem, options, 0, passno)
      fstab.close()
  
  def configure_timezone(self):
      # tzsetup ignores us if these exist
      for tzfile in ('etc/timezone', 'etc/localtime'):
          path = os.path.join(self.target, tzfile)
          if os.path.exists(path):
              os.unlink(path)
  
      self.set_debconf('base-config', 'tzconfig/preseed_zone', self.timezone)
      self.chrex('tzsetup', '-y')
  
  def configure_keymap(self):
      self.set_debconf('debian-installer', 'debian-installer/keymap', self.keymap)
      self.chrex('install-keymap', self.keymap)
  
  def configure_user(self):
      self.chrex('passwd', '-l', 'root')
      self.set_debconf('passwd', 'passwd/username', self.username)
      self.set_debconf('passwd', 'passwd/user-fullname', self.fullname)
      self.set_debconf('passwd', 'passwd/user-password', self.password)
      self.set_debconf('passwd', 'passwd/user-password-again', self.password)
      self.reconfigure('passwd')
  
  def configure_hostname(self):
      fp = open(os.path.join(self.target, 'etc/hostname'), 'w')
      print >>fp, self.hostname
      fp.close()
  
  def configure_hardware(self):
      self.chrex('mount', '-t', 'proc', 'proc', '/proc')
      self.chrex('mount', '-t', 'sysfs', 'sysfs', '/sys')
  
      packages = ['gnome-panel', 'xserver-xorg', 'linux-image-' + self.kernel_version]
      
      try:
          for package in packages:
              self.copy_debconf(package)
              self.reconfigure(package)
      finally:
          self.chrex('umount', '/proc')
          self.chrex('umount', '/sys')
  
  def configure_network(self):
      misc.ex('/usr/share/setup-tool-backends/scripts/network-conf','--get',
      '>',self.target + '/tmp/network.xml')
      self.chex('/usr/share/setup-tool-backends/scripts/network-conf','--set',
      '<','/tmp/network.xml')
  
  def configure_bootloader(self):
      # Copying the old boot config
      files = ['/etc/lilo.conf', '/boot/grub/menu.lst','/etc/grub.conf',
               '/boot/grub/grub.conf']
      TEST = '/mnt/test/'
      target_dev = self.mountpoints['/']
      grub_dev = misc.grub_dev(target_dev)
      distro = self.distro.capitalize()
      proc_file = open('/proc/partitions').readlines()
      parts = []
  
      for entry in proc_file[2:]:
          dev = entry.split()
          if len(dev[3]) == 4:
              parts.append(dev[3])
      misc.ex('mkdir', TEST)
      for part in parts:
          if misc.ex('mount', '/dev/' + part , TEST):
              for file in files:
                  if os.path.exists(TEST + file):
                      misc.ex('cp', TEST + file, self.target + file)
                      
              misc.ex('umount', TEST)
  
      # The new boot
      self.chex('/usr/sbin/mkinitrd')
      # For the Grub
      grub_conf = open(self.target + '/boot/grub/menu.lst', 'a')
      grub_conf.write(' \
      e %s \
      (%s) \
      el (%s)/vmlinuz-%s root=%s ro vga=791 quiet \
      rd (%s)/initrd.img-%s \
      default ' % \
      (distro, grub_dev, grub_dev, self.kernel_version, target_dev, grub_dev, self.kernel_version) )
  
      grub_conf.close()
  
      # For the Yaboot
      if not os.path.exists(self.target + '/etc/yaboot.conf'):
          misc.make_yaboot_header(self.target, target_dev)
      yaboot_conf = open(self.target + '/etc/yaboot.conf', 'a')
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
  
      misc.ex('/usr/share/setup-tool-backends/scripts/boot-conf','--get',
      '>',self.target + '/tmp/boot.xml')
      self.chex('/usr/share/setup-tool-backends/scripts/boot-conf','--set',
      '<','/tmp/boot.xml')
  
  def chrex(self, *args):
    msg = ''
    for word in args:
      msg += str(word) + ' '
    if not misc.ex('chroot', self.target, *args):
      post_log('error', 'chroot' + msg)
      return False
    post_log('info', 'chroot' + msg)
    return True

  
  def copy_debconf(self, package):
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
          self.chrex('dpkg-reconfigure', '-fnoninteractive', package)
  

if __name__ == '__main__':
  vars = misc.get_var()
  config = Config(vars)
  config.run()
  print 101

# vim:ai:et:sts=2:tw=80:sw=2:
