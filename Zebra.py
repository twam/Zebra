#!/usr/bin/env python3

import argparse
import sys
import os
import inspect
import re
import cups
import traceback
import zpl2
import wand
import wand.image
import wand.color
import math


class Zebra:

    def __init__(self, argv):
        self.argv = argv

        self.progname = os.path.basename(self.argv[0])

        # Get path of the directory where this file is stored
        self.basePath = os.path.dirname(os.path.abspath(
            inspect.getfile(inspect.currentframe())))

    def cupsPrint(self, data):
        if not isinstance(data, bytes):
            raise TypeError
        conn = cups.Connection()
        job = conn.createJob(printer=self.args.printer,
                             title=self.progname, options={})
        doc = conn.startDocument(printer=self.args.printer, job_id=job,
                                 doc_name='', format=cups.CUPS_FORMAT_RAW, last_document=1)
        conn.writeRequestData(data, len(data))
        conn.finishDocument(printer=self.args.printer)

    def parseArguments(self):

        parser = argparse.ArgumentParser(
            description='Zebra', prog=self.progname, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        parser.add_argument("-v", "--version",
                            action="version",
                            help="show the version and exit",
                            version="0.1")

        parser.add_argument('-P', '--printer',
                            help='specify CUPS printer name',
                            dest='printer',
                            default='zebra',
                            metavar='printer')

        parser.add_argument('-q', '--quantity',
                            help='print quantity',
                            dest='quantity',
                            default=1,
                            type=int,
                            metavar='quantity')

        parser.add_argument('--debug',
                            help='print debug information',
                            dest='debug',
                            action='store_true')

        parser.add_argument('data',
                            help='data to print',
                            nargs='+',
                            metavar='data')

        parser.add_argument('--dry-run',
                            help='do not print label, but show raw bytes instead',
                            dest='dryRun',
                            action='store_true')

        parser.add_argument('--width',
                            help='label width',
                            dest='labelWidth',
                            metavar='width',
                            required=True)

        parser.add_argument('--height',
                            help='label height',
                            dest='labelHeight',
                            metavar='width',
                            required=True)

        parser.add_argument('--dpi',
                            help='printer DPI',
                            dest='dpi',
                            metavar='dpi',
                            default=300,
                            type=int)

        parser.add_argument('--top',
                            help='label top offset',
                            dest='labelTop',
                            metavar='topoffset',
                            default=0,
                            type=int)

        parser.add_argument('--darkness',
                            help='test printer darkness (0-30)',
                            dest='darkness',
                            metavar='darkness',
                            default=20,
                            type=int)

        parser.add_argument('-t', '--type',
                            help='label type',
                            dest='type',
                            metavar='type',
                            required=True)

        self.args = parser.parse_args(self.argv[1:])

    def parseUnit(self, val):
        if (isinstance(val, int)) or (isinstance(val, float)):
            return val

        matches = re.match(
            '(?P<value>[+-]?([0-9]+)(\.([0-9]+)?)?)(?P<unit>in|mm|cm)?', val)
        if matches:
            parts = matches.groupdict()
            newVal = float(parts['value'])

            if (parts['unit'] == None):
                pass
            elif (parts['unit'] == 'in'):
                newVal *= self.args.dpi
            elif (parts['unit'] == 'cm'):
                newVal *= self.args.dpi / 2.54
            elif (parts['unit'] == 'mm'):
                newVal *= self.args.dpi / 25.4
            else:
                raise Exception('Unit %s unknown!' % parts['unit'])

            return newVal

        raise Exception('Cannot parse %s' % val)

    def addGrid(self, spacing=50):
        for y in range(0, self.args.labelHeight + 1, spacing):
            self.zpl.printBox(0, y, self.args.labelWidth, 1)
        for x in range(0, self.args.labelWidth + 1, spacing):
            self.zpl.printBox(x, 0, 1, self.args.labelHeight)

    def labelTypeText(self):
        # font dimensions
        sizeLarge = 80
        sizeSmall = 50

        # text positions
        fieldSpacing = 5
        textPosX = 0
        textHeightTotal = sizeLarge + \
            (len(self.args.data) - 1) * (sizeSmall + fieldSpacing)
        textPosYFirst = int((self.args.labelHeight - textHeightTotal) / 2)

        offsetY = textPosYFirst
        line = 0
        for item in self.args.data:
            print(item)

            self.zpl.printText(
                x=textPosX,
                y=offsetY,
                width=self.args.labelWidth,
                fontWidth=sizeLarge if line == 0 else sizeSmall,
                fontHeight=sizeLarge if line == 0 else sizeSmall,
                text=item,
                textJustification='C')
            offsetY += (sizeLarge if line ==
                        0 else sizeSmall) + fieldSpacing
            line += 1

    def labelTypeDHL(self):
        with wand.image.Image(filename=self.args.data[0], resolution=int(self.args.dpi * 0.85)) as img:
            img.background_color = wand.color.Color("white")
            img.alpha_channel = 'remove'

            img.rotate(90)
            img.crop(
                top=155,
                left=1540,
                width=self.args.labelWidth,
                height=self.args.labelHeight)

            bytesPerRow = math.ceil(img.width / 8)
            binaryByteCount = bytesPerRow * img.height
            graphicFieldCount = binaryByteCount

            offsetX = int((self.args.labelWidth - img.width) / 2)
            offsetY = int((self.args.labelHeight - img.height) / 2)

            self.zpl.FieldOrigin(offsetX, offsetY)

            if (self.args.debug):
                img.save(filename='test.png')

            rawImg = bytearray(img.make_blob(format='MONO'))
            for i in range(0, len(rawImg)):
                temp = 0
                for j in range(0, 8):
                    if (rawImg[i] & (1 << j)):
                        temp |= (1 << (7 - j))
                rawImg[i] = temp

            self.zpl.GraphicField(compressionType='A',
                                  binaryByteCount=binaryByteCount,
                                  graphicFieldCount=graphicFieldCount,
                                  bytesPerRow=bytesPerRow,
                                  data=rawImg,
                                  optimizeAscii=True)

            self.zpl.FieldSeparator()

    def run(self):
        try:
            self.parseArguments()

            self.zpl = zpl2.Zpl2(firmware='V45.11.7ZA')

            # label data
            self.args.labelWidth = int(self.parseUnit(self.args.labelWidth))
            self.args.labelHeight = int(self.parseUnit(self.args.labelHeight))

            self.zpl.StartFormat()
            self.zpl.SetDarkness(self.args.darkness)
            self.zpl.PrintWidth(self.args.labelWidth)
            self.zpl.LabelLength(self.args.labelHeight)
            self.zpl.LabelTop(self.args.labelTop)
            self.zpl.ChangeInternationalFontEncoding('cp850')

            if (self.args.type == 'text'):
                self.labelTypeText()
            elif (self.args.type == 'dhl'):
                self.labelTypeDHL()

            # Grid
            if (self.args.debug):
                self.addGrid()

            self.zpl.EndFormat()

            if (self.args.dryRun):
                print(self.zpl.getAllBytes())
            else:
                singleData = self.zpl.getAllBytes()
                allData = b"".join([singleData * self.args.quantity])
                self.cupsPrint(allData)

        except Exception as e:
            if (self.args.debug):
                traceback.print_exc()
            if (len(e.args) > 0):
                sys.exit(e.args[0])
            else:
                sys.exit("Unknown error: %s" % sys.exc_info()[0])

if __name__ == '__main__':
    Zebra(sys.argv).run()
