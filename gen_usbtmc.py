#!   /usr/bin/env   python3
# -*- coding: utf-8 -*
'''
This file contains a generic userspace driver for usbtmc devices.

@file
@date Created on Mar. 20, 2015
@author Felipe Torres (torresfelipex1<AT>gmail.com)
@copyright LGPL v2.1
@ingroup measurement
'''

#------------------------------------------------------------------------------|
#                   GNU LESSER GENERAL PUBLIC LICENSE                          |
#                 ------------------------------------                         |
# This source file is free software; you can redistribute it and/or modify it  |
# under the terms of the GNU Lesser General Public License as published by the |
# Free Software Foundation; either version 2.1 of the License, or (at your     |
# option) any later version. This source is distributed in the hope that it    |
# will be useful, but WITHOUT ANY WARRANTY; without even the implied warrant   |
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser   |
# General Public License for more details. You should have received a copy of  |
# the GNU Lesser General Public License along with this  source; if not,       |
# download it from http://www.gnu.org/licenses/lgpl-2.1.html                   |
#------------------------------------------------------------------------------|

#---------------------------------------------------------- --------------------
#                                   Import                                    --
#-------------------------------------------------------------------------------
# Import system modules
import os

class Gen_usbtmc() :
    '''

    '''
    device = "/dev/usbtmc"

    def __init__(self, port, full_support=False):
        '''
        Constructor

        Args:
            port (int) : Port
            full_support (boolean) : Indicates if /dev/usbtmc0 is accessible
        '''

        if full_support :
            self.driver = os.open("/dev/usbtmc0" ,os.O_RDWR)
        else :
            self.driver = None
        self.device = os.open(("/dev/usbtmc%d" % port), os.O_RDWR)

    def listDevices(self) :
        '''
        Method for listing detected devices using USBTMC interface.
        '''
        if self.driver != None :
            return os.read(self.driver, 100)
        else : return None


    def write(self, cmd):
        '''
        Write

        Args:
            cmd (str) : A command to write
        '''
        os.write(self.device, cmd)

    def read(self, length = 1):
        '''
        Read

        Args:
            length (int) : Number of bytes to be read
        '''
        return os.read(self.device, length)
