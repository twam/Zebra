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

    def testChangeInternationalFontEncodingOK(self):
        zpl = ZPL.ZPL(firmware="V45.11.7ZA")
        zpl.ChangeInternationalFontEncoding('cp850')
        self.assertEqual(zpl, [b'^CI13'])

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
