#!   /usr/bin/env   python3
# -*- coding: utf-8 -*
'''
Terminal tool to make Time Interval measures using the Tektronix FCA3103

@file
@date Created on Sep. 16, 2015
@author Felipe Torres (torresfelipex1<AT>gmail.com)
@copyright LGPL v2.1
'''

# ----------------------------------------------------------------------------|
#                   GNU LESSER GENERAL PUBLIC LICENSE                         |
#                 ------------------------------------                        |
# This source file is free software; you can redistribute it and/or modify it |
# under the terms of the GNU Lesser General Public License as published by the|
# Free Software Foundation; either version 2.1 of the License, or (at your    |
# option) any later version. This source is distributed in the hope that it   |
# will be useful, but WITHOUT ANY WARRANTY; without even the implied warrant  |
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser  |
# General Public License for more details. You should have received a copy of |
# the GNU Lesser General Public License along with this  source; if not,      |
# download it from http://www.gnu.org/licenses/lgpl-2.1.html                  |
# ----------------------------------------------------------------------------|

# -----------------------------------------------------------------------------
#                                   Import                                   --
# -----------------------------------------------------------------------------
import datetime
import argparse as arg
from subprocess import check_output

from FCA3103 import FCA3103


def main() :
    '''
    Tool for automatize the control of Tektronix FCA3103 Timer/Counter
    '''
    parser = arg.ArgumentParser(description='Tektronix FCA3103 tool')

    parser.add_argument('--function', '-f', help='Measuring Function', choices=['mtint','tint'],\
    required=True)
    parser.add_argument('--interval', '-t', help='Time between samples', type=int)
    parser.add_argument('--samples', '-s', help='Number of samples', type=int, \
    default=1)
    parser.add_argument('--debug', '-d', help="Enable debug output", action="store_true", \
    default=False)
    parser.add_argument('--device', '-l', help="Device port", type=int, default=1)
    parser.add_argument('--output', '-o', help='Output data file', type=str)
    parser.add_argument('--ref', '-r', help='Input channel for the reference',type=int, \
    choices=[1,2],default=1)
    parser.add_argument('--trigl','-g',help='Input trigger level', type=float, \
    default=1.5)
    parser.add_argument('--skip','-i',help='Ignore values far from mean  plus error',type=int, \
    default=0)
    parser.add_argument('--tstamp','-x', help='Add timestamping for each measure',action="store_true", \
    default=False)

    args = parser.parse_args()

    valid_port = False
    ports = check_output(["""ls /dev | grep usbtmc"""],shell=True)[:-1]
    for p in ports.splitlines():
        p = p.decode('utf-8')
        if int(p[-1]) == args.device:
            valid_port = True
    if not valid_port:
        print("No device found at /dev/usbtmc%d" % (args.device))
        exit(6)  # No such device or address

    device = FCA3103(args.device, args.ref, 2 if args.ref == 1 else 1)
    device.show_dbg = args.debug
    device.t_samples = args.interval
    device.n_samples = args.samples
    device.skip_values = True if args.skip > 0 else False
    device.error = args.skip
    # TODO: Add de posibility of using different trigger values for the inputs
    device.trig_level[0] = device.trig_level[1] = args.trigl
    # try:
    if args.function == 'mtint':
        print("Measuring Mean Time Interval between the inputs (%d secs)..." % (args.samples))
        mean = device.mean_time_interval(args.samples, args.interval)
        print("Mean Time Interval for %d samples: %g" % (args.samples, mean))

    elif args.function == 'tint':
        print("Measuring Time Interval between the inputs (%d secs)..." % (args.samples+10))
        values = device.time_interval(args.samples, tstamp=args.tstamp)
        if args.output:
            with open(args.output,'a+') as file:
                file.write("# Time Interval Measurement (%d samples) with Tektronix FCA3103 (50ps)\n" % args.samples)
                file.write("# %s\n" % datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
                for v in values:
                    if args.tstamp:
                        file.write("%g\t%g\n" % (v[0], v[1]))
                    else:
                        file.write(str(v))
                        file.write("\n")
            print("Output writed to '%s'" % (args.output))
        else:
            print("Time Interval Measurement (%d samples) with Tektronix FCA3103 (50ps)" % args.samples)
            print("%s\n" % datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
            for v in values:
                print(v)

    # except Exception as e:
    #     print(e)

if __name__ == "__main__" :
    main()
