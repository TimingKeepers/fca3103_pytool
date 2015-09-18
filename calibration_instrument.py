#!   /usr/bin/env   python3
# -*- coding: utf-8 -*
'''
Abstract class to define the API for a measurement instrument

@file
@date Created on Apr 16, 2015
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
import abc

# This attribute permits dynamic loading inside wrcalibration class.
__meas_instr__ = "Calibration Instrument"

class Calibration_instrument() :
    '''
    Calibration instrument API

    Abstract class that represents the API that a generic measurement instrument
    must implement to be accepted as calibration instrument for WR Calibration
    procedure.

    The main calibration procedure expects a homogeneus interface to any instrument
    that could be used to measure skew between PPS signals from WR devices.
    '''
    __metaclass__ = abc.ABCMeta

    ## The input channel for the slave signal
    slave_chan  = ""
    ## The input channel for the master signal
    master_chan = ""
    ## Trigger level array. Each position i stores the trigger level for the input i.
    trigger_level = []

    # The following methods must be implemented by a concrete class for a WR device.

    @abc.abstractmethod
    def __init__(self, port, master_chan=None, slave_chan=None) :
        '''
        Constructor

        Args:
            port (int) : Port for the Tektronix FCA3103 using the USB connection.
            master_chan (int) : Input channel for master's PPS signal.
            slave_chan (int) : Input channel for slave's PPS signal.
        '''

    # ------------------------------------------------------------------------ #

    @abc.abstractmethod
    def trigger_level(self, v_min=0, v_max=5) :
        '''
        Abstract method to determine a good trigger level for a input channel.

        It's important to run this method at least once before doing any
        measurement for achieving good time interval measures.

        Ensure that 2 WR devices are connected and servo state is TRACK PHASE.

        Args:
            v_min (float) : Minimum voltage level for the input signal
            v_max (float) : Maximum voltage level for the input signal

        Raises:
            ValueError if master_chan or slave_chan are not set.
            InputNotSet if input channels are not set.
        '''

    # ------------------------------------------------------------------------ #

    @abc.abstractmethod
    def mean_time_interval(self, n_samples, t_samples) :
        '''
        Abstract method to measure time interval between two input signals.

        This method measures time interval between the PPS input from the master
        to the PPS input from the slave. It makes n_samples and calculates the
        mean value.

        Before using this method, master_chan and slave_chan must be set.

        Args:
            n_samples (int) : Number of measures to be done.
            t_samples (int) : Time between samples (should be greater than 1ms)

        Returns:
            The mean time interval master to slave.

        Raises:
            ValueError if master_chan or slave_chan are not set.
            TriggerNotSet if trigger levels are not set.
            MeasuringError if a time interval value is higher than expected.
        '''
