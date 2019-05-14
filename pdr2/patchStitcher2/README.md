# Patch Stitcher #2
Similar to [Patch Stitcher #1](../patchStitcher1), but this one allows you to stitch patches in different tracts together.  The HSC (or LSST) pipeline has to be installed to use this tool.  The overlapping regions between the adjacent tracts are not exactly the same; tract A may have slightly different DNs and astrometry from tract B in the overlapping region.  This tool simply adopts the pixels from tract B in the resultant image.

## Usage
```sh
python patchStitcher2.py -o product ./pdr1_wide/deepCoadd-results/HSC-I/852[45]/*,*/calexp-*.fits
ds9 product/stitched.fits
```
