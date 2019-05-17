# usage:
#   python imageStitcher1.py -o ngc4030-stitch.fits ngc4030-out/deepCoadd/HSC-G/0/*/calexp-HSC-G-0-*

import numpy
from astropy.io import fits as afits
import logging
import math
import logging ; logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')


def stitchedHdu(files, boundary, nodata=float('nan'), meta_index=0, image_index=1, dtype='float32', scale=True):
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

    for fname in files:
        logging.info('pasting %(fname)s...' % locals())
        with afits.open(fname) as hdul:
            try:
                header = hdul[image_index].header
                data = hdul[image_index].data
            except:
                logging.info('failed to read %s' % fname)
                continue
            crpix1 = int(header['CRPIX1'])
            crpix2 = int(header['CRPIX2'])
            naxis1 = header['NAXIS1']
            naxis2 = header['NAXIS2']
            pool[-crpix2 - miny : naxis2 - crpix2 - miny,
                 -crpix1 - minx : naxis1 - crpix1 - minx] = data / hdul[0].header['FLUXMAG0'] if scale else data
    if scale:
        header['FLUXMAG0'] = 1

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


'''
def cutoffBlank(data, mask):
    EDGE = 20
    blank = numpy.bitwise_and(mask, EDGE) != 0

    blank_y = numpy.all(blank, axis=1)
    blank_x = numpy.all(blank, axis=0)

    ok_y = numpy.where(numpy.logical_not(blank_y))[0]
    ok_x = numpy.where(numpy.logical_not(blank_x))[0]

    min_y, max_y = ok_y[0], ok_y[-1]
    min_x, max_x = ok_x[0], ok_x[-1]

    logging.info('(min_x, min_y), (max_x, max_y) = (%d, %d), (%d, %d)' % (min_x, min_y, max_y, max_x))

    return data[min_y : max_y, min_x : max_x]
'''


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='This tool stitches adjacent patches in the same tract together.')
    parser.add_argument('--out', '-o', required=True, help='output file')
    parser.add_argument('files', nargs='+', metavar='FILE', help='patch files to be stitched')
    args = parser.parse_args()

    boundary = boundary(args.files)
    imageHdu = stitchedHdu(args.files, boundary, scale=True)
    # maskHdu  = stitchedHdu(args.files, boundary, image_index=2, dtype='uint16')
    # afits.HDUList([imageHdu, maskHdu]).writeto(args.out, output_verify='fix', clobber=True)
    afits.HDUList([imageHdu]).writeto(args.out, output_verify='fix', clobber=True)
