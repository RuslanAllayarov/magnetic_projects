#from os import X_OK
import numpy as np
import codecs
from tqdm import tqdm
from math import pi, cos, sin
np.random.seed(10)

init_message = '''# OOMMF: irregular mesh v1.0
# Segment count: 1
# Begin: Segment
# Begin: Header
# Title: for_what
# meshtype: irregular
# meshunit: m
# pointcount: 270000
# xstepsize: 5e-09
# ystepsize: 5e-09
# zstepsize: 3e-10
# xmin: 0
# ymin: 0
# zmin: 0
# xmax: 1.5e-06
# ymax: 1.5e-06
# zmax: 9e-10
# valueunit: A/m
# ValueRangeMinMag: 0
# ValueRangeMaxMag: 0
# valuemultiplier: 1
# End: Header
# Begin: Data Text
'''

end_message = '''# End: Data Text
# End: Segment
'''

init_parameters = dict()
init_parameters['Xcell'] = 5*(10**-9)
init_parameters['Ycell'] = 5*(10**-9)
init_parameters['Zcell'] = 0.3*(10**-9)
init_parameters['Xcount'] = 300
init_parameters['Ycount'] = 300
init_parameters['hlayer'] = 0.9*(10**-9)
init_parameters['hadd'] = 2.4*(10**-9)
init_parameters['Mmean'] = 287*(10**-18)
init_parameters['Rmean'] = 140*(10**-9)
init_parameters['Angle'] = 0
init_parameters['Hext'] = 100

##### ADD PARAMETERS
modeling_parameters = dict()
modeling_parameters['CountNP'] = 30
modeling_parameters['Incr'] = 8 # увеличиваем момент наночастиц в Incr раз
modeling_parameters['OUTPUTDIR'] = "data/"
modeling_parameters['OUTPUT'] = "Field_"+ str(modeling_parameters['CountNP']) + "_random_nps_" + str(init_parameters['Angle']) + "_deg.csv"


#! Поле диполя, находящегося в точке (x_part, y_part, z_part)
#! у которого момент равен Mpart
#! намагниченность направлена по вектору (0, sin(angle), cos(angle))
#! Смотрим в точке (x, y, z)
def FieldPart(Mpart, x_part, y_part, z_part, angle, x, y, z):
    anglerad = (angle / 180) * pi
    rx = x - x_part
    ry = y - y_part
    rz = z - z_part
    r = np.sqrt(rx**2 + ry**2 + rz**2)
    Hz = (1/(4*pi))*(3*rz*Mpart*(sin(anglerad)*ry + cos(anglerad)*rz)/(r**5) - Mpart*cos(anglerad)/(r**3))
    Hy = (1/(4*pi))*(3*ry*Mpart*(sin(anglerad)*ry + cos(anglerad)*rz)/(r**5) - Mpart*sin(anglerad)/(r**3))
    Hx = (1/(4*pi))*(3*rx*Mpart*(sin(anglerad)*ry + cos(anglerad)*rz)/(r**5))
    return [Hx, Hy, Hz]

#! Рандомно накидаем частицы
#! Подаем их количество + размеры плафтормы
#! На выходе список с координатами
def CoordsPart():
    Xsize = init_parameters['Xcell'] * init_parameters['Xcount']
    Ysize = init_parameters['Ycell'] * init_parameters['Ycount']
    Xcoords = np.random.uniform(0, Xsize, modeling_parameters['CountNP'])
    Ycoords = np.random.uniform(0, Ysize, modeling_parameters['CountNP'])
    print(f'Coordinates of NP: {list(zip(Xcoords, Ycoords))}')
    return (list(zip(Xcoords, Ycoords)))

