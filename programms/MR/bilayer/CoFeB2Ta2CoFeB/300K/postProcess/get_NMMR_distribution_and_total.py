#! /usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
import argparse
import codecs
from math import pi

def dNMMR(H_z_t, M_z_t, H_z_b, M_z_b, k=1):
    return -k*( 2*(H_z_t-4*pi*M_z_t) + 2*(H_z_b-4*pi*M_z_b) )

def NMMR(H_z_t, M_z_t, H_z_b, M_z_b, k=1):
    return -k * ( (H_z_t - 4 * pi * M_z_t)**2 + (H_z_b - 4 * pi * M_z_b)**2 )

def reading(input_magn, input_hext):
    print("Start reading input files")
    try:
        magn_bottom = defaultdict(list)
        magn_top = defaultdict(list)
        idx = -1
        with codecs.open(input_magn, 'r', encoding='utf-8') as fin:
            for line in fin:
                idx += 1
                if (idx < 29):
                    continue
                x, y, z, mx, my, mz = list(map(float, list(filter(lambda x: len(x) > 0, line.strip().split(' ')))))
                if (z != 7.5e-10):
                    if (z != 2.25e-09):
                        continue
                    else:
                        magn_top[(x, y)] = [mx, my, mz]
                else:
                    magn_bottom[(x, y)] = [mx, my, mz]
    except:
        pass
    try:
        hext_bottom = defaultdict(list)
        hext_top = defaultdict(list)
        idx = -1
        with codecs.open(input_hext, 'r', encoding='utf-8') as fin:
            for line in fin:
                idx += 1
                if (idx < 29):
                    continue
                x, y, z, hx, hy, hz = list(map(float, list(filter(lambda x: len(x) > 0, line.strip().split(' ')))))
                if (z != 7.5e-10):
                    if (z != 2.25e-09):
                        continue
                    else:
                        hext_top[(x, y)] = [hx, hy, hz]
                else:
                    hext_bottom[(x, y)] = [hx, hy, hz]
    except:
        pass
    print("End reading input files")
    return [magn_bottom, magn_top, hext_bottom, hext_top]

def numeric(magn_bottom, magn_top, hext_bottom, hext_top, output_MR=None):
    print("Start numeric calculations")
    NMMR_all = defaultdict(np.float32)
    for key in magn_top.keys():
        NMMR_all[key[0], key[1]] = NMMR(hext_top[key][2], magn_top[key][2], hext_bottom[key][2], magn_bottom[key][2])

    if output_MR is not None:
        with codecs.open(output_MR, 'w', encoding='utf-8') as fout:
            for k in NMMR_all.keys():
                x, y = k
                resist = NMMR_all[k]
                # убираем фиксу
                # фикса
                #if (x > 10**(-6)) | (x < 0.5*10**(-6)) | (y > 10**(-6)) | (y < 0.5*10**(-6)):
                #    continue
                ##########
                # Переведем из м в нм
                fout.write('\t'.join(list(map(str, [x*10**9, y*10**9, resist]))) + '\n')

    SumNMMR = 0
    for key in NMMR_all.keys():
        SumNMMR += NMMR_all[key]

    print("End numeric calculations")
    return SumNMMR

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("MagnFile", help="file with magnetisation distribution", type=str)
    parser.add_argument("FieldFile", help="file with field distribution", type=str)
    parser.add_argument("DistrFile", help="output file with NMMR distribution", type=str)
    args = parser.parse_args()
    print(f"MagnFile={args.MagnFile}")
    print(f"FieldFile={args.FieldFile}")
    MR = numeric(*reading(args.MagnFile, args.FieldFile), args.DistrFile)
    print(f"Resulting MR = {MR}")


main()

