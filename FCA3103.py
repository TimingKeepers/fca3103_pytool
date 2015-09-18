#!   /usr/bin/env   python3
# -*- coding: utf-8 -*
'''
Class that implements the interface Calibration_instrument for the Tektronix FCA3103.

@file
@date Created on Apr. 20, 2015
@author Felipe Torres (torresfelipex1<AT>gmail.com)
@copyright LGPL v2.1
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
import math

# User modules
from calibration_instrument import *
from tektronix_fca3103_drv  import *

# This attribute permits dynamic loading inside wrcalibration class.
__meas_instr__ = "FCA3103"

class FCA3103(Calibration_instrument) :
    '''
    Class that implements the interface Calibration_instrument for the Tektronix FCA3103.

    This implementation allow to use a Tektronix FCA3103 Timer/Counter/Analyzer
    as measurement instrument for White Rabbit calibration procedure.

    If master and slave channels are not specified when making a new copy of
    this class, they must be set before calling any of the methods of the class.
    '''

    ## Number of samples
    n_samples = 5
    ## Time between samples (s)
    t_samples = 0.5
    ## Enable debug message output
    show_dbg = False
    ## If a value is far from mean value don't use it
    skip_values = False
    ## Error value, used for skip a value (in ps)
    error = 500000

    def __init__(self, port, master_chan=None, slave_chan=None) :
        '''
        Constructor

        Args:
            port (int) : Port for the Tektronix FCA3103 using the USB connection.
            master_chan (int) : Input channel for master's PPS signal.
            slave_chan (int) : Input channel for slave's PPS signal.
        '''
        self.drv = FCA3103_drv(port)
        self.master_chan = master_chan
        self.slave_chan = slave_chan
        self.trig_level = [None, ] *2 # This device has 2 input channels.
        self.trig_level[0] = None
        self.trig_level[1] = None

    # ------------------------------------------------------------------------ #

    def trigger_level(self, v_min=0, v_max=5) :
        '''
        Method to determine a good trigger level for a input channel.

        It's important to run this method at least once before doing any
        measurement for achieving good time interval measures.

        Ensure that 2 WR devices are connected and servo state is TRACK PHASE.

        Args:
            v_min (float) : Minimum voltage level for the input signal
            v_max (float) : Maximum voltage level for the input signal

        Raises:
            ValueError if master_chan or slave_chan are not set.
            NotADevicePort if input is a invalid input channel for this device.
        '''
        if self.master_chan == None :
            raise ValueError("FCA3103 ERROR: Master input channel not set.")
        if self.slave_chan == None :
            raise ValueError("FCA3103 ERROR: Slave input channel not set.")

        # Prepare an array with voltage values to be tested
        v_array = []
        i = v_min
        incr = 0.1
        while i < v_max :
            v_array.append(i)
            i += incr

        # Initial device configuration --------------------
        if self.show_dbg :
            print("Setting the initial instrument configuration.")

        # Reset the device
        self.drv.write("*RST")

        # Trigger mode not continuous
        self.drv.write("INIT:CONT OFF")

        # Configure the measure to be performed
        self.drv.write("CONFIGURE:TINTERVAL (@%d),(@%d)" % \
        (self.slave_chan,self.master_chan))

        # Take one sample, really needed?
        self.drv.write("TRIG:COUNT 1;:ARM:COUNT 1")

        # Set input coupling to DC
        self.drv.write("INPUT1:COUPling DC")
        self.drv.write("INPUT2:COUPling DC")

        # Set input impedance to 1 MOhm
        self.drv.write("INPUT1:IMPedance MAX")
        self.drv.write("INPUT2:IMPedance MAX")

        # Set the trigger auto mode off
        self.drv.write("INPUT1:LEVEL:AUTO OFF")
        self.drv.write("INPUT2:LEVEL:AUTO OFF")

        # Measure format (ASCII with time stamping disabled)
        self.drv.write("FORMAT ASCII;:FORMAT:TINF OFF")

        # Check for errors in the initial configuration
        errors = self.drv.query("syst:err?")
        if errors[0] != 0 :
            #TODO: raise an exception
            print("Error in initial config: " + errors)
        elif show_dbg :
            print("No errors in initial config")

        # Test the trigger levels to determine the best ---
        trig_levels = {}

        if self.show_dbg :
            print("Testing trigger level values, it should take a long time ...")

        for i in v_array :
            mean = 0
            # Set trigger level
            self.drv.write("INPUT%d:LEVEL %1.3f" % (self.master_chan,i))
            self.drv.write("INPUT%d:LEVEL %1.3f" % (self.slave_chan,i))

            # Test it
            for j in range(self.n_samples) :
                mean += float(self.drv.query("READ?"))
                time.sleep(self.t_samples)
            mean /= self.n_samples # Get the mean value

            if self.show_dbg :
                print("Trig level : %1.3f V, Mean time interval: %g" % (i, mean))

            trig_levels[i] = mean

        # Take the lower one
        min = 1
        min_key = 0
        for key in trig_levels :
            if abs(trig_levels[key]) < min :
                min = abs(trig_levels[key])
                min_key = key

        self.trig_level[0] = min_key
        self.trig_level[1] = min_key
        print("Trigger level set at %f volts." % (min_key))

    # ------------------------------------------------------------------------ #

    def mean_time_interval(self, n_samples, t_samples) :
        '''
        Method to measure time interval between two input signals.

        This will measure delay master to slave.

        Args:
            n_samples (int) : Number of measures to be done.
            t_samples (int) : Time between samples (should be greater than 1ms)
            input1_trig (float) : Trigger level for the input 1
            input2_trig (float) : Trigger level for the input 2

        Returns:
            The mean value of the N samples.

        Raises:
            ValueError if master_chan or slave_chan are not set or trigger level not set.
        '''
        if self.master_chan == None :
            raise ValueError("FCA3103 ERROR: Master input channel not set.")
        if self.slave_chan == None :
            raise ValueError("FCA3103 ERROR: Slave input channel not set.")

        if self.trig_level[0] == None or \
        self.trig_level[1] == None :
            raise ValueError("FCA3103 ERROR: Trigger level not set.")

        # Initial device configuration --------------------

        # Reset the device
        self.drv.write("*RST")
        time.sleep(0.5)

        # Trigger mode not continuous
        self.drv.write("INIT:CONT OFF")

        # Configure the measure to be performed
        # Skew between the slave and master
        self.drv.write("CONFIGURE:TINTERVAL (@%d),(@%d)" % (self.slave_chan,self.master_chan))

        # Take one sample
        self.drv.write("TRIG:COUNT 1;:ARM:COUNT 1")

        # Set input coupling to AC
        self.drv.write("INPUT1:COUPling DC")
        time.sleep(0.5)
        self.drv.write("INPUT2:COUPling DC")
        time.sleep(0.5)

        # Set input impedance to 1MOhm
        self.drv.write("INPUT1:IMPedance MAX")
        time.sleep(0.5)
        self.drv.write("INPUT2:IMPedance MAX")
        time.sleep(0.5)

        # Set the trigger level for both inputs
        self.drv.write("INPUT1:LEVEL:AUTO OFF")
        time.sleep(0.5)
        self.drv.write("INPUT2:LEVEL:AUTO OFF")
        time.sleep(0.5)
        self.drv.write("INPUT1:LEVEL %1.3f" % self.trig_level[0])
        time.sleep(0.5)
        self.drv.write("INPUT2:LEVEL %1.3f" % self.trig_level[1])
        time.sleep(0.5)

        # Measures format (ASCII with time stamping disabled)
        self.drv.write("FORMAT ASCII;:FORMAT:TINF OFF")
        time.sleep(0.5)

        # Check for errors in the initial configuration
        errors = self.drv.query("syst:err?")
        if errors[0] != 0 :
            # Throw an exception not a print!!
            print("Error in initial config: " + errors)

        # Measurement -------------------------------------

        mean = 0

        for i in range(n_samples) :
            # READ? command is equivalente to ABORT;INITIATE;FETCH?:
            cur = float(self.drv.query("READ?"))
            if cur > mean + self.error :
                if self.skip_values :
                    continue
                else :
                    raise MeasureError("FCA3103 ERROR: current value far from mean value : %f (%f)" % (cur,mean))
            mean += cur

            if self.show_dbg :
                print("%s TINT: %g" % (self.drv.device, cur))
            time.sleep(t_samples)
        mean /= n_samples

        return mean

    # ------------------------------------------------------------------------ #

    def time_interval(self, n_samples, tstamp=False):
        '''
        Method to measure N samples of time interval between the input channels

        Args:
            n_samples (int) : Number of measures to be done
            tstamp (bool) : Enable timestamp for each measure

        Returns:
            A list with the measure values. It's legth could be lower than n_samples
            if skip_values is activated.

        Raises:
            ValueError if master_chan or slave_chan are not set or trigger level not set.
        '''
        if self.master_chan == None :
            raise ValueError("FCA3103 ERROR: Master input channel not set.")
        if self.slave_chan == None :
            raise ValueError("FCA3103 ERROR: Slave input channel not set.")

        if self.trig_level[0] == None or \
        self.trig_level[1] == None :
            raise ValueError("FCA3103 ERROR: Trigger level not set.")

        # Initial device configuration --------------------

        # Reset the device
        self.drv.write("*RST")
        time.sleep(0.5)

        # Trigger mode continuous
        self.drv.write("INIT:CONT OFF")

        # Configure the measure to be performed
        # Skew between the slave and master
        self.drv.write("CONFIGURE:TINTERVAL (@%d),(@%d)" % (self.slave_chan,self.master_chan))

        # Configure the arming sistem
        self.drv.write("TRIG:COUNT 1;:ARM:COUNT %d" % (n_samples))

        # Set input coupling to AC
        self.drv.write("INPUT1:COUPling DC")
        time.sleep(0.5)
        self.drv.write("INPUT2:COUPling DC")
        time.sleep(0.5)

        # Set input impedance to 1MOhm
        self.drv.write("INPUT1:IMPedance MAX")
        time.sleep(0.5)
        self.drv.write("INPUT2:IMPedance MAX")
        time.sleep(0.5)

        # Set the trigger level for both inputs
        self.drv.write("INPUT1:LEVEL:AUTO OFF")
        time.sleep(0.5)
        self.drv.write("INPUT2:LEVEL:AUTO OFF")
        time.sleep(0.5)
        self.drv.write("INPUT1:LEVEL %1.3f" % self.trig_level[0])
        time.sleep(0.5)
        self.drv.write("INPUT2:LEVEL %1.3f" % self.trig_level[1])
        time.sleep(0.5)

        # Measures format (ASCII with time stamping disabled)
        self.drv.write("FORMAT ASCII;:FORMAT:TINF %s" % ("ON" if tstamp else "OFF"))
        time.sleep(0.5)

        # Check for errors in the initial configuration
        # errors = self.drv.query("syst:err?")
        # if errors[0] != 0 :
        #     # Throw an exception not a print!!
        #     print("Error in initial config: " + errors)
        #     return None

        # Initiate the sampling
        self.drv.write("INIT")

        # Measurement -------------------------------------
        samples = []
        end = int(n_samples/2)

        for i in range(end):
            # FETCH? command reads from output buffer
            cur = self.drv.query("FETCH:ARR? 2")
            cur = cur.split(',')

            if tstamp:
                samples.append(( float(cur[0]), float(cur[1]) ))
                samples.append(( float(cur[2]), float(cur[3]) ))
            else:
                samples.append(float(cur[0]))
                samples.append(float(cur[1]))
            time.sleep(2) # Sleep for 2 secs after each fetch
        if end < n_samples:
            cur = self.drv.query("FETCH:ARR? 1")
            cur = cur.split(',')
            if tstamp:
                samples.append(( float(cur[0]), float(cur[1]) ))
            else:
                samples.append(float(cur[0]))

        return samples
