from collections import defaultdict
import numpy as np
import codecs
from tqdm import tqdm
import logging

class GeneratorEnergyDistribution:
    '''
    Generate energy distribution of bilayer under cuboud NP
    Formulas of cube magnetic field are from http://www.scielo.org.mx/pdf/rmfe/v59n1/v59n1a2.pdf
    '''
    MU_0 = 1.2566370614e-6 # [H/A^2]
    EPS = 1e-18
    SPLIT_TOP = 2.25e-9 # [m]
    SPLIT_BOTTOM = 0.75e-9 # [m]
    HEIGHT_TOP = 0.9e-9 # [m]
    HEIGHT_BOTTOM = 1.2e-9 # [m]
    
    def __init__(self, mTop=None, mBottom=None, kTop=None, kBottom=None, jEx=None, jAf=None, \
                xCell=None, yCell=None, zCell=None, \
                xCount=None, yCount=None, zCount=None, \
                fieldDistrFilePath=None, \
                outPath=None):

        # Dict with input field distribution (top layer)
        self.fieldOfNPDataTop = defaultdict(list) # [m, m, m] -> [A/m, A/m, A/m]
        # Dict with input field distribution (bottom layer)
        self.fieldOfNPDataBottom = defaultdict(list) # [m, m, m] -> [A/m, A/m, A/m]

        # Dict with output energy distribution
        self.energyDistrData = defaultdict(float) # [m, m] -> [J/m^2]

        # region's size
        self.xCell = xCell
        self.yCell = yCell
        self.zCell = zCell
        self.xCount = xCount
        self.yCount = yCount
        self.zCount = zCount
        self.makeAssert()

        # bilayer's magnetic parameters
        self.mTop = mTop
        self.mBottom = mBottom
        self.kTop = kTop
        self.kBottom = kBottom
        self.jex = jEx
        self.jAf = jAf

        # input/output options
        assert(fieldDistrFilePath)
        assert(outPath)
        self.outPath = outPath
        self.fieldDistrFilePath = fieldDistrFilePath

        # convert units
        #self.convertUnits()

    def correctReadingInputLine(self, line):
        '''
        Input Format: ' ' + '  '.join(list(map(str, coords))) + '  ' + '  '.join(list(map(str, values)))
        '''
        line = line.strip().split('  ')
        coords = list(map(float, line[:3]))
        fieldComponents = list(map(float, line[3:]))
        # 1 - top split
        if abs((coords[2] - self.SPLIT_TOP)) < self.EPS:
            self.fieldOfNPDataTop[tuple(coords)] = fieldComponents
        else:
            pass
            #logging.info(f"[READING]: difference between z-components: from file = {coords[2]}, diff = {coords[2] - self.SPLIT_TOP}")
        # 2 - bottom split
        if abs((coords[2] - self.SPLIT_BOTTOM)) < self.EPS:
            self.fieldOfNPDataBottom[tuple(coords)] = fieldComponents        

    def readingFieldOfNps(self):
        with codecs.open(self.fieldDistrFilePath, 'r', encoding='utf-8') as fin:
            amountOfAuxiliaryInfoRows = 23
            counter = 0
            for line in fin:
                counter += 1
                if (counter <= amountOfAuxiliaryInfoRows):
                    continue
                try:
                    self.correctReadingInputLine(line)
                except:
                    pass
        logging.info(f"[READING]:count of readed rows: in top layer : {len(list(self.fieldOfNPDataTop.keys()))}, in bottom layer : {len(list(self.fieldOfNPDataBottom.keys()))}")

    def calculateEnergyDistribution(self):
        '''
        Calculate energy distribution:
        - output file format: X[nm] \t Y[nm] \t E(X,Y)[J/m^2]
        '''
        # FIXME: keys of fieldOfNPDataTop and fieldOfNPDataBottom are identical, may be combine them?
        for (coordsTop, coordsBottom) in tqdm(zip(self.fieldOfNPDataTop.copy().keys(), self.fieldOfNPDataBottom.copy().keys())):
            self.energyDistrData[coordsTop[:2]] = self.calculateEnergyDensityInPoint(coordsTop, coordsBottom)

    def calculateEnergyDensityInPoint(self, coordsTop, coordsBottom):
        '''
        Calculate energy distribution at point (x, y, z)
        E_total = E_zeeman + E_exchange + E_af + E_anis
        E_zeeman = -m_0 * (Htop*h_top*Mstop*cos(teta_top) + Hbot*h_bot*Msbot*cos(teta_bot))
        E_anis = -Ks_top * (cos(teta_top))^2 - Ks_bot * (cos(teta_bot))^2
        E_af = -J_af * cos(teta_top - teta_bot)
        '''
        # Zeeman energy
        cos_teta_top = np.dot(coordsTop, [0,0,1])/np.sqrt(np.sum([el**2 for el in coordsTop]))
        cos_teta_bottom = np.dot(coordsBottom, [0,0,1])/np.sqrt(np.sum([el**2 for el in coordsBottom]))
        H_top = np.linalg.norm(self.fieldOfNPDataTop[coordsTop])
        H_bottom = np.linalg.norm(self.fieldOfNPDataTop[coordsBottom])
        zeemanEnergyDensity = -self.MU_0 * (H_top*self.HEIGHT_TOP*self.mTop*cos_teta_top + H_bottom*self.HEIGHT_BOTTOM*self.mBottom*cos_teta_bottom)
        # Anisotropy energy
        K_s_top = self.kTop*self.HEIGHT_TOP # [J/m^3] -> [J/m^2]
        K_s_bottom = self.kBottom*self.HEIGHT_BOTTOM # [J/m^3] -> [J/m^2]
        anisEnergyDensity = -K_s_top*cos_teta_top**2 -K_s_bottom*cos_teta_bottom**2
        # Interlayer AF exchange energy
        teta_top = np.arccos(cos_teta_top)
        teta_bottom = np.arccos(cos_teta_bottom)
        interlayerEnergyDensity = -self.jAf * np.cos(teta_top - teta_bottom)
        # summation
        return zeemanEnergyDensity + anisEnergyDensity + interlayerEnergyDensity


    def makeAssert(self):
        assert(self.xCell != None)
        assert (self.yCell != None)
        assert (self.zCell != None)
        assert(self.xCount != None)
        assert (self.yCount != None)
        assert (self.zCount != None)


    def makeCorrectOutputLine(self, coords, value):
        '''To generate correct output line (correct to push into Wolfram Mathematica)'''
        line = '\t'.join(list(map(str, coords))) + '\t' + str(value)
        return line

    def saveData(self):
        with codecs.open(self.outPath, "w", encoding='utf-8') as fout:
            for k, v in self.energyDistrData.items():
                fout.write(self.makeCorrectOutputLine(k, v) + '\n')
