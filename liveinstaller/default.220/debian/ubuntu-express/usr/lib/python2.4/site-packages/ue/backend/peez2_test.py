#!/usr/bin/python
# -*- coding: utf-8 -*-

# File "peez2_test.py".
# Testing the "peez2" library.
# Created by Antonio Olmo <aolmo@emergya.info> on 29 august 2005.

from peez2 import *

drives = get_drives ()

for i in drives:
    print '%i\t%s\t%i\t%s' % (i ['no'], i ['name'], i ['size'], i ['device'])

for i in drives:
    info = get_info (i ['device'])

    print info ['prim']
    print info ['ext']
    print info ['logic']
    print info ['free']
    print info ['linux']
    print info ['win']

    for j in info ['status']:
        print j

    if info.has_key ('warn'):

        for j in info ['warn']:
            print j

# End of file.

