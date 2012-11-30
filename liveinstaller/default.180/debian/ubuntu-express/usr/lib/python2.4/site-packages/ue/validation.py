# -*- coding: utf-8 -*-

""" U{pylint<http://logilab.org/projects/pylint>} mark: 9.31 """

# File "validation.py".
# Validation library.
# Created by Antonio Olmo <aolmo@emergya.info> on 26 july 2005.
# Last modified on 2 august 2005.

from string import whitespace, uppercase

# Index:
# def check_username (name):
# def check_password (passwd1, passwd2):
# def check_hostname (name):
# def invalid_names ():
    
# Function "check_username" __________________________________________________

def check_username (name):

    """ Check the correctness of a proposed user name.

        @return:
            - C{0} valid.
            - C{1} contains dots.
            - C{2} contains uppercase characters.
            - C{3} wrong length.
            - C{4} contains white spaces.
            - C{5} is already taken or prohibited.
            - C{6} is C{root}. """

    result = 0

    if 'root' == name:
        result = 6
    elif name in invalid_names ():
        result = 5
    elif len (set (name).intersection (set (whitespace))) > 0:
        result = 4
    elif len (name) < 3 or len (name) > 24:
        result = 3
    elif len (set (name).intersection (set (uppercase))) > 0:
        result = 2
    elif '.' in name:
        result = 1

    return result

# Function "check_password" __________________________________________________

def check_password (passwd1, passwd2):

    """ Check the correctness of a proposed password, writen twice.

        @return:
            - C{0} valid.
            - C{1} wrong length. too short.
            - C{2} wrong length. too long.
            - C{3} strings do not match. """

    result = 0

    if passwd1 != passwd2:
        result = 3
    elif len (passwd1) < 4:
        result = 1
    elif len (passwd1) > 16:
        result = 2

    return result

# Function "check_hostname" __________________________________________________

def check_hostname (name):

    """ Check the correctness of a proposed host name.

        @return:
            - C{0} valid.
            - C{1} wrong length.
            - C{2} contains white spaces. """

    result = 0

    if len (set (name).intersection (set (whitespace))) > 0:
        result = 2
    elif len (name) < 3 or len (name) > 18:
        result = 1

    return result

# Function "invalid_names" ___________________________________________________

def invalid_names ():

    """ Find out which user names should not be used.

        @return: a C{set} of prohibited user names. """

    result = set ([])

    for i in open ('/etc/passwd'):

        if ':' in i:
            result.add (i [: i.find (':')])

    return result

# End of file.

