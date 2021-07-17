import argparse
import logging
from class_2Dplotter_Mumax_output import Creator2DPlot

def main():
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                        level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
    logging.info("start plot")
    parser = argparse.ArgumentParser(description=" make 2D-plots of mumax's output table")
    parser.add_argument('inFile', type=str, help='table file automatically saved from mumax')
    # optional 
    parser.add_argument('--isNeedNormalizeMagn', type=bool, default=True, help='Is needed to normalize magnetization')
    parser.add_argument('--isNeedScaleField', type=bool, default=True, help='Is needed to scale values of field [T] -> [Oe]')

    args = parser.parse_args()

    creator = Creator2DPlot(inFile=args.inFile, isNeedNormalizeMagn=args.isNeedNormalizeMagn, isNeedScaleField=args.isNeedScaleField)
    creator.readMuMaxTableFile()
    creator.create2DPicture()
    logging.info("stop plot")

main()
