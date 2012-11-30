#!/usr/bin/python

import pygtk
pygtk.require('2.0')

import gtk.glade
import gnome.ui
import gtkmozembed
import subprocess
import os
from sys import exit
from threading import Thread
from pango import FontDescription
from gettext import bindtextdomain, textdomain, install
from locale import setlocale, LC_ALL

from ue.backend.part import call_autoparted, call_gparted
from ue.validation import *


# Define Ubuntu Express global path
PATH = '/usr/share/ubuntu-express'

# Define glade path
GLADEDIR = PATH + '/glade'

# Define locale path
LOCALEDIR = GLADEDIR + '/locale'


class Wizard:
  '''
  Gtk+ Frontend
  
  This is a wizard interface to interact with the user and the 
  main program. It has some basic methods:
  - set_progress()
  - get_info()
  - get_partitions()
  '''
  # Interfce with the main program
  def get_info(self):
    '''get_info() -> [hostname, fullname, name, password]

    Return a list with those values.
    '''
    return self.info

  def set_progress(self, num, msg=""):
    '''set_progress(num, msg='') -> none

    Put the progress bar in the 'num' percent and if
    there is any value in 'msg', this method print it.
    '''
    """ - Set value attribute to progressbar widget.
        - Modifies Splash Ad Images from distro usage.
        - Modifies Ad texts about distro images. """

    self.progressbar.set_percentage(num/100.0)
    if ( msg != "" ):
      gtk.TextBuffer.set_text(self.installing_text.get_buffer(), msg)

  def get_partitions(self):
    '''get_partitions() -> dict {'mount point' : 'dev'}

    Get the information to be able to partitioning the disk.
    Partitioning the disk and return a dict with the pairs
    mount point and device.
    At least, there must be 2 partitions: / and swap.
    '''
    return self.mountpoints

  def is_active(self):
    return self.installation

  # Constructor and insternal methods
  def __init__(self, distro):
    # define some vars
    self.installation = False
    self.checked_partitions = False
    self.info = []
    
    # set custom language
    self.set_locales(distro)
    
    # load the interface
    self.main_window = gtk.glade.XML('%s/liveinstaller.glade' % GLADEDIR)
    
    # declare attributes
    self.distro = distro

    # Buttons
    self.help = self.main_window.get_widget('help')
    self.cancel = self.main_window.get_widget('cancel')
    self.back = self.main_window.get_widget('back')
    self.next = self.main_window.get_widget('next')
    self.back.hide()
    self.help.hide()
    self.next.set_label('gtk-media-next')
    
    self.steps = self.main_window.get_widget('steps')
    
    self.live_installer = self.main_window.get_widget('live_installer')
    self.browser_vbox = self.main_window.get_widget('browser_vbox')
    self.embedded = self.main_window.get_widget('embedded')
    
    self.installing_text = self.main_window.get_widget('installing_text')
    self.installing_image = self.main_window.get_widget('installing_image')
    self.installing_title = self.main_window.get_widget('installing_title')
    self.progressbar = self.main_window.get_widget('progressbar')
    self.final_title = self.main_window.get_widget('final_title')
    
    self.user_image = self.main_window.get_widget('user_image')
    self.lock_image = self.main_window.get_widget('lock_image')
    self.host_image = self.main_window.get_widget('host_image')
    self.logo_image = self.main_window.get_widget('logo_image')
    self.logo_image1 = self.main_window.get_widget('logo_image1')
    self.logo_image2 = self.main_window.get_widget('logo_image2')
    self.logo_image3 = self.main_window.get_widget('logo_image3')
    self.logo_image4 = self.main_window.get_widget('logo_image4')
    
    self.fullname = self.main_window.get_widget('fullname')
    self.username = self.main_window.get_widget('username')
    self.password = self.main_window.get_widget('password')
    self.verified_password = self.main_window.get_widget('verified_password')
    self.hostname = self.main_window.get_widget('hostname')
    
    # set style
    self.installer_style()
    
  def run(self):
    # show interface
    self.show_browser()
    
    # Declare SignalHandler
    self.main_window.signal_autoconnect(self)
    gtk.main()


  def set_locales(self, distro):
    """internationalization config. Use only once."""
    
    final_localedir = LOCALEDIR + '/' + distro
    bindtextdomain("liveinstaller", final_localedir)
    gtk.glade.bindtextdomain("liveinstaller", final_localedir )
    gtk.glade.textdomain("liveinstaller")
    textdomain("liveinstaller")
    install("liveinstaller", final_localedir, unicode=1)

  def show_browser(self):
    """Embed Mozilla widget into Druid."""
    
    widget = gtkmozembed.MozEmbed()
    try:
      widget.load_url("file://" + PATH + '/htmldocs/' + self.distro + '/index.html')
    except:
      widget.load_url("http://www.ubuntulinux.org/")
    widget.get_location()
    self.browser_vbox.add(widget)
    widget.show()

  def installer_style(self):
    """Set installer screen styles."""
    
    # set pixmaps
    self.logo_image.set_from_file("%s/pixmaps/%s/%s" %(GLADEDIR, self.distro, "logo.png"))
    self.logo_image1.set_from_file("%s/pixmaps/%s/%s" %(GLADEDIR, self.distro, "logo.png"))
    self.logo_image2.set_from_file("%s/pixmaps/%s/%s" %(GLADEDIR, self.distro, "logo.png"))
    self.logo_image3.set_from_file("%s/pixmaps/%s/%s" %(GLADEDIR, self.distro, "logo.png"))
    self.logo_image4.set_from_file("%s/pixmaps/%s/%s" %(GLADEDIR, self.distro, "logo.png"))
    self.user_image.set_from_file("%s/pixmaps/%s/%s" %(GLADEDIR, self.distro, "users.png"))
    self.lock_image.set_from_file("%s/pixmaps/%s/%s" %(GLADEDIR, self.distro, "lockscreen_icon.png"))
    self.host_image.set_from_file("%s/pixmaps/%s/%s" %(GLADEDIR, self.distro, "nameresolution_id.png"))
    self.installing_image.set_from_file("%s/pixmaps/%s/%s" %(GLADEDIR, self.distro, "snapshot1.png"))
    
    # set fullscreen mode
    self.live_installer.fullscreen()
    self.live_installer.show()

  def check_partitions(self):
    #FIXME: Check if it's possible to run the partman-auto
    # if not, will run the Gparted
    
    # This is just a example info.
    # We should take that info from the debconf
    # Something like:
    # re = self.db.get('express/mountpoints')
    # for path, dev in re:
    #   mountpoints[path] = dev
    self.mountpoints = {'/'     : '/dev/hda1',
                        'swap'  : '/dev/hda2',
                        '/home' : '/dev/hda3'}
                   
    self.mountpoints = call_autoparted()
    if self.mountpoints is None:
        self.mountpoints = call_gparted(self.main_window)

    self.checked_partitions = True
    return self.mountpoints

  def images_loop(self):
    import time, glob
    while self.steps.get_current_page() == 4:
      for image in glob.glog("%s/pixmaps/%s/snapshot*.png" % (GLADEDIR, self.distro)):
        self.installing_image.set_from_file(image)
        time.sleep(2)
        
  def info_loop(self):
    #FIXME: We need here a loop
    self.info = []
    self.info.append(self.hostname.get_property('text'))
    self.info.append(self.fullname.get_property('text'))
    self.info.append(self.username.get_property('text'))
    pass1 = self.password.get_property('text')
    pass2 = self.verified_password.get_property('text')
    check = check_password(pass1, pass2)
    print check
    if  check == 0:
      self.info.append(pass1)
    elif check == 1:
    #  self.pass_alert.set_text('Wrong size!')
      self.info.append(pass1)
    elif check == 2:
    #  self.pass_alert.set_text('The passwords doesn\'t match!')
      self.info.append(pass1)


  # Callbacks
  def on_cancel_clicked(self, widget):
    gtk.main_quit()

  def on_next_clicked(self, widget):
    step = self.steps.get_current_page()
    if step == 0:
      self.next.set_label('gtk-go-forward')
      self.help.show()
    elif step == 1:
      if not self.checked_partitions:
        self.check_partitions()
      self.info_loop()
      self.back.show()
      self.browser_vbox.destroy()
    elif step == 3:
      self.back.hide()
      self.help.hide()
      self.embedded.destroy()
      #self.child = Thread(target=self.images_loop())
      #self.child.run()
      self.installation = True
    elif step == 4:
      self.next.set_label('Finish and Reboot')
      #FIXME: Change the method called to reboot
      self.next.connect('clicked', lambda *x: gtk.main_quit())
      self.back.set_label('Just Finish')
      self.back.connect('clicked', lambda *x: gtk.main_quit())
      self.back.show()
      self.cancel.hide()
      
    if step is not 5:
      self.steps.next_page()
    
  def on_back_clicked(self, widget):
    step = self.steps.get_current_page()
    if step == 2:
      self.back.hide()
    
    if step is not 5:
      self.steps.prev_page()

  def on_live_installer_delete_event(self, widget):
    gtk.main_quit()


if __name__ == '__main__':
  # Guadalinex HexColor style #087021
  # Ubuntu HexColor style #9F6C49
  w = Wizard('ubuntu')
  w.run()
  [hostname, fullname, name, password] = w.get_info()
  print '''
  Hostname: %s
  User Full name: %s
  Username: %s
  Password: %s
  Mountpoints : %s
  ''' % (hostname, fullname, name, password, w.get_partitions())

# vim:ai:et:sts=2:tw=80:sw=2:
