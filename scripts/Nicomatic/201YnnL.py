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

datasheet = "https://www.nicomatic.com/data/drawings/2d/BULK/201Ynn%28L%29_cl.pdf"
pn = "201Y{n:02}"

pitch = 2.00

# Connector Dimensions
pad_drill = 0.65
pad_size = 1.25
mount_hole_size = 1.5
mount_hole_drill = 0.9

for pincount in range(4, 52, 2):

    rows = 2
    cols = int(pincount / rows)

    pn_name = pn.format(n=pincount)
    fp_name = "Nicomatic_CMM220_{pn}_{row}x{col}x2.00mm_Vertical".format(pn=pn_name, row=rows, col=cols)

    print(fp_name)

    kicad_mod = Footprint(fp_name)
    description = "Nicomatic CMM220 series connector, " + pn_name + ", top entry type, through hole, Datasheet: {ds}".format(ds=datasheet)
    kicad_mod.setDescription(description)
    kicad_mod.setTags('connector Nicomatic CMM220')

    # Connector Dimensions
    A = (cols - 1) * pitch
    B = A + 4.7
    C = B + 0.7

    x_mid = pitch / 2
    y_mid = A / 2

    y1 = 0
    y2 = 0

    # Outer dimensions of plastic case
    Lb = B - 1
    Wb = 5.5
    xa = pitch / 2 - Wb / 2
    xb = xa + Wb
    ya = y_mid - Lb / 2
    yb = ya + Lb

    kicad_mod.append(Text(type='reference', text='REF**', layer='F.SilkS', at=[-3, y_mid], thickness=silk_reference_fontwidth, size=silk_reference_fontsize, rotation='90'))
    kicad_mod.append(Text(type='user', text='%R', at=[x_mid, y_mid], layer='F.Fab', thickness=fab_reference_fontwidth, size=fab_reference_fontsize, rotation='90'))
    kicad_mod.append(Text(type='value', text=fp_name, at=[xb + 1.2, y_mid], layer='F.Fab', size=value_fontsize, thickness=value_fontwidth, rotation='90'))

    # Create pins
    for i in range(rows):
        kicad_mod.append(PadArray(initial=1+i*cols, start=[i*pitch, 0], pincount=cols, y_spacing=pitch, type=Pad.TYPE_THT, shape=Pad.SHAPE_OVAL, size=pad_size, drill=pad_drill, layers=Pad.LAYERS_THT))

    # Mounting holes

    xh = 2.4
    yh = B / 2

    holes = [
        [x_mid - xh, y_mid - yh],
        [x_mid - xh, y_mid + yh],
        [x_mid + xh, y_mid + yh],
        [x_mid + xh, y_mid - yh],
    ]

    for hole in holes:
        kicad_mod.append(Pad(at=hole, type=Pad.TYPE_THT, shape=Pad.SHAPE_CIRCLE, layers=Pad.LAYERS_THT, size=mount_hole_size, drill=mount_hole_drill))

    # Courtyard
    offset = 0.5
    cx1 = round(xa - offset, 2)
    cx2 = round(xb + offset, 2)
    cy1 = round(ya - offset, 2)
    cy2 = round(yb + offset, 2)

    kicad_mod.append(RectLine(start=[cx1, cy1], end=[cx2, cy2], layer='F.CrtYd', width=0.05))

    # Draw inside shape
    def draw_shape(layer='F.Fab', width=0.1, offset=0):
        O = offset

        # Wall thickness
        T = 0.6 + O

        # Chamfer
        C = 0.75 - O / 2

        # Draw the inside shape

        poly = [
            {'x': xa + T, 'y': y_mid},
            {'x': xa + T, 'y': ya + T + C},
            {'x': xa + T + C, 'y': ya + T},
            {'x': xb - T, 'y': ya + T},
            {'x': xb - T, 'y': y_mid},
        ]

        kicad_mod.append(PolygoneLine(polygone=poly, layer=layer, width=width))
        kicad_mod.append(PolygoneLine(polygone=poly, layer=layer, width=width, y_mirror=y_mid))

    off = 0.12

    draw_shape()
    draw_shape(layer='F.SilkS', width=0.12, offset=off)

    # Draw the outside shape
    kicad_mod.append(RectLine(start=[xa, ya], end=[xb, yb], layer='F.Fab', width=0.1))

    dx = (4.8 - mount_hole_size - 0.5) / 2
    dy = (B - mount_hole_size - 0.5) / 2

    kicad_mod.append(Line(start=[xa - off, y_mid + dy], end=[xa-off, y_mid - dy], layer='F.SilkS', width=0.12))
    kicad_mod.append(Line(start=[xb + off, y_mid + dy], end=[xb+off, y_mid - dy], layer='F.SilkS', width=0.12))

    kicad_mod.append(Line(start=[x_mid - dx, ya-off], end=[x_mid + dx, ya-off], layer='F.SilkS', width=0.12))
    kicad_mod.append(Line(start=[x_mid - dx, yb+off], end=[x_mid + dx, yb+off], layer='F.SilkS', width=0.12))

    # Add pin-1 on F.Fab
    S = pad_size / 2
    kicad_mod.append(RectLine(start=[-S, -S], end=[S, S], width=0.1, layer='F.Fab'))

    # Add pin-1 on F.SilkS
    xp = 0.35
    yp = 0.75
    kicad_mod.append(Line(start=[xa-xp, -yp], end=[xa-xp, yp], width=0.12, layer='F.SilkS'))

    #Add a model
    kicad_mod.append(Model(filename=_3dshapes + fp_name + ".wrl", at=[0,0,0], scale=[1,1,1], rotate=[0,0,0]))

    #filename
    filename = output_dir + fp_name + ".kicad_mod"
    file_handler = KicadFileHandler(kicad_mod)
    file_handler.writeFile(filename)
