#!/usr/bin/env python3

import argparse
import sys
import os
import inspect
import re
import cups
import traceback
import ZPL


class Zebra:

    def __init__(self, argv):
        self.argv = argv

        self.progname = os.path.basename(self.argv[0])

        # Get path of the directory where this file is stored
        self.basePath = os.path.dirname(os.path.abspath(
            inspect.getfile(inspect.currentframe())))

    def cupsPrint(self, data):
        if type(data) != bytes:
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

        parser.add_argument("-v", "--version", action="version",
                            help="show the version and exit", version="0.1")

        parser.add_argument('-P', '--printer', help='specify CUPS printer name',
                            dest='printer', default='zebra', metavar='printer')

        parser.add_argument('-q', '--quantity', help='print quantity',
                            dest='quantity', default=1, type=int, metavar='quantity')

        parser.add_argument('--debug', help='print debug information',
                            dest='debug', action='store_true')

        parser.add_argument(
            '--dry-run', help='do not print label, but show raw bytes instead', dest='dryRun', action='store_true')

        self.args = parser.parse_args(self.argv[1:])

    def run(self):
        try:
            self.parseArguments()

            zpl = ZPL.ZPL(firmware='V45.11.7ZA')
            zpl.StartFormat()
            zpl.ChangeInternationalFontEncoding('cp850')
            zpl.PrintWidth(900)
            zpl.LabelHome(0, 0)
            zpl.FieldOrigin(0, 0)
            zpl.FieldTypeset(100, 200)
            zpl.ScalableBitmappedFont("0", "N", 120, 100)
            zpl.FieldData("Hello World!".encode('cp850'))
            zpl.FieldSeparator()
            zpl.EndFormat()

            if (self.args.dryRun):
                print(zpl.getAllBytes())
            else:
                self.cupsPrint(zpl.getAllBytes())

        except Exception as e:
            if (self.args.debug):
                traceback.print_exc()
            if (len(e.args) > 0):
                sys.exit(e.args[0])
            else:
                sys.exit("Unknown error: %s" % sys.exc_info()[0])

if __name__ == '__main__':
    Zebra(sys.argv).run()