def TotalField(x, y, z, angle, Hext, coords_parts):
    HX_total, HY_total, HZ_total = 0.0, 0.0, 0.0
    #znp_common - z-координата наночастицы
    #! Считает поле от всех наночастиц в конкретной точке    
    znp_common = init_parameters['hlayer'] + init_parameters['hadd'] + \
        (init_parameters['Rmean'] * (modeling_parameters['Incr'] ** 0.333))
    for (xnp, ynp) in coords_parts:
        dHx, dHy, dHz = FieldPart(init_parameters['Mmean'] * modeling_parameters['Incr'], xnp, ynp, znp_common, angle, x, y, z)
        HX_total += dHx
        HY_total += dHy
        HZ_total += dHz
    #! Добавляет к нему внешнее постоянное поле
    multiplier = 1000 / (4 * pi) # Oe -> A/m
    anglerad = (angle / 180) * pi
    HY_total += multiplier * Hext * sin(anglerad)
    HZ_total += multiplier * Hext * cos(anglerad)
    return (HX_total, HY_total, HZ_total)


#! Пайплайн
def Pipeline():
    Ztotal = init_parameters['hlayer']
    Xset = [ (1/2 + i) * init_parameters['Xcell'] for i in range(init_parameters['Xcount'])]
    Yset = [ (1/2 + i) * init_parameters['Ycell'] for i in range(init_parameters['Ycount'])]
    Zset = [ (1/2 + i) * init_parameters['Zcell'] for i in range(int(Ztotal/init_parameters['Zcell']))]

    #! Рандомно генерю наночастицы
    coords_part = CoordsPart()
    with codecs.open(modeling_parameters['OUTPUT'], 'w', encoding='utf-8') as fout:
        # Всякая шелуха вначале
        fout.write(init_message)
        # Цикл по всем ячейкам дискретизации
        for (zdiscr, ydiscr, xdiscr) in tqdm([(z_, y_, x_) for z_ in Zset for y_ in Yset for x_ in Xset]):
            Hx, Hy, Hz = TotalField(xdiscr, ydiscr, zdiscr, init_parameters['Angle'], init_parameters['Hext'], coords_part)
            out_str = '  '.join(list(map(str, [xdiscr, ydiscr, zdiscr, Hx, Hy, Hz])))
            fout.write(' ' + out_str + '\n')
        # Тоже шелуха
        fout.write(end_message)


#! Пайплайн который все углы и поля обойдет и сохранит
def HardPipeline():
    Ztotal = init_parameters['hlayer']
    Xset = [ (1/2 + i) * init_parameters['Xcell'] for i in range(init_parameters['Xcount'])]
    Yset = [ (1/2 + i) * init_parameters['Ycell'] for i in range(init_parameters['Ycount'])]
    Zset = [ (1/2 + i) * init_parameters['Zcell'] for i in range(int(Ztotal/init_parameters['Zcell']))]

    #! Рандомно генерю наночастицы
    coords_part = CoordsPart()
    for angle in [0, 30, 60, 90]:
        for Hext in [100]:
            print(f"COUNTER: angle = {angle}, Hext = {Hext}")
            dirpath = modeling_parameters['OUTPUTDIR'] + str(angle) + "deg_with_N_particles/"
            filepath = dirpath + "field_" + str(Hext) + "_Oe_30_NPs.csv"
            with codecs.open(filepath, 'w', encoding='utf-8') as fout:
                # Всякая шелуха вначале
                fout.write(init_message)
                # Цикл по всем ячейкам дискретизации
                for (zdiscr, ydiscr, xdiscr) in tqdm([(z_, y_, x_) for z_ in Zset for y_ in Yset for x_ in Xset]):
                    Hx, Hy, Hz = TotalField(xdiscr, ydiscr, zdiscr, angle, Hext, coords_part)
                    out_str = '  '.join(list(map(str, [xdiscr, ydiscr, zdiscr, Hx, Hy, Hz])))
                    fout.write(' ' + out_str + '\n')
                # Тоже шелуха
                fout.write(end_message)


HardPipeline()
#Pipeline()
