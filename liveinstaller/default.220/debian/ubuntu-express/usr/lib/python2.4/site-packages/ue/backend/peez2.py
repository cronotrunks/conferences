# -*- coding: utf-8 -*-

""" U{pylint<http://logilab.org/projects/pylint>} mark: 9.07 """

# File "peez2.py".
# Automatic partitioning with "peez2".
# Created by Antonio Olmo <aolmo@emergya.info> on 25 august 2005.
# Last modified on 29 august 2005.

# TODO: improve "locale" detection.

from popen2 import Popen3

# Index:
# def get_drives ():
# def get_info (drive):
# def get_commands (drive):
# def call_peez2 (args):

locale = 'es'
binary = 'peez2'
common_arguments = '2> /dev/null'
    
# Function "get_drives" ______________________________________________________

def get_drives ():

    """ Retrieve the list of drives in the computer. """

    result = []

    lines = call_peez2 () ['out']

    for i in lines:

        if 'LD#' == i [:3]:
            fields = i [3:].split ('|')

            if 'es' == locale:
                drive = {}

                for j in fields:

                    if 'Medio:' == j [:6]:
                        drive ['no'] = int (j [6:])
                    elif 'Modelo:' == j [:7]:
                        drive ['name'] = j [7:]
                    elif 'Ruta:' == j [:5]:
                        drive ['device'] = j [5:]
                    elif 'Total:' == j [:6]:
                        drive ['size'] = int (j [6:])

                result.append (drive)
            elif 'en' == locale:
                drive = {}

                for j in fields:

                    if 'Media:' == j [:6]:
                        drive ['no'] = int (j [6:])
                    elif 'Model:' == j [:6]:
                        drive ['name'] = j [6:]
                    elif 'Path:' == j [:5]:
                        drive ['device'] = j [5:]
                    elif 'Total:' == j [:6]:
                        drive ['size'] = int (j [6:])

                result.append (drive)

    return result

# Function "get_info" ________________________________________________________

def get_info (drive):

    """ Retrieve information about a drive. """

    result = None

    lines = call_peez2 ('-d ' + drive) ['out']

    for i in lines:

        if 'AA#' == i [:3]:

            if None == result:
                result = {}

            if not result.has_key ('warn'):
                result ['warn'] = []

            result ['warn'].append (i [3:-1])
        elif 'VV#' == i [:3]:

            if None == result:
                result = {}

            if 'es' == locale:

                if 'Particiones primarias totales:' == i [3:33]:
                    result ['prim'] = i [33:-1]
                elif 'Particiones extendidas:' == i [3:26]:
                    result ['ext'] = int (i [26:])
                elif 'Particiones l' == i [3:16] and 'gicas:' == i [17:23]:
                    result ['logic'] = int (i [23:])
                elif 'Espacios libres:' == i [3:19]:
                    result ['free'] = int (i [19:])
                elif 'Particiones de linux:' == i [3:24]:
                    result ['linux'] = int (i [24:])
                elif 'Particiones de Windows(TM):' == i [3:30]:
                    result ['win'] = int (i [30:])
                elif 'Disk Status#' == i [3:15]:

                    if not result.has_key ('status'):
                        result ['status'] = []

                    (result ['status']).append (i [15:-1])

            elif 'en' == locale:

                if 'Total primary partitions:' == i [3:28]:
                    result ['prim'] = i [28:-1]
                elif 'Total extended partitions:' == i [3:29]:
                    result ['ext'] = int (i [29:])
                elif 'Total logical partitions:' == i [3:28]:
                    result ['logic'] = int (i [28:])
                elif 'Total free spaces:' == i [3:21]:
                    result ['free'] = int (i [21:])
                elif 'Total linux partitions:' == i [3:26]:
                    result ['linux'] = int (i [26:])
                elif 'Total win partitions:' == i [3:24]:
                    result ['win'] = int (i [24:])
                elif 'Disk Status#' == i [3:15]:

                    if not result.has_key ('status'):
                        result ['status'] = []

                    (result ['status']).append (i [15:-1])

    return result

# Function "get_commands" ____________________________________________________

def get_commands (drive):

    """ Get the recommended sequence of partitioning commands, if any. """

    result = []

    child = call_peez2 ('-a wizard -i -d ' + drive)
    # TODO: parse I/O.
    print child

    # For every command found:
    result.append (None)

    return result

# Function "call_peez2" ______________________________________________________

def call_peez2 (args = ''):

    """ Execute "peez2" with arguments provided, if any. """

    child = Popen3 (binary + ' ' + common_arguments + ' ' + args)

    return {'out': child.fromchild,
            'in':  child.tochild,
            'err': child.childerr}

# End of file.

