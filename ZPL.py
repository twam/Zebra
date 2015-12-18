import re


class ZPLFirmwareMismatch(Exception):
    pass


class ZPL(list):

    def __init__(self, firmware='unknown'):
        self.firmware = firmware

    def append(self, item, encoding='utf_8'):
        if type(item) == str:
            item = item.encode(encoding)
        super(ZPL, self).append(item)

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

    # def __str__(self):
    #     return "^XA" + "".join(self) + "^XZ"

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

        self.append("^A%s%s,%u,%u" % (font, orientation, h, w))

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

        self.append("^CI%u" % characterSet)

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
            self.append("^FO%u,%u,%u" % (x, y, z))
        else:
            self.append("^FO%u,%u" % (x, y))

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
            self.append("^FT%u,%u,%u" % (x, y, z))
        else:
            self.append("^FT%u,%u" % (x, y))

    def FieldData(self, data):
        if (type(data) != str) and (type(data) != bytes):
            raise TypeError
        if len(data) > 3072:
            raise ValueError

        if type(data) == str:
            self.append("^FD" + data)
        else:
            self.append(b"^FD" + data)

    def FieldSeparator(self):
        self.append("^FS")

    def LabelHome(self, x=0, y=0):
        if (type(x) != int) or (type(y) != int):
            raise TypeError
        if (x < 0) or (x > 32000):
            raise ValueError
        if (y < 0) or (y > 32000):
            raise ValueError
        self.append("^LH%u,%u" % (x, y))

    def PrintWidth(self, labelWidth):
        if (type(labelWidth) != int):
            raise TypeError
        if (labelWidth < 2):
            raise ValueError

        self.append("^PW%u" % labelWidth)

    def MediaType(self, mediaType):
        if (mediaType != "T") and (mediaType != "D"):
            raise ValueError
        self.append("^MT%s" % (mediaType))

    def StartFormat(self):
        self.append("^XA")

    def EndFormat(self):
        self.append("^XZ")
