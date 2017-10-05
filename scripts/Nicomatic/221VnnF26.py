#!/usr/bin/env python

import sys
import os

sys.path.append(os.path.join(sys.path[0],"..",".." )) #"kicad_mod")) # load kicad_mod path

# export PYTHONPATH="${PYTHONPATH}<path to kicad-footprint-generator directory>"
from KicadModTree import *

output_dir = os.getcwd()

_3dshapes = "${KISYS3DMOD}/Connectors_Nicomatic.3dshapes/"

fab_line_width = 0.1
silk_line_width = 0.15
value_fontsize = [1,1]
value_fontwidth=0.15
silk_reference_fontsize=[1,1]
silk_reference_fontwidth=0.15
fab_reference_fontsize=[1, 1]
fab_reference_fontwidth=0.15

#if specified as an argument, extract the target directory for output footprints
if len(sys.argv) > 1:
    out_dir = sys.argv[1]

    if os.path.isabs(out_dir) and os.path.isdir(out_dir):
        output_dir = out_dir
    else:
        out_dir = os.path.join(os.getcwd(),out_dir)
        if os.path.isdir(out_dir):
            output_dir = out_dir

if output_dir and not output_dir.endswith(os.sep):
    output_dir += os.sep

if not os.path.isdir(output_dir): #returns false if path does not yet exist!! (Does not check path validity)
    os.makedirs(output_dir)

datasheet = "https://www.nicomatic.com/data/drawings/2d/BULK/221VnnF26_cl.pdf"
pn = "221V{n:02}F26"

pitch = 2.00

# Connector Dimensions
pad_drill = 0.65
pad_size = 1.25
mount_hole_size = 2.2

