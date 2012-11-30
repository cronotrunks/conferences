# -*- coding: utf-8 -*-

# «peez2» - particionamiento automático a través de la herramienta «Peez2»
# 
# Copyright (C) 2005 Junta de Andalucía
# 
# Autor/es (Author/s):
# 
# - Antonio Olmo Titos <aolmo#emergya._info>
# - Mantas Kriauciunas <mantas#akl._lt>
# 
# Este fichero es parte del instalador en directo de Guadalinex 2005.
#
# El instalador en directo de Guadalinex 2005 es software libre. Puede
# redistribuirlo y/o modificarlo bajo los términos de la Licencia Pública
# General de GNU según es publicada por la Free Software Foundation, bien de la
# versión 2 de dicha Licencia o bien (según su elección) de cualquier versión
# posterior. 
# 
# El instalador en directo de Guadalinex 2005 se distribuye con la esperanza de
# que sea útil, pero SIN NINGUNA GARANTÍA, incluso sin la garantía MERCANTIL
# implícita o sin garantizar la CONVENIENCIA PARA UN PROPÓSITO PARTICULAR. Véase
# la Licencia Pública General de GNU para más detalles.
# 
# Debería haber recibido una copia de la Licencia Pública General junto con el
# instalador en directo de Guadalinex 2005. Si no ha sido así, escriba a la Free
# Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301
# USA.
# 
# -------------------------------------------------------------------------
# 
# This file is part of Guadalinex 2005 live installer.
# 
# Guadalinex 2005 live installer is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the License, or
# at your option) any later version.
# 
# Guadalinex 2005 live installer is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
# 
# You should have received a copy of the GNU General Public License along with
# Guadalinex 2005 live installer; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

""" U{pylint<http://logilab.org/projects/pylint>} mark: 8.87 """

# File "peez2.py".
# Automatic partitioning with "peez2".
# Created by Antonio Olmo <aolmo#emergya._info> on 25 aug 2005.
# Last modified by A. Olmo on 2 nov 2005.

# TODO: improve debug and log system.

# Index:
# class Peez2:
# def beautify_size (size):
# def beautify_device (device, locale):

from sys         import stderr
from zlib        import crc32
from time        import sleep
from os.path     import exists
from locale      import getdefaultlocale
from popen2      import Popen3
from string      import lower
from ue.settings import *

