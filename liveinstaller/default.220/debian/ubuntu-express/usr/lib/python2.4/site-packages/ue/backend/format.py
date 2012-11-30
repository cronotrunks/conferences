#!/usr/bin/python

from ue import misc

def format_target(mountpoints):
    '''format_target(mountpoints) -> bool

    From mountpoints extract the devices to partition 
    and do it.
    The method return true or false depends the result
    of this operation.
    '''
    for path, device in mountpoints.items():
        if path in ['/']:
            try:
                print "0 Preparing the disc"
                misc.ex('mkfs.ext3', device)
                print "2 Preparing the disc"
            except:
                return False
        elif path == 'swap':
            try:
                misc.ex('mkswap', device)
                print "3 Preparing the disc"
            except:
                return False
    return True

if __name__ == '__main__':
  mountpoints = misc.get_var()['mountpoints']
  format_target(mountpoints)

# vim:ai:et:sts=2:tw=80:sw=2:
