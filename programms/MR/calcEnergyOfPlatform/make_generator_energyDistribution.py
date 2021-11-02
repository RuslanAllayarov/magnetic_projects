from class_generator_energyDistribution import GeneratorEnergyDistribution
import logging
import argparse

def main():
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                        level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
    logging.info("start generate")
    parser = argparse.ArgumentParser(description="[MacroSpin approach]: Generate energy distribution of bilayer under cuboud Np")    
    # output
    parser.add_argument('outFile', type=str, help='output file for energy distribution which can be used in Wolfram Mathematica')
    # NP field
    # FIXME: make calculation of field here, without import
    parser.add_argument('fieldDistrFilePath', type=str, help='input field distribution in OOMMF format')
    # mesh
    parser.add_argument('--xCellSize', type=float, default=5e-9, help='X-cell"s size [m]')
    parser.add_argument('--yCellSize', type=float, default=5e-9, help='Y-cell"s size [m]')
    parser.add_argument('--zCellSize', type=float, default=0.3e-9, help='Z-cell"s size [m]')
    parser.add_argument('--xCount', type=int, default=100, help='X-cell"s count')
    parser.add_argument('--yCount', type=int, default=100, help='Y-cell"s count')
    parser.add_argument('--zCount', type=int, default=9, help='Z-cell"s count')
    # platform parameters
    parser.add_argument('--mTop', type=float, default=700e3, help='Saturation magnetization of top layer [A/m]')
    parser.add_argument('--mBottom', type=float, default=1200e3, help='Saturation magnetization of bottom layer [A/m]')
    parser.add_argument('--kTop', type=float, default=2e3, help='Magnetic anisotropy constant of top layer [J/m^3]')
    parser.add_argument('--kBottom', type=float, default=2.5e3, help='Magnetic anisotropy constant of bottom layer [J/m^3]')
    parser.add_argument('--jEx', type=float, default=1.3e-11, help='Intralayer exchange constant [J/m]')
    parser.add_argument('--jAf', type=float, default=-0.6e-5, help='Interlayer exchange constant [J/m^2]')

    args = parser.parse_args()

    generator = GeneratorEnergyDistribution(mTop=args.mTop, mBottom=args.mBottom, kTop=args.kTop, kBottom=args.kBottom, jEx=args.jEx, jAf=args.jAf, \
                                    xCell=args.xCellSize, yCell=args.yCellSize, zCell=args.zCellSize, \
                                    xCount=args.xCount, yCount=args.yCount, zCount=args.zCount, \
                                    fieldDistrFilePath=args.fieldDistrFilePath, \
                                    outPath=args.outFile)
    generator.readingFieldOfNps()
    logging.info("Reading field distribution: DONE")
    generator.calculateEnergyDistribution()
    logging.info("Calculation energy distribution: DONE")
    generator.saveData()
    logging.info("stop generate")

main()
