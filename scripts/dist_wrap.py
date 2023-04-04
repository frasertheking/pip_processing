#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- author: Fraser King -*-
# -*- date: March 15, 2023 -*-
# -*- affil: University of Michigan -*-

"""dist_wrap.py
   This file acts as an interface between thee command line and the 
   conv_pip.py convert_dist() utility function.
"""

##### Imports
import sys
import conv_pip

##### Read in arguments
filepath, outpath, var, lat, lon, units, long_name, standard_name, loc = \
      sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8], sys.argv[9]

##### Call conversion utility
conv_pip.convert_dist(filepath, outpath, var, lat, lon, units, long_name, standard_name, loc)