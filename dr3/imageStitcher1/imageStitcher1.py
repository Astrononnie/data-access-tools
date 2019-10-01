# usage:
#   python imageStitcher1.py -o ngc4030-stitch.fits ngc4030-out/deepCoadd/HSC-G/0/*/calexp-HSC-G-0-*

import numpy
from astropy.io import fits as afits
import logging
import math
import logging ; logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
import traceback


def stitchedHdu(files, boundary, nodata=float('nan'), meta_index=0, image_index=1, dtype='float32'):
    #        ^
    #        |
    #        |
    #   +----+----------------+
    #   |    |             (maxx, maxy)
    #   | +--+-------+        |
    #   | |  |    (naxis1-crpix1, naxis2-crpix2)
    #   | |  |       |        |
    #---|-+--O-------+--------+--->
    #   | |  |       |        |
    #   | +--+-------+        |
    #   |(-crpix1, -crpix2)   |
    #   +----+----------------+
    # (minx, miny)
    #

    ((minx, miny), (maxx, maxy)) = boundary

    width = maxx - minx
    height = maxy - miny

    logging.info('allocating image buffer %(width)d x %(height)d' % locals())
    pool = numpy.empty((height, width), dtype=dtype)
    pool.fill(nodata)

    baseFluxMag0 = 10 ** (27 / 2.5)

    for fname in files:
        logging.info('pasting %(fname)s...' % locals())
        try:
            with afits.open(fname) as hdul:
                fluxMag0, fluxMag0Err = getFluxMag0(hdul)
                header = hdul[image_index].header
                data = hdul[image_index].data
            crpix1 = int(header['CRPIX1'])
            crpix2 = int(header['CRPIX2'])
            naxis1 = header['NAXIS1']
            naxis2 = header['NAXIS2']
            pool[-crpix2 - miny : naxis2 - crpix2 - miny,
                 -crpix1 - minx : naxis1 - crpix1 - minx] = (baseFluxMag0 / fluxMag0) * data
        except:
            traceback.print_exc()
    
    header['FLUXMAG0'] = baseFluxMag0

    hdu = afits.ImageHDU(pool)
    header['LTV1']   += -header['CRPIX1'] - minx
    header['LTV2']   += -header['CRPIX2'] - miny
    header['CRPIX1'] = -minx
    header['CRPIX2'] = -miny
    hdu.header = header

    return hdu


def boundary(files, image_index=1):
    #    ^
    #    |    +---------+
    #    |    |        (X,Y)
    #    |    |         |
    #    |    +---------+
    #    |   (x,y)
    #----O------------------->
    #    |

    logging.info('setting stitched image boundary.')
    minx = []
    miny = []
    maxx = []
    maxy = []
    for fname in files:
        logging.info('reading header of %(fname)s...' % locals())
        with afits.open(fname) as hdul:
            header = hdul[image_index].header
            minx.append(int(-header['CRPIX1']))
            miny.append(int(-header['CRPIX2']))
            maxx.append(int(-header['CRPIX1'] + header['NAXIS1']))
            maxy.append(int(-header['CRPIX2'] + header['NAXIS2']))
    return (min(minx), min(miny)), (max(maxx), max(maxy))


def getFluxMag0(hdus):
    if 'FLUXMAG0' in hdus[0].header:
        return hdus[0].header['FLUXMAG0'], float('nan')
    else:
        entryHduIndex = hdus[0].header["AR_HDU"] - 1
        entryHdu = hdus[entryHduIndex]
        photoCalibId = hdus[0].header["PHOTOCALIB_ID"]
        photoCalibEntry, = entryHdu.data[entryHdu.data["id"] == photoCalibId]
        photoCalibHdu = hdus[entryHduIndex + photoCalibEntry["cat.archive"]]
        start = photoCalibEntry["row0"]
        end = start + photoCalibEntry["nrows"]
        photoCalib, = photoCalibHdu.data[start:end]
        calibrationMean = photoCalib["calibrationMean"]
        calibrationErr  = photoCalib["calibrationErr"]
        if calibrationMean != 0.0:
            fluxMag0 = (1.0e+23 * 10**(48.6 / (-2.5)) * 1.0e+9) / calibrationMean
            fluxMag0Err = (1.0e+23 * 10**(48.6 / (-2.5)) * 1.0e+9) / calibrationMean**2 * calibrationErr
        else:
            fluxMag0 = float('nan')
            fluxMag0Err = float('nan')
        return fluxMag0, fluxMag0Err


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='This tool stitches adjacent patches in the same tract together.')
    parser.add_argument('--out', '-o', required=True, help='output file')
    parser.add_argument('files', nargs='+', metavar='FILE', help='patch files to be stitched')
    args = parser.parse_args()

    boundary = boundary(args.files)
    imageHdu = stitchedHdu(args.files, boundary)
    # maskHdu  = stitchedHdu(args.files, boundary, image_index=2, dtype='uint16')
    # afits.HDUList([imageHdu, maskHdu]).writeto(args.out, output_verify='fix', clobber=True)
    afits.HDUList([imageHdu]).writeto(args.out, output_verify='fix', clobber=True)
