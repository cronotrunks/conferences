#!/usr/bin/python

""" Tiny program to test automatic partitioning through "Peez2". """

from sys              import stderr, stdin, exit
from ue.backend.peez2 import Peez2

# Enable next variable during debugging:
DEBUGGING_STATUS = False
ACTUAL_PARTITIONING = True

assistant = Peez2 (debug = DEBUGGING_STATUS)
available_drives = assistant.get_drives ()

##############################################################################
# 1. Select one drive among availables:

if len (available_drives) > 1:
    stderr.write ('Please choose one drive:\n')
    i = 0

    while i < len (available_drives):
        stderr.write ('\t%i - %s\n' % (i, available_drives [i] ['label']))
        i = i + 1

    selected_drive = int (stdin.readline ().strip ())
elif len (available_drives) is 1:
    selected_drive = 0
    stderr.write ('(Selected drive is "%s".)\n' % \
                  available_drives [selected_drive] ['label'])
else:
    stderr.write ('No drive was found!\n')
    exit (1)

drive = available_drives [selected_drive]

##############################################################################
# 2. Select one partitioning method among availables:

available_methods = [['Freespace', None]]

if drive.has_key ('linux_before'):

    if drive ['linux_before'] is not None:
        where = ''

        for i in drive ['linux_before'].keys ():
            where = where + drive ['linux_before'] [i] + ' in ' + \
                    i + ', '

        where = where [:-2]
        available_methods.append (['Recycle', where])

if len (available_methods) > 1:
    stderr.write ('Please choose one partitioning method:\n')
    i = 0

    while i < len (available_methods):
        stderr.write ('\t%i - %s\n' % (i, available_methods [i] [0]))
        i = i + 1

    selected_method = int (stdin.readline ().strip ())
else:
    selected_method = 0
    stderr.write ('(Selected method is "%s".)\n' % \
                  available_methods [selected_method] [0])

method = available_methods [selected_method] [1]

##############################################################################
# 3. Perform partitioning, asking the user for confirmation first:

if method is None:
    stderr.write ('Are you sure you want to perform partitioning? (yes/no):\n')

    if 'yes' == str (stdin.readline ().strip ()).lower ():
        stderr.write ('Performing partitining, please wait...\n')
        result = assistant.auto_partition (drive, do_it = ACTUAL_PARTITIONING)

        if result is None:
            stderr.write ('Something failed!\n')
        else:
            where = ''

            for i in result.keys ():
                where = where + result [i] + ' in ' + \
                        i + ', '

            where = where [:-2]
            stderr.write ('Result: %s.\n' % where)

    else:
        exit (0)
        
else:
    stderr.write ('Result: %s.\n' % method)

# End of file.

