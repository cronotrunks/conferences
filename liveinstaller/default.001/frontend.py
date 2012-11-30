#!/usr/bin/python
#

import pygtk
pygtk.require('2.0')
import gtk.glade
import gnome.ui
import gtkmozembed
from sys import exit
from pango import FontDescription
from gettext import bindtextdomain, textdomain, install
from locale import setlocale, LC_ALL

# Define locale path
DIR = './locale'

class FrontendInstaller:
  """FrontendInstaller class to manage druid installer through backend script"""
  
  def __init__(self):
    # set custom language
    self.set_locales()
    
    # load the interface
    self.main_window = gtk.glade.XML('liveinstaller.glade')
    self.show_browser()
    self.show_end()
    
    # set style
    self.installer_style()
    
    # Declare SignalHandler
    self.main_window.signal_autoconnect(self)

    # socket tests
    socket = gtk.Socket()
    socket.show()
    self.main_window.get_widget('embedded').add(socket)
    print "Socket ID=", socket.get_id()
    socket.connect("plug-added", self.plugged_event, "inserted")

  def plugged_event(widget):
    print "I (",widget,") have just had a plug inserted!"

  def set_locales(self):
    """internationalization config. Use only once."""
    
    bindtextdomain("frontend.py", DIR )
    gtk.glade.bindtextdomain("frontend.py", DIR )
    gtk.glade.textdomain("frontend.py")
    textdomain("frontend.py")
    install("frontend.py", DIR, unicode=1)

  def show_browser(self):
    """Embed Mozilla widget into Druid."""
    
    widget = gtkmozembed.MozEmbed()
    widget.load_url("http://www.gnome.org/")
    widget.get_location()
    self.main_window.get_widget('vbox1').add(widget)
    widget.show()

  def installer_style(self):
    """Set installer screen styles."""
    
    # set screen styles
    self.main_window.get_widget('installing_title').modify_font(FontDescription('Helvetica 30'))
    self.main_window.get_widget('installing_title').modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#087021"))
    self.main_window.get_widget('installing_text').modify_font(FontDescription('Helvetica 12'))
    self.main_window.get_widget('installing_text').modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#087021"))
    
    # set fullscreen mode
    #self.main_window.get_widget('live_installer').fullscreen()
    self.main_window.get_widget('live_installer').show()

  def show_end(self):
    """show and design end page."""
    
    final = self.main_window.get_widget('final')
    final.set_bg_color(gtk.gdk.color_parse("#087021"))
    final.set_logo(gtk.gdk.pixbuf_new_from_file("pixmaps/logo.png"))
    final.modify_font(FontDescription('Helvetica 14'))
    final.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#087021"))
    final.show()

  def main(self):
    gtk.main()

#  def get_language(self):
#    return self.main_window.get_widget('language').get_active_text()
#
#  def get_timezone(self):
#    return self.main_window.get_widget('timezone').get_active_text()

  def get_username(self):
    """get text attribute from username widget."""
    
    return self.main_window.get_widget('username').get_property('text')

  def get_password(self):
    """get text attribute from password widget."""
    
    return self.main_window.get_widget('password').get_property('text')

  def get_hostname(self):
    """get text attribute from hostname widget."""
    
    return self.main_window.get_widget('hostname').get_property('text')

  def set_progress(self, value, text="", image=""):
    """ - Set value attribute to progressbar widget.
        - Modifies Splash Ad Images from distro usage.
        - Modifies Ad texts about distro images. """

    self.main_window.get_widget('progressbar').set_percentage(value/100.0)
    if ( text != "" ):
      buffer = self.main_window.get_widget('installing_text').get_buffer()
      buffer.set_text(text)
      self.main_window.get_widget('installing_image').set_from_file(image)

  def on_frontend_installer_cancel(self, widget):
    gtk.main_quit()

  def on_live_installer_delete_event(self, widget):
    raise Signals("on_live_installer_delete_event")

class Signals(Exception):
  """Base class for exceptions in this module."""

  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

if __name__ == '__main__':
    installer = FrontendInstaller()
    try:
      installer.main()
    except Signals, instance:
      print instance.value
      exit()
