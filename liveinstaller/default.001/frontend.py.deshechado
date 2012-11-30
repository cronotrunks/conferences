#!/usr/bin/python
#
import gtk.glade
import gnome.ui
import os, re, gobject, gettext

# Define locale path
DIR = './locale'

# Define timezones path
DIRNAME = '/usr/share/zoneinfo/'

# Define screens to show (per distro)
# ['welcome', 'timezone', 'user&pass', 'hostname', 'network', 'partitioning',
# 'progress', 'final']

GUADALINEX = [1, 0, 1, 0, 1, 1, 1, 1]
UBUNTU = [1, 1, 1, 1, 1, 1, 1, 1]
### Sacar procentajes de progreso a partir de la cantidad de 1's ###

# Distro selected
DISTRO = GUADALINEX

class FrontendInstaller:

  def __init__(self):
    # load the interface
    self.main_window = gtk.glade.XML('liveinstaller.glade')
    self.show_start()
    self.show_end()
    self.fill_combo()
    
    # Declare SignalHandler
    self.main_window.signal_autoconnect(GladeHandlers.__dict__)

  def set_locales():
    # internationalization config
    gettext.bindtextdomain("frontend.py", DIR )
    gtk.glade.bindtextdomain("frontend.py", DIR )
    gtk.glade.textdomain("frontend.py")
    gettext.textdomain("frontend.py")
    gettext.install("frontend.py", DIR, unicode=1)

# show and design start and end page
  def show_start(self):
    welcome = self.main_window.get_widget('welcome')
    welcome.show()
    welcome.set_bg_color(gtk.gdk.color_parse("#087021"))
    welcome.set_logo(gtk.gdk.pixbuf_new_from_file("pixmaps/logo.png"))

  def show_end(self):
    final = self.main_window.get_widget('final')
    final.show()
    final.set_bg_color(gtk.gdk.color_parse("#087021"))
    final.set_logo(gtk.gdk.pixbuf_new_from_file("pixmaps/logo.png"))

  def fill_combo(self):
    # Fill timezone GtkComboBoxEntry
    lista = gtk.ListStore(gobject.TYPE_STRING)
    
    for root, dirs, files in os.walk(DIRNAME, topdown=False):
      for name in files:
	pointer = os.path.join(root, name).split(DIRNAME)[1]
	if not re.search('right|posix|SystemV|Etc', pointer) and re.search('/', pointer):
	  lista.append([pointer])
    
    self.main_window.get_widget('timezone').set_model(lista)
    self.main_window.get_widget('timezone').set_text_column(0)

  def main(self):
    gtk.main()

# get and set attributes methods
  def set_preseed(self):
    '''Set values to preseed in the installation proccess'''
    
    #self.set_language("tested")
    #self.set_timezone("tested")
    #self.set_username("tested")
    #self.set_password("tested")
    #self.set_hostname("tested")

  def get_language(self):
    return self.main_window.get_widget('language').get_active_text()

  def set_language(self, int):
    self.main_window.get_widget('language').set_active(int)

  def get_timezone(self):
    return self.main_window.get_widget('timezone').get_active_text()

  def set_timezone(self,int):
    self.main_window.get_widget('timezone').set_active(int)

  def get_username(self):
    return self.main_window.get_widget('username').get_property('text')

  def set_username(self, text):
    self.main_window.get_widget('username').set_property('text', text)

  def get_password(self):
    return self.main_window.get_widget('password').get_property('text')

  def set_password(self, text):
    self.main_window.get_widget('password').set_property('text', text)

  def get_hostname(self):
    return self.main_window.get_widget('hostname').get_property('text')

  def set_hostname(self, text):
    self.main_window.get_widget('hostname').set_property('text', text)

  def get_progress(self):
    return self.main_window.get_widget('progressbar').get_value()

  def set_progress(self, value):
    self.main_window.get_widget('progressbar').set_percentage(value)

# Events Handler
class GladeHandlers:
  def on_frontend_installer_cancel(self):
    gtk.main_quit()
  
  def on_live_installer_delete_event(self, widget):
    gtk.main_quit()

if __name__ == '__main__':
  installer = FrontendInstaller()
  installer.main()
