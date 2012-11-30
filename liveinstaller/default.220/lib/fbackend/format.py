#!/usr/bin/python

from ue import misc
from time import sleep

def format_target(mountpoints):
    '''format_target(mountpoints) -> bool

    From mountpoints extract the devices to partition 
    and do it.
    The method return true or false depends the result
    of this operation.
    '''
    for path, device in mountpoints.items():
        if path in ['/']:
            print "0 Preparing the disc"
            misc.pre_log('info','mkfs.ext3' + device)
            sleep(2)
            print "2 Preparing the disc"
        elif path == 'swap':
            misc.pre_log('info', 'mkswap' + device)
            sleep(2)
            print "3 Preparing the disc"
    return True

if __name__ == '__main__':
  mountpoints = misc.get_var()['mountpoints']
  format_target(mountpoints)

# vim:ai:et:sts=2:tw=80:sw=2:
