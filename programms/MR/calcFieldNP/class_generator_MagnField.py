from collections import defaultdict
import numpy as np
import codecs
from math import pi
from tqdm import tqdm
import logging

class GeneratorFieldCuboid:
    '''
    Generate magnetic field of cuboid
    Formulas are from http://www.scielo.org.mx/pdf/rmfe/v59n1/v59n1a2.pdf
    '''
    DEFAULT_CUBE_EDGE_SIZE=30e-9 # diameter of NP, [m]
    DEFAULT_MAGNETIZATION=0 # [emu/cm3]
    DEFAULT_BOTTOM_HEIGTH=1.2e-9 # [m]
    DEFAULT_BUFFER_HEIGHT=0.6e-9 # [m]
    DEFAULT_TOP_HEIGHT=0.9e-9 # [m]

    def __init__(self, edgeSize=None, isCube=True, magnetization=None, axisMoment='z', hadd=None, \
                xCell=None, yCell=None, zCell=None, \
                xCount=None, yCount=None, zCount=None, \
                outPath=None):
        self.edgeSize = edgeSize if (edgeSize != None) else self.DEFAULT_CUBE_EDGE_SIZE
        self.isItCube(isCube)
        self.magn = magnetization if (magnetization != None) else self.DEFAULT_MAGNETIZATION
        self.axisMoment=axisMoment
        self.hadd=hadd
        self.fieldData = defaultdict(list) # [m, m, m] -> [A/m, A/m, A/m]

        # region's size
        self.xCell = xCell
        self.yCell = yCell
        self.zCell = zCell
        self.xCount = xCount
        self.yCount = yCount
        self.zCount = zCount
        self.makeAssert()

        # calculate coordinates of NP's cluster
        self.calculateCoordsNpsCluster()

        # output options
        assert(outPath)
        self.outPath = outPath
        self.outputConfigs = []

        # convert units
        self.convertUnits()

    def calculateCoordsNpsCluster(self):
        '''
        Center of platform, near surface
        '''
        self.zNp = self.DEFAULT_BOTTOM_HEIGTH + self.DEFAULT_BUFFER_HEIGHT + self.DEFAULT_TOP_HEIGHT + \
                    self.hadd + self.edgeSize/2
        self.xNp = self.xCount * self.xCell / 2
        self.yNp = self.yCount * self.yCell / 2

    def correctCoordsByCenter(self, X, Y, Z):
        '''
        We need to change coord's argument:
        F_new(X, Y, Z) = F(X-Xnp, Y-Ynp, Z-Znp)
        '''
        X -= self.xNp
        Y -= self.yNp
        Z -= self.zNp
        return X, Y, Z

    def convertUnits(self):
        '''
        Convert:
        self.magn [emu/cm^3] -> [A/m]
        '''
        CONVERT_MAGN=1e3
        self.magn *= CONVERT_MAGN

    def makeAssert(self):
        assert(self.xCell != None)
        assert (self.yCell != None)
        assert (self.zCell != None)
        assert(self.xCount != None)
        assert (self.yCount != None)
        assert (self.zCount != None)
           

    def isItCube(self, isCube=True):
        if isCube:
            self.a = self.edgeSize/2
            self.b = self.edgeSize/2
            self.c = self.edgeSize/2
    
    def F2(self, X, Y, Z):
        numerator = np.sqrt((X+self.a)**2 + (Y-self.b)**2 + (Z+self.c)**2 ) + self.b - Y
        denominator = np.sqrt((X+self.a)**2 + (Y+self.b)**2 + (Z+self.c)**2 ) - self.b - Y
        return numerator/denominator
    
    def F1(self, X, Y, Z):
        denominator = (Z+self.c)*np.sqrt((X+self.a)**2 + (Y+self.b)**2 + (Z+self.c)**2)
        return np.arctan((X+self.a)*(Y+self.b)/denominator)
    
    def Hx(self, X, Y, Z):
        return (self.magn/(4*pi))*np.log((self.F2(-X, Y, -Z)*self.F2(X, Y, Z))/(self.F2(X, Y, -Z)*self.F2(-X, Y, Z)))

    def Hy(self, X, Y, Z):
        return (self.magn/(4*pi))*np.log((self.F2(-Y, X, -Z)*self.F2(Y, X, Z))/(self.F2(Y, X, -Z)*self.F2(-Y, X, Z)))

    def Hz(self, X, Y, Z):
        return (-self.magn/(4*pi))*( self.F1(-X, Y, Z) + self.F1(-X, Y, -Z) + self.F1(-X, -Y, Z) + self.F1(-X, -Y, -Z) + \
                self.F1(X, Y, Z) + self.F1(X, Y, -Z) + self.F1(X, -Y, Z) + self.F1(X, -Y, -Z))


    def calcField(self, X, Y, Z):
        X, Y, Z = self.correctCoordsByCenter(X, Y, Z)
        return [self.Hx(X, Y, Z), self.Hy(X, Y, Z), self.Hz(X, Y, Z)]
    
    def generateData(self):
        Xset = [ (1/2 + i) * self.xCell for i in range(self.xCount)]
        Yset = [ (1/2 + i) * self.yCell for i in range(self.yCount)]
        Zset = [ (1/2 + i) * self.zCell for i in range(self.zCount)]
        for (zdiscr, ydiscr, xdiscr) in tqdm([(z_, y_, x_) for z_ in Zset for y_ in Yset for x_ in Xset]):
            self.fieldData[xdiscr, ydiscr, zdiscr] = self.calcField(xdiscr, ydiscr, zdiscr)

    def makeCorrectOutputLine(self, coords, values):
        '''To generate correct output line (correct to push into OOMMF)'''
        line = ' ' + '  '.join(list(map(str, coords))) + '  ' + '  '.join(list(map(str, values)))
        return line

    def makeOutputConfigs(self):
        ''' The husk needed for OOMMF '''
        self.outputConfigs.append("# OOMMF: irregular mesh v1.0")
        self.outputConfigs.append("# Segment count: 1")
        self.outputConfigs.append("# Begin: Segment")
        self.outputConfigs.append("# Begin: Header")
        self.outputConfigs.append("# Title: Input magnetization field")
        self.outputConfigs.append("# meshtype: irregular")
        self.outputConfigs.append("# meshunit: m")
        self.outputConfigs.append("# pointcount: 90000") #???
        self.outputConfigs.append(f"# xstepsize: {str(self.xCell)}" ) #???
        self.outputConfigs.append(f"# ystepsize: {str(self.yCell)}") #???
        self.outputConfigs.append(f"# zstepsize: {str(self.zCell)}") #???
        self.outputConfigs.append(f"# xmin: 0")
        self.outputConfigs.append(f"# ymin: 0")
        self.outputConfigs.append(f"# zmin: 0")
        self.outputConfigs.append(f"# xmax: {str(self.xCell * self.xCount)}")
        self.outputConfigs.append(f"# ymax: {str(self.yCell * self.yCount)}")
        self.outputConfigs.append(f"# zmax: {str(self.zCell * self.zCount)}")
        self.outputConfigs.append("# valueunit: A/m")
        self.outputConfigs.append("# ValueRangeMinMag: 0")
        self.outputConfigs.append("# ValueRangeMaxMag: 0")
        self.outputConfigs.append("# valuemultiplier: 1")
        self.outputConfigs.append("# End: Header")
        self.outputConfigs.append("# Begin: Data Text")

    def saveData(self):
        with codecs.open(self.outPath, "w", encoding='utf-8') as fout:
            # write OOMFM's information
            self.makeOutputConfigs()
            for line in self.outputConfigs:
                fout.write(line + '\n')
            for k, v in self.fieldData.items():
                fout.write(self.makeCorrectOutputLine(k, v) + '\n')
            fout.write("# End: Data Text" + '\n')
            fout.write("# End: Segment" + '\n')
