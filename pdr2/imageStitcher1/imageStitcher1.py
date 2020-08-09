# usage:
#   python imageStitcher1.py -o ngc4030-stitch.fits ngc4030-out/deepCoadd/HSC-G/0/*/calexp-HSC-G-0-*

import argparse
import logging
from typing import Any, Dict, List, Tuple, cast

import numpy
from astropy.io import fits as afits


def main():
    parser = argparse.ArgumentParser(description='This tool stitches adjacent patches in the same tract together.')
    parser.add_argument('--out', '-o', required=True, help='output file')
    parser.add_argument('--no-image', dest='image', action='store_false', default=True)
    parser.add_argument('--mask', '-m', action='store_true')
    parser.add_argument('--variance', '-V', action='store_true')
    parser.add_argument('files', nargs='+', metavar='FILE', help='patch files to be stitched')
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

    bbox = containing_bbox(args.files)
    hdul: List = [afits.PrimaryHDU()]
    if args.image:
        hdul.append(ImageStitcher(files=args.files, bbox=bbox).hdu)
    if args.mask:
        hdul.append(MaskStitcher(files=args.files, bbox=bbox).hdu)
    if args.variance:
        hdul.append(VarianceStitcher(files=args.files, bbox=bbox).hdu)
    afits.HDUList(hdul).writeto(args.out, overwrite=True, output_verify='silentfix')


BBox = Tuple[Tuple[int, int], Tuple[int, int]]


class Stitcher:
    dtype = ...
    nodata = ...
    hdu_index = ...
    fits_open_options = dict()

    def __init__(self, *, files: List[str], bbox: BBox):
        self._files = files
        self._bbox = bbox
        self.hdu = self._stitch()

    def _stitch(self):
        ((minx, miny), (maxx, maxy)) = self._bbox

        width = maxx - minx
        height = maxy - miny

        logging.info(f'allocating image buffer {width} x {height}')
        pool = numpy.empty((height, width), dtype=self.dtype)
        pool.fill(self.nodata)

        header = cast(afits.Header, None)
        data = cast(numpy.ndarray, None)

        for fname in self._files:
            logging.info(f'pasting {fname}...')
            with afits.open(fname, **self.fits_open_options) as hdul:
                try:
                    header = hdul[self.hdu_index].header  # type: ignore
                    data = hdul[self.hdu_index].data  # type: ignore
                except:
                    logging.info(f'failed to read {fname}')
                    continue
                crpix1 = int(header['CRPIX1'])  # type: ignore
                crpix2 = int(header['CRPIX2'])  # type: ignore
                naxis1 = header['NAXIS1']
                naxis2 = header['NAXIS2']
                pool[-crpix2 - miny: naxis2 - crpix2 - miny,
                     -crpix1 - minx: naxis1 - crpix1 - minx] = self._normalized_data(data, hdul)

        header['LTV1'] += -header['CRPIX1'] - minx  # type: ignore
        header['LTV2'] += -header['CRPIX2'] - miny  # type: ignore
        header['CRPIX1'] = -minx
        header['CRPIX2'] = -miny
        self._cleanup_header(header)
        return afits.ImageHDU(data=pool, header=header)

    def _normalized_data(self, data: numpy.ndarray, hdul: afits.HDUList) -> numpy.ndarray:
        ...

    def _cleanup_header(self, header: afits.Header) -> None:
        ...


MAG0 = 10 ** (27 / 2.5)


class ImageStitcher(Stitcher):
    dtype = 'float32'
    nodata = float('nan')
    hdu_index = 1

    def _normalized_data(self, data: numpy.ndarray, hdul: afits.HDUList):
        mag0, mag0_err = get_mag0(hdul)
        return data / (mag0 / MAG0)

    def _cleanup_header(self, header: afits.Header):
        header['FLUXMAG0'] = MAG0
        if 'FLUXMAG0ERR' in header:
            del header['FLUXMAG0ERR']


