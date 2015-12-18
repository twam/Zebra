import re


class ZPLFirmwareMismatch(Exception):
    pass


class ZPL(list):
    CONTROL_COMMAND = '~'
    FORMAT_COMMAND = '^'

    def __init__(self, firmware='unknown'):
        self.firmware = firmware
        self.delimiter = b','
        self.tilde = b'~'
        self.caret = b'^'

    def append(self, item, encoding='utf_8'):
        if type(item) == str:
            item = item.encode(encoding)
        super(ZPL, self).append(item)

    def appendCommand(self, commandType, command, *args):
        if (type(commandType) != str) or (type(command) != str):
            raise TypeError
        if (commandType != self.CONTROL_COMMAND) and (commandType != self.FORMAT_COMMAND):
            raise ValueError

        data = b''

        if (commandType == self.CONTROL_COMMAND):
            data = data + self.tilde
        else:
            data = data + self.caret

        data = data + command.encode('ascii')

        for i in range(0, len(args)):
            arg = args[i]

            if (type(arg) == str):
                data = data + arg.encode('ascii')
            elif (type(arg) == int):
                data = data + str(arg).encode('ascii')
            elif (type(arg) == bytes):
                data = data + arg
            else:
                raise Exception("Not supported type")

            if i < len(args) - 1:
                data = data + self.delimiter

        self.append(data)

    def splitFirmware(self, firmware):
        matches = re.search(
            r'^V([0-9]+|x)\.([0-9]+|x)\.([0-9A-Z]+|x)', firmware)
        return matches.groups()

    def checkFirmwareRestrictions(self, restrictions):
        # convert single restriction to list, so we can handle all the same way
        if type(restrictions) == str:
            restrictions = [restrictions]

        # no restrions are always fullfilled
        if restrictions == []:
            return True

        # check all firmware restrictions. if at least one is matched, return
        # true
        firmware_parts = self.splitFirmware(self.firmware)
        for restriction in restrictions:
            restriction_parts = self.splitFirmware(restriction)

            part_fulfilled = [True, True, True]

            for i in range(0, 3):
                if (restriction_parts[i] == 'x'):
                    part_fulfilled[i] = True
                elif (restriction_parts[i] == firmware_parts[i]):
                    part_fulfilled[i] = True
                elif (i < 2) and (int(restriction_parts[i]) <= int(firmware_parts[i])):
                    part_fulfilled[i] = True
                else:
                    part_fulfilled[i] = False

            if part_fulfilled[0] and part_fulfilled[1] and part_fulfilled[2]:
                return True

        return False

    def getAllBytes(self):
        return b"".join(self)

    def ScalableBitmappedFont(self, font, orientation, h, w):
        if (type(font) != str) or (type(orientation) != str) or (type(h) != int) or (type(w) != int):
            raise TypeError
        if not re.match(r'^[A-Z0-9]$', font):
            raise ValueError
        if not re.match(r'^[NRIB]$', orientation):
            raise ValueError
        if (h < 1) or (h > 32000):
            raise ValueError
        if (w < 1) or (w > 32000):
            raise ValueError

        self.append("%cA%s%s%c%u%c%u" % (self.caret, font,
                                         orientation, self.delimiter, h, self.delimiter, w))

    def ChangeCaret(self, caret='^'):
        if (type(caret) != str):
            raise TypeError
        if (len(caret) > 1) or (caret.encode("ascii")[0] > 127):
            raise ValueError

        self.appendCommand(self.FORMAT_COMMAND, "CC", caret)
        # update afterwards as otherwise self.caret would be already new caret
        self.caret = caret.encode('ascii')

    def ChangeDelimiter(self, delimiter=','):
        if (type(delimiter) != str):
            raise TypeError
        if (len(delimiter) > 1) or (delimiter.encode("ascii")[0] > 127):
            raise ValueError

        self.delimiter = delimiter.encode('ascii')
        self.appendCommand(self.FORMAT_COMMAND, "CD", delimiter)

    def ChangeTilde(self, tilde='~'):
        if (type(tilde) != str):
            raise TypeError
        if (len(tilde) > 1) or (tilde.encode("ascii")[0] > 127):
            raise ValueError

        self.tilde = tilde.encode('ascii')
        self.appendCommand(self.FORMAT_COMMAND, "CT", tilde)

    def ChangeInternationalFontEncoding(self, encoding):
        ENCODINGS = [
            ['cp850', 13, []],
            ['shift_jis', 15, []],
            ['euc_jp', 16, []],
            ['cp1252', 27, []],
            ['utf_8', 28, ["V60.14.x", "V50.14.x"]],
            ['utf_16', 29, ["V60.14.x", "V50.14.x"]],
            ['utf_32', 30, ["V60.14.x", "V50.14.x"]],
            ['cp1250', 31, ["Vx.16.x"]],
            ['cp1251', 33, ["Vx.16.x"]],
            ['cp1253', 34, ["Vx.16.x"]],
            ['cp1254', 35, ["Vx.16.x"]],
            ['cp1255', 36, ["Vx.16.x"]],
        ]

        characterSet = 0

        for encoding_set in ENCODINGS:
            if (encoding_set[0] == encoding):
                if self.checkFirmwareRestrictions(encoding_set[2]):
                    characterSet = encoding_set[1]
                else:
                    raise ZPLFirmwareMismatch

        self.appendCommand(self.FORMAT_COMMAND, "CI", characterSet)

    def FieldOrigin(self, x=0, y=0, z=0):
        if (type(x) != int) or (type(y) != int) or (type(z) != int):
            raise TypeError
        if (x < 0) or (x > 32000):
            raise ValueError
        if (y < 0) or (y > 32000):
            raise ValueError
        if (z < 0) or (z > 2):
            raise ValueError

        if self.checkFirmwareRestrictions(["V60.14.x", "V50.14.x"]):
            self.appendCommand(self.FORMAT_COMMAND, "FO", x, y, z)
        else:
            self.appendCommand(self.FORMAT_COMMAND, "FO", x, y)

    def FieldTypeset(self, x=0, y=0, z=0):
        if (type(x) != int) or (type(y) != int) or (type(z) != int):
            raise TypeError
        if (x < 0) or (x > 32000):
            raise ValueError
        if (y < 0) or (y > 32000):
            raise ValueError
        if (z < 0) or (z > 2):
            raise ValueError

        if self.checkFirmwareRestrictions(["V60.14.x", "V50.14.x"]):
            self.appendCommand(self.FORMAT_COMMAND, "FT", x, y, z)
        else:
            self.appendCommand(self.FORMAT_COMMAND, "FT", x, y)

    def FieldData(self, data):
        if (type(data) != str) and (type(data) != bytes):
            raise TypeError
        if len(data) > 3072:
            raise ValueError

        self.appendCommand(self.FORMAT_COMMAND, "FD", data)

    def FieldSeparator(self):
        self.append("^FS")

    def ConfigurationUpdate(self, configuration):
        if (type(configuration) != str):
            raise TypeError
        if not re.match(r'^[FNRS]$', configuration):
            raise ValueError

        self.appendCommand(self.FORMAT_COMMAND, "JU", configuration)

    def LabelHome(self, x=0, y=0):
        if (type(x) != int) or (type(y) != int):
            raise TypeError
        if (x < 0) or (x > 32000):
            raise ValueError
        if (y < 0) or (y > 32000):
            raise ValueError

        self.appendCommand(self.FORMAT_COMMAND, "LH", x, y)

    def PrintWidth(self, labelWidth):
        if (type(labelWidth) != int):
            raise TypeError
        if (labelWidth < 2):
            raise ValueError

        self.appendCommand(self.FORMAT_COMMAND, "PW", labelWidth)

    def MediaType(self, mediaType):
        if (mediaType != "T") and (mediaType != "D"):
            raise ValueError

        self.appendCommand(self.FORMAT_COMMAND, "MT", mediaType)

    def StartFormat(self):
        self.appendCommand(self.FORMAT_COMMAND, "XA")

    def EndFormat(self):
        self.appendCommand(self.FORMAT_COMMAND, "XZ")
