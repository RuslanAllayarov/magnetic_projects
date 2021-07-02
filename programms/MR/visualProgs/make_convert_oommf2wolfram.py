from collections import defaultdict
from class_converter_oommf2wolfram import ParserOommf
import argparse
import logging

def main():
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                        level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
    logging.info("start convert")
    parser = argparse.ArgumentParser(description="convert OOMMF to Vampire")
    parser.add_argument('inFile', type=str, help='distribution file saved from OOMMF')
    parser.add_argument('outFileTop', type=str, help='output file for top layer which we can use in Wolfram')
    parser.add_argument('outFileBottom', type=str, help='output file for bottom layer which we can use in Wolfram')
    # optional 
    parser.add_argument('--scaleCoords', type=float, default=1, help='scale parameter for output coordinates')
    parser.add_argument('--scaleMagn', type=float, default=1, help='scale parameter for output magnetization')
    parser.add_argument('--boundaryMin', type=float, default=0, help='min of boundary"s coordinate of output')
    parser.add_argument('--boundaryMax', type=float, default=1, help='max of boundary"s coordinate of output')
    args = parser.parse_args()
    logging.debug('Scale arguments: scaleCoords = %f, scaleMagn = %f', args.scaleCoords, args.scaleMagn)

    converter = ParserOommf(inputPath=args.inFile, outputPathTop=args.outFileTop, outputPathBottom=args.outFileBottom, \
                            scaleCoords=args.scaleCoords, scaleMagn=args.scaleMagn, 
                            boundaryMin=args.boundaryMin, boundaryMax=args.boundaryMax)
    converter.readFile()
    converter.writeToFiles()
    logging.info("stop convert")

main()