class Peez2:

    """ Encapsulates a sequence of operations with I{Peez2} partition
        assistant. The partition scheme is expressed in MB (2^20 bytes).

        Data structures about three different drives follow. The first one is
        a hard drive::

            {'device': '/dev/hda',
             'info':   {'status':   ['STATUS #FRE|FRC|CLN|JLOG|LIN|WIN|FUL|UNP|UNK',
                                     'VALUE  # 1 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0'],
                        'oks':      [['FREESPACE\\n']],
                        'prim':     '3 + 0 (3)',
                        'win':      0,
                        'free':     1,
                        'ext':      0,
                        'metacoms': ['4\\n',
                                     '5',
                                     '6',
                                     '7'],
                        'linux':    1,
                        'details':  [{'fs':    'ext3',
                                      'no':    '1',
                                      'bytes': 2146765824,
                                      'sec':   '63sec - 4192964sec',
                                      'type':  '0x0:Particion Primaria     ',
                                      'class': 'Type Generic Linux\\n'},
                                     {'fs':    'NOSF',
                                      'no':    '2',
                                      'bytes': 2146798080,
                                      'sec':   '4192965sec - 8385929sec',
                                      'type':  '0x0:Particion Primaria     ',
                                      'class': 'PAV#3'}]},
             'label':  'ST340014A',
             'size':   40020664320L,
             'no':     0}

        This one is a CD-ROM drive::

            {'device': '/dev/hdc',
             'info':   {'warn':   ['Disco vacio sin tabla e particiones o disco no reconocido',
                                   'UNKNOW LAYOUT'],
                        'status': ['STATUS #FRE|FRC|CLN|JLOG|LIN|WIN|FUL|UNP|UNK',
                                   'VALUE  # 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0'],
                        'opts':   [['1',
                                    'CR',
                                    'Nueva partici\xc3\xb3n. Ocupar todo el espacio \\n'],
                                   ['2',
                                    'CR',
                                    'Nueva partici\xc3\xb3n. Dejar espacio libre \\n']]},
             'label':  'HL-DT-STDVD-ROM GDR8163B',
             'size':   575959040,
             'no':     1}

        This is only an example for testing purposes::

            {'device': '/dev/strange',
             'info':   {},
             'size':   1200000000,
             'no':     -1,
             'label':  'FOR DEBUGGING PURPOSES ONLY'}

        """


    # Initialization _________________________________________________________

    def __init__ (self, binary = 'peez2', common_arguments = '2> /dev/null',
                  debug = DEBUGGING_STATUS,
                  partition_scheme = MINIMAL_PARTITION_SCHEME):

        """ Detect locale and scan for drives. """

        self.__binary = binary
        self.__common_arguments = common_arguments
        self.__debug = debug
        self.__partition_scheme = partition_scheme
        self.__locale = getdefaultlocale () [0]
        self.__drives = self.__scan_drives ()

        # Disable this attribute when auto-partitioning is mature enough:
        self.__ONLY_MANUALLY = False

        # Every partitioning command executed will be also written here:
        p = Popen3 ('if [ -e /tmp/guadalinex-express.commands ]; ' + \
                    'then rm /tmp/guadalinex-express.commands; fi')
        p.wait ()

    # Public method "get_drives" _____________________________________________

    def get_drives (self):

        """ Retrieve a list of drives. Each unit is identified by its device
            name (i.e. C{/dev/hda}) and has an associated human-readable label
            (i.e. I{75 GB, maestro en el bus primario (/dev/hda),
            "ST380011A"}). """

        result = []

        for i in self.__drives:

