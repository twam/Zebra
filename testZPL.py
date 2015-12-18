import unittest
import ZPL


class ZPLTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testCheckFirmwareRestrictionsEmptyList(self):
        zpl = ZPL.ZPL(firmware="V45.11.7ZA")
        self.assertTrue(zpl.checkFirmwareRestrictions([]))

    def testCheckFirmwareRestrictionsSingle(self):
        zpl = ZPL.ZPL(firmware="V45.11.7ZA")
        self.assertTrue(zpl.checkFirmwareRestrictions("V45.11.x"))

    def testCheckFirmwareRestrictionsSingleFail(self):
        zpl = ZPL.ZPL(firmware="V45.11.7ZA")
        self.assertFalse(zpl.checkFirmwareRestrictions("V60.14.x"))

    def testCheckFirmwareRestrictionsListFail(self):
        zpl = ZPL.ZPL(firmware="V45.11.7ZA")
        self.assertFalse(zpl.checkFirmwareRestrictions(
            ["V60.14.x", "V50.14.x"]))

    def testCheckFirmwareRestrictionsListFail2(self):
        zpl = ZPL.ZPL(firmware="V45.11.7ZA")
        self.assertFalse(zpl.checkFirmwareRestrictions(
            ["V60.14.x", "Vx.14.x"]))

    def testCheckFirmwareRestrictionsListOK(self):
        zpl = ZPL.ZPL(firmware="V45.11.7ZA")
        self.assertTrue(zpl.checkFirmwareRestrictions(
            ["V60.14.x", "V45.10.x"]))

    def testCheckFirmwareRestrictionsListOK2(self):
        zpl = ZPL.ZPL(firmware="V45.11.7ZA")
        self.assertTrue(zpl.checkFirmwareRestrictions(["V60.14.x", "Vx.10.x"]))

    def testGetAllBytes(self):
        zpl = ZPL.ZPL(firmware="V45.11.7ZA")
        zpl.append("A")
        zpl.append("B")
        zpl.append("C")
        self.assertEqual(zpl.getAllBytes(), b'ABC')

    def testAppendCommandInvalidCommandTypeType(self):
        zpl = ZPL.ZPL(firmware="V45.11.7ZA")
        with self.assertRaises(TypeError):
            zpl.appendCommand(1, 'FO')

    def testAppendCommandInvalidCommandTypeValue(self):
        zpl = ZPL.ZPL(firmware="V45.11.7ZA")
        with self.assertRaises(ValueError):
            zpl.appendCommand('x', 'FO')

    def testAppendCommandInvalidCommandType(self):
        zpl = ZPL.ZPL(firmware="V45.11.7ZA")
        with self.assertRaises(TypeError):
            zpl.appendCommand(zpl.FORMAT_COMMAND, 2)

    def testAppendCommandFormatCommand(self):
        zpl = ZPL.ZPL(firmware="V45.11.7ZA")
        zpl.appendCommand(zpl.FORMAT_COMMAND, "A0", "N", 10, 20)
        self.assertEqual(zpl, [b'^A0N,10,20'])

    def testAppendCommandFormatCommandWithCC(self):
        zpl = ZPL.ZPL(firmware="V45.11.7ZA")
        zpl.ChangeCaret('x')
        zpl.appendCommand(zpl.FORMAT_COMMAND, "A0", "N", 10, 20)
        self.assertEqual(zpl, [b'^CCx', b'xA0N,10,20'])

    def testAppendCommandFormatCommandWithCD(self):
        zpl = ZPL.ZPL(firmware="V45.11.7ZA")
        zpl.ChangeDelimiter(';')
        zpl.appendCommand(zpl.FORMAT_COMMAND, "A0", "N", 10, 20)
        self.assertEqual(zpl, [b'^CD;', b'^A0N;10;20'])

    def testAppendCommandControlCommand(self):
        zpl = ZPL.ZPL(firmware="V45.11.7ZA")
        zpl.appendCommand(zpl.CONTROL_COMMAND, "A0", "N", 10, 20)
        self.assertEqual(zpl, [b'~A0N,10,20'])

    def testAppendCommandControlCommandWithCT(self):
        zpl = ZPL.ZPL(firmware="V45.11.7ZA")
        zpl.ChangeTilde('x')
        zpl.appendCommand(zpl.CONTROL_COMMAND, "A0", "N", 10, 20)
        self.assertEqual(zpl, [b'^CTx', b'xA0N,10,20'])

    def testChangeInternationalFontEncodingOK(self):
        zpl = ZPL.ZPL(firmware="V45.11.7ZA")
        zpl.ChangeInternationalFontEncoding('cp850')
        self.assertEqual(zpl, [zpl.caret + b'CI13'])

    def testChangeInternationalFontEncodingFirmwareMismatch(self):
        zpl = ZPL.ZPL(firmware="V45.11.7ZA")
        with self.assertRaises(ZPL.ZPLFirmwareMismatch):
            zpl.ChangeInternationalFontEncoding('utf_8')

    def testFieldOriginOldFirmware(self):
        zpl = ZPL.ZPL(firmware="V45.11.7ZA")
        zpl.FieldOrigin(1, 2)
        self.assertEqual(zpl, [b'^FO1,2'])

    def testFieldOriginNewFirmware(self):
        zpl = ZPL.ZPL(firmware="V60.14.7ZA")
        zpl.FieldOrigin(1, 2, 1)
        self.assertEqual(zpl, [b'^FO1,2,1'])

    def testStartFormat(self):
        zpl = ZPL.ZPL(firmware="V45.11.7ZA")
        zpl.StartFormat()
        self.assertEqual(zpl, [b'^XA'])

    def testEndFormat(self):
        zpl = ZPL.ZPL(firmware="V45.11.7ZA")
        zpl.EndFormat()
        self.assertEqual(zpl, [b'^XZ'])

    def testChangeCaret(self):
        zpl = ZPL.ZPL(firmware="V45.11.7ZA")
        zpl.StartFormat()
        zpl.ChangeCaret('x')
        zpl.EndFormat()
        self.assertEqual(zpl.getAllBytes(), b'^XA^CCxxXZ')

    def testChangeDelimeter(self):
        zpl = ZPL.ZPL(firmware="V45.11.7ZA")
        zpl.ChangeDelimiter(';')
        zpl.FieldOrigin(1, 2)
        self.assertEqual(zpl.getAllBytes(), b'^CD;^FO1;2')
