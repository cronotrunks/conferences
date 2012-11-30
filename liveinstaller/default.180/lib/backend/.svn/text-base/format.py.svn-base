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
                misc.ex('mkfs.ext3','device')
            except:
                return False
        elif path == 'swap':
            try:
                misc.ex('mkswap','device')
            except:
                return False
    return True

if __name__ == '__main__':
  mountpoints = get_var()
  format_target(mountpoints)

# vim:ai:et:sts=2:tw=80:sw=2:
