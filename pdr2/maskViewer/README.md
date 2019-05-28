maskViewer
============================================================

This is a mask viewer for products of hscPipe,
designed to work without the need for the LSST stack.

Requirements
------------------------------------------------------------

  * python >= 2.7 or python >= 3.6
  * astropy
  * numpy
  * ds9, *xpaaccess* , *xpaset*

Usage
------------------------------------------------------------

### Example

    view-mask.py calexp-HSC-I-0-4,4.fits \
        detected=tomato \
        cr=purple \
        bright_object=palegoldenrod

### Details

    view-mask.py FITS MASK=COLOR [MASK=COLOR ...]

#### FITS

    You can specify the HDU to view by suffixing `[...]` to the image path.
    For example,

    view-mask.py calexp-HSC-I-0-4,4.fits[3] ...
    view-mask.py calexp-HSC-I-0-4,4.fits[VARIANCE] ...

#### colors

Colors can be

   * `#rgb` (e.g. `#fff` for white),
   * `#rrggbb` (e.g. `#000000` for black),
   * or a CSS color name.

You can see available CSS color names by:

    view-mask.py --show colors

#### masks

You can see available masks by:

    view-mask.py FITS --show masks

You will, for instance, see:

    MP_BAD
    MP_BRIGHT_OBJECT
    MP_CLIPPED
    MP_CR
    MP_CROSSTALK
    MP_DETECTED
    MP_DETECTED_NEGATIVE
    MP_EDGE

To view `MP_DETECTED`, write it in the command line
with or without the prefix `MP_` . Mask names are
case insensitive. All of the following command lines
are valid:

  * `view-mask.py FITS MP_DETECTED=white`
  * `view-mask.py FITS DETECTED=white`
  * `view-mask.py FITS detected=white`

Copyright
------------------------------------------------------------

This script is distributed under Creative Commons 0 (CC0).

To the extent possible under law, the person who associated CC0
with this work has waived all copyright and related or neighboring
rights to this work.