##             if self.__debug:
##                 stderr.write ('__get_drives: drive follows.\n' + str (i) + '\n')

            pretty_device = beautify_device (i ['device'], self.__locale)
            pretty_size = beautify_size (i ['size'])
            label = '%s, %s, "%s"' % (pretty_size, pretty_device, i ['label'])

            # First, check that there is room enough for three new partitions:

            # We are not using a more compact construct below to explicit that
            #     the same 3 partitions, in the same order, are always used:
            required_MB = sum (self.__partition_scheme.values ())

            if i ['size'] >= required_MB * 1024 * 1024:
                enough = True
            else:
                enough = False

            # Second, check if there was a previous Linux system,
            #     with enough partitions, and enough space:

            associations = None

            if i ['info'].has_key ('details'):
                actual_sizes = []    # Sizes of actual Linux partitions.
                actual = {}          # Association between sizes and devices.

                # Populate actual data:

                for j in i ['info'] ['details']:

                    if 'linux' in j ['class'].lower () or \
                           'swap' in j ['class'].lower () or \
                           'nofs' in j ['class'].lower () or \
                           'linux' in j ['fs'].lower () or \
                           'swap' in j ['fs'].lower () or \
                           'ext2' in j ['fs'].lower () or \
                           'ext3' in j ['fs'].lower ():
                        actual_sizes.append (int (j ['bytes']))

                        if actual.has_key (str (int (j ['bytes']))):
                            (actual [str (int (j ['bytes']))]).append (i ['device'] + j ['no'])
                        else:
                            actual [str (int (j ['bytes']))] = [i ['device'] + j ['no']]

                # Array of sizes must be ordered:
                actual_sizes.sort ()

                # It is necessary to find at least two partitions:
                if len (actual_sizes) > 1:
                    parts = self.__partition_scheme
                    desired_sizes = []
                    desired = {}

                    if len (actual_sizes) is 2:
                        # There are two partitions, so swap will be
                        #     in a file in root partition:
                        desired_sizes = [(parts ['root'] + parts ['swap']) * 1024 * 1024,
                                         (parts ['home']) * 1024 * 1024]

                        if parts ['root'] + parts ['swap'] == parts ['home']:
                            desired = {str ((parts ['home']) * 1024 * 1024): ['root', 'home']}
                        else:
                            desired = {str ((parts ['root'] + parts ['swap']) * 1024 * 1024): ['root'],
                                       str ((parts ['home']) * 1024 * 1024): ['home']}

                    else:
                        # Three or more Linux partitions
                        #     (let us be verbose for the sake of correction):
                        mountpoints = parts.keys ()

                        for k in mountpoints:
                            desired_sizes.append (parts [k] * 1024 * 1024)

                            if desired.has_key (str (parts [k] * 1024 * 1024)):
                                (desired [str (parts [k] * 1024 * 1024)]).append (k)
                            else:
                                desired [str (parts [k] * 1024 * 1024)] = [k]

                    # This array must be ordered as well:
                    desired_sizes.sort ()

                    associations = {}
                    l = 0
                    r = 0

                    if self.__debug:
                        stderr.write ('__get_drives: actual = "' + str (actual) + '.\n')
                        stderr.write ('__get_drives: actual_sizes = "' + str (actual_sizes) + '.\n')
                        stderr.write ('__get_drives: desired = "' + str (desired) + '.\n')
                        stderr.write ('__get_drives: desired_sizes = "' + str (desired_sizes) + '.\n')

                    while r < len (desired_sizes) and l < len (actual_sizes):

                        if self.__debug:
                            stderr.write ('__get_drives: r = ' + str (r) +
                                          '; l = ' + str (l) + '.\n')

                        if actual_sizes [l] >= desired_sizes [r]:

                            if self.__debug:
                                stderr.write ('__get_drives: ' +
                                              str (actual_sizes [l]) +
                                              ' >= ' + str (desired_sizes [r]) + '.\n')

                            associations [actual [str (actual_sizes [l])] [0]] = \
                                         desired [str (desired_sizes [r])] [0]

                            if self.__debug:
                                stderr.write ('__get_drives: associations [' +
                                              str (actual [str (actual_sizes [l])] [0]) +
                                              '] = desired [' + str (desired_sizes [r]) +
                                              '] [0].\n')

                            r = r + 1

                        l = l + 1

                    if r < len (desired_sizes):
                        associations = None
                    else:
                        # During formatting and copying, "root" is known as "/",
                        # and "home" is known as "/home", so it is necessary to
                        # change them before passing mount point associations to
                        # the backend:

                        for j in associations.keys ():

                            if 'root' == associations [j].lower ():
                                associations [j] = '/'
                            elif 'home' == associations [j].lower ():
                                associations [j] = '/home'

                    if self.__debug:
                        stderr.write ('__get_drives: associations = "' + \
                                      str (associations) + '".\n')

            item = {'id':           str (i ['device']),
                    'label':        label,
                    'info':         i ['info'],
                    'large_enough': enough,
                    'linux_before': associations}
            result.append (item)

        return result

    # Public method "only_manually" __________________________________________

    def only_manually (self):

        """ Decide if manual partitioning should be the only way
            available. """

        return self.__ONLY_MANUALLY

    # Private method "__scan_drives" _________________________________________

    def __scan_drives (self):

        """ Retrieve the list of drives in the computer. Devices B{not}
            beginning with C{/dev/hd} or C{/dev/sd} are ignored. """

        result = []

        lines = self.__call_peez2 () ['out']

        for i in lines:

            if 'LD#' == i [:3]:
                fields = i [3:].split ('|')
                drive = {}

                for j in fields:

                    if 'Media:' == j [:6]:
                        drive ['no'] = int (j [6:])
                    elif 'Model:' == j [:6]:
                        drive ['label'] = j [6:]
                    elif 'Path:' == j [:5]:
                        drive ['device'] = j [5:]
                    elif 'Total:' == j [:6]:
                        drive ['size'] = int (j [6:])

                if '/dev/hd' == drive ['device'] [:7] or \
                       '/dev/sd' == drive ['device'] [:7]:
                    extended_info = self.__get_info (drive ['device'])
                    drive ['info'] = extended_info
                    result.append (drive)
                else:

                    if self.__debug:
                        stderr.write ('__scan_drives: drive "' +
                                      drive ['device'] + '" ignored.\n')

        return result

    # Private method "__get_info" ____________________________________________

    def __get_info (self, drive, size = None, more_args = '', input = None):

        """ Retrieve information about a C{drive}. If a C{size} (in MB) is
            given, then options to get this space are parsed as well. It is
            also possible to specify some additional arguments (like C{-j} or
            C{-x}). C{input} may be a string that will be piped into
            I{Peez2}. """

        result = None

        # We are not using a more compact construct below to reflect that the
        # same 3 partitions are always used, and in the same order:
        parts = self.__partition_scheme

        if '' != more_args:
            more_args = more_args + ' '

        more_args = more_args + '-v '

        if None != size:

            if None == input:
                lines = self.__call_peez2 ('-a wizard %s-d %s -m %i -M %i' %
                                           (more_args, drive, size, size))['out']
            else:
                lines = self.__call_peez2 ('-a wizard %s-d %s -m %i -M %i' %
                                           (more_args, drive, size, size),
                                           input)['out']

        else:

            if None == input:
                lines = self.__call_peez2 ('-a validate %s-d %s -s %i:%i:%i' %
                                           (more_args, drive, parts ['swap'],
                                            parts ['root'],
                                            parts ['home'])) ['out']
            else:
                lines = self.__call_peez2 ('-a validate %s-d %s -s %i:%i:%i' %
                                           (more_args, drive, parts ['swap'],
                                            parts ['root'], parts ['home']),
                                           input) ['out']

        after_menu = False

        for i in lines:

            # This case temporarily solves last "Peez2" bug:
            if i.startswith ('Please select a choice:') or \
               i.startswith ('Por favor, seleccione una opc'):
                after_menu = True
            # "Aviso":
            elif 'AA#' == i [:3]:

                if None == result:
                    result = {}

                if not result.has_key ('warn'):
                    result ['warn'] = []

                result ['warn'].append (i [3:-1])
            # "información varia":
            elif 'VV#' == i [:3]:

                if None == result:
                    result = {}

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

            # "Listado de particiones":
            elif 'LP#' == i [:3]:
                fields = i [3:].split ('#')

                if None == result:
                    result = {}

                if not result.has_key ('parts'):
                    result ['parts'] = []

                this_part = {'name': fields [0]}

                for j in fields [1:]:

                    if 'GAINED:' == j [:7]:
                        this_part ['gained'] = int (j [7:].strip ())
                    elif 'SIZE:' == j [:5]:
                        this_part ['size'] = int (j [5:].strip ())
                    elif 'FS:' == j [:3]:
                        this_part ['fs'] = j [3:].strip ()
                    elif 'TYPE:' == j [:5]:
                        this_part ['type'] = j [5:].strip ()

                result ['parts'].append (this_part)
            # "Opción":
            elif 'OO#' == i [:3]:
                fields = i [3:].split ('#')

                if None == result:
                    result = {}

                if not result.has_key ('opts'):
                    result ['opts'] = []

                result ['opts'].append (fields)
            # "Acción 'validate' exitosa":
            elif 'OK#' == i [:3]:
                fields = i [3:].split ('#')

                if None == result:
                    result = {}

                if not result.has_key ('oks'):
                    result ['oks'] = []

                result ['oks'].append (fields)
            elif 'CC#' == i [:3] and after_menu:
                fields = i [3:].split ('#')

                if None == result:
                    result = {}

                if not result.has_key ('commands'):
                    result ['commands'] = []

                result ['commands'].append (fields [1])
            elif 'MC#' == i [:3]:
                fields = i [3:].split ('#')

                if None == result:
                    result = {}

                if not result.has_key ('metacoms'):
                    result ['metacoms'] = []

                result ['metacoms'].append (fields [1])
            elif 'OD#' == i [:3] and after_menu:

                if None == result:
                    result = {}

                if not result.has_key ('dest'):
                    result ['dest'] = i [3:]

        lines = self.__call_peez2 ('-a show -d %s -v' % drive) ['out']
        string_of_lines = ''

        for i in lines:
            string_of_lines = string_of_lines + i

        string_of_lines = string_of_lines.split ('\n')

        for i in string_of_lines:

            # "registro de 'lista de particiones'":
            if 'PAV' == i [:3] or 'PAH' == i [:3]:

                # This patch temporarily solves Peez2 output bug:
                # TODO: remove this patch?
                next = i [3:].find ('PAV')
                other_next = i [3:].find ('PAH')

                if other_next < next and other_next > -1:
                    next = other_next

                if next > -1:
                    string_of_lines.append (i [3:] [next:])
                    this_one = i [4:] [:next]
                else:
                    this_one = i [4:]

                if 'PAV#' == i [:4]:

                    fields = this_one.split ('|')

                    if None == result:
                        result = {}

                    if not result.has_key ('details'):
                        result ['details'] = []

                    this_part = {'no':    fields [0],
                                 'type':  fields [1],
                                 'fs':    fields [2],
                                 'sec':   fields [3],
                                 'bytes': int (fields [4]),
                                 'class': fields [5]}
                    result ['details'].append (this_part)

