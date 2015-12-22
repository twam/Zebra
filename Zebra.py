#!/usr/bin/env python3

import argparse
import sys
import os
import inspect
import re
import cups
import traceback
import zpl2


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

        self.args = parser.parse_args(self.argv[1:])

    def run(self):
        try:
            self.parseArguments()

            self.zpl = zpl2.Zpl2(firmware='V45.11.7ZA')

            # label data
            labelWidth = 900
            labelHeight = 300

            # font dimensions
            sizeLarge = 80
            sizeSmall = 50

            # text positions
            fieldSpacing = 5
            textPosX = 0
            textHeightTotal = sizeLarge + \
                (len(self.args.data) - 1) * (sizeSmall + fieldSpacing)
            textPosYFirst = int((labelHeight - textHeightTotal) / 2)

            offsetY = textPosYFirst

            self.zpl.StartFormat()
            self.zpl.LabelTop(10)
            self.zpl.ChangeInternationalFontEncoding('cp850')
            self.zpl.PrintWidth(labelWidth)

            line = 0
            for item in self.args.data:
                print(item)

                self.zpl.printText(
                    x=textPosX,
                    y=offsetY,
                    width=labelWidth,
                    fontWidth=sizeLarge if line == 0 else sizeSmall,
                    fontHeight=sizeLarge if line == 0 else sizeSmall,
                    text=item,
                    textJustification='C')
                offsetY += (sizeLarge if line ==
                            0 else sizeSmall) + fieldSpacing
                line += 1

            # Grid
            if (self.args.debug):
                for y in range(0, 301, 50):
                    self.zpl.printBox(0, y, 900, 1)
                for x in range(0, 901, 50):
                    self.zpl.printBox(x, 0, 1, 300)

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
