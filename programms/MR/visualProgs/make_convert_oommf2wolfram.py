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
    args = parser.parse_args()
    
    converter = ParserOommf(inputPath=args.inFile, outputPathTop=args.outFileTop, outputPathBottom=args.outFileBottom)
    converter.readFile()
    converter.writeToFiles()
    logging.info("stop comvert")

main()