from logging.handlers import DEFAULT_TCP_LOGGING_PORT
import numpy as np
import sys
from collections import defaultdict
import codecs

class ParserOommf:
    SCALE_COORDS=1
    SCALE_VALUES=1

    def __init__(self, inputPath=None, outputPath=None, scaleCoords=1, scaleValues=1):
        assert(inputPath)
        assert(outputPath)
        self.pathIn = inputPath
        self.pathOut = outputPath
        self.parsedData = defaultdict(np.float)
        self.configs = defaultdict(str)
        self.scaleCoords = scaleCoords
        self.scaleValues = scaleValues

    def chooseOutType(self, x, y, z, mx, my, mz):
        '''We need do choose of type of builted distribution:
            Mz(x, y) OR Mx(y, z) OR f(Mx, My, Mz)(x, y) OR etc.'''
        self.parsedData[x, y] = mz

    def readFile(self):
        with codecs.open(self.pathIn, "r", encoding='utf-8') as fin:
            for line in fin:
                # process of configs
                if line.startswith('#'):
                    line = line.strip().split(':')
                    param = line[0].split(' ')[1]
                    if param in ['Title', 'Desc', 'xstepsize', 'ystepsize', 'zstepsize', \
                                    'xmin', 'ymin', 'zmin', 'xmax', 'ymax', 'zmax' \
                                    'valueunit']:
                        self.configs[param] = ': '.join(line[1:])
                    continue
                # process of data
                line = line.strip().split()
                x, y, z = list(map(np.float, line[:3]))
                mx, my, mz = list(map(np.float, line[3:]))
                self.chooseOutType(x, y, z, mx, my, mz)

    def changeOutputScale(self):
        '''if we want to write data not nm or A/m'''


    def writeToFile(self):
        with codecs.open(self.pathOut, "w", encoding='utf-8') as fout:
            for k, v in self.parsedData.items():
                coords = '\t'.join(list(map(str, k)))
                value = str(v)
                fout.write(coords + '\t' + value + '\n')



                
