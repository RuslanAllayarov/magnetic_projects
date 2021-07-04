from class_generator_MagnField import GeneratorFieldCuboid
import logging
import argparse

def main():
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                        level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
    logging.info("start generate")
    parser = argparse.ArgumentParser(description="generate field's file for OOMMF's modeling")    
    # output
    parser.add_argument('outFile', type=str, help='output file for field"s distribution which we can use in OOMMF')
    # optional 
    parser.add_argument('--radius', type=float, default=15e-9, help='radius of NP [m]')
    parser.add_argument('--mSat', type=float, default=300, help='saturation magnetization [emu/cm^3]')
    parser.add_argument('--axisMoment', type=str, default='z', help='axis direction of magnetization')
    # mesh
    parser.add_argument('--xCellSize', type=float, default=5e-9, help='X-cell"s size [m]')
    parser.add_argument('--yCellSize', type=float, default=5e-9, help='Y-cell"s size [m]')
    parser.add_argument('--zCellSize', type=float, default=0.3e-9, help='Z-cell"s size [m]')
    parser.add_argument('--xCount', type=int, default=100, help='X-cell"s count')
    parser.add_argument('--yCount', type=int, default=100, help='Y-cell"s count')
    parser.add_argument('--zCount', type=int, default=9, help='Z-cell"s count')

    args = parser.parse_args()

    generator = GeneratorFieldCuboid(radius=args.radius, isCube=True, magnetization=args.mSat, axisMoment='z', \
                                    xCell=args.xCellSize, yCell=args.yCellSize, zCell=args.zCellSize, 
                                    xCount=args.xCount, yCount=args.yCount, zCount=args.zCount,
                                    outPath=args.outFile)
    generator.generateData()
    generator.saveData()
    logging.info("stop generate")

main()