# python module calling butler
import lsst.daf.persistence as dafPersist

# Specify rerun directory in which the data you want to use is stored
dataDir = "<HOME>/HSC/rerun/<RERUN>"

# Call butler
butler = dafPersist.Butler(dataDir)

# Specify the target data and searched by butler
#
# CORR-0029414-059.fits
# 'calexp' means CORR-*.fits
# For calexp type data, you need to specify visit and ccd in dataId
dataId = {'visit': 29414, 'ccd': 59}
exp = butler.get('calexp', dataId)


import lsst.afw.display.ds9 as ds9

ds9.mtv(exp)
ds9.setMaskTransparency(50)

# get the exposure from the butler
sources = butler.get('src', dataId)

# plot the sources
X = sources.getX()
Y = sources.getY()
for x, y in zip(X, Y):
    ds9.dot('o', x, y, size=20)

