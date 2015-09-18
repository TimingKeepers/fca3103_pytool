#!   /usr/bin/env   python3
# -*- coding: utf-8 -*
'''
Driver for the Tektronix FCA 3103 Timer/Counter/Analyzer

@file
@date Created on Apr. 20, 2015
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

#-------------------------------------------------------------------------------
#                                   Import                                    --
#-------------------------------------------------------------------------------
# Import system modules
import time

# User modules
from gen_usbtmc import *

class FCA3103_drv() :
    '''
    Tektronix FCA 3103 driver.
    '''

    def __init__(self, port,full_support=False) :
        '''
        Constructor

        Args:
            port (int) : Port index of usbtmc device (from 0 to 16)
            full_support (boolean) : Indicates if custom usbtmc driver is loaded
        '''
        self.driver = Gen_usbtmc(port,full_support)

        if full_support :
            devices = self.driver.listDevices()
            lines = devices.splitlines()

            self.manufacturer = lines[port].split('\t')[1]
            self.device = lines[port].split('\t')[2]
            self.serial = lines[port].split('\t')[3]
        else :
            info = self.query("*IDN?")
            self.manufacturer = info.split(",")[0]
            self.device = info.split(",")[1]
            self.serial = info.split(",")[2]

    # ------------------------------------------------------------------------ #

    def deviceInfo(self) :
        '''
        Method to retrieve device information.

        Returns:
            A string with manufacturer, device name and serial number.
        '''
        return ("%s %s (s/n : %s)" % (self.manufacturer, self.device, self.serial))

    # ------------------------------------------------------------------------ #

    def query(self, cmd, length=100) :
        '''
        Method to write a command and read the result.

        Args:
            cmd (str) :  A SCPI valid command for the device.
            length (int) : Length of the input read. Default : 100.

        Returns:
            Command "cmd" response.
        '''
        self.driver.write(str.encode(cmd))
        time.sleep(1)
        ret = self.driver.read(length)[:-1]

        return bytes.decode(ret)

    # ------------------------------------------------------------------------ #

    def read(self, length=1) :
        '''
        Method to read from output buffer of the instrument

        Args:
            length (int) : Number of bytes to read. Default : 1.
        '''
        ret = self.driver.read(length)[:-1]
        return bytes.decode(ret)

    # ------------------------------------------------------------------------ #

    def write(self, cmd, check=False) :
        '''
        Method for writing to input buffer of the instrument.

        Args:
            cmd (str) : A SCPI valid command for the device.
            check (boolean) : When true the driver will ask for errors in previous command.

        Returns:
            If check=True it returns a tuple (error code,error message).
        '''
        self.driver.write(str.encode(cmd))
        time.sleep(1)

        if check :
            return self.query("syst:err?")
