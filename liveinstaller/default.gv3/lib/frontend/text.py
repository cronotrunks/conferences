# -*- coding: utf-8 -*-

'''
Text Frontend

Text frontend implementation for the installer
'''

class Wizard:
  def __init__(self):
    print "Welcome to the UbuntuExpress"

  def set_progress(self,num):
    for i in range(0,num):
      print ".",
    print "\n%d " % num

  def get_hostname(self):
    print "Please enter the hostname for this system."
    hostname = raw_input("Hostname: ")
    return hostname

  def get_locales(self):
    pass

  def get_user(self):
    pass

  def get_partitions(self):
    pass
  
# vim:ai:et:sts=2:tw=80:sw=2:
