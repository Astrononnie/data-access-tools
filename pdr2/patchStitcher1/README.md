# Patch Stitcher #1
A patch is a 4k x 4k image.  It is relatively large, but one may wish to generate a larger image.  This tool stitches adjacent patches in the same tract together.

# Usage
```sh
python patchStitcher1.py -o stitched.fits calexp-HSC-I-9813-*.fits

ds9 stitched.fits
```