# -*- coding: utf-8 -*-

"""
Noui Frontend

Noui frontend implementation for the installer
This UI implementation consist actually in no UI at all.
It means it's a no interactive method to get the answers.
We don't ask because the answers already exists.

To do that we need to preseed the answers. We'll use a new debconf
package called "express" for this prupose.
We'll take some answers form the express package and others from 
the system. It's because of the user could change some stuff
like timezone, keymap and locales.
"""

import debconf
    
from ue.backend.part import call_autoparted, call_gparted


class Wizard:
  '''
  This is a wizard interface to interact with the user and the 
  main program. It has some basic methods:
   - set_progress()
   - get_info()
   - get_partitions()
  '''
  def __init__(self):
    debconf.runFrontEnd()
    self.db = debconf.Debconf()

  def set_progress(self,num,msg=''):
    '''set_progress(num, msg='') -> none

    Put the progress bar in the 'num' percent and if
    there is any value in 'msg', this method print it.
    '''
    print "%d\t%s" % (num,msg)

  def get_info(self):
    '''get_info() -> [hostname, fullname, name, password]

    Get from the Debconf database the information about
    hostname and user. Return a list with those values.
    '''
    info = []
    # Just for tests. We should use a especific package for this
    # It seems to be because of the installer preseed, so it could be
    # a good idea something like:
    # info.append(self.db.get('express/username'))
    info.append(self.db.get('base-config/get-hostname'))
    info.append(self.db.get('passwd/user-fullname'))
    info.append(self.db.get('passwd/username'))
    info.append(self.db.get('passwd/user-password'))
    return info
    
  def get_partitions(self):
    '''get_partitions() -> dict {'mount point' : 'dev'}

    Get the information to be able to partitioning the disk.
    Partitioning the disk and return a dict with the pairs
    mount point and device.
    At least, there must be 2 partitions: / and swap.
    '''
    #FIXME: We've to put here the autopartitioning stuff
    
    # This is just a example info.
    # We should take that info from the debconf
    # Something like:
    # re = self.db.get('express/mountpoints')
    # for path, dev in re:
    #   mountpoints[path] = dev
    mountpoints = {'/'     : '/dev/hda1',
                   'swap'  : '/dev/hda2',
                   '/home' : '/dev/hda3'}
    mountpoints = call_autoparted()
    if mountpoints is None:
      print 'Autopartioning fail!'

    return mountpoints
 
if __name__ == '__main__':
  w = Wizard()
  hostname, fullname, name, password = w.get_info()
  print '''
  Hostname: %s
  User Full name: %s
  Username: %s
  Password: %s
  Mountpoints : %s
  ''' % (hostname, fullname, name, password, w.get_partitions())

# vim:ai:et:sts=2:tw=80:sw=2:
