import codecs
import logging
from collections import defaultdict
from statistics import mode
import numpy as np
from mayavi import mlab

class CreatorMayavi3DPlot:
    DEFAULT_SCALE_COORDS=1
    DEFAULT_SCALE_MAGN=1
    EPSILON=np.float(1e-10)
    '''
    Create 3D picture from Mayavi package
    '''
    def __init__(self, inFile=None, scaleCoords=None, scaleMagn=None, \
                boundaryMin=None, boundaryMax=None):
        assert(inFile)
        self.inputPath=inFile
        self.scaleCoords = scaleCoords if (scaleCoords != None) else self.DEFAULT_SCALE_COORDS
        self.scaleMagn = scaleMagn if (scaleMagn != None) else self.DEFAULT_SCALE_MAGN
        self.configs = defaultdict(str)
        self.parsedData = defaultdict(list)
        # support vars
        self.HEIGHT_BOTTOM=None
        self.HEIGHT_TOP=None
        self.addOutputVars()
        # boundary conditions
        self.boundaryMin = boundaryMin
        self.boundaryMax = boundaryMax
        self.convertUnits()

    def convertUnits(self):
        '''
        Convert:
        '''
        pass

    def addOutputVars(self):
        '''Add output vars for coordinates and magnetization'''
        self.xData = []
        self.yData = []
        self.zData = []
        self.mxData = []
        self.myData = []
        self.mzData = []

    def readConfigsFromInput(self, line):
        line = line.strip().split(':')
        param = line[0].split(' ')[1]
        if param in ['Title', 'Desc', 'xstepsize', 'ystepsize', 'zstepsize', \
                    'xmin', 'ymin', 'zmin', 'xmax', 'ymax', 'zmax', 'valueunit']:
            self.configs[param] = ': '.join(line[1:])
            logging.debug('[CONFIG] %s : %s', param, self.configs[param])

    def normMagn(self, lst):
        '''
        mx, my, mz -> mx/mod, my/mod, mz/mod
        '''
        module = np.sqrt(np.sum(list(map(lambda el: el**2, lst))))
        try:
            if module != 0:
                return list(map(lambda el: el / module, lst))
            else:
                return lst
        except:
            logging.error("error in normalization of magnetization")

    def isInsideBoundary(self, x, y):
        ''' filter by XY coordinates [boundaryMin, boundaryMax]'''
        if (x >= self.boundaryMin) & (x <= self.boundaryMax) & (y >= self.boundaryMin) & (y <= self.boundaryMax):
            return True
        return False


    def readOOMMFFile(self):
        '''
        Read OOMMF output (magnetization) and save it
        '''
        with codecs.open(self.inputPath, "r", encoding='utf-8') as fin:
            logging.debug('[READ] open file %s', self.inputPath)
            for line in fin:
                # process of configs
                if line.startswith('#'):
                    self.readConfigsFromInput(line)
                    continue
                # process of data
                line = line.strip().split()
                x, y, z = list(map(np.float, line[:3]))
                # boundary's filter
                if not self.isInsideBoundary(x, y):
                    continue
                mx, my, mz = self.normMagn(list(map(np.float, line[3:])))
                self.saveMagn(x, y, z, mx, my, mz)

    def changeOutputScale(self, xComp, yComp, zComp, Type='length'):
        '''
        if we want to write data not nm or A/m
        [FIXME] We can add different multipliers for all coords and magn. components (for correct image in Mayavi)
        '''
        if Type == 'length':
            xComp, yComp, zComp = list(map(lambda el: el*self.scaleCoords, [xComp, yComp, zComp]))
            # Additional actions
            zComp *= 50
        if Type == 'magnetization':
            xComp, yComp, zComp = list(map(lambda el: el*self.scaleMagn, [xComp, yComp, zComp]))
        return xComp, yComp, zComp

    def isfilteredOutputByZ(self, z):
        '''Choose by 1 slice in top and bottom layers'''
        if ((np.abs(z-self.HEIGHT_BOTTOM) > self.EPSILON) & (np.abs(z-self.HEIGHT_TOP) > self.EPSILON)):
            return False
        return True

    def saveDataImpl(self, x, y, z, mx, my, mz):
        '''Just save data in correspondent lists'''
        # save coordinates
        self.xData.append(x)
        self.yData.append(y)
        self.zData.append(z)
        # save magnetization
        self.mxData.append(mx)
        self.myData.append(my)
        self.mzData.append(mz)

    def saveMagn(self, x, y, z, mx, my, mz):
        '''
        Save x, y, z, mx, my, mz data from OOMMF file (just for top and bottom layer)
        '''
        # filter by 1 slice in top and 1 in bottom layers
        self.HEIGHT_BOTTOM = np.float(self.configs['zmin']) + np.float(self.configs['zstepsize'])/2
        self.HEIGHT_TOP = np.float(self.configs['zmax']) - np.float(self.configs['zstepsize'])/2
        if (self.isfilteredOutputByZ(z)):
            x, y, z = self.changeOutputScale(x, y, z, Type='length')
            mx, my, mz = self.changeOutputScale(mx, my, mz, Type='magnetization')
            self.saveDataImpl(x, y, z, mx, my, mz)


    @mlab.show
    def createMayaviPucture(self):
        '''Start Mayavi session'''
        pointer = mlab.quiver3d(self.xData, self.yData, self.zData, self.mxData, self.myData, self.mzData,\
                        line_width=10, mask_points=3, scalars=self.mzData,\
                        mode='cone', colormap="plasma", scale_mode="none", scale_factor=200)
        pointer.glyph.color_mode = 'color_by_scalar'
        # scale_factor=75, mask_points=5, colormap="plasma"

