import codecs
import logging
from collections import defaultdict
import numpy as np
from matplotlib import pyplot as plt
import matplotlib

matplotlib.use('TKAgg')

class Creator2DPlot:
    EPSILON=np.float(1e-10)
    DEFAULT_SCALE_MAGN=1e-3 # [A/m] -> [emu/cm^3]
    DEFAULT_SCALE_FIELD=1e4 # T -> Oe
    TEMPLATE_LINE="t mx my mz Bx By Bz mfull_x mfull_y mfull_z"
    '''
    Create 2D picture from table.txt file
    Needed format - TEMPLATE_LINE
    '''
    def __init__(self, inFile=None, numberXColumn=None, numberYColumn=None, \
                isNeedNormalizeMagn=None, isNeedScaleField=None):
        assert(inFile)
        self.inputPath=inFile
        self.isNeedNormalizeMagn=isNeedNormalizeMagn
        self.isNeedScaleField=isNeedScaleField
        self.parsedData = defaultdict(list)


    def changeUnits(self, lst, Type = 'magn'):
        '''
        Convert input data:
        magn [A/m] -> [emu/cm^3]
        field [T] -> Oe
        '''
        if Type == 'magn':
            lst = list(map(lambda el: el*self.DEFAULT_SCALE_MAGN, lst)) 
        if Type == 'field':
            lst = list(map(lambda el: el*self.DEFAULT_SCALE_FIELD, lst))
        return lst


    def readConfigsFromInput(self, line):
        pass


    def normalizeVector(self, lst):
        module = np.sqrt(np.sum(list(map(lambda el: el**2, lst))))
        return list(map(lambda el: el/module, lst))

    def extractMagn(self, line):
        '''
        extract magnetization from table.txt
        '''
        values = line[7:10]
        if self.isNeedNormalizeMagn:
            values = self.normalizeVector(values)
        return values

    def extractField(self, line):
        '''
        extract external field from table.txt
        '''
        values = line[4:7]
        if self.isNeedScaleField:
            values = self.changeUnits(values, Type='field')
        return values



    def readMuMaxTableFile(self):
        '''
        Read mumax's table.txt and store it
        '''
        with codecs.open(self.inputPath, "r", encoding='utf-8') as fin:
            logging.debug('[READ] open file %s', self.inputPath)
            for line in fin:
                # process of configs
                if line.startswith('#'):
                    self.readConfigsFromInput(line)
                    continue
                # process of data
                line = list(map(np.float, line.strip().split('\t')))
                mx, my, mz = self.extractMagn(line)
                Bx, By, Bz = self.extractField(line)
                self.parsedData['x'].append(Bz)
                self.parsedData['y'].append(mz)
                logging.debug('[READ] x = %f \t y = %f', Bz, mz)


    def create2DPicture(self):
        '''Create plot'''
        #self.parsedData['pointSize'] = np.abs(self.parsedData['y']) * 100
        plt.scatter('x', 'y', data=self.parsedData)
        plt.xlabel('Bz')
        plt.ylabel('mz')
        plt.show()