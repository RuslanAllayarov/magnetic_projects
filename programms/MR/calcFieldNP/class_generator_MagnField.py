from collections import defaultdict
import numpy as np
import codecs

class generatorFieldCuboid:
    '''
    Generate magnetic field of cuboid
    Formulas are from http://www.scielo.org.mx/pdf/rmfe/v59n1/v59n1a2.pdf
    '''
    DEFAULT_RADIUS=0 # nm
    DEFAULT_MAGNETIZATION=0 # emu/cm3

    def __init__(self, radius=None, isCube=True, magnetization=None, axisMoment='z', \
                xMax=None, yMax=None, zMax=None, \
                xStep=None, yStep=None, zStep=None):
        self.raduis = radius if (radius != None) else self.DEFAULT_RADIUS
        self.isItCube(isCube)
        self.magn = magnetization if (magnetization != None) else self.DEFAULT_MAGNETIZATION
        self.axisMoment=axisMoment
        self.fieldData = defaultdict(list)

        # region's size
        assert(xMax & yMax & zMax)
        assert(xStep & yStep & zStep)
        self.xmin = 0
        self.ymin = 0
        self.zmin = 0
        self.xmax = xMax
        self.ymax = yMax
        self.zmax = zMax
        self.xStep = xStep
        self.yStep = yStep
        self.zStep = zStep
        

    def isItCube(self, isCube=True):
        if isCube:
            self.a = self.raduis
            self.b = self.raduis
            self.c = self.raduis
    
    def F2(self, X, Y, Z):
        numerator = np.sqrt((X+self.a)**2 + (Y-self.b)**2 + (Z+self.c)**2 ) + self.b - Y
        denominator = np.sqrt((X+self.a)**2 + (Y+self.b)**2 + (Z+self.c)**2 ) - self.b - Y
        return numerator/denominator
    
    def F1(self, X, Y, Z):
        denominator = (Z+self.c)*np.sqrt((X+self.a)**2 + (Y+self.b)**2 + (Z+self.c)**2)
        return np.arctan((X+self.a)*(Y+self.b)/denominator)
    
    def Hx(self, X, Y, Z):
        pass

    def Hy(self, X, Y, Z):
        pass

    def Hz(self, X, Y, Z):
        pass

