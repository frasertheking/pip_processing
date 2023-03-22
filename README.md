# PIP Processing

This repository contains a set of utility scripts in Python which convert Precipitation Imaging Probe (PIP) data from .dat to a zlib compressed CF-1.10 format netCDF.

The utility conversion scripts are contained in conv_pip.py, along with a set of wrapper functions (ed_wrap.py and dist_wrap.py) which can be used in a shell script. This allows for easy conversion of thousands of files, as you can see in the example shell script example_convert.sh.

We include methods for extracting both 2D variables (i.e. DSD, VVD and RHO) along with 1D summary table data (i.e. effective density, rain rate and non-rain rate).

## Required Packages
- pandas
- xarray

## Example
If you download a set of Level 3/Study PIP data, you can edit the data path in example_convert.sh and run it with the following command:

```bash
  ./example_convert.sh
```

## Level 3 Particle Tables
Since the particle table files are compressed with a unique file/directory structure, we have a slightly different workflow for converting these to netCDF files.

```bash
  ./example_pt_convert.sh
```

## Contact
Fraser King
kingfr@umich.edu
University of Michigan