class VarianceStitcher(Stitcher):
    dtype = 'float32'
    nodata = float('nan')
    hdu_index = 3

    def _normalized_data(self, data: numpy.ndarray, hdul: afits.HDUList):
        mag0, mag0_err = get_mag0(hdul)
        return data / ((mag0 / MAG0) ** 2)

    def _cleanup_header(self, header: afits.Header):
        header['FLUXMAG0'] = MAG0
        if 'FLUXMAG0ERR' in header:
            del header['FLUXMAG0ERR']


class MaskStitcher(Stitcher):
    dtype = 'int32'
    nodata = 0
    hdu_index = 2
    fits_open_options = dict(do_not_scale_image_data=True)

    def __init__(self, *args, **kwargs):
        self._mp: Dict[str, int] = {}
        super().__init__(*args, **kwargs)

    def _normalized_data(self, data: numpy.ndarray, hdul: afits.HDUList):
        header: afits.Header = hdul[self.hdu_index].header  # type: ignore
        mp_keys = [k for k in header.keys() if k.startswith('MP_')]
        pool = numpy.zeros_like(data)
        for k in mp_keys:
            b1 = header[k]
            if k not in self._mp:
                self._mp[k] = len(self._mp)
            b2 = self._mp[k]
            pool[(data & (1 << b1)) != 0] |= 1 << b2
        return pool

    def _cleanup_header(self, header: afits.Header):
        for k, b in self._mp.items():
            header[k] = b


def containing_bbox(files: List[str], image_index=1) -> BBox:
    #    ^
    #    |    +---------+
    #    |    |        (X,Y)
    #    |    |         |
    #    |    +---------+
    #    |   (x,y)
    # ----O------------------->
    #    |

    logging.info('setting stitched image boundary.')
    minx = []
    miny = []
    maxx = []
    maxy = []
    for fname in files:
        logging.info('reading header of %(fname)s...' % locals())
        with afits.open(fname) as hdul:
            header = hdul[image_index].header  # type: ignore
            assert float.is_integer(header['CRPIX1'])
            assert float.is_integer(header['CRPIX2'])
            minx.append(int(-header['CRPIX1']))
            miny.append(int(-header['CRPIX2']))
            maxx.append(int(-header['CRPIX1'] + header['NAXIS1']))
            maxy.append(int(-header['CRPIX2'] + header['NAXIS2']))
    return (min(minx), min(miny)), (max(maxx), max(maxy))


def get_mag0(_hdul: afits.HDUList) -> Tuple[float, float]:
    hdul: Any = _hdul
    if 'FLUXMAG0' in hdul[0].header:
        return hdul[0].header['FLUXMAG0'], hdul[0].header.get('FLUXMAG0ERR', float('nan'))
    else:
        entryHduIndex = hdul[0].header["AR_HDU"] - 1
        entryHdu = hdul[entryHduIndex]
        photoCalibId = hdul[0].header["PHOTOCALIB_ID"]
        photoCalibEntry, = entryHdu.data[entryHdu.data["id"] == photoCalibId]
        photoCalibHdu = hdul[entryHduIndex + photoCalibEntry["cat.archive"]]
        start = photoCalibEntry["row0"]
        end = start + photoCalibEntry["nrows"]
        photoCalib, = photoCalibHdu.data[start:end]
        calibrationMean = photoCalib["calibrationMean"]
        calibrationErr = photoCalib["calibrationErr"]
        if calibrationMean != 0.0:
            fluxMag0 = (1.0e+23 * 10**(48.6 / (-2.5)) * 1.0e+9) / calibrationMean
            fluxMag0Err = (1.0e+23 * 10**(48.6 / (-2.5)) * 1.0e+9) / calibrationMean**2 * calibrationErr
        else:
            fluxMag0 = float('nan')
            fluxMag0Err = float('nan')
        return fluxMag0, fluxMag0Err


if __name__ == '__main__':
    main()