for pincount in range(4, 62, 2):

    rows = 2
    cols = int(pincount / rows)

    pn_name = pn.format(n=pincount)
    fp_name = "Nicomatic_CMM220_{pn}_{row}x{col}x2.00mm_Angled".format(pn=pn_name, row=rows, col=cols)

    print(fp_name)

    kicad_mod = Footprint(fp_name)
    description = "Nicomatic CMM220 series connector, " + pn_name + ", side entry type, through hole, Datasheet: {ds}".format(ds=datasheet)
    kicad_mod.setDescription(description)
    kicad_mod.setTags('connector Nicomatic CMM220')

    # Connector Dimensions
    A = (cols - 1) * pitch
    B = A + 7
    C = B + 5

    # todo
    x_mid = 0
    y_mid = A / 2

    y1 = 0
    y2 = 0

    xb = pitch + 6
    xa = xb - 5.6
    ya = y_mid - C / 2
    yb = ya + C
    ym = y_mid - B / 2

    kicad_mod.append(Text(type='reference', text='REF**', layer='F.SilkS', at=[-2, y_mid], thickness=silk_reference_fontwidth, size=silk_reference_fontsize, rotation='90'))
    kicad_mod.append(Text(type='user', text='%R', at=[2 * pitch, y_mid], layer='F.Fab', thickness=fab_reference_fontwidth, size=fab_reference_fontsize, rotation='90'))
    kicad_mod.append(Text(type='value', text=fp_name, at=[9, y_mid], layer='F.Fab', size=value_fontsize, thickness=value_fontwidth, rotation='90'))

    # Create pins
    for i in range(rows):
        kicad_mod.append(PadArray(initial=1+i*cols, start=[i*pitch, 0], pincount=cols, y_spacing=pitch, type=Pad.TYPE_THT, shape=Pad.SHAPE_OVAL, size=pad_size, drill=pad_drill, layers=Pad.LAYERS_THT))

    # distance to mechanical fixing
    dm = (C - B) / 2.0 - 1.5
    xm = xa - 3

    # distance between pins and case
    po = 0.5

    poly = [
        {'x': xb, 'y': y_mid},
        {'x': xb, 'y': yb},
        {'x': xa, 'y': yb},
        {'x': xa, 'y': yb - dm},
        {'x': xm, 'y': yb - dm},
        {'x': xm, 'y': yb - dm - 3},
        {'x': xa, 'y': yb - dm - 3},
        {'x': xa, 'y': y_mid + A/2 + 1},
        {'x': xa + po, 'y': y_mid + A/2 + 1},
        {'x': xa + po, 'y': y_mid},
    ]

    kicad_mod.append(PolygoneLine(polygone=poly, layer='F.Fab', width=0.1))
    kicad_mod.append(PolygoneLine(polygone=poly, layer='F.Fab', width=0.1, y_mirror=y_mid))

    # Create notch in connector
    N = 2
    kicad_mod.append(PolygoneLine(layer='F.Fab', width=0.1, polygone=[
        {'x': xb, 'y': y_mid - N/2},
        {'x': xb - 1.5 * N, 'y': y_mid - N/2},
        {'x': xb - 1.5 * N, 'y': y_mid + N/2},
        {'x': xb, 'y': y_mid + N/2},
    ]))

    # Create fab line for each pin column
    for i in range(cols):
        y = i * pitch
        w = 0.4
        kicad_mod.append(RectLine(start=[0, y-w/2], end=[xa + po, y+w/2], width=0.1, layer='F.Fab'))

    # Add mounting holes
    xh = 1.0
    yh1 = y_mid + B / 2
    yh2 = y_mid - B / 2

    kicad_mod.append(Pad(at=[xh, yh1], size=mount_hole_size, drill=mount_hole_size, shape=Pad.SHAPE_CIRCLE, type=Pad.TYPE_NPTH, layers=Pad.LAYERS_NPTH))
    kicad_mod.append(Pad(at=[xh, yh2], size=mount_hole_size, drill=mount_hole_size, shape=Pad.SHAPE_CIRCLE, type=Pad.TYPE_NPTH, layers=Pad.LAYERS_NPTH))

    # Courtyard
    cx1 = round(-pad_size/2, 2)
    cy1 = round(ya, 2)
    cx2 = round(xb, 2)
    cy2 = round(yb, 2)

    kicad_mod.append(RectLine(start=[cx1, cy1], end=[cx2, cy2], layer='F.CrtYd', width=0.05, offset=0.5))

    # Silkscreen
    O = 0.15
    silk = [
        {'x': xb + O, 'y': y_mid},
        {'x': xb + O, 'y': ya - O},
        {'x': xa - O, 'y': ya - O},
        {'x': xa - O, 'y': ya - O + dm},
        {'x': xm -O, 'y': ya - O + dm},
        {'x': xm -O, 'y': y_mid - B/2 + 1.5 + O},
        {'x': xa -O, 'y': y_mid - B/2 + 1.5 + O},
        {'x': xa -O, 'y': y_mid - B/2 + 1.5 + O + 0.5},
    ]

    kicad_mod.append(PolygoneLine(polygone=silk, layer='F.SilkS', width=0.12))
    kicad_mod.append(PolygoneLine(polygone=silk, layer='F.SilkS', width=0.12, y_mirror=y_mid))


    D = pad_size / 2 + 0.35
    L = 1.5

    P1 = [
            {'x': L - D, 'y': -D},
            {'x': -D, 'y': -D},
            {'x': -D, 'y': -D + L},
        ]

    # Add Pin-1 marker on Silkscreen
    kicad_mod.append(PolygoneLine(layer='F.SilkS', width=0.12, polygone=P1))
    kicad_mod.append(PolygoneLine(layer='F.Fab', width=0.1, polygone=P1))

    #Add a model
    kicad_mod.append(Model(filename=_3dshapes + fp_name + ".wrl", at=[0,0,0], scale=[1,1,1], rotate=[0,0,0]))

    #filename
    filename = output_dir + fp_name + ".kicad_mod"
    file_handler = KicadFileHandler(kicad_mod)
    file_handler.writeFile(filename)
