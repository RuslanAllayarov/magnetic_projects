from class_generator_energyDistribution import GeneratorEnergyDistribution
import logging
import argparse

def main():
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                        level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
    logging.info("start generate")
    parser = argparse.ArgumentParser(description="[MacroSpin approach]: Generate energy distribution of bilayer under cuboud Np")    

    # output
    parser.add_argument('--outFile', type=str, required=True, help='output file for energy distribution which can be used in Wolfram Mathematica')
    parser.add_argument('--scaleCoeff', type=float, default=1, help='scale coeffitient for output energy distribution')
    parser.add_argument('--xMin', type=float, default=0, help='left boundary at X-axis [m]')
    parser.add_argument('--xMax', type=float, default=1, help='right boundary at X-axis [m]')
    parser.add_argument('--yMin', type=float, default=0, help='left boundary at Y-axis [m]')
    parser.add_argument('--yMax', type=float, default=1, help='right boundary at Y-axis [m]')

    # input distributions
    # FIXME: make calculation of field here, without import
    parser.add_argument('--fieldFile', type=str, required=True, help='input field distribution in OOMMF format')
    parser.add_argument('--magnFile', type=str, required=True, help='input magnetization distribution from OOMMF')

    # mesh
    # FIXME all vars're unused
    parser.add_argument('--xCellSize', type=float, default=5e-9, help='X-cell"s size [m]')
    parser.add_argument('--yCellSize', type=float, default=5e-9, help='Y-cell"s size [m]')
    parser.add_argument('--zCellSize', type=float, default=0.3e-9, help='Z-cell"s size [m]')
    parser.add_argument('--xCount', type=int, default=100, help='X-cell"s count')
    parser.add_argument('--yCount', type=int, default=100, help='Y-cell"s count')
    parser.add_argument('--zCount', type=int, default=9, help='Z-cell"s count')

    # platform parameters
    parser.add_argument('--mTop', type=float, default=700e3, help='Saturation magnetization of top layer [A/m]') # FIXME unused var
    parser.add_argument('--mBottom', type=float, default=1200e3, help='Saturation magnetization of bottom layer [A/m]') # FIXME unused var
    parser.add_argument('--kTop', type=float, default=2e3, help='Magnetic anisotropy constant of top layer [J/m^3]')
    parser.add_argument('--kBottom', type=float, default=2.5e3, help='Magnetic anisotropy constant of bottom layer [J/m^3]')
    parser.add_argument('--jEx', type=float, default=1.3e-11, help='Intralayer exchange constant [J/m]')
    parser.add_argument('--jAf', type=float, default=-0.6e-5, help='Interlayer exchange constant [J/m^2]')

    # select energy contributions
    parser.add_argument('--isIncludeZeeman', type=int, default=1, help='Is include Zeeman energy to total energy or not? 0 - not , 1 - yes')
    parser.add_argument('--isIncludeAF', type=int, default=1, help='Is include AF exchange energy to total energy or not? 0 - not , 1 - yes')
    parser.add_argument('--isIncludeAnisotropy', type=int, default=1, help='Is include Anisotropy energy to total energy or not? 0 - not , 1 - yes')

    args = parser.parse_args()
    generator = GeneratorEnergyDistribution(mTop=args.mTop, mBottom=args.mBottom, kTop=args.kTop, kBottom=args.kBottom, jEx=args.jEx, jAf=args.jAf, \
                                    xCell=args.xCellSize, yCell=args.yCellSize, zCell=args.zCellSize, \
                                    xCount=args.xCount, yCount=args.yCount, zCount=args.zCount, \
                                    fieldDistrFilePath=args.fieldFile, \
                                    magnDistrFilePath=args.magnFile, \
                                    isIncludeZeeman=args.isIncludeZeeman, isIncludeAF=args.isIncludeAF, isIncludeAnisotropy=args.isIncludeAnisotropy, \
                                    outPath=args.outFile, scaleCoeff=args.scaleCoeff, xMin=args.xMin, xMax=args.xMax, yMin=args.yMin, yMax=args.yMax)
    generator.readingFieldOfNps()
    generator.readingMagnetization()
    logging.info("Reading field and magentization distributions: DONE")
    generator.calculateEnergyDistribution()
    logging.info("Calculation energy distribution: DONE")
    generator.saveData()
    logging.info("stop generate")

main()
