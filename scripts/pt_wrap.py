#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- author: Fraser King -*-
# -*- date: March 22, 2023 -*-
# -*- affil: University of Michigan -*-

"""pt_wrap.py
   This file acts as an interface between thee command line and the 
   conv_pt.py convert_particle_table() utility function.
"""

##### Imports
import sys
import conv_pt

##### Read in arguments
filepath, outpath, lat, lon = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]

##### Call conversion utility
conv_pt.convert_particle_table(filepath, outpath, lat, lon)