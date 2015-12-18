import unittest
import ZPL


class ZPLTests(unittest.TestCase):

    def setUp(self):
        self.zpl = ZPL.ZPL(firmware="V45.11.7ZA")
        pass

    def tearDown(self):
        pass

    def testCheckFirmwareRestrictionsEmptyList(self):
        self.assertTrue(self.zpl.checkFirmwareRestrictions([]))

    def testCheckFirmwareRestrictionsSingle(self):
        self.assertTrue(self.zpl.checkFirmwareRestrictions("V45.11.x"))

    def testCheckFirmwareRestrictionsSingleFail(self):
        self.assertFalse(self.zpl.checkFirmwareRestrictions("V60.14.x"))

    def testCheckFirmwareRestrictionsListFail(self):
        self.assertFalse(self.zpl.checkFirmwareRestrictions(
            ["V60.14.x", "V50.14.x"]))

    def testCheckFirmwareRestrictionsListFail2(self):
        self.assertFalse(self.zpl.checkFirmwareRestrictions(
            ["V60.14.x", "Vx.14.x"]))

    def testCheckFirmwareRestrictionsListOK(self):
        self.assertTrue(self.zpl.checkFirmwareRestrictions(
            ["V60.14.x", "V45.10.x"]))

    def testCheckFirmwareRestrictionsListOK2(self):
        self.assertTrue(self.zpl.checkFirmwareRestrictions(
            ["V60.14.x", "Vx.10.x"]))

    def testGetAllBytes(self):
        self.zpl.append("A")
        self.zpl.append("B")
        self.zpl.append("C")
        self.assertEqual(self.zpl.getAllBytes(), b'ABC')

    def testAppendCommandInvalidCommandTypeType(self):
        with self.assertRaises(TypeError):
            self.zpl.appendCommand(1, 'FO')

    def testAppendCommandInvalidCommandTypeValue(self):
        with self.assertRaises(ValueError):
            self.zpl.appendCommand('x', 'FO')

    def testAppendCommandInvalidCommandType(self):
        with self.assertRaises(TypeError):
            self.zpl.appendCommand(self.zpl.FORMAT_COMMAND, 2)

    def testAppendCommandFormatCommand(self):
        self.zpl.appendCommand(self.zpl.FORMAT_COMMAND, "A0", "N", 10, 20)
        self.assertEqual(self.zpl, [b'^A0N,10,20'])

    def testAppendCommandFormatCommandWithCC(self):
        self.zpl.ChangeCaret('x')
        self.zpl.appendCommand(self.zpl.FORMAT_COMMAND, "A0", "N", 10, 20)
        self.assertEqual(self.zpl, [b'^CCx', b'xA0N,10,20'])

    def testAppendCommandFormatCommandWithCD(self):
        self.zpl.ChangeDelimiter(';')
        self.zpl.appendCommand(self.zpl.FORMAT_COMMAND, "A0", "N", 10, 20)
        self.assertEqual(self.zpl, [b'^CD;', b'^A0N;10;20'])

    def testAppendCommandControlCommand(self):
        self.zpl.appendCommand(self.zpl.CONTROL_COMMAND, "A0", "N", 10, 20)
        self.assertEqual(self.zpl, [b'~A0N,10,20'])

    def testAppendCommandControlCommandWithCT(self):
        self.zpl.ChangeTilde('x')
        self.zpl.appendCommand(self.zpl.CONTROL_COMMAND, "A0", "N", 10, 20)
        self.assertEqual(self.zpl, [b'^CTx', b'xA0N,10,20'])

    def testChangeInternationalFontEncodingOK(self):
        self.zpl.ChangeInternationalFontEncoding('cp850')
        self.assertEqual(self.zpl, [self.zpl.caret + b'CI13'])

    def testChangeInternationalFontEncodingFirmwareMismatch(self):
        with self.assertRaises(ZPL.ZPLFirmwareMismatch):
            self.zpl.ChangeInternationalFontEncoding('utf_8')

    def testFieldOriginOldFirmware(self):
        self.zpl.FieldOrigin(1, 2)
        self.assertEqual(self.zpl, [b'^FO1,2'])

    def testFieldOriginNewFirmware(self):
        self.zpl = ZPL.ZPL(firmware="V60.14.7ZA")
        self.zpl.FieldOrigin(1, 2, 1)
        self.assertEqual(self.zpl, [b'^FO1,2,1'])

    def testStartFormat(self):
        self.zpl.StartFormat()
        self.assertEqual(self.zpl, [b'^XA'])

    def testEndFormat(self):
        self.zpl.EndFormat()
        self.assertEqual(self.zpl, [b'^XZ'])

    def testChangeCaret(self):
        self.zpl.StartFormat()
        self.zpl.ChangeCaret('x')
        self.zpl.EndFormat()
        self.assertEqual(self.zpl.getAllBytes(), b'^XA^CCxxXZ')

    def testChangeDelimeter(self):
        self.zpl.ChangeDelimiter(';')
        self.zpl.FieldOrigin(1, 2)
        self.assertEqual(self.zpl.getAllBytes(), b'^CD;^FO1;2')
