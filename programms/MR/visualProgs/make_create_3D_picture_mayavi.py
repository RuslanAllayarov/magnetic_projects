from matplotlib.pyplot import sca
from class_creator_3D_picture_mayavi import CreatorMayavi3DPlot
import argparse
import logging

def main():
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                        level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
    logging.info("start create")
    parser = argparse.ArgumentParser(description="create OOMMF magnetization's output to Mayavi 3D plot (interactively)")
    parser.add_argument('inFile', type=str, help='distribution file saved from OOMMF')
    # optional 
    parser.add_argument('--scaleCoords', type=float, default=1, help='scale parameter for output coordinates')
    parser.add_argument('--scaleMagn', type=float, default=1, help='scale parameter for output magnetization')
    parser.add_argument('--boundaryMin', type=float, default=0, help='min of boundary"s coordinate of output')
    parser.add_argument('--boundaryMax', type=float, default=1, help='max of boundary"s coordinate of output')
    args = parser.parse_args()
    logging.debug('Scale arguments: scaleCoords = %f, scaleMagn = %f', args.scaleCoords, args.scaleMagn)

    creator = CreatorMayavi3DPlot(inFile=args.inFile, scaleCoords=args.scaleCoords, scaleMagn=args.scaleMagn)
    creator.readOOMMFFile()
    creator.createMayaviPucture()
    logging.info("stop create")

main()