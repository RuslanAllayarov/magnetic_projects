from operator import truediv
import numpy as np
from collections import defaultdict
import codecs
import logging

class ParserOommf:
    '''Parser of OOMMF output for bilayer's modeling'''
    SCALE_COORDS=1
    SCALE_MAGN=1
    EPSILON=np.float(1e-10)
    BOUNDARY_MIN=0
    BOUNDARY_MAX=1

    def __init__(self, inputPath=None, outputPathTop=None, outputPathBottom=None, scaleCoords=None, scaleMagn=None, \
                boundaryMin=None, boundaryMax=None):
        assert(inputPath)
        assert(outputPathTop)
        assert(outputPathBottom)
        self.pathIn = inputPath
        self.pathTopOut = outputPathTop
        self.pathBottomOut = outputPathBottom
        self.parsedDataTop = defaultdict(np.float)
        self.parsedDataBottom = defaultdict(np.float)
        self.configs = defaultdict(str)
        self.scaleCoords = scaleCoords if (scaleCoords != None) else self.SCALE_COORDS
        self.scaleMagn = scaleMagn if (scaleMagn != None) else self.SCALE_MAGN
        # filters
        self.boundaryMin = boundaryMin if (boundaryMin != None) else self.BOUNDARY_MIN
        self.boundaryMax = boundaryMax if (boundaryMax != None) else self.BOUNDARY_MAX
        

    def readConfigsFromInput(self, line):
        line = line.strip().split(':')
        param = line[0].split(' ')[1]
        if param in ['Title', 'Desc', 'xstepsize', 'ystepsize', 'zstepsize', \
                    'xmin', 'ymin', 'zmin', 'xmax', 'ymax', 'zmax', 'valueunit']:
            self.configs[param] = ': '.join(line[1:])
            logging.debug('[CONFIG] %s : %s', param, self.configs[param])

    def isSkipUnnecessary(self, x, y):
        '''If we want filter by coordinator's boundary'''
        if ( (x > self.boundaryMin) & (x < self.boundaryMax) & \
             (y > self.boundaryMin) & (y < self.boundaryMax) ):
            return False
        return True

    def readFile(self):
        with codecs.open(self.pathIn, "r", encoding='utf-8') as fin:
            logging.debug('[READ] open file %s', self.pathIn)
            for line in fin:
                # process of configs
                if line.startswith('#'):
                    self.readConfigsFromInput(line)
                    continue
                # process of data
                line = line.strip().split()
                x, y, z = list(map(np.float, line[:3]))
                mx, my, mz = list(map(np.float, line[3:]))
                # filter by XY boundaries
                if (self.isSkipUnnecessary(x, y)):
                    continue
                self.chooseOutType(x, y, z, mx, my, mz)

    def chooseOutType(self, x, y, z, mx, my, mz):
        '''We need do choose of type of builted distribution:
            Mz(x, y) OR Mx(y, z) OR f(Mx, My, Mz)(x, y) OR etc.'''
        #[FIXME: scale only for x, y coordinates]
        x, y, _ = self.changeOutputScale(x, y, 0, Type='length')
        mx, my, mz = self.changeOutputScale(mx, my, mz, Type='magnetization')
        # case of BOTTOM layer
        HEIGHT_BOTTOM = np.float(self.configs['zmin']) + np.float(self.configs['zstepsize'])/2
        if np.abs(z-HEIGHT_BOTTOM) < self.EPSILON:
            self.parsedDataBottom[x, y] = mz
        # case of BOTTOM layer
        HEIGHT_TOP = np.float(self.configs['zmax']) - np.float(self.configs['zstepsize'])/2
        if np.abs(z-HEIGHT_TOP) < self.EPSILON:
            self.parsedDataTop[x, y] = mz

    def changeOutputScale(self, xComp, yComp, zComp, Type='length'):
        '''if we want to write data not nm or A/m'''
        if Type == 'length':
            xComp, yComp, zComp = list(map(lambda el: el*self.scaleCoords, [xComp, yComp, zComp]))
        if Type == 'magnetization':
            xComp, yComp, zComp = list(map(lambda el: el*self.scaleMagn, [xComp, yComp, zComp]))
        return xComp, yComp, zComp

    def writerImpl(self, outPath, data):
        with codecs.open(outPath, "w", encoding='utf-8') as fout:
            for k, v in data.items():
                coords = '\t'.join(list(map(str, k)))
                values = str(v)
                fout.write(coords + '\t' + values + '\n')

    def writeToFiles(self):
        logging.info('[WRITE] bottom output: %s', self.pathBottomOut)
        self.writerImpl(self.pathBottomOut, self.parsedDataBottom)
        logging.info('[WRITE] top output: %s', self.pathTopOut)
        self.writerImpl(self.pathTopOut, self.parsedDataTop)
