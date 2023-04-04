#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- author: Fraser King -*-
# -*- date: March 15, 2023 -*-
# -*- affil: University of Michigan -*-

"""ed_wrap.py
   This file acts as an interface between thee command line and the 
   conv_pip.py convert_ed() utility function.
"""

##### Imports
import sys
import conv_pip

##### Read in arguments
filepath, outpath, lat, lon, loc = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5],

##### Call conversion utility
conv_pip.convert_ed(filepath, outpath, lat, lon, loc)