##         if self.__debug and result.has_key ('details'):
##             stderr.write ('__get_info: details "' + \
##                           str (result ['details']) + '"\n')

        return result

    # Public method "auto_partition" _________________________________________

    def auto_partition (self, drive, steps = None, \
                        do_it = ACTUAL_PARTITIONING):

        """ Make 3 partitions automatically on the specified C{device}. When
            C{progress_bar} is not C{None}, it is updated dinamically as the
            partitioning process goes on. """

        result = None

        if steps is not None:
            status = 0.1
            steps.put ('%f|Iniciando el proceso de particionado automático...' %
                       status)
            status = status + 0.1

        if drive.has_key ('info'):

            if drive ['info'].has_key ('primary'):

                if drive ['info'] ['primary'] < 2:
                    # Make 3 new primary partitions?
                    pass

            components = self.__partition_scheme.keys ()
            stop = False
            # We suppose that there is no extended partition:
            ext_part = False
            # Initially, every new partition will be logical:
            try_primary = False

            if drive.has_key ('info'):

                if drive ['info'].has_key ('ext'):

                    if drive ['info'] ['ext'] > 0:
                        # Actually, there is already an extended partition:
                        ext_part = True

            for part in components:

                if self.__debug:
                    stderr.write ('auto_partition: part = "' + str (part) + '".\n')

                if try_primary:
                    # Create a primary partition:
                    required = int (round (self.__partition_scheme [part]) * 1.02)
                    info = self.__get_info (drive ['id'], required)
                    type = 'primaria'
                else:

                    if ext_part:
                        # A new logical partition is created. It has 2% more space
                        # so "recycle" partitioning method is enabled if user
                        # decides to reinstall in the same drive:
                        required = int (round (self.__partition_scheme [part]) * 1.02)
                        info = self.__get_info (drive ['id'], required, '-j')
                        type = 'lógica'
                    else:
                        # It is necessary to create an extended partition
                        # (with 8% more space -- 6% of 3 partitions and 2% more to be sure):
                        required = int (round (sum (self.__partition_scheme.values ()) * 1.08))
                        info = self.__get_info (drive ['id'], required, '-x')
                        components.append (part)
                        type = 'extendida'

                if steps is not None:
                    steps.put ('%f|Creando una partición %s de %s...' % \
                               (status, type, beautify_size (int (required) * 1024 * 1024)))
                    status = status + 0.1

                # Now we have to decide which option is better:
                if info.has_key ('opts'):

                    if self.__debug:
                        stderr.write ('auto_partition: has_key ("opts").\n')

                    options = info ['opts']
                else:

                    if self.__debug:
                        stderr.write ('auto_partition: NO has_key ("opts").\n')

                    if try_primary:
                        # Definitively, no more partitions can be created.
                        # Stop partitioning:

                        if self.__debug:
                            stderr.write ('auto_partition: stopped!\n')

                        stop = True
                        break
                    else:
                        # Next partitions should be primary, or not be at all:

                        if self.__debug:
                            stderr.write ('auto_partition: switching to primary.\n')

                        components.append (part)
                        try_primary = True
                        continue

                what = -1
                i = 1

                while -1 == what and i <= len (options):

                    if 'CR' == options [i - 1] [1] [:2]:
                        what = i

                    i = i + 1

                i = 1

                while -1 == what and i <= len (options):

                    if 'RE' == options [i - 1] [1] [:2]:
                        what = i

                    i = i + 1

                if what is -1:

                    if self.__debug:
                        stderr.write ('auto_partition: there are no valid options.\n')

                    if try_primary:
                        # Definitively, no more partitions can be created.
                        # Stop partitioning:

                        if self.__debug:
                            stderr.write ('auto_partition: stopped!\n')

                        stop = True
                        break
                    else:
                        # Next partitions should be primary, or not be at all:

                        if self.__debug:
                            stderr.write ('auto_partition: switching to primary.\n')

                        components.append (part)
                        try_primary = True
                        continue

                else:

                    if try_primary:
                        info = self.__get_info (drive ['id'], required,
                                                '-i', str (what) + '\n')

                    else:
                    
                        if not ext_part:
                            info = self.__get_info (drive ['id'], required,
                                                    '-x -i', str (what) + '\n')
                        else:
                            info = self.__get_info (drive ['id'], required,
                                                    '-j -i', str (what) + '\n')

                    if info.has_key ('commands'):
                        c = info ['commands']

                    p = Popen3 ('echo "Creando ' + str (part) +
                                '..." >> /tmp/guadalinex-express.commands')
                    p.wait ()
                    subprogress = 0.2 / (len (c) + 1)

                    for i in c:

                        if steps is not None:
                            steps.put ('%f|Creando una partición %s de %s...' % \
                                       (status, type, beautify_size (int (required) * 1024 * 1024)))
                            status = status + subprogress

                        # Print the commands:
                        if self.__debug:
                            stderr.write ('auto_partition: command: "' +
                                          i.strip () + '" executed.\n')

                        p = Popen3 ('echo "' + i.strip () +
                                    '" >> /tmp/guadalinex-express.commands')
                        p.wait ()

                        if do_it:
                            # Do it! Execute commands to make partitions!

                            if 'parted ' in i and exists ('/proc/partitions'):
                                partitions_file = file ('/proc/partitions')
                                previous_partitions = partitions_file.read ()
                                partitions_file.close ()
                                previous_checksum = crc32 (previous_partitions)

                            # Execute the command:
                            p = Popen3 (i)
                            p.wait ()

                            # Let the system be aware of the changes:
                            if 'parted ' in i and exists ('/proc/partitions'):
                                current_checksum = previous_checksum

                                while current_checksum is previous_checksum:
                                    sleep (1)
                                    partitions_file = file ('/proc/partitions')
                                    current_partitions = partitions_file.read ()
                                    partitions_file.close ()
                                    current_checksum = crc32 (current_partitions)

                            sleep (5)

                    if info.has_key ('metacoms'):
                        mc = info ['metacoms']

                        for i in mc:

                            if self.__debug:
                                stderr.write ('# ' + i)

                    if self.__debug:
                        stderr.write ("info.has_key ('dest') = " +
                                      str (info.has_key ('dest')) +
                                      '; ext_part = ' + str (ext_part) + '.\n')

                    if ext_part:

                        if info.has_key ('dest'):

                            if result is None:
                                result = {}

                            result [(info ['dest']).strip ()] = part.strip ()

                            if self.__debug:
                                stderr.write (str (part.strip ()) + \
                                              ' added as ' + \
                                              str ((info ['dest']).strip ()) + '\n')

                    else:
                        ext_part = True

        # During formatting and copying, "root" is known as "/",
        # and "home" is known as "/home", so it is necessary to
        # change them before passing mount point associations to
        # the backend:

        if steps is not None:
            steps.put ('%f|Terminando el proceso de particionado...' %
                       status)

        if stop:
            result = 'STOPPED'
        else:

            for i in result.keys ():

                if 'root' == result [i].lower ():
                    result [i] = '/'
                elif 'home' == result [i].lower ():
                    result [i] = '/home'

        if self.__debug:
            stderr.write ('auto_partition: result = "' + str (result) + '".\n')

        return result

    # Private method "__call_peez2" __________________________________________

    def __call_peez2 (self, args = '', input = ''):

        """ Execute I{peez2} with arguments provided, if any. It is also
            possible to specify an input. """

        command = self.__binary + ' ' + args + ' ' + self.__common_arguments
        command = 'LANGUAGE=C ' + command

        if '' != input:
            command = 'echo -e "' + input + '" | ' + command

        if self.__debug:
            stderr.write ('__call_peez2: command "' + command + '" executed.\n')

        child = Popen3 (command, False, 1048576)
