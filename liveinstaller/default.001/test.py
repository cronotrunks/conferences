#!/usr/bin/python
#
import gtk.glade
import gnome.ui
import os, re, gobject, gettext

DIR = './locale'
DIRNAME = '/usr/share/zoneinfo/'

class FrontendInstaller:

  def __init__(self):
    # internationalization config
    gettext.bindtextdomain("test.py", DIR )
    gtk.glade.bindtextdomain("test.py", DIR )
    gtk.glade.textdomain("test.py")
    gettext.textdomain("test.py")
    gettext.install("test.py",DIR,unicode=1)
    
    # load the interface
    self.main_window = gtk.glade.XML('liveinstaller.glade')
    
    # declare widget objects
    welcome = self.main_window.get_widget('welcome')
    final = self.main_window.get_widget('final')
    self.timezone = self.main_window.get_widget('timezone')
    self.progressbar = self.main_window.get_widget('progressbar')
    
    # show and design start and end page
    welcome.show()
    final.show()
    
    #welcome.set_bg_color(gtk.gdk.color_parse("#087021"))
    welcome.set_logo(gtk.gdk.pixbuf_new_from_file("pixmaps/logo.png"))
    final.set_bg_color(gtk.gdk.color_parse("#087021"))
    final.set_logo(gtk.gdk.pixbuf_new_from_file("pixmaps/logo.png"))
    
    # Fill timezone GtkComboBoxEntry 
    lista = gtk.ListStore(gobject.TYPE_STRING)
    
    for root, dirs, files in os.walk(DIRNAME, topdown=False):
      for name in files:
	pointer = os.path.join(root, name).split(DIRNAME)[1]
	if not re.search('right|posix|SystemV|Etc', pointer) and re.search('/', pointer):
	  lista.append([pointer])
    
    #self.timezone.set_model(lista)
    #self.timezone.set_text_span_column(0)
    
    # ProgressBar shows data
    self.progressbar.set_percentage(.75)
    
    # Declare SignalHandler
    self.main_window.signal_autoconnect(FrontendInstaller.GladeHandlers.__dict__)

  def main(self):
    gtk.main()

  class GladeHandlers:
    # Funciones para manejar los eventos de glade
    def on_frontend_installer_cancel(self):
      gtk.main_quit()
    
    def on_live_installer_delete_event(self, widget):
      gtk.main_quit()

if __name__ == '__main__':
  installer = FrontendInstaller()
  installer.main()
