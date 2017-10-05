#!/usr/bin/env python

import sys
import os

sys.path.append(os.path.join(sys.path[0],"..",".." )) #"kicad_mod")) # load kicad_mod path

# export PYTHONPATH="${PYTHONPATH}<path to kicad-footprint-generator directory>"
from KicadModTree import *

LAYERS_SMT = ['F.Cu','F.Mask','F.Paste']
LAYERS_THT = ['*.Cu','*.Mask']
LAYERS_NPTH = ['*.Cu', '*.Mask']

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

datasheet = "https://www.nicomatic.com/data/drawings/2d/BULK/D321VnnnD57_cl.pdf"
pn = "D321V{n:03}D57"

pitch = 2.00

# Connector Dimensions
pad_drill = 0.65
pad_size = 1.25
mount_hole_size = 2.75
pad_y = 1.5
pad_x = 2.5

for pincount in range(6, 93, 3):

    rows = 3
    cols = int(pincount / 3)

    pn_name = pn.format(n=pincount)
    fp_name = "Nicomatic_{pn}_3x{col}x2.00mm_Angled".format(pn=pn_name, col=cols)

    print(fp_name)

    kicad_mod = Footprint(fp_name)
    description = "Nicomatic D321V series connector, " + pn_name + ", side entry type, through hole, Datasheet: {ds}".format(ds=datasheet)
    kicad_mod.setDescription(description)
    kicad_mod.setTags('connector Nicomatic D321V')

    # Connector Dimensions
    A = (cols - 1) * pitch
    B = A + 10
    C = B + 5

    # todo
    x_mid = 0
    y_mid = A / 2

    y1 = 0
    y2 = 0

    xb = 2 * pitch + 6
    xa = xb - 5.6
    ya = y_mid - C / 2
    yb = ya + C
    ym = y_mid - B / 2

    kicad_mod.append(Text(type='reference', text='REF**', layer='F.SilkS', at=[-2, y_mid], thickness=silk_reference_fontwidth, size=silk_reference_fontsize, rotation='90'))
    kicad_mod.append(Text(type='user', text='%R', at=[3 * pitch, y_mid], layer='F.Fab', thickness=fab_reference_fontwidth, size=fab_reference_fontsize, rotation='90'))
    kicad_mod.append(Text(type='value', text=fp_name, at=[4 * pitch, y_mid], layer='F.Fab', size=value_fontsize, thickness=value_fontwidth, rotation='90'))

    # Create pins
    for i in range(rows):
        kicad_mod.append(PadArray(initial=1+i*cols, start=[i*pitch, 0], pincount=cols, y_spacing=pitch, type=Pad.TYPE_THT, shape=Pad.SHAPE_OVAL, size=pad_size, drill=pad_drill, layers=Pad.LAYERS_THT))

    # distance to mechanical fixing
    dm = (C - B) / 2.0 - 2
    xm = xb - 10.1

    # distance between pins and case
    po = 0.5

    poly = [
        {'x': xb, 'y': y_mid},
        {'x': xb, 'y': yb},
        {'x': xa, 'y': yb},
        {'x': xa, 'y': yb - dm},
        {'x': xm, 'y': yb - dm},
        {'x': xm, 'y': yb - dm - 4},
        {'x': xa, 'y': yb - dm - 4},
        {'x': xa, 'y': y_mid + A/2 + 1},
        {'x': xa + po, 'y': y_mid + A/2 + 1},
        {'x': xa + po, 'y': y_mid},
    ]

    kicad_mod.append(PolygoneLine(polygone=poly, layer='F.Fab', width=0.1))
    kicad_mod.append(PolygoneLine(polygone=poly, layer='F.Fab', width=0.1, y_mirror=y_mid))

    # Create fab line for each pin column
    for i in range(cols):
        y = i * pitch
        w = 0.4
        kicad_mod.append(RectLine(start=[0, y-w/2], end=[xa + po, y+w/2], width=0.1, layer='F.Fab'))

    # Draw pin-1 notch on case
    wn = 1
    kicad_mod.append(PolygoneLine(layer='F.Fab', width=0.1, polygone=[
        {'x': xb, 'y': -wn/2},
        {'x': xb - wn, 'y': -wn/2},
        {'x': xb - wn, 'y': wn/2},
        {'x': xb, 'y': wn/2},
    ]))

    # Add mounting holes
    xh = 2.15
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
        {'x': xm -O, 'y': y_mid - B/2 + 2 + O},
        {'x': xa -O, 'y': y_mid - B/2 + 2 + O},
        {'x': xa -O, 'y': y_mid - B/2 + 2 + O + 1.5},
    ]

    kicad_mod.append(PolygoneLine(polygone=silk, layer='F.SilkS', width=0.12))
    kicad_mod.append(PolygoneLine(polygone=silk, layer='F.SilkS', width=0.12, y_mirror=y_mid))

    ym = -1
    mm = 1

    # Add Pin-1 marker on Silkscreen
    kicad_mod.append(PolygoneLine(layer='F.SilkS', width=0.12, polygone=[
        {'x': 0, 'y': ym},
        {'x': mm / 2, 'y': ym - mm},
        {'x': -mm / 2, 'y': ym - mm},
        {'x': 0, 'y': ym},
    ]))

    """
    # Add mounting hole
    mx = -mount_hole_offset_x
    my = (pin_per_row - 1) * pitch + mount_hole_offset_y

    # Tab dimensions
    tw = 7
    tt = 0.5

    # Couryard
    kicad_mod.append(RectLine(start=[x1,y1], end=[x2,y2], layer='F.CrtYd', width='0.05', offset=0.5))

    def draw_outline(offset=0, layer='F.Fab', width=0.1):
        O = offset
        R = 1.0

        if pincount == 2:
            poly = [
                {'x': x2 + O - R, 'y': y1 - O},
                {'x': x1 - O, 'y': y1 - O},
                {'x': x1 - O, 'y': y2 + O},
                {'x': x2 + O - R, 'y': y2 + O},
            ]

            kicad_mod.append(PolygoneLine(polygone=poly, layer=layer, width=width))
        else:
            # top line
            kicad_mod.append(Line(start=[tt+x1-O+R, y1-O], end=[x2+O-R, y1-O], layer=layer, width=width))
            # bottom line
            kicad_mod.append(Line(start=[tt+x1-O+R, y2+O], end=[x2+O-R, y2+O], layer=layer, width=width))

            # left line (including tab)
            poly = [
                {'x': tt+x1-O, 'y': y1-O+R},
                {'x': tt+x1-O, 'y': y_mid - tw/2.0 - O},
                {'x': x1-O, 'y': y_mid - tw/2.0 - O},
                {'x': x1-O, 'y': y_mid + tw/2.0 + O},
                {'x': tt+x1-O, 'y': y_mid + tw/2.0 + O},
                {'x': tt+x1-O, 'y': y2+O-R}
            ]

            kicad_mod.append(PolygoneLine(polygone=poly, width=width, layer=layer))

            # top left
            kicad_mod.append(Arc(center=[tt+x1-O+R, y1-O+R], start=[tt+x1-O, y1-O+R], angle=90.0, layer=layer, width=width))
            # bottom left
            kicad_mod.append(Arc(center=[tt+x1-O+R, y2+O-R], start=[tt+x1-O+R, y2+O], angle=90.0, layer=layer, width=width))


        # right line
        kicad_mod.append(Line(start=[x2+O, y1-O+R], end=[x2+O, y2+O-R], layer=layer, width=width))

        # top right
        kicad_mod.append(Arc(center=[x2+O-R, y1-O+R], start=[x2+O-R, y1-O], angle=90.0, layer=layer, width=width))

        # bottom right
        kicad_mod.append(Arc(center=[x2+O-R, y2+O-R], start=[x2+O, y2+O-R], angle=90.0, layer=layer, width=width))


    draw_outline()
    draw_outline(offset=0.1, layer='F.SilkS', width=0.12)

    # Add pin-1 marker on F.SilkS
    Q = 0.35 # offset
    L = 1.5
    p1 = [
        {'x': x1 - Q, 'y': y1 - Q + L},
        {'x': x1 - Q, 'y': y1 - Q},
        {'x': x1 - Q + L, 'y': y1 - Q},
    ]

    kicad_mod.append(PolygoneLine(polygone=p1, layer='F.SilkS', width=0.12))

    # Add pin-1 marker on F.Fab
    D = -0.5 - pad_y / 2
    M = 1.0
    p1 = [
        {'x': -M/2, 'y': D - M},
        {'x': M/2, 'y': D - M},
        {'x': 0, 'y': D},
        {'x': -M/2, 'y': D - M},
    ]

    kicad_mod.append(PolygoneLine(polygone=p1, layer='F.Fab', width=0.10))

    """
    #Add a model
    kicad_mod.append(Model(filename=_3dshapes + fp_name + ".wrl", at=[0,0,0], scale=[1,1,1], rotate=[0,0,0]))


    #filename
    filename = output_dir + fp_name + ".kicad_mod"
    file_handler = KicadFileHandler(kicad_mod)
    file_handler.writeFile(filename)