#        child.wait ()

        return {'out': child.fromchild,
                'in':  child.tochild,
                'err': child.childerr}

# Function "beautify_size" ___________________________________________________

def beautify_size (size):

    """ Format the size of a drive into a friendly string, i.e. C{64424509440}
        will produce I{60 GB}. """

    result = None

    try:
        bytes = int (size)
    except:
        bytes = -1

    if bytes >= 1024 * 1024 * 1024:
        result = '%i GB' % int (round (bytes / float (1024 * 1024 * 1024)))
    elif bytes >= 1024 * 1024:
        result = '%i MB' % int (round (bytes / float (1024 * 1024)))
    elif bytes >= 1024:
        result = '%i KB' % int (round (bytes / float (1024)))
    elif bytes >= 0:
        result = '%i B' % bytes

    return result

# Function "beautify_device" _________________________________________________

def beautify_device (device, locale):

    """ Format the name of a device to make it more readable, i.e. C{/dev/hdb}
        will produce I{primary slave (/dev/hdb)}, I{esclavo en el bus
        primario (dev/hdb)}, etc. depending on the I{locale}. """

    result = None

    try:
        name = str (device).strip ()
        lang = str (locale) [:2]
    except:
        name = ''

    if '' != name:

        if '/dev/hda' == name:

            if 'es' == lang:
                result = 'maestro en el bus primario (' + name + ')'
            elif 'en' == lang:
                result = 'primary master (' + name + ')'

        elif '/dev/hdb' == name:

            if 'es' == lang:
                result = 'esclavo en el bus primario (' + name + ')'
            elif 'en' == lang:
                result = 'primary slave (' + name + ')'

        elif '/dev/hdc' == name:

            if 'es' == lang:
                result = 'maestro en el bus secundario (' + name + ')'
            elif 'en' == lang:
                result = 'secondary master (' + name + ')'

        elif '/dev/hdd' == name:

            if 'es' == lang:
                result = 'maestro en el bus secundario (' + name + ')'
            elif 'en' == lang:
                result = 'secondary slave (' + name + ')'

        if None == result:
            result = name

    return result

# End of file.

